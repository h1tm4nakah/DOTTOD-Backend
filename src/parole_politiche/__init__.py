"""Flask app initialization via factory pattern."""
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from parole_politiche.config import get_config
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

cors = CORS()
db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()

# Config names comes from setup.py
def create_app(config_name="production"):
    app = Flask("parole_politiche", static_url_path='/static')
    app.config.from_object(get_config(config_name))

    from parole_politiche.api import api_bp

    app.register_blueprint(api_bp)

    cors.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    return app
