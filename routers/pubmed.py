from fastapi import APIRouter, Query, Depends, Request
from models.schemas import PubMedSearchResponse
from services import pubmed_service
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
    pagination: dict = Depends(get_pagination_params),
):
    """
    Searches PubMed for medical research articles.

    This endpoint supports pagination. Use the `page` and `size` query
    parameters to navigate through the search results.
    """
    page = pagination["page"]
    size = pagination["size"]

    result = pubmed_service.search_pubmed(q, page=page, size=size)

    paginated_data = create_paginated_response(
        items=result["results"],
        total=result["total"],
        page=page,
        size=size,
        base_url=str(request.url_for("search")),
    )

    return create_success_response(paginated_data.dict())
