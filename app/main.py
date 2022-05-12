from flask import Flask
from initial import initialize
from blueprints.external_access import external_access
from blueprints.internal_access import internal_access
from flask_bootstrap import Bootstrap5

app = Flask(__name__)
bootstrap = Bootstrap5(app)
app.register_blueprint(external_access)
app.register_blueprint(internal_access)


def initialize_all():
    json_dir = './initial/'

    initialize.initialize_table('User', f'{json_dir}users.json')
    initialize.initialize_table('Item', f'{json_dir}items.json')
    initialize.initialize_table('Image', f'{json_dir}images.json')
    initialize.initialize_table('Link', f'{json_dir}links.json')


initialize_all()


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=80)
