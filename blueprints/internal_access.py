from flask import Blueprint, request, render_template
from peewee import IntegrityError
import db_handler
from auth import auth
from support import resp, create_response

ARTICLE_SELECT_LIMIT = 100
internal_access = Blueprint('internal_access', __name__, template_folder='templates')


@internal_access.route('/status/', methods=['GET'])
@auth.login_required
def show_status():

    status_table = db_handler.get_status_table()
    return render_template('status.html', status_table=status_table)


@internal_access.route("/api/set_sku", methods=['POST'])
@auth.login_required
def set_sku():
    try:
        request_data = request.get_json(force=True)

        for element in request_data:
            db_handler.add_or_update_item(element)

        return resp(200, create_response())

    except IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@internal_access.route("/api/set_price", methods=['POST'])
@auth.login_required
def set_price():
    try:
        request_data = request.get_json(force=True)

        for element in request_data:
            item = db_handler.get_item(element['uuid'])
            db_handler.update_item(item, element)

        return resp(200, create_response())

    except IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@internal_access.route("/api/delete_sku", methods=['DELETE'])
@auth.login_required
def delete_sku():
    try:
        request_data = request.get_json(force=True)

        for element in request_data:
            db_handler.delete_item(element)

        return resp(200, create_response())

    except IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@internal_access.route('/api/set_picture', methods=['POST'])
@auth.login_required
def set_picture():
    try:
        filtered_picture_data = db_handler.form_filtered_image_data(request.get_json(force=True))

        for element in filtered_picture_data:
            db_handler.add_or_update_picture(element)

        return resp(200, create_response())

    except IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@internal_access.route("/api/create_link", methods=['POST'])
@auth.login_required
def create_link():
    try:

        request_data = request.get_json(force=True)
        invalid_articles = db_handler.check_articles(request_data)

        if len(invalid_articles) > 0:
            return resp(400, {'success': False, 'error': invalid_articles})

        link_ref = db_handler.create_link(request_data)
        return resp(200, create_response(True, None, link_ref))

    except:
        return resp(400, create_response(False, str('error')))


@internal_access.route("/api/delete_link", methods=['DELETE'])
@auth.login_required
def delete_link():
    """delete all links older than date"""
    try:
        db_handler.delete_links(request.args.get('date'))
        return resp(200, create_response())

    except IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@internal_access.route("/api/get_pictures_by_item", methods=['GET'])
@auth.login_required
def get_pictures_by_item():
    try:
        pictures_uuids = db_handler.get_pictures_by_item(request.args.get('uuid'))
        return resp(200, create_response(data=pictures_uuids))

    except IntegrityError as e:
        return resp(400, create_response(False, str(e)))
