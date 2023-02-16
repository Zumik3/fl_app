import db_connector
import base64
from uuid import uuid4
from support import main_dict, get_data_from_link, MAXIMUM_IMAGE_SIZE, ITEMS_PER_PAGE, WrongRefException, \
    MissingArgumentException
from datetime import datetime
from typing import NamedTuple, Iterable, List, Dict, Union, Any, Optional
from peewee import DatabaseError
from repositories import ImageRepository
from excel_handler import save_collection_to_excel

IMAGE_TYPE_DEFAULT = 0


class ItemBuffer(NamedTuple):
    prev_uuid: str
    next_uuid: str
    item: db_connector.Item
    ref_uuid: str


def get_status_table():
    status_table = []
    names = ['connection', 'items', 'images', 'images (small)', 'images (big)', 'images (angle)', 'links',
             'image size (Mb)']
    queries = [
        db_connector.db.connect(reuse_if_open=True),
        db_connector.Item.select().count(),
        db_connector.Image.select().count(),
        db_connector.Image.select().where(db_connector.Image.type == 0).count(),
        db_connector.Image.select().where(db_connector.Image.type == 1).count(),
        db_connector.Image.select().where(db_connector.Image.type == 2).count(),
        db_connector.Link.select().count(),
        (db_connector.Image.select(db_connector.fn.SUM(db_connector.Image.size).alias('size')))
    ]
    for name, query in zip(names, queries):
        try:
            if name == 'connection':
                status_table.append({name: True})
            elif name == 'image size (Mb)':
                cursor = query.execute()
                for (element) in cursor:
                    status_table.append({name: f'{element.size / 1024:.2f}'})
            else:
                status_table.append({name: query})
        except DatabaseError:
            status_table.append({name: False})

    return status_table


def get_image_table_name(image_type: int) -> str or None:
    if image_type == 0:
        return 'BaseImage'
    elif image_type == 1:
        return 'BigImage'
    elif image_type == 2:
        return 'AngleImage'
    else:
        return None


def insert_rows(table_name: str, collection: Iterable) -> None:
    getattr(db_connector, table_name).insert_many(collection).execute()


def is_empty(table_name: str) -> bool:
    result = getattr(db_connector, table_name).get_or_none()
    return True if result is None else False


def append_picture_for_select(element) -> dict:
    result = {key: getattr(element.item, key) for key in main_dict}
    result['uuid'] = element.item.uuid
    result['image_base64'] = get_base64_picture(element)
    result['width'] = element.width
    result['height'] = element.height

    return result


def get_raw_picture(image: db_connector.Image) -> db_connector.BigImage \
                                                  | db_connector.BaseImage | \
                                                  db_connector.AngleImage | None:
    table_name = get_image_table_name(image.type)
    image_table = getattr(db_connector, table_name)
    return image_table.get_or_none(image_table.image_id == image.uuid)


def get_base64_picture(image: db_connector.Image) -> str:
    picture = get_raw_picture(image)
    return base64.encodebytes(picture.picture).decode('UTF-8') if picture is not None else ''


def append_picture_for_insert(element) -> dict or None:
    item = db_connector.Item.get_or_none(
        db_connector.Item.uuid == element['item'])

    if item is not None and element['size'] <= MAXIMUM_IMAGE_SIZE:
        return {'item': item, 'uuid': uuid4(), 'type': element['type'],
                'image': base64.b64decode(element['image']),
                'link': element['link'], 'size': element['size'],
                'width': element['width'], 'height': element['height']}
    else:
        return None


def check_articles(articles_list: list) -> list:
    """returns list of invalid articles"""
    items = {uuid: check_article(uuid) for uuid in articles_list}
    return [key for key in items.keys() if items[key] is None]


def check_article(uuid: str) -> db_connector.Item or None:
    return db_connector.Item.get_or_none(db_connector.Item.uuid == uuid)


def create_link(articles: list or tuple) -> uuid4 or None:
    """create a link for a list or tuple of articles, ttl - 30 days"""
    try:
        link_uuid = uuid4()
        collection = [{'ref': link_uuid, 'data': articles, 'created_date': datetime.now(),
                       'count': len(articles)}]
        insert_rows('Link', collection)

        return link_uuid

    except db_connector.DatabaseError:
        return None


def get_link(ref: str) -> db_connector.Link or None:
    return db_connector.Link.get_or_none(db_connector.Link.ref == ref)


def get_item(uuid: str) -> db_connector.Item or None:
    return db_connector.Item.get_or_none(db_connector.Item.uuid == uuid)


def get_picture(item_uuid: str, link: str = None, image_type: int = 0) -> db_connector.Image or None:
    if image_type in (0, 1):  # check link only for angle pics
        cursor = db_connector.Image.select().join(db_connector.Item).where(
            (db_connector.Item.uuid == item_uuid)
            & (db_connector.Image.type == image_type))
    else:
        cursor = db_connector.Image.select().join(db_connector.Item).where(
            (db_connector.Item.uuid == item_uuid)
            & (db_connector.Image.link == link)
            & (db_connector.Image.type == image_type))

    for result in cursor:
        return result


@db_connector.db.atomic()
def delete_pictures(item: db_connector.Item, image_types: tuple) -> None:
    """Delete all pictures for article. Selection by type"""
    query = db_connector.Image.delete().where((db_connector.Image.item == item) &
                                              (db_connector.Image.type << image_types))
    query.execute()


@db_connector.db.atomic()
def delete_links(date: str or datetime.date) -> None:
    try:
        internal_date = date if type(date) == datetime.date else datetime.strptime(date, '%Y%m%d')
        query = db_connector.Link.delete().where(db_connector.Link.created_date <= internal_date)
        query.execute()

    except db_connector.DatabaseError as e:
        raise e


def initialize_item_buff(args) -> ItemBuffer or None:
    prev_uuid, next_uuid = None, None
    uuid = args.get('uuid')

    if uuid is None:
        raise MissingArgumentException('uuid')

    link = get_link(args['ref'])

    if link is None:
        raise WrongRefException(args['ref'])

    data = get_data_from_link(link)

    for i in range(len(data)):
        if data[i] == uuid:
            prev_uuid = data[i - 1]
            next_uuid = data[(i + 1) % len(data)]

    return ItemBuffer(prev_uuid=prev_uuid, next_uuid=next_uuid,
                      item=check_article(uuid), ref_uuid=link.ref)


def get_raw_picture_by_id(uuid: str) -> db_connector.Image | None:
    picture = db_connector.Image.get_or_none(db_connector.Image.uuid == uuid)
    if picture is not None:
        return get_raw_picture(picture)


def get_picture_by_id(uuid: str) -> db_connector.AngleImage or None:
    angle_pic = db_connector.Image.get_or_none(db_connector.Image.uuid == uuid)
    if angle_pic is not None:
        return append_picture_for_select(angle_pic)


def form_image_collection(item: db_connector.Item, image_type: int) -> List or None:
    cursor = db_connector.Image.select().join(db_connector.Item).where(
        (db_connector.Item.uuid == item.uuid) & (db_connector.Image.type == image_type))

    return [append_picture_for_select(element) for element in cursor]


def form_angle_collection(item: db_connector.Item) -> db_connector.db.cursor() or None:
    return db_connector.Image.select().join(db_connector.Item).where(
        (db_connector.Item.uuid == item.uuid) & (
                db_connector.Image.type == 2)).order_by(db_connector.Image.link)


def form_article_collection(link: db_connector.Link, page: int = 1) -> db_connector.db.cursor:
    data_array = get_data_from_link(link)
    return db_connector.Image.select().join(db_connector.Item).where(
        (db_connector.Item.uuid << data_array) & (db_connector.Image.type == 0)) \
        .order_by(db_connector.Item.article).paginate(page, ITEMS_PER_PAGE)


def form_filtered_image_data(iterable: Iterable) -> list:
    picture_data = [append_picture_for_insert(element) for element in iterable]
    # if append_picture_for_insert(element) is not None]
    return list(filter(lambda x: x is not None, picture_data))


@db_connector.db.atomic()
def add_or_update_item(element) -> None:
    item = get_item(element['uuid'])

    if item is not None:
        update_item(item, element)
    else:
        db_connector.Item.insert(element).execute()


def update_item(item, element) -> None:
    for key in element.keys():
        setattr(item, key, element[key])

    item.save()


@db_connector.db.atomic()
def add_or_update_picture(element: dict) -> None:
    current_image = get_picture(element['item'], element['link'], element['type'])
    picture_data = element.pop('image')
    if current_image is not None:
        db_connector.Image.update(element).where(db_connector.Image.uuid == current_image.uuid)
    else:
        insert_rows('Image', element)
        current_image = get_picture(element['item'], element['link'], element['type'])

    table_name = get_image_table_name(element['type'])
    if table_name is None:
        return

    current_table = getattr(db_connector, table_name)
    pic = current_table.get_or_none(current_table.image_id == current_image)

    if pic is None:
        current_table.insert(image_id=current_image, picture=picture_data).execute()
    else:
        current_table.update(image_id=current_image, picture=picture_data).\
            where(current_table.id == pic.id).execute()


@db_connector.db.atomic()
def delete_item(uuid: str) -> None:
    item = get_item(uuid)

    if item is not None:
        delete_pictures(item, (0, 1, 2))
        item.delete_instance()


@db_connector.db.atomic()
def delete_picture(uuid) -> None:
    repository = ImageRepository()
    repository.delete_picture(uuid)


def get_raw_picture_by_item(item_id: str,
                            image_type: Optional[Union[int, str]] = IMAGE_TYPE_DEFAULT) -> bytes or None:
    if item_id is None:
        return None

    image_type = IMAGE_TYPE_DEFAULT if image_type is None else int(image_type)
    repository = ImageRepository()
    image_id = repository.get_image_id_by_item(item_id, image_type)

    return repository.get_raw_picture(image_id, image_type)


def get_pictures_by_item(uuid: str) -> list:
    base_images = db_connector.Image.select(
        db_connector.Image.link, db_connector.Image.type,
        db_connector.BaseImage.picture.alias('picture')).join(db_connector.BaseImage).where(
        db_connector.Image.item == uuid)
    big_images = db_connector.Image.select(
        db_connector.Image.link, db_connector.Image.type,
        db_connector.BigImage.picture.alias('picture')).join(db_connector.BigImage).where(
        db_connector.Image.item == uuid)
    angle_images = db_connector.Image.select(
        db_connector.Image.link, db_connector.Image.type,
        db_connector.AngleImage.picture.alias('picture')).join(db_connector.AngleImage).where(
        db_connector.Image.item == uuid)

    cursor = (base_images | big_images | angle_images)

    return [{'uuid': element.uuid, 'type': element.type,
             'link': element.link,
             'image': base64.encodebytes(element.baseimage.picture).decode('UTF-8')}
            for element in cursor]


def form_pagination(link, page: int) -> list:
    data_array = get_data_from_link(link)
    pages = (len(data_array) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE
    pages = max(1, pages)

    selected_pages = (0, page - 3, page - 2, page - 1, page, page + 1, pages - 1)
    pagination: List[Dict[str, Union[Union[str, bool, int], Any]]] = []
    for count in range(pages):

        if count in selected_pages:
            current_page: int = count + 1
            ref_str = f'ref={link.ref}&page={current_page}'
            pagination.append({'ref': ref_str, 'current_page': current_page == page, 'page': current_page})

    return pagination


def form_base64_excel_collection(link: db_connector.Link, page: int = 1) -> str or None:
    article_collection = form_article_collection(link, page)
    image_collection = [append_picture_for_select(element)
                        for element in article_collection]

    return save_collection_to_excel(image_collection)
