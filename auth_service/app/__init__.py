from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import config
from flasgger import Swagger
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
swagger = Swagger()
cors = CORS()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/api/v1/auth')
    swagger.init_app(app)
    return app
