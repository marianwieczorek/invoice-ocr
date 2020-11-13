import copy as cp
import math
import random as rnd
import typing

import cv2
import numpy as np
import tensorflow as tf
import tensorflow.keras as keras

import invoice.common.images as img
import invoice.common.labels as lbl
import invoice.training.data_generator as tr_batch


class Sample(object):
    def __init__(self, image_name: str, angle: float, label: int, noise: img.NoiseParams):
        self.image_name = image_name
        self.angle = angle
        self.label = label
        self.noise = noise


class ImageCache(object):
    def __init__(self, base_path: str, capacity: int):
        self._base_path = base_path
        self._names: typing.List[typing.Optional[str]] = capacity * [None]
        self._cache: typing.List[typing.Optional[np.ndarray]] = capacity * [None]
        self._index = 0

    def load(self, image_name: str) -> np.ndarray:
        image = [image for name, image in zip(self._names, self._cache) if name == image_name]
        if not image:
            image = [self._expensive_load(image_name)]
        return image[0]

    def _expensive_load(self, image_name: str) -> np.ndarray:
        image = cv2.imread(self._base_path + image_name)
        self._names[self._index] = image_name
        self._cache[self._index] = image
        self._index = 0 if self._index == len(self._cache) - 1 else self._index + 1
        return image


def create_intervals(num_intervals: int, min_angle: float) -> typing.List[float]:
    positive_intervals = [min_angle * (5.0 ** index) for index in range(num_intervals)]
    positive_intervals += [math.pi]
    negative_intervals = list(reversed([-angle for angle in positive_intervals]))
    return negative_intervals + positive_intervals


def load_data(base_path: str) -> typing.Dict[str, float]:
    data = lbl.load_json(base_path + 'labels.json')
    data = (lbl.Label.from_json(label_json) for label_json in data)
    data = ((label.image, label.mean_angle) for label in data)
    return {image_name: angle for image_name, angle in data}


def split_data(data: typing.List[str]) -> typing.Tuple[typing.List[str], typing.List[str]]:
    data = cp.copy(data)
    rnd.shuffle(data)
    split_index = max(len(data) // 10, 1)
    return data[:split_index], data[split_index:]


def random_sample(data: typing.Dict[str, float], image_name: str, intervals: typing.List[float]) -> Sample:
    current_angle = data[image_name]
    desired_angle = random_angle(intervals)
    label = create_label(desired_angle, intervals)
    return Sample(image_name, desired_angle - current_angle, label, create_noise())


def random_angle(intervals: typing.List[float]) -> float:
    index = rnd.randrange(len(intervals) - 1)
    return rnd.uniform(intervals[index], intervals[index + 1])


def create_label(angle: float, intervals: typing.List[float]) -> int:
    greater_than = (angle >= lower_bound for lower_bound in intervals)
    less_than = (angle <= upper_bound for upper_bound in intervals)
    _ = next(less_than)
    is_in = (gt and lt for gt, lt in zip(greater_than, less_than))

    def until_in_interval():
        for value in is_in:
            if value:
                break
            yield 1

    index = sum(until_in_interval()) - 1
    index = index if index >= 0 else len(intervals) - 3
    return index


def create_noise() -> img.NoiseParams:
    return img.NoiseParams(rnd.random(), 1.5)


def sample_to_image(cache: ImageCache, sample: Sample, input_size: int, num_classes: int):
    x = cache.load(sample.image_name)
    x = img.rotate_and_crop(x, sample.angle)
    x = img.fit(x, input_size)
    x = img.noise(x, sample.noise)
    x = img.normalize_colors(x)
    x = x[:, :, :2]
    x = x / 255.0
    y = keras.utils.to_categorical(sample.label, num_classes=num_classes)
    return x, y


KernelSize = typing.Union[int, typing.Tuple[int, int]]
Stride = KernelSize


def create_model(img_size: int, num_outputs: int) -> keras.models.Model:
    def conv2d(num_filters: int,
               kernel_size: KernelSize) -> keras.layers.Conv2D:
        return keras.layers.Conv2D(num_filters,
                                   kernel_size,
                                   padding='same',
                                   activation='relu',
                                   kernel_regularizer=keras.regularizers.l1(0.01))

    def separable_conv2d(num_filters: int, kernel_size: KernelSize) -> keras.layers.SeparableConv2D:
        return keras.layers.SeparableConv2D(num_filters,
                                            kernel_size,
                                            padding='same',
                                            activation='relu',
                                            kernel_regularizer=keras.regularizers.l1(0.01))

    def max_pool2d(pool_size: KernelSize) -> keras.layers.MaxPool2D:
        return keras.layers.MaxPool2D(pool_size)

    def dense(num_outputs_: int) -> keras.layers.Dense:
        return keras.layers.Dense(num_outputs_, activation='relu',
                                  kernel_regularizer=keras.regularizers.l1(0.01))

    def stack(*tensors: tf.Tensor) -> tf.Tensor:
        return tf.concat(tensors, axis=3)

    def scale_input(tensor: tf.Tensor) -> tf.Tensor:
        tensor = separable_conv2d(4, 3)(tensor)
        tensor = max_pool2d(2)(tensor)
        tensor = separable_conv2d(8, 3)(tensor)
        tensor = max_pool2d(2)(tensor)
        tensor = separable_conv2d(16, 3)(tensor)
        tensor = max_pool2d(2)(tensor)
        return tensor

    def extract_features(tensor: tf.Tensor) -> tf.Tensor:
        input_tensor = tensor
        tensor = conv2d(1, 9)(tensor)

        stack_size = 8
        tensor_stack: typing.List[typing.Optional[tf.Tensor]] = stack_size * [None]
        tensor_stack[0] = tensor
        for index in range(1, stack_size):
            tensor = conv2d(1, 7)(stack(input_tensor, tensor))
            tensor_stack[index] = tensor

        return conv2d(1, 5)(stack(*tensor_stack))

    def axis_reduction(tensor: tf.Tensor, axis: int) -> tf.Tensor:
        if axis == 1:
            pool_size = (2, 1)
        elif axis == 2:
            pool_size = (1, 2)
        else:
            raise ValueError(f'Invalid axis. Expected: 2 or 3, but was: {axis}')

        depth = 2
        while tensor.shape[axis] > 1:
            tensor = separable_conv2d(depth, 3)(tensor)
            tensor = max_pool2d(pool_size)(tensor)
            depth += 1
        return tensor

    def xy_reduction(tensor_x: tf.Tensor, tensor_y: tf.Tensor) -> tf.Tensor:
        tensor_x = tf.transpose(tensor_x, [0, 1, 3, 2])
        tensor_y = tf.transpose(tensor_y, [0, 1, 3, 2])
        tensor = stack(tensor_x, tensor_y)
        return conv2d(1, 9)(tensor)

    def classify(tensor: tf.Tensor) -> tf.Tensor:
        tensor = keras.layers.Flatten()(tensor)
        tensor = dense(num_outputs)(tensor)
        tensor = keras.layers.Dropout(rate=0.05)(tensor)
        return keras.layers.Dense(num_outputs, activation='relu')(tensor)

    def build_model():
        input_tensor = keras.layers.Input(shape=(img_size, img_size, 2))

        output_tensor = scale_input(input_tensor)
        output_tensor = extract_features(output_tensor)

        tensor_x = output_tensor
        tensor_x = axis_reduction(tensor_x, 2)

        tensor_y = tf.transpose(output_tensor, [0, 2, 1, 3])
        tensor_y = axis_reduction(tensor_y, 2)

        output_tensor = xy_reduction(tensor_x, tensor_y)
        output_tensor = axis_reduction(output_tensor, axis=1)
        output_tensor = classify(output_tensor)

        model = keras.models.Model(inputs=input_tensor, outputs=output_tensor)
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['categorical_accuracy'])
        return model

    return build_model()


def main():
    print('Creating classes... ', end='')
    intervals = create_intervals(4, math.radians(0.8))
    input_size = 512
    num_classes = len(intervals) - 2
    batch_size = 64
    print(f'{[math.degrees(v) for v in intervals]} in [°]')

    print('Creating model... ', end='')
    model = create_model(input_size, num_classes)
    print('done!')
    model.summary()

    print('Loading data from json file... ', end='')
    base_path = '../assets/'
    data = load_data(base_path)
    print(f'{len(data)} images loaded.')

    print('Split images into training and test data... ', end='')
    val_images, train_images = split_data(list(data.keys()))
    print(f'{len(train_images)} training and {len(val_images)} validation images created.')

    image_cache = ImageCache(base_path, len(train_images))

    def tr(sample):
        return sample_to_image(image_cache, sample, input_size, num_classes)

    print('Creating training samples... ', end='')
    train_samples = [random_sample(data, name, intervals) for name in train_images for _ in range(100)]
    print(f'{len(train_samples)} training samples created.')

    print('Creating generator for training... ', end='')
    train_seq = tr_batch.DataGenerator(train_samples, batch_size, tr)
    print('done!')

    print('Creating validation samples... ', end='')
    val_samples = [random_sample(data, name, intervals) for name in val_images for _ in range(20)]
    print(f'{len(val_samples)} validation samples created.')

    print('Creating validation data set... ', end='')
    val_seq = tr_batch.DataGenerator(val_samples, batch_size, tr)
    print('done!')

    print('Fit model...')
    num_epochs = 2
    model.fit(train_seq,
              steps_per_epoch=len(train_samples) // batch_size,
              epochs=num_epochs,
              validation_data=val_seq)


if __name__ == '__main__':
    main()
