import math
import random as rnd
import typing

import cv2
import imutils
import numpy as np


class NoiseParams(object):
    def __init__(self, seed: float, sigma: float):
        self.seed = seed
        self.sigma = sigma


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


def crop_to_square(image: np.ndarray, size: int) -> np.ndarray:
    actual_height, actual_width = image.shape[:2]
    h_off = max((actual_height - size) // 2, 0)
    w_off = max((actual_width - size) // 2, 0)
    return image[h_off:h_off + size, w_off:w_off + size]


def rotate_and_crop(image: np.ndarray, angle: float) -> np.ndarray:
    result = imutils.rotate_bound(image, math.degrees(angle))

    crop_angle = abs(angle) % (math.pi / 4.0)
    height, width = image.shape[:2]
    size = min(height, width)
    valid_size = int(size / (math.cos(crop_angle) + math.sin(crop_angle)))

    result = crop_to_square(result, valid_size)
    if result.shape[:2] != (valid_size, valid_size):
        raise ValueError(f'Image has undesired size: {result.shape} instead of {valid_size}')
    return result


def noise(image: np.ndarray, noise_params: NoiseParams) -> np.ndarray:
    def gen_noise(n: int):
        random = rnd.Random(noise_params.seed)
        for _ in range(n):
            yield random.gauss(0.0, noise_params.sigma)

    noise_values = np.array([value for value in gen_noise(image.size)]).reshape(image.shape)
    image = image + noise_values
    image[image < 0.0] = 0.0
    image[image > 255.0] = 255.0
    image = image.astype(np.uint8)
    return image


def fit(image: np.ndarray, size: int) -> np.ndarray:
    height, width = image.shape[:2]
    if width == height:
        image = cv2.resize(image, dsize=(size, size))
    elif width > height:
        image = imutils.resize(image, width=size)
    else:
        image = imutils.resize(image, height=size)
    return image
