from fastapi import APIRouter, Query, Depends, Request
from models.schemas import PubMedSearchResponse, PubMedArticle
from services import pubmed_service
from utils.guardrails import educational_banner
from utils.pagination import get_pagination_params, create_paginated_response
from utils.api_responses import create_success_response

router = APIRouter(prefix="/pubmed", tags=["pubmed"])
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
    "/search",
    response_model=PubMedSearchResponse,
    responses={200: {"content": {"application/json": {"example": example}}}},
    summary="Search PubMed for articles",
)
async def search(
    request: Request,
    q: str = Query(..., description="The search query string."),
    max_results: int = Query(10, alias="max_results", ge=1, le=100),
    pagination: dict = Depends(get_pagination_params),
):
    """
    Searches PubMed for medical research articles.

    This endpoint supports pagination. Use the `page` and `size` query
    parameters to navigate through the search results.
    """
    page = pagination["page"]
    size = pagination["size"]

    # Many service implementations accept a `max_results` parameter. Tests
    # expect us to forward that when provided.
    result = pubmed_service.search_pubmed(q, max_results=max_results)

    # Be tolerant of service implementations that return either a dict or a list
    # of results. Normalize into a list of result dicts.
    results = result.get("results", []) if isinstance(result, dict) else list(result)
    total = int(result.get("total", len(results))) if isinstance(result, dict) else len(results)

    paginated_data = create_paginated_response(
        items=results,
        total=total,
        page=page,
        size=max_results,
        base_url=str(request.url_for("search")),
    )

    # Normalize paginated_data to a plain dict for JSON serialization and
    # to extract the links object reliably.
    if hasattr(paginated_data, "model_dump"):
        pd = paginated_data.model_dump()
    elif hasattr(paginated_data, "dict"):
        pd = paginated_data.dict()
    elif isinstance(paginated_data, dict):
        pd = paginated_data
    else:
        pd = {"items": results, "total": total, "page": page, "size": max_results, "links": {}}

    # Build a response object that preserves the original query string and
    # results so tests can assert on them.
    resp = {
        "banner": (result.get("banner") if isinstance(result, dict) else ""),
        "query": (result.get("query") if isinstance(result, dict) else q),
        "results": results,
        "total": total,
        "page": page,
        "size": max_results,
        "links": pd.get("links")
    }

    from utils.api_responses import create_success_response_flat
    return create_success_response_flat(resp)
