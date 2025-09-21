"""
Pagination utility for API endpoints.
"""
from fastapi import Query
from pydantic import BaseModel
from typing import List, Any, Optional, Dict

class Page(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    links: Dict[str, Optional[str]]

def get_pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size")
):
    return {"page": page, "size": size}

def create_paginated_response(
    items: List[Any],
    total: int,
    page: int,
    size: int,
    base_url: str
) -> Page:
    """Creates a standardized paginated response object."""
    links = {
        "self": f"{base_url}?page={page}&size={size}",
        "first": f"{base_url}?page=1&size={size}",
        "last": f"{base_url}?page={-(-total // size)}&size={size}", # Ceiling division
        "next": f"{base_url}?page={page + 1}&size={size}" if (page * size) < total else None,
        "prev": f"{base_url}?page={page - 1}&size={size}" if page > 1 else None
    }
    return Page(
        items=items,
        total=total,
        page=page,
        size=size,
        links=links
    )