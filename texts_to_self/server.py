from flask import Flask
from texts_to_self.tasks import make_celery


app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)

celery = make_celery(app)

@app.route('/')
def hello():
    return 'Flask is Live!'

from texts_to_self.model import connect_to_db, db

connect_to_db(app)
db.init_app(app)
    #
    # from texts_to_self.tasks import make_celery
    #
    # make_celery(app)

from texts_to_self import main, auth

app.register_blueprint(auth.bp)
app.register_blueprint(main.bp)
app.add_url_rule('/', endpoint='user')

