from flask import json, Response
from collections import OrderedDict

INVALID_TOKEN_MESSAGE = 'Invalid token passed'
UNAUTHORIZED_ACCESS_MESSAGE = 'Unauthorized access'
LINK_NOT_FOUND_MESSAGE = 'Link is not found'
ARTICLE_NOT_IN_LINK = 'Article is not in link'
AUTHORIZATION_TOKEN = 'd4SjCgRP35p55IsGHVWpTSBAIHusQmcS'

DEFAULT_PICTURE_COLUMN_WIDTH = 15
DEFAULT_ROW_HEIGHT = 55
IMAGE_COLUMN_NAME = 'Изображение'
SHEET_NAME = 'Sheet_'

MAXIMUM_IMAGE_SIZE = 2048  # in Kb
BASE_IMAGE_WIDTH = 105
BASE_IMAGE_HEIGHT = 65
BASE_IMAGE_RATIO = 0.35

ITEMS_PER_PAGE = 50
TEMP_PIC_FILENAME = '_temp.jpg'

main_dict = OrderedDict(article='Артикул', collection='Сезон',
                        brand='Марка', type='Тип', color='Цвет',
                        segment='Сегмент', material='Материал', lining='Подкладка',
                        insole='Стелька', size_chart='Размерная сетка',
                        packaged='В коробе/упаковке', price='Цена')


class ImageTableNameMapper:
    image_table_names = {0: 'BaseImage', 1: 'BigImage', 2: 'AngleImage'}

    def __init__(self, image_type: int):
        self.image_table = self.image_table_names[image_type]


class WrongRefException(BaseException):
    def __init__(self, ref):
        super().__init__(f'Ref: {ref} is not found in DB')


class MissingArgumentException(BaseException):
    def __init__(self, arg):
        self.arg = arg
        self.message = f'Missing argument: {self.arg}'
        super().__init__(self.message)


def resp(code, data):
    return Response(status=code,
                    mimetype='application/json',
                    response=json.dumps(data) + '\n')


def create_response(success: bool = True, error: str = None,
                    ref: str = None, data=None) -> dict:
    result = {"success": success, "error": error, "ref": ref, "data": data}

    return {key: value for key, value in result.items() if value is not None}


def get_data_from_link(link):
    return json.loads(str(link.data).replace("'", "\""))
