import random
import typing

import cv2
import numpy as np
import tensorflow.keras as keras

import invoice.training.images as im
import invoice.training.loaders as ldr


image_size = 25


def generate_image_rotation_pairs(data_list: typing.List[ldr.JsonData], base_path: str):
    rotation_list = list(range(-100, 100, 1))
    image_gen = (ldr.load_image_from_json(data, base_path) for data in data_list)
    image_gen = (im.fit(image, 300) for image in image_gen)
    rotation_gen = (ldr.load_rotation_from_json(data) for data in data_list)

    image_rotation_gen = ((im.rotate_and_crop(image, angle - rotation), angle)
                          for image, rotation in zip(image_gen, rotation_gen)
                          for angle in rotation_list)
    image_rotation_gen = ((im.fit(image, image_size), rotation) for image, rotation in image_rotation_gen)
    image_rotation_gen = ((im.add_padding(image), rotation) for image, rotation in image_rotation_gen)
    image_rotation_gen = ((normalize_image(image), normalize_rotation(rotation))
                          for image, rotation in image_rotation_gen)
    return image_rotation_gen


def normalize_image(image: np.ndarray) -> np.ndarray:
    return 2.0 * (image / 255.0) - 1.0


def normalize_rotation(angle: float) -> float:
    return angle / 180.0


def create_model(input_shape: typing.Tuple[int, int, int]) -> keras.models.Model:
    model = keras.models.Sequential()

    model.add(keras.layers.Flatten(input_shape=input_shape))
    model.add(keras.layers.Dense(360, activation='relu'))
    model.add(keras.layers.Dense(180, activation='relu'))
    model.add(keras.layers.Dropout(rate=0.2))
    model.add(keras.layers.Dense(1))
    model.compile(optimizer='adam', loss='mse', metrics=['mse'])
    return model


def main():
    print('Loading json file...')
    base_path = '../assets/'
    data_list = ldr.load_json_data(base_path + 'labels.json')
    random.shuffle(data_list)
    data_test, data_train = data_list[:1], data_list[1:]

    if True:
        cv2.imshow('Test image', im.fit(ldr.load_image_from_json(data_test[0], base_path), image_size))
        cv2.waitKey(1000)

    print('Generating testing data...')
    image_rotation_gen = generate_image_rotation_pairs(data_test, base_path)
    x_test, y_test = zip(*image_rotation_gen)
    x_test = np.array(x_test)
    y_test = np.array(y_test)

    print('Generating training data...')
    image_rotation_gen = generate_image_rotation_pairs(data_train, base_path)
    x_train, y_train = zip(*image_rotation_gen)
    x_train = np.array(x_train)
    y_train = np.array(y_train)

    print('Training model...')
    input_shape = x_train[0].shape
    model = create_model(input_shape)
    model.fit(x_train, y_train, epochs=10, validation_data=(x_test, y_test), verbose=1)

    print('Done!')


if __name__ == '__main__':
    main()
