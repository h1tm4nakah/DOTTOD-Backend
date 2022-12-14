from flask_restx import Namespace, fields

exhibition_ns = Namespace(name="exhibition", validate=True)

piece_base_model = exhibition_ns.model(
    "Piece",
    {
        "slug": fields.String,
        "input_original": fields.String,
        "input_translated": fields.String,
        "artifact_url_1": fields.String,
        "artifact_url_2": fields.String,
        "artifact_url_3": fields.String,
        "artifact_url_4": fields.String,
        "tweeted_at": fields.String,
        "tweet_id": fields.String,
        "tweet_response_id": fields.String,
    }
)

participant_model = exhibition_ns.model(
    "ParticipantBase",
    {
        "username": fields.String,
        "profile_url": fields.String,
        "affiliated_party": fields.String,
    }
)

piece_with_participant_model = exhibition_ns.inherit(
    "PieceWithParticipant",
    piece_base_model,
    {
        "participant": fields.Nested(participant_model)
    }
)
participant_base_model = exhibition_ns.inherit(
    "Participant",
    participant_model,
    {
        "pieces": fields.List(fields.Nested(piece_base_model))
    }
)
