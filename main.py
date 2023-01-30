from flask import Flask
from blueprints.external_access import external_access
from blueprints.internal_access import internal_access
from flask_bootstrap import Bootstrap5
from db_connector import db


app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.register_blueprint(external_access)
app.register_blueprint(internal_access)


@app.before_request
def _db_connect():
    """ This hook ensures that a connection is opened to handle any queries """
    db.connect(reuse_if_open=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)
