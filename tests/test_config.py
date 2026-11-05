"""Tests for the configuration module."""

from core.environment.environment import _Settings


class TestSettings:
    def test_defaults(self):
        import os

        s = _Settings(SECRET_KEY="x")
        assert s.ENVIRONMENT in ("prod", "dev")
        assert s.JWT_TOKEN_LIFETIME_MINUTES == 15
        assert s.JWT_REFRESH_LIFETIME_DAYS == 30
        assert s.HOST == "0.0.0.0"
        assert s.PORT == 8000

    def test_environment_literal_validation(self):
        import pydantic
        import pytest

        with pytest.raises(pydantic.ValidationError):
            _Settings(SECRET_KEY="x", ENVIRONMENT="staging")

    def test_jwt_ttls_configurable(self):
        s = _Settings(SECRET_KEY="x", JWT_TOKEN_LIFETIME_MINUTES=5, JWT_REFRESH_LIFETIME_DAYS=7)
        assert s.JWT_TOKEN_LIFETIME_MINUTES == 5
        assert s.JWT_REFRESH_LIFETIME_DAYS == 7
