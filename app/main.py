from flask import Flask
from app.support import resp
from initial import initialize
from blueprints.external_access import external_access
from blueprints.internal_access import internal_access
from flask_bootstrap import Bootstrap5


app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.register_blueprint(external_access)
app.register_blueprint(internal_access)

JSON_DIR = './initial/'


def initialize_all():

    initialize.initialize_table('User', f'{JSON_DIR}users.json')
    initialize.initialize_table('Item', f'{JSON_DIR}items.json')
    initialize.initialize_table('Image', f'{JSON_DIR}images.json')
    initialize.initialize_table('Link', f'{JSON_DIR}links.json')


initialize_all()


@app.route('/ping2/')
def index2():

    return resp(200, {'status': True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)
