"""API blueprint configuration."""
from flask import Blueprint
from flask_restx import Api

from parole_politiche.api.serializers import exhibition_ns

api_bp = Blueprint("api", __name__, url_prefix="/api")
authorizations = {"Bearer": {"type": "apiKey", "in": "header", "name": "Authorization"}}

api = Api(
    api_bp,
    version="1.0",
    title="Parole Politiche API with JWT-Based Authentication",
    description="Welcome to the Parole documentation site!",
    doc="/docs",
    authorizations=authorizations,
)

api.add_namespace(exhibition_ns, path="/exhibition")