from fastapi import APIRouter

from src.dependencies import GetFullInstructor

router = APIRouter()


@router.get("/test")
async def test(inst: GetFullInstructor):
    print(inst)
    return inst
