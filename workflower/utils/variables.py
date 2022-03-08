import os


def get_env() -> str:
    """
    Get the environment the app is running in, indicated by WORKFLOWER_ENV
    environment variable.
    The default VALUE is production.
    """
    return os.environ.get("WORKFLOWER_ENV") or "production"
