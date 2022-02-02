"""
Server.
"""
import uvicorn


class Server:
    def __init__(self, config: uvicorn.Config):
        self.config = config
