from flask_httpauth import HTTPBasicAuth
from werkzeug.security import check_password_hash
from app import db_connector, support


auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):

    user = db_connector.User.get_or_none(
        db_connector.User.username == username)

    if user is not None and check_password_hash(user.password, password):
        return username


@auth.error_handler
def unauthorized():
    return support.resp(401, {'error': support.UNAUTHORIZED_ACCESS_MESSAGE})
