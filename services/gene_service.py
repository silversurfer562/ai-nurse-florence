"""
Gene Information Service

Provides gene lookup and disease-gene association data using myGene.info API.
"""

from typing import List, Dict, Any, Optional
from utils.logging import get_logger
from utils.cache import cached

logger = get_logger(__name__)

# Lazy-load the live connector
try:
    import live_mygene
    _has_mygene = True
except Exception as e:
    logger.warning(f"Failed to import live_mygene module: {e}")
    _has_mygene = False


@cached(ttl_seconds=3600)  # Cache gene lookups for 1 hour
def get_genes_for_disease(disease_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Get genes associated with a disease.

    Args:
        disease_name: Name of the disease
        limit: Maximum number of genes to return

    Returns:
        List of gene dictionaries with relevant information
    """
    if not _has_mygene:
        logger.info("myGene.info connector not available")
        return []

    try:
        logger.info(f"Fetching genes for disease: {disease_name}")
        genes = live_mygene.query_genes_by_disease(disease_name, limit=limit)

        # Format for frontend display
        formatted_genes = []
        for gene in genes:
            formatted = {
                "symbol": gene.get("symbol"),
                "name": gene.get("name"),
                "entrez_id": gene.get("entrez_id"),
                "summary": gene.get("summary", "")[:300] + "..." if len(gene.get("summary", "")) > 300 else gene.get("summary", ""),
                "type": gene.get("type", "protein-coding"),
                "chromosome": gene.get("chromosome"),
                "pharmgkb_id": gene.get("pharmgkb_id"),
                "ncbi_url": f"https://www.ncbi.nlm.nih.gov/gene/{gene.get('entrez_id')}" if gene.get("entrez_id") else None,
                "relevance_score": round(gene.get("score", 0), 2)
            }
            formatted_genes.append(formatted)

        logger.info(f"Found {len(formatted_genes)} genes for disease: {disease_name}")
        return formatted_genes

    except Exception as e:
        logger.error(f"Error fetching genes for disease {disease_name}: {e}", exc_info=True)
        return []


@cached(ttl_seconds=3600)
def get_gene_details(gene_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific gene.

    Args:
        gene_id: Gene ID (Entrez ID, symbol, etc.)

    Returns:
        Dictionary with detailed gene information
    """
    if not _has_mygene:
        return None

    try:
        logger.info(f"Fetching details for gene: {gene_id}")
        gene = live_mygene.get_gene(gene_id)

        if not gene:
            return None

        formatted = {
            "symbol": gene.get("symbol"),
            "name": gene.get("name"),
            "entrez_id": gene.get("entrez_id"),
            "summary": gene.get("summary", ""),
            "type": gene.get("type", "protein-coding"),
            "chromosome": gene.get("chromosome"),
            "start": gene.get("start"),
            "end": gene.get("end"),
            "pathways": gene.get("pathways", []),
            "go_terms": gene.get("go_terms", {}),
            "ncbi_url": f"https://www.ncbi.nlm.nih.gov/gene/{gene.get('entrez_id')}" if gene.get("entrez_id") else None
        }

        return formatted

    except Exception as e:
        logger.error(f"Error fetching gene details for {gene_id}: {e}", exc_info=True)
        return None
