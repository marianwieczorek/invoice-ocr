import math
import typing

import cv2
import imutils
import numpy as np


def normalize_colors(image: np.ndarray) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]

    def quantiles(values: np.ndarray, p: float) -> typing.Tuple[float, float]:
        v_min, v_max = np.quantile(values, [p, 1.0 - p])
        if v_max - v_min < 1e-1:
            v_max = v_min + 1.0
        return v_min, v_max

    def normalize_min(values: np.ndarray) -> np.ndarray:
        v_min, v_max = quantiles(values.ravel(), 0.1)
        values = v_max * (values - v_min) / (v_max - v_min)
        values = values.astype(int)
        values[values < 0] = 0
        values[values > 255] = 255
        return values

    def normalize_min_max(values: np.ndarray) -> np.ndarray:
        v_min, v_max = quantiles(values.ravel(), 0.02)
        values = 255.0 * (values - v_min) / (v_max - v_min)
        values = values.astype(int)
        values[values < 0] = 0
        values[values > 255] = 255
        return values

    hsv[:, :, 0] = 0
    hsv[:, :, 1] = normalize_min(saturation)
    hsv[:, :, 2] = normalize_min_max(value)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)


def sorted_color(color: np.ndarray) -> np.ndarray:
    c_max = max(color)
    c_min = min(color)
    return np.array([c_max, c_min, c_min])


def crop(image: np.ndarray, size: typing.Tuple[int, int]) -> np.ndarray:
    height, width = image.shape[:2]
    h_size = min(size[0], height)
    h_off = max((height - h_size) // 2, 0)
    w_size = min(size[1], height)
    w_off = max((width - w_size) // 2, 0)
    return image[h_off:h_off + h_size, w_off:w_off + w_size]


def rotate_and_crop(image: np.ndarray, angle: float) -> np.ndarray:
    result = imutils.rotate_bound(image, math.degrees(angle))

    crop_angle = abs(angle) % (math.pi / 4.0)
    height, width = image.shape[:2]
    size = min(height, width)
    valid_size = int(size / (math.cos(crop_angle) + math.sin(crop_angle)))

    result = crop(result, (valid_size, valid_size))
    return result


def fit(image: np.ndarray, size: int) -> np.ndarray:
    height, width = image.shape[:2]
    if width > height:
        return imutils.resize(image, width=size)
    return imutils.resize(image, height=size)
