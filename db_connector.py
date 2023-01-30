from abc import ABC
from peewee import *
from uuid import uuid4
from playhouse.shortcuts import ReconnectMixin
from credent import LOGIN, PASSWD, DB_NAME, DB_HOST


class ReconnectMySQLDatabase(ReconnectMixin, MySQLDatabase, ABC):
    pass


db = ReconnectMySQLDatabase(DB_NAME, host=DB_HOST, port=3306,
                            user=LOGIN, passwd=PASSWD)


class BaseModel(Model):
    class Meta:
        database = db


class MediumBlobField(BlobField, ABC):
    field_type = 'MEDIUMBLOB'


class MediumTextField(TextField, ABC):
    field_type = 'MEDIUMTEXT'


class User(BaseModel):
    """Users for internal API"""
    uuid = CharField(primary_key=True, default=uuid4, max_length=36)
    username = CharField(column_name='username', max_length=100)
    password = CharField(column_name='password', max_length=200)
    email = CharField(column_name='email', max_length=100)
    active = BooleanField(column_name='active')

    class Meta:
        table_name = 'users'


class Item(BaseModel):
    """Description of article and it's props"""
    uuid = CharField(primary_key=True, default=uuid4, max_length=36)
    article = CharField(column_name='article', max_length=50)
    group = CharField(column_name='group', max_length=50, default='_')
    collection = CharField(column_name='collection', max_length=50)
    brand = CharField(column_name='brand', max_length=50)
    type = CharField(column_name='type', max_length=50)
    color = CharField(column_name='color', max_length=50)
    segment = CharField(column_name='segment', max_length=50)
    material = CharField(column_name='material', max_length=50)
    lining = CharField(column_name='lining', max_length=50)
    insole = CharField(column_name='insole', max_length=50)
    size_chart = CharField(column_name='size_chart', max_length=100)
    packaged = IntegerField(column_name='packaged')
    price = FloatField(column_name='price')

    class Meta:
        table_name = 'items'


class Image(BaseModel):
    """Images descriptions for articles"""
    uuid = CharField(primary_key=True, default=uuid4, max_length=36)
    item = ForeignKeyField(Item, to_field='uuid', index=True)
    type = IntegerField(column_name='type', index=True)  # 0 - main pic, 1 - big pic
    link = CharField(column_name='link', index=True)
    size = FloatField(column_name='size')
    width = FloatField(column_name='width', default=0)
    height = FloatField(column_name='height', default=0)

    class Meta:
        table_name = 'images'


class BaseImage(BaseModel):
    image_id = ForeignKeyField(Image, to_field='uuid', index=True)
    picture = MediumBlobField(column_name='picture')

    class Meta:
        table_name = 'base_images'


class BigImage(BaseModel):
    image_id = ForeignKeyField(Image, to_field='uuid', index=True)
    picture = MediumBlobField(column_name='picture')

    class Meta:
        table_name = 'big_images'


class AngleImage(BaseModel):
    image_id = ForeignKeyField(Image, to_field='uuid', index=True)
    picture = MediumBlobField(column_name='picture')

    class Meta:
        table_name = 'angle_images'


class Link(BaseModel):
    """Contains links that collect articles for external users"""
    ref = CharField(primary_key=True, default=uuid4, column_name='ref')
    data = MediumTextField(column_name='data')
    created_date = DateField(column_name='created_date')
    count = IntegerField(column_name='count')

    class Meta:
        table_name = 'links'


if not Item.table_exists():
    Item.create_table()
if not Image.table_exists():
    Image.create_table()
if not User.table_exists():
    User.create_table()
if not Link.table_exists():
    Link.create_table()
if not BaseImage.table_exists():
    BaseImage.create_table()
if not BigImage.table_exists():
    BigImage.create_table()
if not AngleImage.table_exists():
    AngleImage.create_table()
