from fastapi import FastAPI
from workflower.api.endpoints import router


def create_api():
    """
    Api Factory.
    """
    fastapi_app = FastAPI()
    fastapi_app.include_router(router)
    return fastapi_app
