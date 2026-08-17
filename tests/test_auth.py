import os
import unittest

os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")

from app.auth import create_access_token, decode_access_token, hash_password, verify_password


class AuthTests(unittest.TestCase):
    def test_password_hashing_and_verification(self) -> None:
        password = "super-secret"
        hashed = hash_password(password)

        self.assertNotEqual(hashed, password)
        self.assertTrue(verify_password(password, hashed))
        self.assertFalse(verify_password("wrong-password", hashed))

    def test_access_token_round_trip(self) -> None:
        token = create_access_token("42")
        payload = decode_access_token(token)

        self.assertIsNotNone(payload)
        assert payload is not None
        self.assertEqual(payload["sub"], "42")
        self.assertEqual(payload["type"], "access")

    def test_invalid_password_hash_and_token_are_rejected(self) -> None:
        self.assertFalse(verify_password("password", "pbkdf2_sha256$invalid"))
        self.assertFalse(verify_password("password", "pbkdf2_sha256$-1$YWJj$YWJj"))
        self.assertIsNone(decode_access_token("not-a-token"))


if __name__ == "__main__":
    unittest.main()
