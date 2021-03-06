from flask import Flask
from app.api import image_service
from config import config


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    app.register_blueprint(blueprint=image_service, url_prefix='/api/v1/image')
    return app
