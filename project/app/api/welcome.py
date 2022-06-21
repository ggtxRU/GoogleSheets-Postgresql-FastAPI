from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/welcome")
async def welcome():
    return Response("Welcome to FastAPI application!\nAuthor: GGTX\nThx for watching.")
