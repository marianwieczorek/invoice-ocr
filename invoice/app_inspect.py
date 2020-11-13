import cv2
import matplotlib.pyplot as plt

import invoice.common.images as img
import invoice.common.labels as lbl
import invoice.common.ui as ui


class Renderer(object):
    def __init__(self, base_path: str, labels):
        self._base_path = base_path

        # State
        self._labels = labels
        self._index = 0
        self._image = None

        # Ui
        self._image_axis = None
        self._buttons = []

        self._load_image()

    def _current_file(self) -> str:
        return ui.get_file(self._index, self._labels.keys())

    def _on_reset(self):
        self._load_image()
        self._update()

    def _on_normalize(self):
        self._image = img.normalize_colors(self._image)
        self._update()

    def _on_crop(self):
        height, width, _ = self._image.shape
        size = min(height, width)
        self._image = img.crop_to_square(self._image, size)
        self._update()

    def _on_rotate(self):
        current_file = self._current_file()
        label = lbl.Label(current_file, self._labels[current_file])
        self._image = img.rotate_and_crop(self._image, -label.mean_angle)
        self._update()

    def _on_previous(self):
        self._index = max(self._index - 1, 0)
        self._load_image()
        self._update()

    def _on_next(self):
        self._index = min(self._index + 1, len(self._labels) - 1)
        self._load_image()
        self._update()

    def _load_image(self):
        image = cv2.imread(self._base_path + self._current_file())
        height, width, _ = image.shape
        self._image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    def _update(self):
        if self._image_axis:
            self._image_axis.clear()
            self._image_axis.imshow(self._image)
            self._image_axis.xaxis.set_visible(False)
            self._image_axis.yaxis.set_visible(False)
            plt.draw()

    def show(self):
        fig = plt.figure()
        self._image_axis = fig.gca()

        # Add buttons
        plt.subplots_adjust(bottom=0.08)
        self._buttons.append(ui.create_button(0, 8, 'Reset', lambda _: self._on_reset()))
        self._buttons.append(ui.create_button(2, 8, 'Rotate', lambda _: self._on_rotate()))
        self._buttons.append(ui.create_button(3, 8, 'Normalize', lambda _: self._on_normalize()))
        self._buttons.append(ui.create_button(4, 8, 'Crop', lambda _: self._on_crop()))
        self._buttons.append(ui.create_button(6, 8, 'Previous', lambda _: self._on_previous()))
        self._buttons.append(ui.create_button(7, 8, 'Next', lambda _: self._on_next()))

        self._update()
        plt.show()


def main():
    base_path = '../assets/'
    labels = lbl.load_json(base_path + 'labels.json')
    labels = (lbl.Label.from_json(data) for data in labels)
    labels = {label.image: label.lines for label in labels}

    renderer = Renderer(base_path, labels)
    renderer.show()


if __name__ == '__main__':
    main()
