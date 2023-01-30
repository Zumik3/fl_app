import datetime
import db_handler
from flask import json
from werkzeug.security import generate_password_hash
from os import path


def hash_field(collection, hash_field_name):
    def hash_password(item):
        item[hash_field_name] = generate_password_hash(item[hash_field_name])
        return item

    return [hash_password(item) for item in collection]


def load_json_from_file(file_path):
    if path.isfile(file_path) and path.splitext(file_path)[-1] == '.json':
        with open(file_path) as f:
            try:
                return json.load(f)
            except Exception as e:
                print(f'json load error: {e}')


def prepare_link(element):
    return {'created_date': datetime.datetime.now(), 'data': element['data'],
            'ref': element['ref']}


def initialize_table(table_name, file_path):
    if db_handler.is_empty(table_name):
        elements_data = load_json_from_file(file_path)

        if 'users' in file_path:
            elements_data = hash_field(elements_data, 'password')

        elif 'images' in file_path:
            elements_data = [db_handler.append_picture_for_insert(element)
                             for element in elements_data]
            elements_data = [element for element in elements_data
                             if element is not None]

        elif 'links' in file_path:
            elements_data = [prepare_link(element)
                             for element in elements_data]

        db_handler.insert_rows(table_name, elements_data)
