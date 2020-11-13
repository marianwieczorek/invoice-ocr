import random as rnd
import typing

import numpy as np
import tensorflow.keras as keras

import invoice.training.async_tasks as async_tasks

Sample = typing.Type['SampleType']
Data = typing.Tuple[np.ndarray, np.ndarray]
Transformation = typing.Callable[[Sample], Data]


class DataGenerator(keras.utils.Sequence):

    def __init__(self, samples: typing.List[Sample], batch_size: int, tr: Transformation):
        self._batch_size = batch_size
        self._tr = tr

        self._samples = samples
        self._last_index = None
        self._generator = None

        self.on_epoch_end()

    def __len__(self):
        return len(self._samples) // self._batch_size

    def __getitem__(self, index: int):
        batch = self._batch(index)
        tasks = [lambda: self._tr(sample) for sample in batch]
        results = async_tasks.execute_tasks_async(tasks)
        x, y = zip(*results)
        return np.array(x), np.array(y)

    def on_epoch_end(self):
        rnd.shuffle(self._samples)

    def _batch(self, index: int):
        offset = index * self._batch_size
        return [self._samples[offset + i] for i in range(self._batch_size)]
