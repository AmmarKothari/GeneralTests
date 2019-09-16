import flask
import config

app = flask.Flask(__name__)
app.config.from_object(config.Config)

from app import routes