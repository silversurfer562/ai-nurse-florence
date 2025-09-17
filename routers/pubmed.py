from fastapi import APIRouter, Query
from models.schemas import PubMedSearchResponse, PubMedArticle
from services.pubmed_service import search_pubmed
from utils.guardrails import educational_banner

router = APIRouter(prefix="/v1", tags=["pubmed"])
example = {
    "banner": "Draft for clinician review — not medical advice. No PHI stored.",
    "query": "COPD exacerbation patient education",
    "results": [
        {
            "pmid": "12345678",
            "title": "Patient education in COPD exacerbation",
            "abstract": "...",
            "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/",
        }
    ],
}


@router.get(
    "/pubmed/search",
    response_model=PubMedSearchResponse,
    responses={200: {"content": {"application/json": {"example": example}}}},
)
def pubmed_search(
    q: str = Query(..., description="Query string"),
    max_results: int = Query(10, ge=1, le=50),
) -> PubMedSearchResponse:
    raw = search_pubmed(q, max_results=max_results)
    results = [
        PubMedArticle(
            pmid=r.get("pmid"),
            title=r.get("title"),
            abstract=r.get("abstract"),
            url=r.get("url"),
        )
        for r in raw
    ]
    return PubMedSearchResponse(banner=educational_banner(), query=q, results=results)
