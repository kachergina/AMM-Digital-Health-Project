"""Shared pytest fixtures for the AMM Digital System tests."""

import pytest

from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.testing = True
    return app.test_client()
