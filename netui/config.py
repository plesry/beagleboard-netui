from os.path import abspath, dirname, join
basedir = abspath(dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = 'netui-flask-secret-key'
    CSRF_ENABLED = True
    CSRF_SESSION_KEY = 'netui-flask-secret-key'
    DB_REL_PATH = 'db/netui.sqlite'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + join(basedir, DB_REL_PATH)

    UPLOAD_FOLDER = 'uploads/'
    ALLOWED_EXTENSIONS = set(['sqlite', 'csv'])


class ProductionConfig(Config):
    DEBUG = False


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
