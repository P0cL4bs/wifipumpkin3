from wifipumpkin3.core.servers.rest.ext import auth
from wifipumpkin3.core.servers.rest.blueprints import restapi
from wifipumpkin3.core.utility.collection import SettingsINI
import uuid


def load_extensions(app):
    auth.init_app(app)
    restapi.init_app(app)


def secretkey_generate():
    return str(uuid.uuid4())


def init_app(app, config):
    conf = SettingsINI.getInstance()
    secret_key = secretkey_generate()
    conf.set("rest_api_settings", "SECRET_KEY", secret_key)
    app.config.update(TESTING=False, SECRET_KEY=secret_key)
