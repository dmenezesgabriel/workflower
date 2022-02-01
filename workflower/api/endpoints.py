from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def home():
    return {"message": "Hello, from home!"}


@router.get("/hello")
async def say_hello():
    return {"message": "Hello, World!"}
