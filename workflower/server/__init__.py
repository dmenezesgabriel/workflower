import uvicorn


def create_server(app):
    """
    Server factory.
    """
    config = uvicorn.Config(app=app)
    return uvicorn.Server(config)
