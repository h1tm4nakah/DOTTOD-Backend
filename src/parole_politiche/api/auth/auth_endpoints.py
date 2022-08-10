"""API endpoint definitions for /auth namespace."""
import datetime
from http import HTTPStatus
from flask_restx import Namespace, Resource
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import contains_eager
from sqlalchemy import desc, or_
from parole_politiche.api.auth.auth_parsers import (
    auth_reqparser,
    admin_tweet_date_parser,
    get_submitted_tweets,
    admin_tweet_submit_translation_parser,
    get_translation_filters,
    get_generation_filters,
    admin_tweet_submit_generated_parser,
)
from parole_politiche.api.auth.auth_helpers import process_login_request, process_logout_request
from parole_politiche.api.auth.auth_decorators import token_required
from parole_politiche.api.auth.auth_serializers import (
    auth_ns, admin_tweet_basic_model, participant_admin_model, piece_admin_model
)
from parole_politiche.api.serializers import piece_base_model
from parole_politiche.models.exhibition import Participant, Piece
from typing import List, Dict
from parole_politiche import db
from parole_politiche.clients.twitter_client import TwitterClient
from parole_politiche.clients.gpt3_client import GPT3Client
from parole_politiche.clients.dalle2_client import Dalle2Client
from parole_politiche.utils.tweet_utils import filter_tweet_text, get_tweet_score

@auth_ns.route("/login", endpoint="auth_login")
class LoginUser(Resource):
    """Handles HTTP requests to URL: /api/auth/login."""

    @auth_ns.expect(auth_reqparser)
    @auth_ns.response(int(HTTPStatus.OK), "Login succeeded.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Email or password does not match")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Authenticate an existing user and return an access token."""
        request_data = auth_reqparser.parse_args()
        email = request_data.get("email")
        password = request_data.get("password")
        print(f"* Attempt to login from email: {email}")
        return process_login_request(email, password)


@auth_ns.route("/logout", endpoint="auth_logout")
class LogoutUser(Resource):
    """Handles HTTP requests to URL: /api/auth/logout."""

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Log out succeeded, token is no longer valid.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    def post(self):
        """Add token to blacklist, deauthenticating the current user."""
        return process_logout_request()


@auth_ns.route("/tweets/generate", endpoint="auth_generate_tweets")
class GenerateTweetsAPIs(Resource):
    """Handles HTTP requests to URL: /api/auth/tweets/generate."""

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Log out succeeded, token is no longer valid.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    @auth_ns.expect(admin_tweet_date_parser)
    @token_required
    @auth_ns.marshal_with(admin_tweet_basic_model)
    def get(self):
        """Fetch best tweet at a given date"""
        args_dict = admin_tweet_date_parser.parse_args()
        if "date" not in args_dict:
            date = datetime.datetime.now()
        else:
            date = args_dict["date"]

        filters =[]
        if "usernames" in args_dict:
            for u in args_dict["usernames"]:
                print(u)
                filters.append((Participant.username == u))

        print(f"Generating tweets for date {date} and users {args_dict['usernames']}")
        # Response doc: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
        # Get all participants aka users we are monitoring, from the database
        participants: List[Participant] = db.session.query(Participant).filter(or_(*filters)).all()
        tweet_list: List[Dict[str,str]] = []
        # Iterate though them and fetch the tweets
        p: Participant
        for p in participants:
            tweets: List[Dict[str, str]] = TwitterClient.get_tweets(p, date)
            # Check if we have at least one tweet
            if tweets:
                selected_tweet = None
                for t in tweets:
                    if selected_tweet is None:
                        selected_tweet = t
                    else:
                        if get_tweet_score(t) > get_tweet_score(selected_tweet):
                            selected_tweet = t

                print(f"Selected Tweet of user @{p.username} --> [ID: {selected_tweet.id}] {filter_tweet_text(selected_tweet.text)}")
                print(selected_tweet.created_at)
                tweet_list.append(
                    {
                        "tweet": filter_tweet_text(selected_tweet.text),
                        "tweeted_at": selected_tweet.created_at,
                        "username": p.username,
                        "tweet_id": selected_tweet.id,
                        "retweet_count": selected_tweet.public_metrics['retweet_count'],
                        "reply_count": selected_tweet.public_metrics['reply_count'],
                        "like_count": selected_tweet.public_metrics['like_count']
                    }
                )

        return tweet_list, int(HTTPStatus.OK)

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Log out succeeded, token is no longer valid.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    @token_required
    @auth_ns.marshal_with(piece_base_model)
    def post(self):
        tweets_dict: List[Dict[str,str]] = get_submitted_tweets()
        generated_pieces: List[Piece] = []
        print(f"Accessing storing generated tweets with args: {generated_pieces}")
        for tweet in tweets_dict:
            try:
                db.session.query(Piece).filter_by(slug=f"{tweet['username']}-{tweet['tweet_id']}").one()
                print(f"The Tweet {tweet['tweet_id']} already exist in the database")
            except NoResultFound:
                try:
                    piece: Piece = Piece(
                            slug=f"{tweet['username']}-{tweet['tweet_id']}",
                            input_original=tweet['tweet'],
                            tweet_id=tweet['tweet_id'],
                            tweet_retweet_count=tweet['retweet_count'],
                            tweet_reply_count=tweet['reply_count'],
                            tweet_like_count=tweet['like_count'],
                            tweeted_at=datetime.datetime.strptime(tweet['tweeted_at'], '%d/%m/%Y %H:%M:%S'),
                            account_username=tweet['username']
                        )
                    print(f"--- Storing: {piece}")
                    db.session.add(piece)
                    db.session.commit()
                    generated_pieces.append(piece)
                    print(f"The Tweet {tweet['tweet_id']} was successfully added to the database")
                except Exception as e:
                    print(f"Something went wromg when creating tweet {tweet['tweet_id']} --> {e}")

        return generated_pieces, int(HTTPStatus.OK)


@auth_ns.route("/tweets/translate", endpoint="auth_translate_tweets")
class TranslateTweetsAPIs(Resource):
    """Handles HTTP requests to URL: /api/auth/tweets/translate."""

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Log out succeeded, token is no longer valid.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    @token_required
    @auth_ns.marshal_with(participant_admin_model)
    def get(self):
        tweet_filter = get_translation_filters()
        participants: List[Participant] = (
            db.session.query(Participant)
            .join(Piece, Participant.pieces)
            .options(contains_eager(Participant.pieces))
            .filter(
                tweet_filter
            )
            .order_by(desc(Piece.created_at))
            .all()
        )
        return participants, int(HTTPStatus.OK)


@auth_ns.route("/tweets/translate/<string:tweet_id>", endpoint="auth_translate_tweets_patch")
class TranslateTweetsPatchAPIs(Resource):
    """Handles HTTP requests to URL: /api/auth/tweets/translate."""

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Log out succeeded, token is no longer valid.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    @token_required
    @auth_ns.marshal_with(piece_admin_model)
    def patch(self, tweet_id):
        piece: Piece = db.session.query(Piece).filter_by(tweet_id=tweet_id).first()
        if piece is None:
            return {}, int(HTTPStatus.BAD_REQUEST)

        translation_dict = admin_tweet_submit_translation_parser.parse_args()
        if "input_translated" in translation_dict:
            piece.input_translated = translation_dict["input_translated"]
            db.session.commit()
        else:
            try:
                translated_prompt: str = GPT3Client.get_translation(piece.input_original)
                piece.input_translated = translated_prompt
                print(f"Successfully translated:\n{piece.input_original}\nto\n{piece.input_translated}")
            except Exception:
                print(f"Something went wrong translating piece {piece.input_original}")

        return piece, int(HTTPStatus.OK)


@auth_ns.route("/tweets/images", endpoint="auth_generate_images")
class GenerateImagesAPIs(Resource):
    """Handles HTTP requests to URL: /api/auth/tweets/images."""

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Log out succeeded, token is no longer valid.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    @token_required
    @auth_ns.marshal_with(participant_admin_model)
    def get(self):
        tweet_filter = get_generation_filters()
        participants: List[Participant] = (
            db.session.query(Participant)
            .join(Piece, Participant.pieces)
            .options(contains_eager(Participant.pieces))
            .filter(
                tweet_filter
            ).filter(Piece.input_translated.is_not(None))
            .order_by(desc(Piece.created_at))
            .all()
        )
        return participants, int(HTTPStatus.OK)


@auth_ns.route("/tweets/images/<string:tweet_id>", endpoint="auth_generate_images_by_id")
class GenerateImagesAPIsByID(Resource):
    """Handles HTTP requests to URL: /api/auth/tweets/images."""

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Log out succeeded, token is no longer valid.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    @token_required
    @auth_ns.marshal_with(piece_admin_model)
    def get(self, tweet_id):
        piece: Piece = db.session.query(Piece).filter_by(tweet_id=tweet_id).first()
        if piece is None:
            return {}, int(HTTPStatus.BAD_REQUEST)

        generated_images = Dalle2Client.generate_image(piece)

        piece.artifact_url_1 = generated_images[0]
        piece.artifact_url_2 = generated_images[1]
        piece.artifact_url_3 = generated_images[2]
        piece.artifact_url_4 = generated_images[3]

        db.session.commit()

        return piece, int(HTTPStatus.OK)

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Log out succeeded, token is no longer valid.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    @token_required
    @auth_ns.marshal_with(piece_admin_model)
    def patch(self, tweet_id):
        piece: Piece = db.session.query(Piece).filter_by(tweet_id=tweet_id).first()
        if piece is None:
            return {}, int(HTTPStatus.BAD_REQUEST)

        generated_images = admin_tweet_submit_generated_parser.parse_args()
        print(generated_images)
        if "artifact_url_1" in generated_images and generated_images["artifact_url_1"] is not None:
            if generated_images["artifact_url_1"] != piece.artifact_url_1:
                ucare_url_1 = Dalle2Client.uploadcare.upload(generated_images["artifact_url_1"])
                piece.artifact_url_1 = ucare_url_1
        else:
            piece.artifact_url_1 = None

        if "artifact_url_2" in generated_images and generated_images["artifact_url_2"] is not None:
            if generated_images["artifact_url_2"] != piece.artifact_url_2:
                ucare_url_2 = Dalle2Client.uploadcare.upload(generated_images["artifact_url_2"])
                piece.artifact_url_2 = ucare_url_2
        else:
            piece.artifact_url_2 = None

        if "artifact_url_3" in generated_images and generated_images["artifact_url_3"] is not None:
            if generated_images["artifact_url_3"] != piece.artifact_url_3:
                ucare_url_3 = Dalle2Client.uploadcare.upload(generated_images["artifact_url_3"])
                piece.artifact_url_3 = ucare_url_3
        else:
            piece.artifact_url_3 = None

        if "artifact_url_4" in generated_images and generated_images["artifact_url_4"] is not None:
            if generated_images["artifact_url_4"] != piece.artifact_url_4:
                ucare_url_4 = Dalle2Client.uploadcare.upload(generated_images["artifact_url_4"])
                piece.artifact_url_4 = ucare_url_4
        else:
            piece.artifact_url_4 = None

        db.session.commit()

        return piece, int(HTTPStatus.OK)


@auth_ns.route("/participants", endpoint="auth_get_particpants_filters")
class GetPartsFilters(Resource):
    """Handles HTTP requests to URL: /api/auth/participants."""

    @auth_ns.doc(security="Bearer")
    @auth_ns.response(int(HTTPStatus.OK), "Log out succeeded, token is no longer valid.")
    @auth_ns.response(int(HTTPStatus.BAD_REQUEST), "Validation error.")
    @auth_ns.response(int(HTTPStatus.UNAUTHORIZED), "Token is invalid or expired.")
    @auth_ns.response(int(HTTPStatus.INTERNAL_SERVER_ERROR), "Internal server error.")
    @token_required
    def get(self):
        participants: Participant = db.session.query(Participant).all()
        return [{"value": p.username, "label": p.username} for p in participants], int(HTTPStatus.OK)