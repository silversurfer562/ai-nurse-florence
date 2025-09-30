"""
Drug Interaction Service - AI Nurse Florence
Phase 4.2: Additional Medical Services

Provides comprehensive drug interaction checking with smart caching,
severity assessment, and clinical decision support.
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

# Import utilities following conditional imports pattern
try:
    from src.utils.smart_cache import smart_cache_manager, CacheStrategy
    _has_smart_cache = True
except ImportError:
    _has_smart_cache = False
    smart_cache_manager = None  # type: ignore
    CacheStrategy = None  # type: ignore

try:
    from src.utils.config import get_settings
    _has_config = True
except ImportError:
    _has_config = False
    def get_settings():  # type: ignore
        return type('Settings', (), {'educational_banner': 'Educational use only - not medical advice'})()

try:
    import httpx
    _has_httpx = True
except ImportError:
    _has_httpx = False
    httpx = None  # type: ignore

logger = logging.getLogger(__name__)

class InteractionSeverity(Enum):
    """Drug interaction severity levels."""
    MINOR = "minor"
    MODERATE = "moderate"
    MAJOR = "major"
    CONTRAINDICATED = "contraindicated"

class InteractionMechanism(Enum):
    """Drug interaction mechanisms."""
    PHARMACOKINETIC = "pharmacokinetic"      # Absorption, distribution, metabolism, excretion
    PHARMACODYNAMIC = "pharmacodynamic"      # Additive, synergistic, antagonistic effects
    PHARMACEUTICAL = "pharmaceutical"        # Physical/chemical incompatibility
    UNKNOWN = "unknown"

@dataclass
class Drug:
    """Drug information structure."""
    name: str
    generic_name: str
    brand_names: List[str]
    drug_class: str
    route: str
    dosage: Optional[str] = None
    indication: Optional[str] = None

@dataclass
class DrugInteraction:
    """Drug interaction result structure."""
    drug1: Drug
    drug2: Drug
    severity: InteractionSeverity
    mechanism: InteractionMechanism
    description: str
    clinical_significance: str
    recommendations: List[str]
    evidence_level: str
    onset: str  # rapid, delayed
    documentation: str  # excellent, good, fair, poor
    references: List[str]

class DrugInteractionService:
    """
    Drug interaction checking service with smart caching and clinical decision support.
    
    Features:
    - Comprehensive drug interaction database
    - Smart caching with drug-specific strategies
    - Severity-based risk assessment
    - Clinical recommendations and alternatives
    - Real-time interaction alerts
    - Evidence-based interaction data
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.cache_enabled = _has_smart_cache and smart_cache_manager is not None
        self.session = None
        
        # Initialize drug database (in production, this would be a real database)
        self._init_drug_database()
        
        if self.cache_enabled:
            logger.info("Drug interaction service initialized with smart caching")
        else:
            logger.info("Drug interaction service initialized without smart caching")
    
    def _init_drug_database(self):
        """Initialize drug database with common medications."""
        self.drugs_db = {
            # Cardiovascular medications
            "warfarin": Drug(
                name="warfarin", generic_name="warfarin", brand_names=["Coumadin", "Jantoven"],
                drug_class="anticoagulant", route="oral"
            ),
            "aspirin": Drug(
                name="aspirin", generic_name="aspirin", brand_names=["Bayer", "Ecotrin"],
                drug_class="antiplatelet", route="oral"
            ),
            "metoprolol": Drug(
                name="metoprolol", generic_name="metoprolol", brand_names=["Lopressor", "Toprol-XL"],
                drug_class="beta_blocker", route="oral"
            ),
            "lisinopril": Drug(
                name="lisinopril", generic_name="lisinopril", brand_names=["Prinivil", "Zestril"],
                drug_class="ace_inhibitor", route="oral"
            ),
            
            # Diabetes medications
            "metformin": Drug(
                name="metformin", generic_name="metformin", brand_names=["Glucophage", "Fortamet"],
                drug_class="biguanide", route="oral"
            ),
            "insulin": Drug(
                name="insulin", generic_name="insulin", brand_names=["Humulin", "Novolin"],
                drug_class="hormone", route="injection"
            ),
            
            # Antibiotics
            "amoxicillin": Drug(
                name="amoxicillin", generic_name="amoxicillin", brand_names=["Amoxil", "Trimox"],
                drug_class="penicillin", route="oral"
            ),
            "ciprofloxacin": Drug(
                name="ciprofloxacin", generic_name="ciprofloxacin", brand_names=["Cipro"],
                drug_class="fluoroquinolone", route="oral"
            ),
            
            # Pain medications
            "ibuprofen": Drug(
                name="ibuprofen", generic_name="ibuprofen", brand_names=["Advil", "Motrin"],
                drug_class="nsaid", route="oral"
            ),
            "acetaminophen": Drug(
                name="acetaminophen", generic_name="acetaminophen", brand_names=["Tylenol"],
                drug_class="analgesic", route="oral"
            )
        }
        
        # Initialize interaction rules
        self._init_interaction_rules()
    
    def _init_interaction_rules(self):
        """Initialize drug interaction rules."""
        self.interaction_rules = [
            # Major interactions
            {
                "drugs": ["warfarin", "aspirin"],
                "severity": InteractionSeverity.MAJOR,
                "mechanism": InteractionMechanism.PHARMACODYNAMIC,
                "description": "Increased risk of bleeding due to additive anticoagulant effects",
                "clinical_significance": "Significantly increased bleeding risk requiring close monitoring",
                "recommendations": [
                    "Monitor INR closely if combination necessary",
                    "Consider alternative antiplatelet if appropriate",
                    "Educate patient on bleeding precautions",
                    "Consider PPI for GI protection"
                ],
                "evidence_level": "1A",
                "onset": "delayed",
                "documentation": "excellent"
            },
            {
                "drugs": ["warfarin", "ciprofloxacin"],
                "severity": InteractionSeverity.MAJOR,
                "mechanism": InteractionMechanism.PHARMACOKINETIC,
                "description": "Ciprofloxacin inhibits warfarin metabolism, increasing anticoagulant effect",
                "clinical_significance": "Significant increase in INR and bleeding risk",
                "recommendations": [
                    "Monitor INR closely during and after ciprofloxacin therapy",
                    "Consider warfarin dose reduction",
                    "Consider alternative antibiotic if possible",
                    "Monitor for signs of bleeding"
                ],
                "evidence_level": "1A",
                "onset": "delayed",
                "documentation": "excellent"
            },
            
            # Moderate interactions
            {
                "drugs": ["metoprolol", "insulin"],
                "severity": InteractionSeverity.MODERATE,
                "mechanism": InteractionMechanism.PHARMACODYNAMIC,
                "description": "Beta-blockers may mask hypoglycemic symptoms",
                "clinical_significance": "Reduced awareness of hypoglycemic episodes",
                "recommendations": [
                    "Monitor blood glucose more frequently",
                    "Educate patient on non-adrenergic hypoglycemic symptoms",
                    "Consider cardioselective beta-blocker",
                    "Ensure patient has glucose monitoring supplies"
                ],
                "evidence_level": "2A",
                "onset": "rapid",
                "documentation": "good"
            },
            {
                "drugs": ["lisinopril", "ibuprofen"],
                "severity": InteractionSeverity.MODERATE,
                "mechanism": InteractionMechanism.PHARMACODYNAMIC,
                "description": "NSAIDs may reduce antihypertensive effectiveness",
                "clinical_significance": "Potential reduction in blood pressure control",
                "recommendations": [
                    "Monitor blood pressure regularly",
                    "Consider acetaminophen for pain relief",
                    "Use lowest effective NSAID dose for shortest duration",
                    "Monitor renal function"
                ],
                "evidence_level": "2A",
                "onset": "delayed",
                "documentation": "good"
            },
            
            # Minor interactions
            {
                "drugs": ["metformin", "acetaminophen"],
                "severity": InteractionSeverity.MINOR,
                "mechanism": InteractionMechanism.PHARMACOKINETIC,
                "description": "Minimal clinical significance with normal doses",
                "clinical_significance": "Generally not clinically significant",
                "recommendations": [
                    "No dosage adjustment typically needed",
                    "Monitor if high doses used chronically"
                ],
                "evidence_level": "3",
                "onset": "delayed",
                "documentation": "fair"
            }
        ]
    
    def _normalize_drug_name(self, drug_name: str) -> str:
        """Normalize drug name for lookup."""
        # Remove common suffixes and normalize case
        normalized = drug_name.lower().strip()
        normalized = re.sub(r'\s+(xl|xr|er|sr|cr|la|cd)$', '', normalized)
        normalized = re.sub(r'\s+\d+\s*mg$', '', normalized)
        normalized = re.sub(r'[^\w\s]', '', normalized)
        return normalized.strip()
    
    def _find_drug_in_database(self, drug_name: str) -> Optional[Drug]:
        """Find drug in database by name or brand name."""
        normalized_name = self._normalize_drug_name(drug_name)
        
        # Direct lookup
        if normalized_name in self.drugs_db:
            return self.drugs_db[normalized_name]
        
        # Search by brand names
        for drug in self.drugs_db.values():
            for brand in drug.brand_names:
                if self._normalize_drug_name(brand) == normalized_name:
                    return drug
        
        return None
    
    async def _get_session(self):  # type: ignore
        """Get or create HTTP session for external API calls."""
        if not _has_httpx or httpx is None:
            return None
            
        if self.session is None:
            self.session = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0),
                headers={
                    "User-Agent": "AI-Nurse-Florence/2.1.0 (Drug Interaction Checker)",
                    "Accept": "application/json"
                }
            )
        return self.session
    
    def _create_cache_key(self, drug_list: List[str]) -> str:
        """Create cache key for drug interaction check."""
        sorted_drugs = sorted([self._normalize_drug_name(drug) for drug in drug_list])
        return f"drug_interactions_{'_'.join(sorted_drugs)}"

    async def _check_interactions_with_openai(
        self,
        drugs: List[str],
        patient_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Use OpenAI to check for drug interactions."""
        try:
            # Get OpenAI service from service registry
            from src.services import get_service
            openai_service = get_service('openai')
            if not openai_service:
                raise Exception("OpenAI service not available")
        except Exception as e:
            raise Exception(f"OpenAI service not available: {e}")

        # Build the prompt
        drug_list = ", ".join(drugs)
        prompt = f"""Analyze the following medications for a nurse's clinical reference: {drug_list}

Please provide TWO sections:

SECTION 1 - Individual Drug Information:
For EACH medication in the list, provide:
1. Drug name (generic and common brand names)
2. Drug class/category
3. Primary indication (what it's used for)
4. Key nursing considerations (monitoring, administration)
5. Common side effects nurses should watch for
6. Important contraindications or warnings

SECTION 2 - Drug Interactions:
For each pair of medications that have clinically significant interactions, provide:
1. Drug names (drug1 and drug2)
2. Severity level (minor, moderate, major, or contraindicated)
3. Mechanism of interaction (pharmacokinetic, pharmacodynamic, pharmaceutical, or unknown)
4. Description of the interaction
5. Clinical significance
6. Specific clinical recommendations (as a list)
7. Evidence level (1A, 1B, 2A, 2B, 3, or expert opinion)
8. Onset (rapid or delayed)
9. Documentation quality (excellent, good, fair, or poor)

{"Patient context: " + str(patient_context) if patient_context else ""}

Return the response in JSON format with this structure:
{{
  "drug_information": [
    {{
      "name": "drug name (generic)",
      "brand_names": ["brand1", "brand2"],
      "drug_class": "therapeutic class",
      "indication": "primary use",
      "nursing_considerations": ["consideration 1", "consideration 2"],
      "common_side_effects": ["side effect 1", "side effect 2"],
      "warnings": ["warning 1", "warning 2"]
    }}
  ],
  "interactions": [
    {{
      "drug1": "drug name",
      "drug2": "drug name",
      "severity": "major|moderate|minor|contraindicated",
      "mechanism": "pharmacokinetic|pharmacodynamic|pharmaceutical|unknown",
      "description": "detailed description",
      "clinical_significance": "clinical impact statement",
      "recommendations": ["recommendation 1", "recommendation 2", ...],
      "evidence_level": "1A|1B|2A|2B|3|expert opinion",
      "onset": "rapid|delayed",
      "documentation": "excellent|good|fair|poor"
    }}
  ],
  "summary": "overall summary including individual drugs and interaction risk",
  "clinical_alerts": ["alert 1", "alert 2", ...]
}}

If there are no significant interactions, return an empty interactions array but ALWAYS include drug_information for all medications."""

        # Call OpenAI
        try:
            import json
            # Use generate_response with context for better medical accuracy
            context = "You are analyzing drug interactions. Provide accurate, evidence-based medical information in the exact JSON format requested."
            openai_response = await openai_service.generate_response(prompt, context)
            response_text = openai_response.get("response", "")

            # Log response details for debugging
            logger.info(f"OpenAI response keys: {list(openai_response.keys())}")
            logger.info(f"OpenAI response text length: {len(response_text)}")
            if len(response_text) == 0:
                logger.error(f"Empty response from OpenAI. Full response: {openai_response}")
                raise Exception(f"Empty response from OpenAI service. Service status: {openai_response.get('service_note', 'unknown')}")

            # Parse JSON from response
            # Try to extract JSON from markdown code blocks if present
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()

            ai_response = json.loads(json_str)

            # Build standardized response
            banner = getattr(self.settings, 'educational_banner', 'Educational use only - not medical advice')
            return {
                "banner": banner,
                "drugs_checked": drugs,
                "drug_information": ai_response.get("drug_information", []),
                "total_interactions": len(ai_response.get("interactions", [])),
                "interactions": ai_response.get("interactions", []),
                "summary": ai_response.get("summary", ""),
                "clinical_alerts": ai_response.get("clinical_alerts", []),
                "patient_context": patient_context,
                "data_source": "OpenAI (Medical AI)",
                "service_note": "AI-generated analysis based on medical literature. Verify with authoritative sources.",
                "timestamp": datetime.now().isoformat()
            }

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse OpenAI response as JSON: {e}")
            logger.debug(f"OpenAI response: {response_text[:500]}")
            raise Exception(f"Failed to parse AI response: {str(e)}")
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise

    async def _get_drug_info_from_database(self, drug_names: List[str]) -> List[Dict[str, Any]]:
        """Retrieve detailed drug information from database."""
        try:
            from src.models.database import get_db_session, Medication
            from sqlalchemy import select
            import json as json_module

            drug_info_list = []

            async for session in get_db_session():
                for drug_name in drug_names:
                    # Search for medication (case-insensitive)
                    query = select(Medication).where(
                        Medication.name.ilike(drug_name)
                    ).where(Medication.is_active == True)

                    result = await session.execute(query)
                    medication = result.scalar_one_or_none()

                    if medication and medication.brand_names:
                        # Parse JSON fields
                        brand_names = json_module.loads(medication.brand_names) if medication.brand_names else []
                        nursing_considerations = json_module.loads(medication.nursing_considerations) if medication.nursing_considerations else []
                        common_side_effects = json_module.loads(medication.common_side_effects) if medication.common_side_effects else []
                        warnings = json_module.loads(medication.warnings) if medication.warnings else []

                        drug_info_list.append({
                            "name": medication.name,
                            "brand_names": brand_names,
                            "drug_class": medication.drug_class or "N/A",
                            "indication": medication.indication or "N/A",
                            "nursing_considerations": nursing_considerations,
                            "common_side_effects": common_side_effects,
                            "warnings": warnings
                        })
                        logger.info(f"Found detailed info for {medication.name} in database")

            return drug_info_list

        except Exception as e:
            logger.warning(f"Failed to get drug info from database: {e}")
            return []

    async def check_drug_interactions(
        self,
        drugs: List[str],
        patient_context: Optional[Dict[str, Any]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Check for drug interactions in a medication list.
        First tries to get detailed info from database, then falls back to OpenAI if needed.

        Args:
            drugs: List of drug names to check
            patient_context: Optional patient context (age, conditions, etc.)
            use_cache: Whether to use caching

        Returns:
            Drug interaction results with recommendations
        """
        start_time = datetime.now()

        if len(drugs) < 2:
            return {
                "banner": getattr(self.settings, 'educational_banner', 'Educational use only - not medical advice'),
                "message": "At least 2 drugs required for interaction checking",
                "drugs_provided": len(drugs),
                "timestamp": datetime.now().isoformat()
            }

        # Check cache first
        cache_key = self._create_cache_key(drugs)
        cached_result = None

        if use_cache and self.cache_enabled and smart_cache_manager and CacheStrategy:
            try:
                cached_result = await smart_cache_manager.smart_cache_get(
                    CacheStrategy.MEDICAL_REFERENCE,
                    f"interactions_{cache_key}",
                    drugs=drugs
                )
            except Exception as e:
                logger.warning(f"Cache retrieval failed: {e}")

        if cached_result:
            logger.info(f"Drug interaction cache hit for: {drugs}")
            cached_result["cache_hit"] = True
            cached_result["response_time_ms"] = (datetime.now() - start_time).total_seconds() * 1000
            return cached_result

        # Use OpenAI to check interactions and get comprehensive drug information
        try:
            response = await self._check_interactions_with_openai(drugs, patient_context)
            response["cache_hit"] = False
            response["response_time_ms"] = (datetime.now() - start_time).total_seconds() * 1000

            # Cache the result
            if use_cache and self.cache_enabled and smart_cache_manager and CacheStrategy:
                try:
                    await smart_cache_manager.smart_cache_set(
                        CacheStrategy.MEDICAL_REFERENCE,
                        f"interactions_{cache_key}",
                        response,
                        drugs=drugs
                    )
                    logger.info(f"Cached drug interaction result for: {drugs}")
                except Exception as e:
                    logger.warning(f"Failed to cache drug interaction result: {e}")

            return response

        except Exception as e:
            logger.error(f"Error checking drug interactions with OpenAI: {e}")
            return {
                "banner": getattr(self.settings, 'educational_banner', 'Educational use only - not medical advice'),
                "error": "Drug interaction analysis requires OpenAI API",
                "error_details": str(e),
                "drugs_checked": drugs,
                "service_note": "⚠️ Drug Interaction Checker requires OpenAI API. This is an AI-powered feature that provides comprehensive drug information and interaction analysis using medical AI.",
                "timestamp": datetime.now().isoformat()
            }
    
    def _check_drug_pair_interaction(self, drug1: Drug, drug2: Drug) -> Optional[DrugInteraction]:
        """Check for interaction between two drugs."""
        
        for rule in self.interaction_rules:
            rule_drugs = set(rule["drugs"])
            check_drugs = {drug1.name, drug2.name}
            
            if rule_drugs == check_drugs:
                return DrugInteraction(
                    drug1=drug1,
                    drug2=drug2,
                    severity=rule["severity"],
                    mechanism=rule["mechanism"],
                    description=rule["description"],
                    clinical_significance=rule["clinical_significance"],
                    recommendations=rule["recommendations"],
                    evidence_level=rule["evidence_level"],
                    onset=rule["onset"],
                    documentation=rule["documentation"],
                    references=[]  # Would be populated from database
                )
        
        return None
    
    def _get_severity_summary(self, interactions: List[DrugInteraction]) -> Dict[str, int]:
        """Get summary of interaction severities."""
        summary = {
            "contraindicated": 0,
            "major": 0,
            "moderate": 0,
            "minor": 0
        }
        
        for interaction in interactions:
            summary[interaction.severity.value] += 1
        
        return summary
    
    def _generate_clinical_alerts(self, interactions: List[DrugInteraction]) -> List[str]:
        """Generate clinical alerts based on interactions."""
        alerts = []
        
        # Check for contraindicated interactions
        contraindicated = [i for i in interactions if i.severity == InteractionSeverity.CONTRAINDICATED]
        if contraindicated:
            alerts.append("⚠️ CONTRAINDICATED: Immediate medication review required")
        
        # Check for major interactions
        major = [i for i in interactions if i.severity == InteractionSeverity.MAJOR]
        if major:
            alerts.append(f"🔴 MAJOR: {len(major)} major interaction(s) require close monitoring")
        
        # Check for moderate interactions
        moderate = [i for i in interactions if i.severity == InteractionSeverity.MODERATE]
        if moderate:
            alerts.append(f"🟡 MODERATE: {len(moderate)} moderate interaction(s) require monitoring")
        
        # Check for bleeding risk
        bleeding_risk_drugs = ["warfarin", "aspirin", "ibuprofen"]
        bleeding_interactions = [
            i for i in interactions 
            if any(drug in bleeding_risk_drugs for drug in [i.drug1.name, i.drug2.name])
        ]
        if bleeding_interactions:
            alerts.append("🩸 BLEEDING RISK: Monitor for signs of bleeding")
        
        return alerts
    
    async def get_drug_alternatives(self, drug_name: str, indication: Optional[str] = None) -> Dict[str, Any]:
        """Get alternative medications for a given drug."""
        
        drug = self._find_drug_in_database(drug_name)
        if not drug:
            return {
                "banner": getattr(self.settings, 'educational_banner', 'Educational use only - not medical advice'),
                "message": f"Drug '{drug_name}' not found in database",
                "alternatives": [],
                "timestamp": datetime.now().isoformat()
            }
        
        # Find alternatives in same drug class
        alternatives = []
        for db_drug in self.drugs_db.values():
            if (db_drug.drug_class == drug.drug_class and 
                db_drug.name != drug.name):
                alternatives.append({
                    "name": db_drug.name,
                    "generic_name": db_drug.generic_name,
                    "brand_names": db_drug.brand_names,
                    "drug_class": db_drug.drug_class,
                    "route": db_drug.route
                })
        
        return {
            "banner": getattr(self.settings, 'educational_banner', 'Educational use only - not medical advice'),
            "original_drug": {
                "name": drug.name,
                "generic_name": drug.generic_name,
                "drug_class": drug.drug_class
            },
            "indication": indication,
            "alternatives": alternatives,
            "alternative_count": len(alternatives),
            "recommendation": "Consult with prescriber before making any medication changes",
            "timestamp": datetime.now().isoformat()
        }
    
    async def close(self):
        """Clean up resources."""
        if self.session:
            await self.session.aclose()

# Global service instance
drug_interaction_service = DrugInteractionService()

# Service registration function
async def register_drug_interaction_service():
    """Register drug interaction service for dependency injection."""
    logger.info("Drug interaction service registered successfully")
    return drug_interaction_service
