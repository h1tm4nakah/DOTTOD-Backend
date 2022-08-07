"""Installation script for parole politiche application."""
from pathlib import Path
from setuptools import setup, find_packages

DESCRIPTION = (
    "Boilerplate Flask API with Flask-RESTx, SQLAlchemy, pytest, flake8, "
    "tox configured"
)
APP_ROOT = Path(__file__).parent
README = (APP_ROOT / "README.md").read_text()
AUTHOR = "Pietro Rustici"
AUTHOR_EMAIL = "p.rustici@gmail.com"
PROJECT_URLS = {
    "Documentation": "https://tba.com",
    "Bug Tracker": "https://tba.com",
    "Source Code": "https://tba.com",
}
INSTALL_REQUIRES = [
    "Flask==1.1.4",
    "Flask-Bcrypt",
    "Flask-Cors",
    "Flask-Migrate",
    "flask-restx",
    "Flask-SQLAlchemy",
    "PyJWT",
    "python-dateutil",
    "python-dotenv",
    "requests",
    "urllib3",
    "werkzeug==0.16.1",
    "mysqlclient",
    "markupsafe==2.0.1",
    "itsdangerous==1.1.0",
    "gunicorn",
    "tweepy",
    "openai",
    "dalle2",
    "pyuploadcare",
]

EXTRAS_REQUIRE = {
    "dev": [
        "black",
        "flake8",
        "pre-commit",
        "pydocstyle",
        "tox",
    ]
}

setup(
    name="parole_politiche",
    description=DESCRIPTION,
    long_description=README,
    long_description_content_type="text/markdown",
    version="0.1",
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    maintainer=AUTHOR,
    maintainer_email=AUTHOR_EMAIL,
    license="MIT",
    url="https://tba.com",
    project_urls=PROJECT_URLS,
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
)
