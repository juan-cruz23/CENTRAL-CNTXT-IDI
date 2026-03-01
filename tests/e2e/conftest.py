import os
import pytest


@pytest.fixture(scope="session")
def screenshots_dir():
    """Ensure screenshots directory exists."""
    path = os.path.join(os.path.dirname(__file__), "screenshots")
    os.makedirs(path, exist_ok=True)
    return path
