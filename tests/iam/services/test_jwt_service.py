from datetime import UTC, datetime, timedelta
from uuid import uuid4

import jwt
import pytest

from conf.config import Config
from conf.container import Container
from iam.services.jwt_service import JwtPayload, JWTService


@pytest.fixture
def jwt_service(container: Container) -> JWTService:
    return container.jwt_service


def test_jwt_service_encodes_and_decodes_an_access_token(jwt_service: JWTService):
    now = datetime.now(UTC)
    payload: JwtPayload = {
        "sub": uuid4().hex,
        "jti": uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=15)).timestamp()),
    }

    token = jwt_service.encode(**payload)

    assert isinstance(token, str)
    assert jwt_service.decode(token) == payload


def test_jwt_service_rejects_an_expired_access_token(jwt_service: JWTService):
    now = datetime.now(UTC)
    payload: JwtPayload = {
        "sub": uuid4().hex,
        "jti": uuid4().hex,
        "iat": int((now - timedelta(days=2)).timestamp()),
        "exp": int((now - timedelta(days=1)).timestamp()),
    }

    token = jwt_service.encode(**payload)

    with pytest.raises(ValueError):
        jwt_service.decode(token)


def test_jwt_service_rejects_a_tampered_access_token(jwt_service: JWTService):
    now = datetime.now(UTC)
    payload: JwtPayload = {
        "sub": uuid4().hex,
        "jti": uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=15)).timestamp()),
    }

    token = jwt_service.encode(**payload)

    with pytest.raises(ValueError):
        jwt_service.decode(f"{token}tampered")


def test_jwt_service_requires_all_access_token_claims(jwt_service: JWTService, config: Config):
    now = datetime.now(UTC)
    token = jwt.encode(
        {
            "iss": config.jwt_issuer,
            "aud": config.jwt_audience,
            "sub": uuid4().hex,
            "jti": uuid4().hex,
            "iat": int(now.timestamp()),
        },
        config.jwt_secret,
        algorithm=JWTService.ALG,
    )

    with pytest.raises(ValueError):
        jwt_service.decode(token)
