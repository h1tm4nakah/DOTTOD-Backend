"""Class definition for Exhibition model."""
from sqlalchemy.sql import func
from parole_politiche import db

class Participant(db.Model):
    """Exhibition Participant model for a generic resource in a REST API."""
    __tablename__ = "participant"
    
    username = db.Column(db.String(15), primary_key=True)
    profile_url = db.Column(db.String(300), nullable=False)
    twitter_id = db.Column(db.Integer, nullable=False)
    affiliated_party = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    @classmethod
    def find_by_username(cls, username):
        return cls.query.filter_by(username=username).first()
    
class Piece(db.Model):
    """Exhibition Piece model for a generic resource in a REST API."""
    __tablename__ = "piece"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(100), nullable=False, unique=True)
    input_original = db.Column(db.String(300), nullable=False)
    input_translated = db.Column(db.String(300), nullable=True)
    tweet_id = db.Column(db.String(100), nullable=False)
    tweet_retweet_count = db.Column(db.Integer, default=1, nullable=False)
    tweet_reply_count = db.Column(db.Integer, default=1, nullable=False)
    tweet_like_count = db.Column(db.Integer, default=1, nullable=False)
    artifact_url_1 = db.Column(db.String(300), nullable=True)
    artifact_url_2 = db.Column(db.String(300), nullable=True)
    artifact_url_3 = db.Column(db.String(300), nullable=True)
    artifact_url_4 = db.Column(db.String(300), nullable=True)
    tweeted_at = db.Column(db.DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    # FK
    account_username = db.Column(db.String(15), db.ForeignKey("participant.username"), nullable=False)

    # Relations
    participant = db.relationship("Participant", backref=db.backref("pieces"))

    @classmethod
    def find_by_slug(cls, slug):
        return cls.query.filter_by(slug=slug).first()
