import db_connector
import base64
from uuid import uuid4
from support import main_dict


def insert_rows(table_name, collection):
    getattr(db_connector, table_name).insert_many(collection).execute()


def is_empty(table_name):
    result = getattr(db_connector, table_name).get_or_none()
    return True if result is None else False


def append_picture_for_select(element):
    result = {key: getattr(element.item, key) for key in main_dict}
    result['uuid'] = element.item.uuid
    result['image_base64'] = base64.encodebytes(element.image).decode('UTF-8')

    return result


def append_picture_for_insert(element):
    item = db_connector.Item.get_or_none(db_connector.Item.uuid == element['item'])
    if item is not None:
        return {'item': item, 'uuid': uuid4(), 'type': element['type'],
                'image': base64.b64decode(element['image']), 'link': element['link']}
    else:
        return None


def check_articles(collection):
    def check_article(uuid):
        return db_connector.Item.get_or_none(db_connector.Item.uuid == uuid)

    items = [check_article(uuid) for uuid in collection]
    return [item for item in items if item is None]


def create_link(articles):
    link_uuid = uuid4()
    collection = [{'ref': link_uuid, 'data': articles}]
    insert_rows('link', collection)

    return link_uuid


def get_link(ref):
    return db_connector.Link.get_or_none(db_connector.Link.ref == ref)
