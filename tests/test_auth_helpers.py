"""Tests for core.helpers.auth — password hashing utilities."""

from core.helpers.auth import check_password, generate_new_password, generate_password_hash


class TestPasswordHashing:
    def test_generate_password_hash_is_bcrypt(self):
        h = generate_password_hash("s3cret")
        assert h.startswith("$2")

    def test_check_password_correct(self):
        h = generate_password_hash("s3cret")
        assert check_password("s3cret", h) is True

    def test_check_password_wrong(self):
        h = generate_password_hash("s3cret")
        assert check_password("nope", h) is False

    def test_hash_is_salted(self):
        assert generate_password_hash("same") != generate_password_hash("same")

    def test_generate_new_password_length_and_hash_match(self):
        data = generate_new_password()
        assert len(data.password) == 12
        assert check_password(data.password, data.hash)


class TestJWT:
    def test_access_token_roundtrip(self):
        from core.helpers.auth import create_access_token, decode_token

        token = create_access_token(sub=42)
        payload = decode_token(token)
        assert payload["sub"] == "42"
        assert payload["type"] == "access"

    def test_expired_token_rejected(self):
        import pytest
        from jwt import ExpiredSignatureError

        from core.helpers.auth import create_access_token, decode_token

        token = create_access_token(sub=1, expires_delta_seconds=-10)
        with pytest.raises(ExpiredSignatureError):
            decode_token(token)
