"""Decorators that decode and verify authorization tokens."""
from functools import wraps

from flask import request

from parole_politiche.api.auth.auth_exceptions import ApiUnauthorized, ApiForbidden
from parole_politiche.models.user import User


def token_required(f):
    """Execute function if request contains valid access token."""

    @wraps(f)
    def decorated(*args, **kwargs):
        token_payload = _check_access_token(role="generic")
        for name, val in token_payload.items():
            setattr(decorated, name, val)
        return f(*args, **kwargs)

    return decorated


def _check_access_token(role):
    token = request.headers.get("Authorization")
    if not token:
        raise ApiUnauthorized(description="Unauthorized", role=role)
    result = User.decode_access_token(token)
    if result.failure:
        raise ApiUnauthorized(
            description=result.error,
            role=role,
            error="invalid_token",
            error_description=result.error,
        )
    return result.value