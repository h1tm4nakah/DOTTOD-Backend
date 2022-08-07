from http import HTTPStatus
from flask_restx import Resource, marshal
from parole_politiche import db
from parole_politiche.api.serializers import (
    exhibition_ns,
    participant_base_model
)
from parole_politiche.api.parsers import get_exhibition_filters_req_parser
from parole_politiche.models.exhibition import Participant, Piece
from sqlalchemy import desc
from sqlalchemy.orm import contains_eager
from typing import List


@exhibition_ns.route("", endpoint="exhibition_list")
@exhibition_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
@exhibition_ns.response(int(HTTPStatus.UNAUTHORIZED), "Unauthorized.")
@exhibition_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
class ExhibitionList(Resource):
    """Handles HTTP requests to URL: /exhibition."""

    @exhibition_ns.expect(get_exhibition_filters_req_parser)
    @exhibition_ns.marshal_with(participant_base_model)
    def get(self):
        participants: List[Participant] = (
            db.session.query(Participant)
            .join(Piece, Participant.pieces)
            .options(contains_eager(Participant.pieces))
            .order_by(desc(Piece.created_at))
            .all()
        )
        return participants, HTTPStatus.OK
