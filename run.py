"""Flask CLI/Application entry point."""
import os
import time
import click
from parole_politiche import create_app, db
from parole_politiche.models.exhibition import Participant, Piece
from parole_politiche.models.user import User
from parole_politiche.clients.twitter_client import TwitterClient
from parole_politiche.clients.gpt3_client import GPT3Client
from parole_politiche.clients.dalle2_client import Dalle2Client
from parole_politiche.utils.tweet_utils import filter_tweet_text, get_tweet_score
from typing import List, Dict
from sqlalchemy.orm.exc import NoResultFound

app = create_app(os.getenv("FLASK_ENV", "development"))

@app.after_request
def after_request_callback(response):
    if os.getenv("FLASK_ENV") == "development":
        time.sleep(0.5)

    @response.call_on_close
    def process_after_request():
        # Do whatever is necessary here
        pass

    return response


@app.shell_context_processor
def shell():
    return {
        "db": db,
        "Participant": Participant,
        "Piece": Piece,
        "User": User,
    }


@app.cli.command("generate_images", short_help="Generate images using DALL-E 2")
def generate_images():
    # Get pieces that have a translation and at least one image is empty
    pieces: List[Piece] = db.session.query(Piece).filter(
        (Piece.input_translated.is_not(None))
        & (
            (Piece.artifact_url_1.is_(None))
            | (Piece.artifact_url_2.is_(None))
            | (Piece.artifact_url_3.is_(None))
            | (Piece.artifact_url_4.is_(None))
        )
    ).all()
    print(f"Selected {len(pieces)} pieces")
    for piece in pieces:
        Dalle2Client.generate_image_and_store(piece)


@app.cli.command("translate_tweets", short_help="Translate Tweets using GPT3")
def translate_tweets():
    # Get all untranslated pieces
    pieces: List[Piece] = db.session.query(Piece).filter(
        Piece.input_translated.is_(None)
    ).all()
    # Foreach piece get the translation and store it in the db
    for piece in pieces:
        try:
            translated_prompt: str = GPT3Client.get_translation(piece.input_original)
            piece.input_translated = translated_prompt
            print(f"Successfully translated:\n{piece.input_original}\nto\n{piece.input_translated}")
            db.session.commit()
        except Exception:
            print(f"Something went wrong translating piece {piece.input_original}")


@app.cli.command("get_tweets", short_help="Get user tweets")
def get_tweets():
    # Response doc: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/tweet
    # Get all participants aka users we are monitoring, from the database
    participants: List[Participant] = db.session.query(Participant).all()
    # Iterate though them and fetch the tweets
    p: Participant
    for p in participants:
        tweets: List[Dict[str, str]] = TwitterClient.get_tweets(p)
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

            try:
                db.session.query(Piece).filter_by(slug=f"{p.username}-{selected_tweet.id}").one()
                print(f"The Tweet {t.id} already exist in the database")
            except NoResultFound:
                piece: Piece = Piece(
                    slug=f"{p.username}-{selected_tweet.id}",
                    input_original=filter_tweet_text(selected_tweet.text),
                    tweet_id=selected_tweet.id,
                    tweet_retweet_count=selected_tweet.public_metrics['retweet_count'],
                    tweet_reply_count=selected_tweet.public_metrics['reply_count'],
                    tweet_like_count=selected_tweet.public_metrics['like_count'],
                    tweeted_at=selected_tweet.created_at,
                    account_username=p.username
                )
                db.session.add(piece)
    db.session.commit()


@app.cli.command("add_user", short_help="Add a new user")
@click.argument("email")
@click.argument("password")
def add_user(email, password):
    """Add a new user to the database with email address = EMAIL."""
    if User.find_by_email(email):
        error = f"Error: {email} is already registered"
        click.secho(f"{error}\n", fg="red", bold=True)
        return 1

    new_user = User(email=email, password=password)
    db.session.add(new_user)
    db.session.commit()

    click.secho(f"Successfully added new {new_user}", fg="blue", bold=True)
    return 0


@app.cli.command("reply_to_tweet", short_help="Reply to tweet")
def reply_to_tweet():
    piece: Piece = db.session.query(Piece).first()
    print(piece.__dict__)
    if piece.artifact_url_1 is None:
        return

    TwitterClient.reply_to_tweet(piece)



if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1919, debug=True)


