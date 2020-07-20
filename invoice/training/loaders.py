import json
import typing

import cv2
import numpy as np

JsonData = typing.Mapping[str, typing.Union[str, int, float]]


class InvoiceLoadException(Exception):
    pass


def load_json_data(path: str) -> typing.List[JsonData]:
    try:
        with open(path) as file:
            return json.load(file)
    except OSError as e:
        raise InvoiceLoadException(f'Could not load json: {path}') from e


def load_image_from_json(data: JsonData, base_path: str) -> np.ndarray:
    path = base_path + data['file']
    image = cv2.imread(path, cv2.IMREAD_COLOR)
    if image is None:
        raise InvoiceLoadException(f'Could not load image: {path}')
    return image


def load_rotation_from_json(data: JsonData) -> float:
    return data['rotation-deg']
