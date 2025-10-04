"""
Gene Information API Endpoints

Provides gene lookup and disease-gene association data.
"""

from typing import Dict, List

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from services.gene_service import get_gene_details, get_genes_for_disease

router = APIRouter(prefix="/genes", tags=["Genes"])


class GeneInfo(BaseModel):
    """Gene information response"""

    symbol: str
    name: str
    entrez_id: int | None
    summary: str
    type: str
    chromosome: str | None
    pharmgkb_id: str | None
    ncbi_url: str | None
    relevance_score: float | None

    class Config:
        from_attributes = True


class GeneDetailsResponse(BaseModel):
    """Detailed gene information"""

    symbol: str
    name: str
    entrez_id: int | None
    summary: str
    type: str
    chromosome: str | None
    start: int | None
    end: int | None
    pathways: List[str]
    go_terms: Dict[str, List[str]]
    ncbi_url: str | None

    class Config:
        from_attributes = True


@router.get("/disease/{disease_name}", response_model=List[GeneInfo])
async def get_disease_genes(
    disease_name: str,
    limit: int = Query(5, ge=1, le=20, description="Maximum number of genes to return"),
):
    """
    Get genes associated with a disease.

    **Example:**
    ```
    GET /api/v1/genes/disease/diabetes?limit=5
    GET /api/v1/genes/disease/alzheimer
    ```

    Returns genes sorted by relevance score (higher = more relevant).
    """
    try:
        genes = get_genes_for_disease(disease_name, limit=limit)
        return genes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching genes: {str(e)}")


@router.get("/{gene_id}", response_model=GeneDetailsResponse)
async def get_gene_info(gene_id: str):
    """
    Get detailed information about a specific gene.

    **Parameters:**
    - gene_id: Gene symbol (e.g., "BRCA1") or Entrez ID (e.g., "672")

    **Example:**
    ```
    GET /api/v1/genes/BRCA1
    GET /api/v1/genes/672
    ```
    """
    gene = get_gene_details(gene_id)

    if not gene:
        raise HTTPException(status_code=404, detail=f"Gene not found: {gene_id}")

    return gene


@router.get("/search/{query}", response_model=List[GeneInfo])
async def search_genes(
    query: str, limit: int = Query(10, ge=1, le=50, description="Maximum results")
):
    """
    Search for genes by name or symbol.

    **Example:**
    ```
    GET /api/v1/genes/search/insulin?limit=10
    GET /api/v1/genes/search/BRCA
    ```
    """
    try:
        import live_mygene

        results = live_mygene.search_genes(query, limit=limit)

        formatted = []
        for gene in results:
            formatted.append(
                {
                    "symbol": gene.get("symbol"),
                    "name": gene.get("name"),
                    "entrez_id": gene.get("entrez_id"),
                    "summary": gene.get("summary", ""),
                    "type": gene.get("type", "protein-coding"),
                    "chromosome": None,
                    "pharmgkb_id": None,
                    "ncbi_url": (
                        f"https://www.ncbi.nlm.nih.gov/gene/{gene.get('entrez_id')}"
                        if gene.get("entrez_id")
                        else None
                    ),
                    "relevance_score": gene.get("score"),
                }
            )

        return formatted
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching genes: {str(e)}")
