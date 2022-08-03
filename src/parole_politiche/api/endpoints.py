from http import HTTPStatus
from flask_restx import Resource, marshal
from parole_politiche import db
from parole_politiche.api.serializers import (
    exhibition_ns,
    exhibition_base_model
)
from parole_politiche.api.parsers import get_exhibition_filters_req_parser

@exhibition_ns.route("", endpoint="exhibition_list")
@exhibition_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
@exhibition_ns.response(int(HTTPStatus.UNAUTHORIZED), "Unauthorized.")
@exhibition_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
class ExhibitionList(Resource):
    """Handles HTTP requests to URL: /exhibition."""

    @exhibition_ns.doc(security="Bearer")
    @exhibition_ns.expect(get_exhibition_filters_req_parser)
    @exhibition_ns.marshal_with(exhibition_base_model)
    def get(self):

        return {}, HTTPStatus.OK
