"""
Example test file showing how to use pytest markers for CI optimization
"""
import pytest


@pytest.mark.unit
def test_quick_example():
    """Quick unit test that runs in CI"""
    assert 1 + 1 == 2


@pytest.mark.slow
@pytest.mark.integration
def test_database_connection():
    """Slow integration test - skipped in quick CI"""
    # This test would connect to database
    # Skipped in quick CI with -m "not slow"
    pass


@pytest.mark.smoke
def test_api_health():
    """Basic smoke test for API health"""
    # This would test if API starts correctly
    from app.route.route import create_app
    app = create_app()
    assert app is not None


@pytest.mark.slow
@pytest.mark.e2e
def test_full_workflow():
    """End-to-end test - skipped in quick CI"""
    # This would test complete user workflow
    # Skipped in quick CI with -m "not slow"
    pass