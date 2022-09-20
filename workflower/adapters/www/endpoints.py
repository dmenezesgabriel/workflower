from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))

router = APIRouter()


@router.get("/")
async def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/hello")
async def say_hello():
    return {"message": "Hello, World!"}
