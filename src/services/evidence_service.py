"""
Evidence service for literature search and clinical guidelines
Integrates with external medical databases
"""

import logging
from typing import List, Dict, Any, Optional
from ..models.schemas import (
    LiteratureSearchRequest,
    LiteratureSearchResponse,
    LiteratureItem,
    EvidenceLevel,
)
from ..utils.redis_cache import cached


class EvidenceService:
    """Evidence-based literature and guidelines service"""

    def __init__(self):
        self.mock_database = self._load_mock_literature()

    @cached(ttl_seconds=7200, key_prefix="literature_search")
    async def search_literature(
        self, request: LiteratureSearchRequest
    ) -> LiteratureSearchResponse:
        """
        Search medical literature with external API integration
        Falls back to mock data if external services unavailable
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
        from src.models.schemas import EvidenceLevel as _EvidenceLevel

        evidence_levels: Dict[_EvidenceLevel, int] = {}
        for article in articles:
            level = article.evidence_level or _EvidenceLevel.LEVEL_VII
            evidence_levels[level] = evidence_levels.get(level, 0) + 1

        summary = f"Found {len(articles)} relevant studies for '{query}'.\n\n"
        summary += "Evidence Strength Distribution:\n"

        for level, count in sorted(evidence_levels.items(), key=lambda x: x[0].value):
            summary += f"\u2022 {level.value}: {count} studies\n"

        summary += "\nKey themes identified: "
        # Simple keyword extraction from titles
        common_words: Dict[str, int] = {}
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
        """Get clinical practice guidelines for condition"""
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
