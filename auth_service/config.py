import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'trantrungnhat'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ITSDANGEROUS_SECRET_KEY = os.environ.get('SECRET_KEY_ITSDANGEROUS') or 'trantrungnhat'
    ITSDANGEROUS_EXPIRATION = int(os.environ.get('ITSDANGEROUS_EXPIRATION', 3600))  # s
    SECRET_JWT_KEY = os.environ.get('SECRET_JWT_KEY') or 'jwt_trantrungnhat'
    BLOG_ADMIN = os.environ.get('BLOG_ADMIN') or 'trantrungnhat6196@gmail.com'
    RABBITMQ_URL = 'localhost'
    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'mysql+pymysql://root:Wakerjacob@90@localhost' \
                                                                    ':3306/authentication'


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'mysql+pymysql://root:Wakerjacob@90@mysql' \
                                                                    ':3306/authentication'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
