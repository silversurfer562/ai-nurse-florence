from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get(
    "/health",
    responses={200: {"content": {"application/json": {"example": {"status": "ok"}}}}},
)
def health():
    return {"status": "ok"}
