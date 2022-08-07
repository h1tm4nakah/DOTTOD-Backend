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
