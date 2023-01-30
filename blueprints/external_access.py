from io import BytesIO
from flask import Blueprint, request, render_template, send_file
import db_handler
import excel_handler
from support import *


BIG_IMAGE_TYPE = 1

external_access = Blueprint('external_access', __name__,
                            template_folder='templates')


@external_access.route('/collection', methods=['GET'])
def show_collection():
    link = db_handler.get_link(request.args.get('ref'))
    if link is None:
        return resp(404, create_response(False, LINK_NOT_FOUND_MESSAGE))

    page = request.args.get('page')
    if page is None:
        page = 1
    elif type(page) != type(int):
        try:
            page = int(page)
        except ValueError:
            page = 1

    article_collection = db_handler.form_article_collection(link, page)
    image_collection = [db_handler.append_picture_for_select(element)
                        for element in article_collection]

    pagination = db_handler.form_pagination(link, page)

    return render_template('collection.html', image_collection=image_collection,
                           main_dict=main_dict, pagination=pagination)


@external_access.route("/article", methods=['GET'])
def show_article():
    item_buff = db_handler.initialize_item_buff(request.args)
    image_collection = db_handler.form_image_collection(item_buff.item, BIG_IMAGE_TYPE)
    angle_collection = db_handler.form_angle_collection(item_buff.item)

    return render_template('article.html', image_collection=image_collection,
                           angle_collection=angle_collection, item_buff=item_buff)


@external_access.route("/angle", methods=['GET'])
def show_angle():
    angle = db_handler.get_picture_by_id(request.args.get('uuid'))

    return render_template('angle.html', angle=angle)


@external_access.route("/getfile/", methods=['GET'])
def get_file():
    """prepare excel file, contains data from link"""
    link = db_handler.get_link(request.args.get('ref'))
    try:
        page = int(request.args.get('page'))
    except ValueError:
        page = 1

    if link is None:
        return resp(404, create_response(False, LINK_NOT_FOUND_MESSAGE))

    article_collection = db_handler.form_article_collection(link, page=page)
    image_collection = [db_handler.append_picture_for_select(element)
                        for element in article_collection]

    base64_excel = excel_handler.save_collection_to_excel(image_collection, True)

    return Response(status=200, mimetype="text/plain", response=base64_excel)


@external_access.route("/get_picture", methods=['GET'])
def get_picture():
    try:
        item_id = request.args.get('uuid')
        image_type = request.args.get('type')

        raw_picture = db_handler.get_raw_picture_by_item(item_id, image_type)
        result = send_file(BytesIO(raw_picture), mimetype='image/jpg')
    except:
        result = Response(status=200, mimetype="text/plain", response='{not found}')

    return result
