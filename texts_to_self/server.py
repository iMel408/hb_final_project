from flask import Flask


def create_app():

    app = Flask('texts_to_self')
    app.config.from_pyfile('config.py', silent=True)

    @app.route('/')
    def hello():
        return 'Flask is Live!'

    from texts_to_self.model import connect_to_db, db

    with app.app_context():
        connect_to_db(app)
        db.init_app(app)


    from texts_to_self import main, auth

    app.register_blueprint(auth.bp)
    app.register_blueprint(main.bp)
    app.add_url_rule('/', endpoint='user')


    from texts_to_self.tasks import make_celery

    make_celery(app)

    return app


if __name__ == "__main__":
    app.debug = True

    connect_to_db(app)