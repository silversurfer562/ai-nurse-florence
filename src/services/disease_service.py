"""
Disease information service following External Service Integration
MyDisease.info API integration from copilot-instructions.md
"""

import asyncio
import importlib
import logging
from types import ModuleType
from typing import Any, Dict, List, Optional, Tuple, cast

from ..utils.config import get_educational_banner, get_settings
from ..utils.exceptions import ExternalServiceException
from ..utils.redis_cache import cached
from .base_service import BaseService

logger = logging.getLogger(__name__)

# Conditional imports following copilot-instructions.md
httpx: Optional[ModuleType] = None
_has_httpx = False
try:
    _httpx_mod = importlib.import_module("httpx")
    httpx = _httpx_mod
    _has_httpx = True
except Exception:
    _has_httpx = False

# Backwards-compatibility: expose legacy names for tests that monkeypatch
_has_requests = _has_httpx  # Use httpx availability for requests compatibility
requests = None


def _requests_get(*args: Any, **kwargs: Any) -> Any:
    """Legacy compatibility helper retained for tests; prefers httpx when available."""
    if _has_httpx and httpx is not None:
        # Use httpx synchronously only if necessary; prefer async paths.
        Client = getattr(httpx, "Client")
        with Client(timeout=10) as client:
            return client.get(*args, **kwargs)
    raise RuntimeError("requests/httpx not available in this environment")


try:
    import importlib

    _mesh_mod = importlib.import_module("src.services.mesh_service")
    map_to_mesh = getattr(_mesh_mod, "map_to_mesh")
    _has_mesh = True
except Exception:

    def map_to_mesh(query: str, top_k: int = 5) -> List[Any]:
        return []

    _has_mesh = False

# Optional prompt enhancement module (graceful degradation)
try:
    import importlib

    _pe_mod = importlib.import_module("src.services.prompt_enhancement")
    enhance_prompt = getattr(_pe_mod, "enhance_prompt")
    _has_prompt_enhancement = True
except Exception:
    _has_prompt_enhancement = False

    def enhance_prompt(prompt: str, purpose: str) -> Tuple[str, bool, None]:
        return prompt, False, None


class DiseaseService(BaseService[Dict[str, Any]]):
    """
    Disease information service using MyDisease.info API
    Following External Service Integration from copilot-instructions.md
    """

    def __init__(self) -> None:
        super().__init__("disease")
        self.base_url = "https://mydisease.info/v1"
        self.settings = get_settings()

    # Settings, logger and helpers are provided; class defines safe fallbacks below

    @cached(ttl_seconds=3600)
    async def lookup_disease(
        self, query: str, include_symptoms: bool = True, include_treatments: bool = True
    ) -> Dict[str, Any]:
        """
        Lookup disease information with caching
        Following Caching Strategy from copilot-instructions.md
        """
        self._log_request(
            query,
            include_symptoms=include_symptoms,
            include_treatments=include_treatments,
        )

        try:
            # Use live service if available and enabled
            if self.settings.USE_LIVE_SERVICES and _has_httpx:
                result = await self._fetch_from_api(
                    query, include_symptoms, include_treatments
                )
                self._log_response(query, True, source="live_api")
                return self._create_response(result, query, source="mydisease_api")
            else:
                # Fallback to stub data
                result = self._create_stub_response(
                    query, include_symptoms, include_treatments
                )
                self._log_response(query, True, source="stub_data")
                return self._create_response(result, query, source="stub_data")

        except Exception as e:
            self._log_response(query, False, error=str(e))
            # Return fallback data instead of raising exception
            fallback_data = self._create_stub_response(
                query, include_symptoms, include_treatments
            )
            return self._handle_external_service_error(e, fallback_data)

    async def _fetch_from_api(
        self, query: str, include_symptoms: bool, include_treatments: bool
    ) -> Dict[str, Any]:
        """Fetch disease data from MyDisease.info API asynchronously using httpx"""
        if not _has_httpx:
            raise ExternalServiceException(
                "httpx library not available", "disease_service"
            )

        # Try MeSH normalization to improve lookup
        try:
            if _has_mesh:
                mesh_matches = map_to_mesh(query, top_k=2)
                if mesh_matches:
                    mesh_term = mesh_matches[0].get("term")
                    if mesh_term:
                        query = mesh_term
        except Exception:
            logger.debug("MeSH normalization failed, continuing with original query")

        # Search for disease
        search_url = f"{self.base_url}/query"
        params = {"q": query, "fields": "mondo,disgenet,ctd", "size": 5}

        AsyncClient = getattr(httpx, "AsyncClient")
        Timeout = getattr(httpx, "Timeout")
        async with AsyncClient(timeout=Timeout(10.0)) as client:
            response = await client.get(search_url, params=params)
            response.raise_for_status()
            data = response.json()
        hits = data.get("hits", [])

        if not hits:
            return self._create_not_found_response(query)

        # Process the first result
        disease_data = hits[0]
        return self._format_disease_data(
            disease_data, include_symptoms, include_treatments
        )

    def _format_disease_data(
        self, raw_data: Dict[str, Any], include_symptoms: bool, include_treatments: bool
    ) -> Dict[str, Any]:
        """Format disease data from API response"""
        mondo_data = raw_data.get("mondo", {})
        disgenet_data = raw_data.get("disgenet", {})

        formatted = {
            "name": mondo_data.get("label", "Unknown condition"),
            "description": mondo_data.get("definition", "No description available"),
            "mondo_id": mondo_data.get("mondo", ""),
            "synonyms": mondo_data.get("synonym", []),
        }

        if include_symptoms:
            formatted["symptoms"] = self._extract_symptoms(disgenet_data)

        if include_treatments:
            formatted["treatments"] = self._extract_treatments(raw_data)

        return formatted

    # Minimal logging helpers in case BaseService doesn't provide them at runtime
    def _log_request(self, *args: Any, **kwargs: Any) -> None:
        logger.debug(f"DiseaseService request: {args} {kwargs}")

    def _log_response(self, *args: Any, **kwargs: Any) -> None:
        logger.debug(f"DiseaseService response: {args} {kwargs}")

    def _handle_external_service_error(
        self, error: Exception, fallback_data: Any = None
    ) -> Dict[str, Any]:
        logger.warning(f"External service error: {error}")
        return fallback_data or {}

    def _extract_symptoms(self, disgenet_data: Dict[str, Any]) -> List[str]:
        """Extract symptoms from DisGeNET data"""
        # Simplified symptom extraction
        return [
            "Symptoms vary by individual",
            "Consult healthcare provider for proper diagnosis",
            "May include common signs and symptoms for this condition",
        ]

    def _extract_treatments(self, raw_data: Dict[str, Any]) -> List[str]:
        """Extract treatment information"""
        return [
            "Treatment should be individualized",
            "Follow evidence-based clinical guidelines",
            "Consult with healthcare team for treatment options",
        ]

    def _create_stub_response(
        self, query: str, include_symptoms: bool, include_treatments: bool
    ) -> Dict[str, Any]:
        """
        Create stub response when live services unavailable
        Following Conditional Imports Pattern from copilot-instructions.md
        """
        stub_data = {
            "name": f"Information about {query}",
            "description": f"This is educational information about {query}. "
            + (
                self.settings.EDUCATIONAL_BANNER
                if hasattr(self, "settings")
                else get_educational_banner()
            ),
            "mondo_id": "MONDO:0000001",
            "synonyms": [query.lower(), query.title()],
        }

        if include_symptoms:
            stub_data["symptoms"] = [
                "Symptoms vary by individual and condition severity",
                "Common signs may include relevant clinical manifestations",
                "Seek healthcare evaluation for proper assessment",
            ]

        if include_treatments:
            stub_data["treatments"] = [
                "Treatment approach depends on individual circumstances",
                "Evidence-based interventions following clinical guidelines",
                "Collaborative care with healthcare team recommended",
            ]

        return stub_data

    def _create_not_found_response(self, query: str) -> Dict[str, Any]:
        """Create response when disease not found"""
        return {
            "name": f"No specific information found for '{query}'",
            "description": "Consider rephrasing your search or consulting medical literature",
            "mondo_id": "",
            "synonyms": [],
            "symptoms": [],
            "treatments": [],
            "suggestions": [
                "Try using medical terminology",
                "Check spelling and try alternative names",
                "Consider broader or more specific terms",
            ],
        }

    async def _process_request(self, query: str, **kwargs: Any) -> Dict[str, Any]:
        """Implementation of abstract method from BaseService (async)"""
        result = await self.lookup_disease(query, **kwargs)
        return cast(Dict[str, Any], result)


# Service factory function following Conditional Imports Pattern
def create_disease_service() -> Optional[DiseaseService]:
    """
    Create disease service with graceful degradation.
    Returns None if service cannot be initialized.
    """
    try:
        return DiseaseService()
    except Exception as e:
        logger.warning(f"Disease service unavailable: {e}")
        return None


async def lookup_disease_info(query: str) -> Dict[str, Any]:
    """
    Look up disease information following External Service Integration pattern.

    Args:
        query: Disease name or condition to look up

    Returns:
        Dict containing disease information with educational banner
    """
    settings = get_settings()
    banner = get_educational_banner()

    try:
        # Enhance prompt for better search results
        if _has_prompt_enhancement:
            effective_query, needs_clarification, clarification_question = (
                enhance_prompt(query, "disease_lookup")
            )

            if needs_clarification:
                return {
                    "banner": banner,
                    "query": query,
                    "needs_clarification": True,
                    "clarification_question": clarification_question,
                }
        else:
            effective_query = query

        # Extract medical terms from natural language queries
        medical_query = _extract_medical_terms(effective_query)
        logger.info(f"Query transformation: '{effective_query}' -> '{medical_query}'")

        # Use live MyDisease.info API if available and enabled
        if settings.effective_use_live_services and _has_httpx:
            try:
                result = await _lookup_disease_live(medical_query)
                result["banner"] = banner
                result["query"] = query
                return result

            except Exception as e:
                logger.warning(f"MyDisease.info API failed, using stub response: {e}")

        # Fallback stub response following Conditional Imports Pattern
        return _create_disease_stub_response(query, banner)

    except Exception as e:
        logger.error(f"Disease lookup failed: {e}")
        return _create_disease_stub_response(query, banner)


async def search_disease_conditions(query: str, limit: int = 10) -> Dict[str, Any]:
    """
    Search for disease conditions with autocomplete functionality.
    Returns MONDO disease ontology terms for guided form input.
    """
    settings = get_settings()

    try:
        if settings.effective_use_live_services and _has_httpx:
            results = await _search_conditions_live(query, limit)
            return {
                "suggestions": results,
                "total_results": len(results)
            }
        else:
            # Fallback to predefined common conditions
            return _get_common_conditions_stub(query, limit)

    except Exception as e:
        logger.warning(f"Condition search failed: {e}")
        return _get_common_conditions_stub(query, limit)


async def _search_conditions_live(query: str, limit: int) -> List[Dict[str, Any]]:
    """Search live MyDisease.info API for condition suggestions."""
    base_url = "https://mydisease.info/v1/query"

    # Build search query for better autocomplete results
    search_query = f"{query}*"  # Wildcard search for prefix matching

    params = {
        "q": search_query,
        "fields": "mondo.label,mondo.mondo,mondo.definition,mondo.synonym",
        "size": limit * 2,  # Get more results to filter and rank
        "from": 0
    }

    if not _has_httpx:
        raise ExternalServiceException("httpx not available", "disease_service")

    AsyncClient = getattr(httpx, "AsyncClient")
    Timeout = getattr(httpx, "Timeout")

    async with AsyncClient(timeout=Timeout(10.0)) as client:
        response = await client.get(base_url, params=params)
        response.raise_for_status()
        data = response.json()

    hits = data.get("hits", [])
    suggestions = []

    for hit in hits[:limit]:
        mondo_data = hit.get("mondo", {})
        if not mondo_data:
            continue

        name = mondo_data.get("label", "")
        mondo_id = mondo_data.get("mondo", "")
        definition = mondo_data.get("definition", "")

        # Extract synonyms
        synonyms = []
        synonym_data = mondo_data.get("synonym", {})
        if isinstance(synonym_data, dict):
            exact_synonyms = synonym_data.get("exact", [])
            synonyms.extend(exact_synonyms[:3])  # Limit synonyms
        elif isinstance(synonym_data, list):
            synonyms.extend(synonym_data[:3])

        if name and mondo_id:
            suggestions.append({
                "name": name,
                "mondo_id": mondo_id,
                "description": definition[:200] + "..." if len(definition) > 200 else definition,
                "synonyms": synonyms
            })

    return suggestions


def _get_common_conditions_stub(query: str, limit: int) -> Dict[str, Any]:
    """Fallback stub with common medical conditions for autocomplete."""

    common_conditions = [
        {
            "name": "diabetes mellitus",
            "mondo_id": "MONDO:0005015",
            "description": "A metabolic disorder characterized by high blood glucose levels.",
            "synonyms": ["diabetes", "DM"]
        },
        {
            "name": "hypertension",
            "mondo_id": "MONDO:0005044",
            "description": "Persistent high arterial blood pressure.",
            "synonyms": ["high blood pressure", "HTN"]
        },
        {
            "name": "pneumonia",
            "mondo_id": "MONDO:0005249",
            "description": "Infection that inflames air sacs in lungs.",
            "synonyms": ["lung infection"]
        },
        {
            "name": "breast cancer",
            "mondo_id": "MONDO:0007254",
            "description": "Cancer that forms in tissues of the breast.",
            "synonyms": ["breast carcinoma", "mammary cancer"]
        },
        {
            "name": "heart failure",
            "mondo_id": "MONDO:0005252",
            "description": "Condition where heart cannot pump blood effectively.",
            "synonyms": ["cardiac failure", "CHF"]
        },
        {
            "name": "asthma",
            "mondo_id": "MONDO:0004979",
            "description": "Respiratory condition with inflamed airways.",
            "synonyms": ["bronchial asthma"]
        },
        {
            "name": "stroke",
            "mondo_id": "MONDO:0005098",
            "description": "Interruption of blood supply to brain.",
            "synonyms": ["cerebrovascular accident", "CVA"]
        },
        {
            "name": "depression",
            "mondo_id": "MONDO:0002050",
            "description": "Mental health disorder causing persistent sadness.",
            "synonyms": ["major depressive disorder", "MDD"]
        }
    ]

    # Filter conditions based on query
    query_lower = query.lower()
    filtered_conditions = []

    for condition in common_conditions:
        # Check if query matches name or synonyms
        condition_name = str(condition["name"])
        condition_synonyms = condition.get("synonyms", [])

        name_match = query_lower in condition_name.lower()
        synonym_match = any(query_lower in str(syn).lower() for syn in condition_synonyms)

        if name_match or synonym_match:
            filtered_conditions.append(condition)

    # Return up to limit results
    results = filtered_conditions[:limit]

    return {
        "suggestions": results,
        "total_results": len(filtered_conditions)
    }


def _extract_medical_terms(query: str) -> str:
    """
    Extract medical terms from natural language queries.
    Converts questions like "tell me about breast cancer symptoms" to "breast cancer"
    """
    import re

    # Convert to lowercase for processing
    lower_query = query.lower().strip()

    # Remove common question words and phrases
    question_patterns = [
        r'^(what is|what are|tell me about|information about|describe|explain)\s+',
        r'\s+(symptoms?|treatment|causes?|diagnosis|prognosis|management)$',
        r'^(how to|can you|please)\s+',
        r'\s+(please|thank you)$'
    ]

    medical_terms = lower_query
    for pattern in question_patterns:
        medical_terms = re.sub(pattern, '', medical_terms).strip()

    # Handle specific medical term extractions
    medical_conditions = [
        r'(diabetes mellitus|diabetes)',
        r'(breast cancer|mammary carcinoma)',
        r'(lung cancer|pulmonary carcinoma)',
        r'(hypertension|high blood pressure)',
        r'(heart failure|cardiac failure)',
        r'(pneumonia)',
        r'(asthma|bronchial asthma)',
        r'(depression|major depressive disorder)',
        r'(anxiety|anxiety disorder)',
        r'(alzheimer|dementia)',
        r'(stroke|cerebrovascular accident)',
        r'(kidney disease|renal disease)',
        r'(arthritis|osteoarthritis|rheumatoid arthritis)',
    ]

    # Check for known medical conditions
    for condition_pattern in medical_conditions:
        match = re.search(condition_pattern, medical_terms)
        if match:
            # Return the most specific term (usually the first in the group)
            return match.group(1)

    # If no specific condition found, look for any medical terms
    # Extract potential disease names (usually nouns that could be conditions)
    medical_keywords = [
        'cancer', 'carcinoma', 'tumor', 'malignancy', 'neoplasm',
        'diabetes', 'hypertension', 'hypotension', 'tachycardia', 'bradycardia',
        'pneumonia', 'bronchitis', 'asthma', 'copd',
        'arthritis', 'osteoporosis', 'fracture',
        'infection', 'sepsis', 'fever',
        'cardiac', 'pulmonary', 'renal', 'hepatic', 'neurologic',
        'syndrome', 'disease', 'disorder', 'condition',
        'failure', 'insufficiency', 'dysfunction'
    ]

    # Look for medical keywords in the query
    words = medical_terms.split()
    medical_terms_found = []

    for word in words:
        # Check if word contains or is a medical keyword
        for keyword in medical_keywords:
            if keyword in word.lower() or word.lower() in keyword:
                medical_terms_found.append(word)
                break

    # If we found medical terms, use those
    if medical_terms_found:
        return ' '.join(medical_terms_found)

    # Remove articles and common words as fallback
    stop_words = ['a', 'an', 'the', 'of', 'in', 'on', 'at', 'to', 'for', 'with', 'by', 'about', 'treatment', 'symptoms', 'causes', 'diagnosis']
    words = medical_terms.split()
    filtered_words = [word for word in words if word.lower() not in stop_words and len(word) > 2]

    # If we have filtered words, return them joined
    if filtered_words:
        return ' '.join(filtered_words)    # Fallback to original query if nothing else works
    return query.strip()


async def _lookup_disease_live(query: str) -> Dict[str, Any]:
    """Look up disease using live MyDisease.info API following External Service Integration."""

    # MyDisease.info API
    base_url = "https://mydisease.info/v1/query"

    params: dict[str, str | int | float | bool | None] = {
        "q": query,
        "fields": "disease_ontology,mondo,summary",
        "size": 1,
    }

    if _has_httpx and httpx is not None:
        # runtime check above ensures httpx is present; narrow for static checkers
        AsyncClient = getattr(httpx, "AsyncClient")
        Timeout = getattr(httpx, "Timeout")
        async with AsyncClient(timeout=Timeout(10.0)) as client:
            response = await client.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
    else:
        # Call synchronous helper in a thread to avoid blocking the event loop
        if _requests_get is None:
            raise RuntimeError(
                "requests/httpx helper not available in this environment"
            )
        response = await asyncio.to_thread(
            _requests_get, base_url, {"params": params, "timeout": 10}
        )
        response.raise_for_status()
        data = response.json()

    hits = data.get("hits", [])
    if hits:
        disease_data = hits[0]
        return _format_comprehensive_disease_response(disease_data, query)
    else:
        return {
            "summary": f"No specific information found for '{query}'. Consult medical literature.",
            "description": "Disease information not available in database",
            "symptoms": [],
            "sources": ["MyDisease.info"],
        }


def _format_comprehensive_disease_response(disease_data: Dict[str, Any], query: str) -> Dict[str, Any]:
    """
    Format comprehensive disease response with structured medical information,
    citations, and links using template-guided construction.
    """
    mondo_data = disease_data.get("mondo", {})

    # Primary disease information
    primary_name = mondo_data.get("label", query)
    mondo_id = mondo_data.get("mondo", "")
    definition = mondo_data.get("definition", "")

    # Extract synonyms and alternative names
    synonyms = _extract_synonyms(mondo_data)

    # Extract related MONDO terms (ancestors, children, descendants)
    related_mondos = _extract_related_mondos(mondo_data)

    # Extract and format citations
    citations = _extract_citations(definition)

    # Extract external resources and links
    external_links = _extract_external_links(mondo_data)

    # Build structured summary using template
    summary = _build_disease_summary_template(
        primary_name=primary_name,
        mondo_id=mondo_id,
        definition=definition,
        synonyms=synonyms,
        related_mondos=related_mondos,
        citations=citations,
        external_links=external_links
    )

    # Build clinical sources list
    sources = _build_sources_list(citations, external_links)

    # Enhanced symptoms/clinical guidance
    clinical_guidance = _build_clinical_guidance(primary_name, mondo_id)

    return {
        "summary": summary,
        "description": definition,
        "symptoms": clinical_guidance,
        "sources": sources,
    }


def _extract_synonyms(mondo_data: Dict[str, Any]) -> List[str]:
    """Extract synonyms and alternative names from MONDO data."""
    synonyms = []
    if "synonym" in mondo_data:
        synonym_data = mondo_data["synonym"]
        if isinstance(synonym_data, dict):
            # Extract exact synonyms
            exact_synonyms = synonym_data.get("exact", [])
            synonyms.extend(exact_synonyms)
            # Also get related synonyms if available
            related_synonyms = synonym_data.get("related", [])
            synonyms.extend(related_synonyms[:3])  # Limit related synonyms
        elif isinstance(synonym_data, list):
            synonyms.extend(synonym_data)

    # Remove duplicates and limit to 7 total
    return list(dict.fromkeys(synonyms))[:7]


def _extract_related_mondos(mondo_data: Dict[str, Any]) -> Dict[str, List[str]]:
    """Extract related MONDO terms with their relationships."""
    related = {
        "parents": mondo_data.get("parents", [])[:3],
        "children": mondo_data.get("children", [])[:5],
        "ancestors": mondo_data.get("ancestors", [])[:3]
    }

    # Filter out empty lists
    return {k: v for k, v in related.items() if v}


def _extract_citations(definition: str) -> List[Dict[str, str]]:
    """Extract citations from definition text."""
    import re

    citations = []

    # Extract PMID citations
    pmid_matches = re.findall(r'PMID:(\d+)', definition)
    for pmid in pmid_matches:
        citations.append({
            "type": "PubMed",
            "id": pmid,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "display": f"PMID:{pmid}"
        })

    # Extract DOI citations
    doi_matches = re.findall(r'https://doi\.org/([\w\.\-/]+)', definition)
    for doi in doi_matches:
        citations.append({
            "type": "DOI",
            "id": doi,
            "url": f"https://doi.org/{doi}",
            "display": f"DOI:{doi}"
        })

    # Extract other URLs
    url_matches = re.findall(r'https?://[^\s\]]+', definition)
    for url in url_matches:
        if 'doi.org' not in url and 'pubmed' not in url:
            citations.append({
                "type": "URL",
                "id": url,
                "url": url,
                "display": url
            })

    return citations


def _extract_external_links(mondo_data: Dict[str, Any]) -> List[Dict[str, str]]:
    """Extract external resource links from MONDO data."""
    links = []

    # Curated content resources
    curated_resources = mondo_data.get("curated_content_resource", {})
    if "https" in curated_resources:
        for url in curated_resources["https"]:
            links.append({
                "type": "Clinical Resource",
                "url": url,
                "display": "ClinicalGenome Knowledge Base" if "clinicalgenome" in url else "Medical Resource"
            })

    # Cross-references
    xrefs = mondo_data.get("xrefs", {})
    for db_name, ids in xrefs.items():
        if db_name == "orphanet":
            for orphanet_id in ids[:2]:  # Limit to 2
                links.append({
                    "type": "Orphanet",
                    "url": f"https://www.orpha.net/consor/cgi-bin/Disease_Search.php?lng=EN&data_id={orphanet_id}",
                    "display": f"Orphanet:{orphanet_id}"
                })
        elif db_name == "ncit":
            for ncit_id in ids[:1]:  # Limit to 1
                links.append({
                    "type": "NCI Thesaurus",
                    "url": f"https://ncithesaurus.nci.nih.gov/ncitbrowser/ConceptReport.jsp?dictionary=NCI_Thesaurus&code={ncit_id}",
                    "display": f"NCIT:{ncit_id}"
                })

    return links


def _build_disease_summary_template(
    primary_name: str,
    mondo_id: str,
    definition: str,
    synonyms: List[str],
    related_mondos: Dict[str, List[str]],
    citations: List[Dict[str, str]],
    external_links: List[Dict[str, str]]
) -> str:
    """Build comprehensive disease summary using structured template."""

    template_parts = []

    # Header with primary disease name and classification
    template_parts.append(f"# {primary_name}")
    if mondo_id:
        template_parts.append(f"**Medical Classification:** {mondo_id}")

    # Clinical definition
    if definition:
        # Clean up definition (remove citation markers for cleaner display)
        clean_definition = definition
        import re
        clean_definition = re.sub(r'\s*\[https?://[^\]]+\]', '', clean_definition)
        clean_definition = re.sub(r'\s*PMID:\d+', '', clean_definition)
        template_parts.append(f"\n**Clinical Definition:**\n{clean_definition}")

    # Synonyms and alternative terms
    if synonyms:
        synonym_text = ", ".join(synonyms[:5])
        template_parts.append(f"\n**Also Known As:** {synonym_text}")

    # Related conditions (disease hierarchy)
    if related_mondos:
        template_parts.append("\n**Related Conditions:**")
        if "parents" in related_mondos:
            template_parts.append(f"• *Broader categories:* {', '.join(related_mondos['parents'])}")
        if "children" in related_mondos:
            template_parts.append(f"• *Subtypes:* {', '.join(related_mondos['children'][:3])}")

    # Citations and evidence
    if citations:
        template_parts.append("\n**Evidence & Citations:**")
        for citation in citations[:3]:  # Limit to 3 most relevant
            if citation["type"] == "PubMed":
                template_parts.append(f"• [{citation['display']}]({citation['url']}) *(opens in new tab)*")
            elif citation["type"] == "DOI":
                template_parts.append(f"• [Research Article: {citation['display']}]({citation['url']}) *(opens in new tab)*")
            else:
                template_parts.append(f"• [Reference]({citation['url']}) *(opens in new tab)*")

    # External medical resources
    if external_links:
        template_parts.append("\n**Additional Resources:**")
        for link in external_links[:3]:  # Limit to 3 most relevant
            template_parts.append(f"• [{link['display']}]({link['url']}) *(opens in new tab)*")

    return "\n".join(template_parts)


def _build_sources_list(citations: List[Dict[str, str]], external_links: List[Dict[str, str]]) -> List[str]:
    """Build comprehensive sources list for API response."""
    sources = ["MyDisease.info API", "MONDO Disease Ontology"]

    # Add citation sources
    for citation in citations:
        if citation["type"] == "PubMed":
            sources.append("PubMed Literature Database")
        elif citation["type"] == "DOI":
            sources.append("Peer-Reviewed Medical Literature")

    # Add external resource sources
    for link in external_links:
        if link["type"] not in [s.replace(" Database", "").replace(" Knowledge Base", "") for s in sources]:
            sources.append(f"{link['type']} Database")

    # Remove duplicates while preserving order
    return list(dict.fromkeys(sources))


def _build_clinical_guidance(primary_name: str, mondo_id: str) -> List[str]:
    """Build clinical guidance based on disease type and classification."""
    guidance = [
        f"Review clinical guidelines for {primary_name.lower()} diagnosis and management",
        "Consult evidence-based protocols for patient assessment",
        "Follow institutional policies for condition-specific care"
    ]

    # Add specific guidance based on disease characteristics
    if any(keyword in primary_name.lower() for keyword in ['diabetes', 'glucose', 'insulin']):
        guidance.extend([
            "Monitor blood glucose levels per protocol",
            "Assess for diabetic complications (neuropathy, nephropathy, retinopathy)",
            "Review medication adherence and dietary compliance"
        ])
    elif any(keyword in primary_name.lower() for keyword in ['hypertension', 'blood pressure']):
        guidance.extend([
            "Monitor blood pressure trends and medication effectiveness",
            "Assess for target organ damage",
            "Evaluate cardiovascular risk factors"
        ])
    elif any(keyword in primary_name.lower() for keyword in ['cardiac', 'heart', 'cardiovascular']):
        guidance.extend([
            "Monitor cardiac rhythm and hemodynamic status",
            "Assess functional capacity and exercise tolerance",
            "Review cardiac medications and contraindications"
        ])
    else:
        guidance.extend([
            "Conduct systematic symptom assessment",
            "Document functional impact and quality of life measures",
            "Coordinate with interdisciplinary healthcare team"
        ])

    if mondo_id:
        guidance.append(f"Reference MONDO classification {mondo_id} for additional clinical details")

    return guidance


def _create_disease_stub_response(query: str, banner: str) -> Dict[str, Any]:
    """Create stub response for disease lookup following Conditional Imports Pattern."""

    return {
        "banner": banner,
        "query": query,
        "summary": f"Educational information about {query}. This is stub data - use live services for actual medical information.",
        "description": f"{query} is a medical condition that requires professional healthcare guidance.",
        "symptoms": [
            "Consult healthcare provider for symptoms",
            "Review medical literature for detailed information",
            "Seek professional medical advice",
        ],
        "sources": ["Educational stub data"],
        "needs_clarification": False,
    }
