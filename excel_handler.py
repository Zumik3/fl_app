import pandas as pd
import base64
from support import *
import os
import re
from io import BytesIO
from uuid import uuid4
from typing import NamedTuple


class ScaleSizes(NamedTuple):
    x_scale: float
    y_scale: float


def file_to_base64(file_name: str) -> str:
    with open(file_name, 'rb') as infile:
        raw_data = infile.read()
        return base64.encodebytes(raw_data).decode('UTF-8')


def add_picture_to_excel(worksheet, image: dict, column: int, row: int) -> None:
    """add base64-image to excel worksheet"""
    image_base64 = image['image_base64']
    base64_data = re.sub('^data:image/.+;base64,', '', image_base64)
    byte_data = base64.b64decode(base64_data)
    image_data = BytesIO(byte_data)

    min_scale = get_scale_sizes(image['width'], image['height'])

    worksheet.insert_image(row, column, 'image',
                           {'image_data': image_data, 'x_scale': min_scale,
                            'y_scale': min_scale, 'x_offset': 2, 'y_offset': 2})


def save_collection_to_excel(image_collection: list, remove_file: bool = True) -> base64:
    """Save collection to Excel file in base64"""
    df = pd.DataFrame({main_dict[x]: [a[x] for a in image_collection]
                       for x in main_dict})

    df.insert(0, IMAGE_COLUMN_NAME, "")

    file_name = str(uuid4())
    excel_writer = pd.ExcelWriter(file_name, engine='xlsxwriter')
    df.to_excel(excel_writer, sheet_name='Sheet1', index=False)

    worksheet = excel_writer.sheets['Sheet1']
    worksheet.set_column(0, len(main_dict), DEFAULT_PICTURE_COLUMN_WIDTH)
    worksheet.set_default_row(DEFAULT_ROW_HEIGHT)

    for i in range(len(image_collection)):
        add_picture_to_excel(worksheet, image_collection[i], 0, i + 1)

    excel_writer.save()

    base64result = file_to_base64(file_name)

    if remove_file:
        os.remove(file_name)

    return base64result


def get_scale_sizes(width: float, height: float) -> float:

    if width > 0:
        x_scale = BASE_IMAGE_WIDTH / width
    else:
        x_scale = BASE_IMAGE_RATIO

    if height > 0:
        y_scale = BASE_IMAGE_HEIGHT / height
    else:
        y_scale = BASE_IMAGE_RATIO

    return min(x_scale, y_scale)
