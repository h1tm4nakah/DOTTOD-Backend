from flask_restx import Namespace, Model, fields
from parole_politiche.api.auth.auth_parsers import user_model

auth_ns = Namespace(name="auth", validate=True)
auth_ns.models[user_model.name] = user_model

admin_tweet_basic_model = auth_ns.model(
    "AdminTweet",
    {
        "tweet": fields.String,
        "tweeted_at": fields.String,
        "username": fields.String,
        "tweet_id": fields.String,
        "retweet_count": fields.String,
        "reply_count": fields.String,
        "like_count": fields.String,
    }
)

piece_admin_model = auth_ns.model(
    "PieceAdmin",
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
        "tweet_retweet_count": fields.String,
        "tweet_reply_count": fields.String,
        "tweet_like_count": fields.String,
    }
)


participant_admin_model = auth_ns.model(
    "ParticipantAdmin",
    {
        "username": fields.String,
        "profile_url": fields.String,
        "affiliated_party": fields.String,
        "pieces": fields.List(fields.Nested(piece_admin_model))
    }
)



