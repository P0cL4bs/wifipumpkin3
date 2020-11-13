from wifipumpkin3.core.utility.collection import SettingsINI
import uuid
from flask import request, jsonify
import jwt
from functools import wraps


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if "x-access-token" in request.headers:
            token = request.headers["x-access-token"]

        if not token:
            return jsonify({"message": "Token is missing!"})
        conf = SettingsINI.getInstance()

        try:
            app_secret_key = conf.get("rest_api_settings", "SECRET_KEY")
            data = jwt.decode(token, app_secret_key)
            app_public_id = conf.get("rest_api_settings", "public_id")
            if app_public_id != data["public_id"]:
                return jsonify({"message": "Token is invalid!"})
        except:
            return jsonify({"message": "Token is invalid!"})

        return f(*args, **kwargs)

    return decorated


def init_app(app):
    conf = SettingsINI.getInstance()
    conf.set("rest_api_settings", "public_id", str(uuid.uuid4()))
