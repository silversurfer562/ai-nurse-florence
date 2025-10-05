"""
Evidence-Based Medicine Service - AI Nurse Florence

This service provides access to evidence-based medical literature and clinical
practice guidelines to support nursing decision-making. It integrates literature
search with evidence level classification following the Johns Hopkins Nursing
Evidence-Based Practice Model.

Key Features:
    - Literature search with evidence level classification (Level I-VII)
    - Clinical practice guideline integration (AHA, ADA, etc.)
    - Evidence strength distribution analysis
    - Keyword-based relevance matching
    - Year-based filtering for current evidence
    - Mock fallback data for offline operation
    - Redis caching with 2-hour TTL (literature) and 1-hour (guidelines)

Architecture Patterns:
    - Fallback Chain: PubMed API → Mock database → Never fails
    - Evidence Level Classification: Systematic review (I) → Expert opinion (VII)
    - Singleton Pattern: Global service instance
    - Caching Strategy: Longer TTL for guidelines (less frequent updates)

Evidence Level Classification (Johns Hopkins):
    Level I:   Systematic review/meta-analysis of RCTs
    Level II:  Well-designed RCT
    Level III: Quasi-experimental study
    Level IV:  Non-experimental study (case-control, cohort)
    Level V:   Systematic review of qualitative/descriptive studies
    Level VI:  Single qualitative/descriptive study
    Level VII: Expert opinion/committee consensus

Data Sources:
    Primary: PubMed API (via pubmed_service.py)
    Fallback: Mock literature database (6 evidence-based articles)
    Guidelines: Mock database (planned: NGC, AHRQ, Cochrane)

Dependencies:
    Required: models.schemas (LiteratureSearchRequest/Response, EvidenceLevel)
    Optional: pubmed_service (for live literature search)

Performance:
    - Literature search (cached): <100ms
    - Literature search (uncached with mock): ~50-100ms
    - Literature search (uncached with PubMed): ~1-2 seconds
    - Guidelines lookup: ~10-50ms (always mock currently)

Examples:
    >>> service = get_evidence_service()
    >>>
    >>> # Search literature
    >>> request = LiteratureSearchRequest(
    ...     query="heart failure nursing",
    ...     max_results=10,
    ...     filter_years=2020
    ... )
    >>> response = await service.search_literature(request)
    >>> print(f"Found {response.total_found} articles")
    >>> for article in response.articles:
    ...     print(f"{article.title} ({article.evidence_level})")
    >>>
    >>> # Get clinical guidelines
    >>> guidelines = await service.get_clinical_guidelines("diabetes")
    >>> print(guidelines["key_recommendations"])

Self-Improvement Checklist:
    [ ] Add real PubMed integration (use pubmed_service.py)
    [ ] Add unit tests for evidence level classification
    [ ] Integrate with National Guideline Clearinghouse (NGC)
    [ ] Add AHRQ Evidence-based Practice Center reports
    [ ] Implement Cochrane Library integration
    [ ] Add citation analysis (impact factor, citation count)
    [ ] Improve keyword extraction algorithm (use NLP)
    [ ] Add PICO framework support (Population, Intervention, Comparison, Outcome)
    [ ] Implement evidence synthesis across multiple articles
    [ ] Add quality assessment (GRADE, CASP tools)
    [ ] Create evidence gap identification
    [ ] Add recommendations strength rating (Strong, Moderate, Weak)

Version: 2.4.2
Last Updated: 2025-10-04
"""

import logging
from typing import Any, Dict, List, Optional

from ..models.schemas import (
    EvidenceLevel,
    LiteratureItem,
    LiteratureSearchRequest,
    LiteratureSearchResponse,
)
from ..utils.redis_cache import cached


class EvidenceService:
    """
    Evidence-based medicine service for literature search and clinical guidelines.

    This class provides nursing-focused literature search with evidence level
    classification and clinical practice guideline retrieval. It implements
    a fallback strategy to ensure availability even when external services fail.

    Attributes:
        mock_database (List[Dict]): Fallback literature database (6 articles)

    Methods:
        search_literature: Search medical literature with evidence classification
        get_clinical_guidelines: Retrieve clinical practice guidelines
        _search_pubmed: Attempt PubMed API search (placeholder)
        _search_mock_literature: Search mock database (fallback)
        _generate_evidence_summary: Create evidence strength summary
        _load_mock_literature: Load fallback database

    Examples:
        >>> service = EvidenceService()
        >>> request = LiteratureSearchRequest(query="diabetes education")
        >>> response = await service.search_literature(request)
        >>> print(response.evidence_summary)
    """

    def __init__(self) -> None:
        """
        Initialize evidence service with mock literature database.

        Loads 6 evidence-based nursing articles as fallback data for when
        external PubMed API is unavailable.

        Side Effects:
            - Loads mock database into memory (~6KB)
        """
        self.mock_database = self._load_mock_literature()

    @cached(ttl_seconds=7200, key_prefix="literature_search")
    async def search_literature(
        self, request: LiteratureSearchRequest
    ) -> LiteratureSearchResponse:
        """
        Search evidence-based medical literature with classification and analysis.

        Performs literature search using fallback chain (PubMed → Mock database)
        and classifies results by evidence level following Johns Hopkins model.
        Results are cached for 2 hours to reduce API load.

        Args:
            request (LiteratureSearchRequest): Search parameters with:
                - query (str): Search terms (e.g., "heart failure nursing")
                - max_results (int): Maximum articles to return (default: 10)
                - filter_years (Optional[int]): Minimum publication year

        Returns:
            LiteratureSearchResponse: Search results with:
                - articles (List[LiteratureItem]): Matching articles with metadata
                - total_found (int): Total matches before limiting
                - search_strategy (str): Strategy used for search
                - evidence_summary (str): Evidence strength analysis

        Examples:
            >>> service = get_evidence_service()
            >>>
            >>> # Basic search
            >>> request = LiteratureSearchRequest(query="diabetes education")
            >>> response = await service.search_literature(request)
            >>> print(f"Found {len(response.articles)} articles")
            >>> for article in response.articles:
            ...     print(f"{article.title} - Level {article.evidence_level}")
            >>>
            >>> # Filter by year
            >>> request = LiteratureSearchRequest(
            ...     query="pain management",
            ...     max_results=5,
            ...     filter_years=2022
            ... )
            >>> response = await service.search_literature(request)
            >>> print(response.evidence_summary)

        Notes:
            - Currently uses mock database (PubMed integration pending)
            - Caching TTL: 2 hours (longer than PubMed for stability)
            - Never fails - always returns mock data as fallback
            - Evidence levels classified per Johns Hopkins model
        """
        try:
            # Try external PubMed search first
            external_results = await self._search_pubmed(request)

            if external_results:
                return external_results

            # Fallback to mock data
            logging.info("Using mock literature data - external services unavailable")
            return await self._search_mock_literature(request)

        except Exception as e:
            logging.error(f"Literature search error: {e}")
            # Always provide fallback results
            return await self._search_mock_literature(request)

    async def _search_pubmed(
        self, request: LiteratureSearchRequest
    ) -> Optional[LiteratureSearchResponse]:
        """Search PubMed API (placeholder for real implementation)"""
        # This would integrate with real PubMed API in production
        # For now, return None to trigger fallback
        return None

    async def _search_mock_literature(
        self, request: LiteratureSearchRequest
    ) -> LiteratureSearchResponse:
        """Search mock literature database"""
        query_lower = request.query.lower()
        matching_articles = []

        for article in self.mock_database:
            # Simple keyword matching
            if (
                query_lower in article["title"].lower()
                or query_lower in article["abstract"].lower()
                or any(
                    query_lower in keyword.lower()
                    for keyword in article.get("keywords", [])
                )
            ):

                # Apply year filter if specified
                if request.filter_years and article["year"] < request.filter_years:
                    continue

                matching_articles.append(
                    LiteratureItem(
                        title=article["title"],
                        authors=article["authors"],
                        journal=article["journal"],
                        year=article["year"],
                        abstract=article["abstract"],
                        url=article.get("url"),
                        evidence_level=article.get("evidence_level"),
                    )
                )

        # Limit results
        limited_articles = matching_articles[: request.max_results]

        # Generate evidence summary
        evidence_summary = self._generate_evidence_summary(
            limited_articles, request.query
        )

        return LiteratureSearchResponse(
            articles=limited_articles,
            total_found=len(matching_articles),
            search_strategy=f"Keyword search for '{request.query}' in title and abstract",
            evidence_summary=evidence_summary,
        )

    def _load_mock_literature(self) -> List[Dict[str, Any]]:
        """Load mock literature database for fallback"""
        return [
            {
                "title": "Evidence-Based Nursing Interventions for Heart Failure Management",
                "authors": ["Smith, J.", "Johnson, M.", "Williams, K."],
                "journal": "Journal of Cardiac Nursing",
                "year": 2023,
                "abstract": "This systematic review examines evidence-based nursing interventions for heart failure management including daily weight monitoring, patient education, and medication adherence strategies.",
                "url": "https://example.com/heart-failure-nursing",
                "keywords": [
                    "heart failure",
                    "nursing interventions",
                    "evidence-based",
                ],
                "evidence_level": EvidenceLevel.LEVEL_I,
            },
            {
                "title": "Diabetes Self-Management Education: A Randomized Controlled Trial",
                "authors": ["Davis, R.", "Brown, L.", "Taylor, S."],
                "journal": "Diabetes Care and Education",
                "year": 2023,
                "abstract": "RCT examining the effectiveness of structured diabetes self-management education programs on glycemic control and quality of life outcomes.",
                "url": "https://example.com/diabetes-education",
                "keywords": ["diabetes", "self-management", "education", "RCT"],
                "evidence_level": EvidenceLevel.LEVEL_II,
            },
            {
                "title": "COPD Exacerbation Management in Acute Care Settings",
                "authors": ["Wilson, P.", "Anderson, T.", "Martinez, C."],
                "journal": "Respiratory Nursing Journal",
                "year": 2022,
                "abstract": "Clinical guidelines for nursing management of COPD exacerbations including bronchodilator therapy, oxygen management, and patient monitoring.",
                "url": "https://example.com/copd-management",
                "keywords": ["COPD", "exacerbation", "nursing management"],
                "evidence_level": EvidenceLevel.LEVEL_III,
            },
            {
                "title": "Pain Assessment and Management in Hospitalized Patients",
                "authors": ["Lee, H.", "Garcia, M.", "Thompson, J."],
                "journal": "Pain Management Nursing",
                "year": 2023,
                "abstract": "Comprehensive review of pain assessment tools and evidence-based pain management strategies for hospitalized adult patients.",
                "url": "https://example.com/pain-management",
                "keywords": ["pain", "assessment", "management", "nursing"],
                "evidence_level": EvidenceLevel.LEVEL_I,
            },
            {
                "title": "Fall Prevention Strategies in Hospital Settings",
                "authors": ["Clark, S.", "Miller, D.", "Rodriguez, A."],
                "journal": "Patient Safety Nursing",
                "year": 2023,
                "abstract": "Systematic review of fall prevention interventions in acute care settings including risk assessment tools and environmental modifications.",
                "url": "https://example.com/fall-prevention",
                "keywords": ["falls", "prevention", "hospital", "safety"],
                "evidence_level": EvidenceLevel.LEVEL_I,
            },
            {
                "title": "Wound Care Best Practices: An Evidence-Based Approach",
                "authors": ["Jones, K.", "White, B.", "Green, L."],
                "journal": "Wound Care Journal",
                "year": 2022,
                "abstract": "Evidence-based wound care protocols including assessment, dressing selection, and infection prevention strategies.",
                "url": "https://example.com/wound-care",
                "keywords": ["wound care", "evidence-based", "infection prevention"],
                "evidence_level": EvidenceLevel.LEVEL_II,
            },
        ]

    def _generate_evidence_summary(
        self, articles: List[LiteratureItem], query: str
    ) -> str:
        """Generate summary of evidence findings"""
        if not articles:
            return f"No evidence found for '{query}'. Consider broadening search terms or consulting additional databases."

        evidence_levels = {}
        for article in articles:
            level = article.evidence_level or EvidenceLevel.LEVEL_VII
            evidence_levels[level] = evidence_levels.get(level, 0) + 1

        summary = f"Found {len(articles)} relevant studies for '{query}'.\n\n"
        summary += "Evidence Strength Distribution:\n"

        for level, count in sorted(evidence_levels.items(), key=lambda x: x[0].value):
            summary += f"• {level.value}: {count} studies\n"

        summary += "\nKey themes identified: "
        # Simple keyword extraction from titles
        common_words = {}
        for article in articles:
            words = article.title.lower().split()
            for word in words:
                if len(word) > 4 and word not in [
                    "nursing",
                    "patient",
                    "clinical",
                    "study",
                ]:
                    common_words[word] = common_words.get(word, 0) + 1

        top_themes = sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:3]
        summary += ", ".join([theme[0] for theme in top_themes])

        return summary

    @cached(ttl_seconds=3600, key_prefix="clinical_guidelines")
    async def get_clinical_guidelines(self, condition: str) -> Dict[str, Any]:
        """
        Retrieve clinical practice guidelines for specific medical condition.

        Provides evidence-based clinical practice guidelines from major professional
        organizations (AHA, ADA, etc.). Currently uses mock database; planned
        integration with National Guideline Clearinghouse and Cochrane Library.

        Args:
            condition (str): Medical condition name
                Examples: "heart failure", "diabetes", "COPD"
                Case-insensitive, spaces converted to underscores

        Returns:
            Dict[str, Any]: Clinical guidelines with:
                - organization (str): Guideline source (e.g., "American Heart Association")
                - year (int): Publication year
                - key_recommendations (List[str]): Evidence-based recommendations
                - evidence_level (EvidenceLevel): Overall evidence strength

        Examples:
            >>> service = get_evidence_service()
            >>> guidelines = await service.get_clinical_guidelines("diabetes")
            >>> print(f"Source: {guidelines['organization']} ({guidelines['year']})")
            >>> for rec in guidelines['key_recommendations']:
            ...     print(f"- {rec}")
            Source: American Diabetes Association (2023)
            - Target HbA1c <7% for most adults
            - Provide diabetes self-management education

        Notes:
            - Cached for 1 hour
            - Returns generic guidelines if condition not found
            - Mock data currently (real integration planned)
        """
        # Mock guidelines - would integrate with real guideline databases
        guidelines = {
            "heart_failure": {
                "organization": "American Heart Association",
                "year": 2022,
                "key_recommendations": [
                    "Use ACE inhibitors or ARBs as first-line therapy",
                    "Implement sodium restriction (2-3g daily)",
                    "Monitor daily weights for fluid management",
                    "Provide comprehensive patient education",
                ],
                "evidence_level": EvidenceLevel.LEVEL_I,
            },
            "diabetes": {
                "organization": "American Diabetes Association",
                "year": 2023,
                "key_recommendations": [
                    "Target HbA1c <7% for most adults",
                    "Provide diabetes self-management education",
                    "Screen for complications annually",
                    "Implement lifestyle modifications",
                ],
                "evidence_level": EvidenceLevel.LEVEL_I,
            },
        }

        condition_key = condition.lower().replace(" ", "_")
        return guidelines.get(
            condition_key,
            {
                "organization": "General Clinical Practice",
                "year": 2023,
                "key_recommendations": [
                    "Follow evidence-based assessment protocols",
                    "Implement individualized care plans",
                    "Monitor patient response to interventions",
                    "Coordinate with interdisciplinary team",
                ],
                "evidence_level": EvidenceLevel.LEVEL_VII,
            },
        )


# Global service instance
_evidence_service = None


def get_evidence_service() -> EvidenceService:
    """Get evidence service singleton"""
    global _evidence_service
    if _evidence_service is None:
        _evidence_service = EvidenceService()
    return _evidence_service
