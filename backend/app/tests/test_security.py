from app.core.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_round_trip():
    stored_hash = hash_password("correct horse battery staple")

    assert verify_password("correct horse battery staple", stored_hash)
    assert not verify_password("wrong password", stored_hash)


def test_access_token_round_trip():
    token = create_access_token("user-123")

    assert decode_access_token(token) == "user-123"
