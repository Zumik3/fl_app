import db_connector
from support import image_table_names


class ImageRepository:
    image = db_connector.Image

    @staticmethod
    def _get_image_table_name(image_type: int):
        return image_table_names[image_type]

    def get_image_id_by_item(self, item_id: str, image_type: int = 0) -> image or None:
        image = self.image.get_or_none(self.image.item == item_id,
                                       self.image.type == image_type)
        if image is not None:
            return image.uuid

    def get_raw_picture(self, image_id: str, image_type: int = 0):
        table_name = self._get_image_table_name(image_type)
        image_table = getattr(db_connector, table_name)
        typed_image = image_table.get_or_none(image_table.image_id == image_id)
        if typed_image is not None:
            return typed_image.picture


class UserRepository:
    user = db_connector.User

    def get_user_by_username(self, username):
        return self.user.get_or_none(
            self.user.username == username)
