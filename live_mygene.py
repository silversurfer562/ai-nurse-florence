"""
MyGene.info API connector for gene information lookup.

API Documentation: https://docs.mygene.info/
"""
import requests
from typing import Dict, Any, List, Optional

BASE_URL = "https://mygene.info/v3"

def query_genes_by_disease(disease_name: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Query genes associated with a disease.

    Args:
        disease_name: Disease name to search for
        limit: Maximum number of genes to return

    Returns:
        List of gene dictionaries with relevant fields
    """
    try:
        # Search for genes associated with the disease
        response = requests.get(
            f"{BASE_URL}/query",
            params={
                "q": f'disease:"{disease_name}"',
                "size": limit,
                "fields": "symbol,name,entrezgene,summary,ensembl.gene,genomic_pos,type_of_gene,pharmgkb,generif"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        hits = data.get("hits", [])
        genes = []

        for hit in hits:
            gene = {
                "gene_id": hit.get("_id"),
                "entrez_id": hit.get("entrezgene"),
                "symbol": hit.get("symbol"),
                "name": hit.get("name"),
                "summary": hit.get("summary", ""),
                "type": hit.get("type_of_gene", "protein-coding"),
                "score": hit.get("_score", 0)
            }

            # Add genomic position if available
            if "genomic_pos" in hit:
                pos = hit["genomic_pos"]
                if isinstance(pos, list) and len(pos) > 0:
                    pos = pos[0]
                gene["chromosome"] = pos.get("chr")
                gene["start"] = pos.get("start")
                gene["end"] = pos.get("end")

            # Add PharmGKB ID if available (for drug-gene interactions)
            if "pharmgkb" in hit:
                gene["pharmgkb_id"] = hit["pharmgkb"]

            genes.append(gene)

        return genes

    except Exception as e:
        print(f"MyGene.info query error: {e}")
        return []


def get_gene(gene_id: str) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific gene.

    Args:
        gene_id: Gene ID (Entrez ID, Ensembl ID, or gene symbol)

    Returns:
        Dict containing gene details
    """
    try:
        response = requests.get(
            f"{BASE_URL}/gene/{gene_id}",
            params={
                "fields": "symbol,name,summary,entrezgene,ensembl.gene,genomic_pos,type_of_gene,pharmgkb,generif,pathway,go"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        gene = {
            "gene_id": data.get("_id"),
            "entrez_id": data.get("entrezgene"),
            "symbol": data.get("symbol"),
            "name": data.get("name"),
            "summary": data.get("summary", ""),
            "type": data.get("type_of_gene", "protein-coding")
        }

        # Add genomic position
        if "genomic_pos" in data:
            pos = data["genomic_pos"]
            if isinstance(pos, list) and len(pos) > 0:
                pos = pos[0]
            gene["chromosome"] = pos.get("chr")
            gene["start"] = pos.get("start")
            gene["end"] = pos.get("end")

        # Add pathways
        if "pathway" in data:
            pathways = data["pathway"]
            if isinstance(pathways, dict):
                gene["pathways"] = []
                # Extract pathway names
                for key, value in pathways.items():
                    if isinstance(value, list):
                        gene["pathways"].extend([p.get("name") for p in value if isinstance(p, dict) and "name" in p])

        # Add GO terms
        if "go" in data:
            go_data = data["go"]
            gene["go_terms"] = {
                "biological_process": [term.get("term") for term in go_data.get("BP", []) if isinstance(term, dict)][:5],
                "molecular_function": [term.get("term") for term in go_data.get("MF", []) if isinstance(term, dict)][:5],
                "cellular_component": [term.get("term") for term in go_data.get("CC", []) if isinstance(term, dict)][:5]
            }

        return gene

    except Exception as e:
        print(f"MyGene.info get_gene error: {e}")
        return None


def search_genes(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Search for genes by name or symbol.

    Args:
        query: Search query
        limit: Maximum number of results

    Returns:
        List of matching genes
    """
    try:
        response = requests.get(
            f"{BASE_URL}/query",
            params={
                "q": query,
                "size": limit,
                "fields": "symbol,name,entrezgene,summary,type_of_gene"
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        hits = data.get("hits", [])
        genes = []

        for hit in hits:
            genes.append({
                "gene_id": hit.get("_id"),
                "entrez_id": hit.get("entrezgene"),
                "symbol": hit.get("symbol"),
                "name": hit.get("name"),
                "summary": hit.get("summary", "")[:200] + "..." if hit.get("summary") and len(hit.get("summary", "")) > 200 else hit.get("summary", ""),
                "type": hit.get("type_of_gene", "protein-coding"),
                "score": hit.get("_score", 0)
            })

        return genes

    except Exception as e:
        print(f"MyGene.info search error: {e}")
        return []
