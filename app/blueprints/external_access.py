from flask import Blueprint, abort, Response, json, request, render_template
from jinja2 import TemplateNotFound
from app import db_connector, db_handler, excel_handler
from app.support import *

external_access = Blueprint('external_access', __name__, template_folder='templates')


@external_access.route('/ping/')
def index():

    try:
        return resp(200, {'status': True})
    except TemplateNotFound:
        abort(404)
        

@external_access.route('/collection/', methods=['GET'])
def show_collection():

    ref = request.args.get('ref')
    keyword = request.args.get('keyword')

    link = db_handler.get_link(ref)
    if link is None:
        return resp(404, create_response(False, LINK_NOT_FOUND_MESSAGE))

    data_array = get_data_from_link(link)
    if keyword is not None:
        query_result = db_connector.Image.select().join(db_connector.Item).where(
            (db_connector.Item.uuid << data_array) & (db_connector.Item.article.contains(keyword)))
    else:
        query_result = db_connector.Image.select().join(db_connector.Item).where(
            (db_connector.Item.uuid << data_array) & (db_connector.Image.type == 0))

    image_collection = [db_handler.append_picture_for_select(element) for element in query_result]

    return render_template('index.html', image_collection=image_collection, main_dict=main_dict)


@external_access.route("/article/", methods=['GET'])
def show_article():

    uuid = request.args.get('uuid')
    query_result = db_connector.Image.select().join(db_connector.Item).where(
        db_connector.Item.uuid == uuid)
    image_collection = [db_handler.append_picture_for_select(element) for element in query_result]

    return render_template("article.html", image_collection=image_collection)


@external_access.route("/getfile/", methods=['GET'])
def get_file():

    ref = request.args.get('ref')

    link = db_handler.get_link(ref)
    if link is None:
        return resp(404, create_response(False, LINK_NOT_FOUND_MESSAGE))

    file_name = './' + ref + '.xlsx'
    data_array = get_data_from_link(link)

    query_result = db_connector.Image.select().join(db_connector.Item).where(
        (db_connector.Item.uuid << data_array) & (db_connector.Image.type == 0))

    image_collection = [db_handler.append_picture_for_select(element) for element in query_result]
    result = excel_handler.main_table_to_excel(file_name, image_collection, True)

    return Response(status=200, mimetype="text/plain", response=result)

