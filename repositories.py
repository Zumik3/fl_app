import uuid

import db_connector
from support import ImageTableNameMapper


class ImageRepository:
    image = db_connector.Image

    def get_image_id_by_item(self, item_id: str, image_type: int = 0) -> uuid.uuid4() or None:
        return self.image.get_or_none(self.image.item == item_id,
                                      self.image.type == image_type).uuid

    def get_image_id_by_item_and_angle(self, item_id: str, image_angle: str = None) -> uuid.uuid4() or None:
        return self.image.get_or_none((self.image.item == item_id) & (self.image.type == 2) &
                                      (self.image.link.endswith('_' + image_angle))).uuid

    @staticmethod
    def get_raw_picture(image_id: str, image_type: int = 0):
        table_name = ImageTableNameMapper(image_type).image_table
        image_table = getattr(db_connector, table_name)
        typed_image = image_table.get_or_none(image_table.image_id == image_id)

        if typed_image is not None:
            return typed_image.picture

    @db_connector.db.atomic()
    def delete_picture(self, picture_uuid: str):
        picture = self.image.get_or_none(db_connector.Image.uuid == picture_uuid)
        if picture is not None:
            picture.delete_instance()


class UserRepository:
    user = db_connector.User

    def get_user_by_username(self, username):
        return self.user.get_or_none(
            self.user.username == username)
