import typing

import imutils
import numpy as np


def rotate_and_crop(image: np.ndarray, angle: float) -> np.ndarray:
    result = imutils.rotate_bound(image, angle)

    in_height, in_width = image.shape[:2]
    out_height, out_width = result.shape[:2]
    if (in_height - in_width) * (out_height - out_width) < 0.0:
        in_width, in_height = in_height, in_width

    result = crop(result, (in_height, in_width))
    return result


def crop(image: np.ndarray, size: typing.Tuple[int, int]) -> np.ndarray:
    height, width = image.shape[:2]
    h = max((height - size[0]) // 2, 0)
    w = max((width - size[1]) // 2, 0)
    return image[h:height - h, w:width - w]


def fit(image: np.ndarray, size: int) -> np.ndarray:
    height, width = image.shape[:2]
    if width > height:
        return imutils.resize(image, width=size)
    return imutils.resize(image, height=size)


def add_padding(image: np.ndarray) -> np.ndarray:
    height, width = image.shape[:2]
    size = max(height, width)
    h = size - height
    w = size - width
    return np.pad(image.data, ((0, h), (0, w), (0, 0)))
