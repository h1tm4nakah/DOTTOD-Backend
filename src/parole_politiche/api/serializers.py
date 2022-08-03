from flask_restx import Namespace, Model, fields

exhibition_ns = Namespace(name="exhibition", validate=True)

exhibition_base_model = exhibition_ns.model(
    "Exhibition",
    {
        "id": fields.Integer,
        "name": fields.String,
        "category": fields.String,
        "group": fields.String,
    }
)