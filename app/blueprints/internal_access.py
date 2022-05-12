from flask import Blueprint, request, render_template
from app import db_connector, db_handler
from app.auth import auth
from app.support import resp, create_response

ARTICLE_SELECT_LIMIT = 100
internal_access = Blueprint('internal_access', __name__, template_folder='templates')


@internal_access.route('/status/', methods=['GET'])
@auth.login_required
def show_status():
    status_table = []
    try:
        db_connector.db.connect(reuse_if_open=True)
        status_table.append({'DBConnection': True})
    except db_connector.DatabaseError:
        status_table.append({'DBConnection': False})

    try:
        status_table.append({'Items': db_connector.Item.select().count()})
    except db_connector.DatabaseError:
        status_table.append({'Items': False})

    try:
        status_table.append({'Images': db_connector.Image.select().count()})
    except db_connector.DatabaseError:
        status_table.append({'Images': False})

    try:
        status_table.append({'Users': db_connector.User.select().count()})
    except db_connector.DatabaseError:
        status_table.append({'Users': False})

    return render_template('status.html', status_table=status_table)


@internal_access.route("/api/set_sku", methods=['POST'])
@auth.login_required
def set_sku():
    request_data = request.get_json(force=True)
    data_array = request_data['data']

    try:
        db_connector.Item.insert_many(data_array).execute()
        db_connector.db.close()
        return resp(200, create_response())

    except db_connector.IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@internal_access.route('/api/set_picture', methods=['POST'])
@auth.login_required
def set_picture():
    request_data = request.get_json(force=True)

    picture_data = [db_handler.append_picture_for_insert(element) for element in request_data]
    filtered_picture_data = list(filter(lambda x: x is not None, picture_data))

    try:
        if len(filtered_picture_data) > 0:
            db_connector.Image.insert_many(filtered_picture_data).execute()
            db_connector.db.close()

        return resp(200, create_response())

    except db_connector.IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@internal_access.route("/api/create_link", methods=['POST'])
@auth.login_required
def create_link():
    request_data = request.get_json(force=True)
    result = db_handler.check_articles(request_data)

    if len(result) > 0:
        return resp(400, {"success": False, "error": f"Element {result} not found in DB"})

    try:
        link = db_handler.create_link(request_data)
        return resp(200, create_response(True, None, link.ref))

    except db_connector.IntegrityError as e:
        return resp(400, create_response(False, str(e)))


@internal_access.route("/api/articles_list", methods=['GET'])
@auth.login_required
def articles_list():
    keyword = request.args.get('keyword')
    articles = {}

    if keyword is not None:
        query_result = db_connector.Item.select().where(
            db_connector.Item.article.contains(keyword)).order_by(db_connector.Item.group)\
                .limit(ARTICLE_SELECT_LIMIT)

        current_group = None
        # a_list = []
        for i in query_result:
            if current_group != i.group:
                articles[i.group] = []
                current_group = i.group

            temp_d = {'article': i.article, 'uuid': i.uuid,
                      'pictures': db_handler.get_pictures_for_item(i)}
            articles[i.group].append(temp_d)
            # a_list.append(i)

        # res = db_handler.append_pictures_for_article_list(a_list)

    return render_template('article_list.html', articles=articles)


@internal_access.route("/article/edit", methods=['GET'])
@auth.login_required
def article_edit():
    uuid = request.args.get('uuid')
    query_result = db_connector.Image.select().join(db_connector.Item).where(
        db_connector.Item.uuid == uuid)
    image_collection = [db_handler.append_picture_for_select(element) for element in query_result]

    return render_template("article_edit.html", image_collection=image_collection)



