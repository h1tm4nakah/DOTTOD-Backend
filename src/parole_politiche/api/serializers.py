from flask_restx import Namespace, fields

exhibition_ns = Namespace(name="exhibition", validate=True)

piece_base_model = exhibition_ns.model(
    "Piece",
    {
        "slug": fields.String,
        "input_original": fields.String,
        "input_translated": fields.String,
        "artifact_url": fields.String,
        "tweeted_at": fields.String,
    }
)

participant_base_model = exhibition_ns.model(
    "Participant",
    {
        "username": fields.String,
        "profile_url": fields.String,
        "affiliated_party": fields.String,
        "pieces": fields.List(fields.Nested(piece_base_model))
    }
)
