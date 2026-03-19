import os


def get_environment() -> str:
    """Get the value of an environment variable."""
    return os.getenv("ENV")


def is_production() -> bool:
    """Check if the environment is production."""
    return get_environment() == "production"


def is_development() -> bool:
    """Check if the environment is development."""
    return get_environment() == "development"
