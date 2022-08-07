"""Business logic for /auth API endpoints."""
from http import HTTPStatus

from flask import current_app, jsonify
from flask_restx import abort
from itsdangerous import URLSafeTimedSerializer
from parole_politiche import db
from parole_politiche.api.auth.auth_decorators import token_required
from parole_politiche.models.user import BlacklistedToken, User
from parole_politiche.utils.datetime_util import (
    remaining_fromtimestamp,
    format_timespan_digits,
)


def process_login_request(email, password):
    user = User.find_by_email(email)
    if not user or not user.check_password(password):
        abort(HTTPStatus.UNAUTHORIZED, "L'email o la password non corrispondono", status="fail")
    access_token = user.encode_access_token()

    return _create_auth_successful_response(
        token=access_token,
        status_code=HTTPStatus.OK,
        message="successfully logged in",
    )


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config.get("SECRET_KEY"))
    try:
        email = serializer.loads(
            token,
            salt=current_app.config.get("SECURITY_PASSWORD_SALT"),
            max_age=expiration
        )
    except:
        return False
    return email


@token_required
def get_logged_in_user():
    public_id = get_logged_in_user.public_id
    user = User.find_by_public_id(public_id)
    expires_at = get_logged_in_user.expires_at
    user.token_expires_in = format_timespan_digits(remaining_fromtimestamp(expires_at))
    return user


@token_required
def process_logout_request():
    access_token = process_logout_request.token
    expires_at = process_logout_request.expires_at
    blacklisted_token = BlacklistedToken(access_token, expires_at)
    db.session.add(blacklisted_token)
    db.session.commit()
    response_dict = dict(status="success", message="successfully logged out")
    return response_dict, HTTPStatus.OK


def _create_auth_successful_response(token, status_code, message):
    response = jsonify(
        status="success",
        message=message,
        access_token=token,
        token_type="bearer",
        expires_in=_get_token_expire_time(),
    )
    response.status_code = status_code
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"
    return response


def _get_token_expire_time():
    token_age_h = current_app.config.get("TOKEN_EXPIRE_HOURS")
    token_age_m = current_app.config.get("TOKEN_EXPIRE_MINUTES")
    expires_in_seconds = token_age_h * 3600 + token_age_m * 60
    return expires_in_seconds if not current_app.config["TESTING"] else 5