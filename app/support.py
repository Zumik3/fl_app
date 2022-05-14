from flask import json, Response

INVALID_TOKEN_MESSAGE = 'Invalid token passed'
UNAUTHORIZED_ACCESS_MESSAGE = 'Unauthorized access'
LINK_NOT_FOUND_MESSAGE = 'Link is not found'
ARTICLE_NOT_IN_LINK = 'Article not in link'
AUTHORIZATION_TOKEN = 'd4SjCgRP35p55IsGHVWpTSBAIHusQmcS'

DEFAULT_PICTURE_COLUMN_WIDTH = 15
DEFAULT_ROW_HEIGHT = 55
IMAGE_COLUMN_NAME = 'Изображение'
SHEET_NAME = 'Sheet_'

main_dict = dict(article='Артикул', collection='Сезон',
                 brand='Марка', type='Тип', color='Цвет',
                 segment='Сегмент', material='Материал', lining='Подкладка',
                 insole='Стелька', size_chart='Размерная сетка',
                 packaged='В коробе', price='Цена')


def resp(code, data):
    return Response(status=code,
                    mimetype='application/json',
                    response=json.dumps(data) + '\n')


def create_response(success=True, error=None, ref=None):
    """
    Creates dict for HTTP response
    :param success:
    :param error:
    :param ref:
    :return: Dict
    """
    result = {"success": success}
    if error is not None:
        result["error"] = error
    if ref is not None:
        result["ref"] = ref
    return result


def get_data_from_link(link):
    return json.loads(str(link.data).replace("'", "\""))
