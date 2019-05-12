from flask import Flask
from celery import Celery


def create_app():

    app = Flask(__name__, instance_relative_config=True)

    app.config.from_pyfile('config.py', silent=True)

    @app.route('/')
    def hello():

        return 'Flask is Live!'

    from texts_to_self.model import connect_to_db, db
    connect_to_db(app)
    db.init_app(app)

    from texts_to_self import main, auth
    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.add_url_rule('/', endpoint='user')

    return app


# def make_celery(app):
#     celery = Celery(
#         app.import_name,
#         backend=app.config['CELERY_RESULT_BACKEND'],
#         broker=app.config['CELERY_BROKER_URL']
#     )
#     connect_to_db(app)
#     celery.conf.update(app.config)
#
#     class ContextTask(celery.Task):
#
#         def __call__(self, *args, **kwargs):
#             with app.app_context():
#                 return self.run(*args, **kwargs)
#
#     celery.Task = ContextTask
#
#     return celery