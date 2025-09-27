"""
Common type definitions for use throughout the application.

This module defines reusable type annotations and protocols
to ensure consistent typing across the codebase.
"""
from typing import Dict, List, Any, Optional, TypeVar, Protocol, TypedDict

# Simple type aliases
JSON = Dict[str, Any]
QueryParams = Dict[str, str]
Headers = Dict[str, str]

# Type variable for generic functions
T = TypeVar('T')

# Service result types
class ReferenceDict(TypedDict):
    """A reference to an external source."""
    title: str
    url: str
    source: str


class DiseaseResult(TypedDict):
    """Result of a disease lookup."""
    banner: str
    query: str
    name: str
    summary: str
    references: List[ReferenceDict]


class PubMedArticleDict(TypedDict):
    """A PubMed article result."""
    pmid: Optional[str]
    title: str
    abstract: Optional[str]
    url: Optional[str]


class PubMedResult(TypedDict):
    """Result of a PubMed search."""
    banner: str
    query: str
    results: List[PubMedArticleDict]
    total: int


class MedlinePlusResult(TypedDict):
    """Result of a MedlinePlus lookup."""
    topic: str
    summary: str
    references: List[ReferenceDict]


class TrialLocationDict(TypedDict):
    """A clinical trial location."""
    facility: str
    city: str
    state: Optional[str]
    country: str


class ClinicalTrialDict(TypedDict):
    """A clinical trial result."""
    nct_id: Optional[str]
    title: str
    status: Optional[str]
    conditions: List[str]
    locations: List[TrialLocationDict]
    url: Optional[str]


class TrialsResult(TypedDict):
    """Result of a clinical trials search."""
    banner: str
    condition: str
    status: Optional[str]
    results: List[ClinicalTrialDict]


# Protocol definitions for service interfaces
class DiseaseService(Protocol):
    """Protocol for disease information services."""
    def __call__(self, term: str) -> DiseaseResult:
        """Look up disease information."""
        ...


class PubMedService(Protocol):
    """Protocol for PubMed search services."""
    def __call__(self, query: str, max_results: int = 10) -> PubMedResult:
        """Search PubMed for articles."""
        ...


class MedlinePlusService(Protocol):
    """Protocol for MedlinePlus services."""
    def __call__(self, topic: str) -> MedlinePlusResult:
        """Get a summary from MedlinePlus."""
        ...


class TrialsService(Protocol):
    """Protocol for clinical trials services."""
    def __call__(
        self, condition: str, status: Optional[str] = None, max_results: int = 10
    ) -> TrialsResult:
        """Search for clinical trials."""
        ...


class ReadabilityService(Protocol):
    """Protocol for readability analysis services."""
    def __call__(self, text: str) -> Dict[str, Any]:
        """Analyze the readability of text."""
        ...


class SummarizeService(Protocol):
    """Protocol for text summarization services."""
    def __call__(self, text: str, model: str = "gpt-4o-mini", **kwargs: Any) -> str:
        """Summarize text."""
        ...