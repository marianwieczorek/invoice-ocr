import os
import typing

import cv2
import matplotlib.pyplot as plt

import invoice.common.labels as lbl
import invoice.common.ui as ui


def is_image_file(filename: str) -> bool:
    img_ext = ['.bmp', '.gif', '.jpeg', '.jpg', '.png']
    return any(filename.lower().endswith(ext) for ext in img_ext)


def list_image_files(path: str) -> typing.List[str]:
    return [file for file in os.listdir(path) if is_image_file(file)]


class ClickListener(object):

    def __init__(self, label_builder):
        self._label_builder = label_builder
        self._is_editing = False

    def on_mouse_pressed(self, event):
        if self._label_builder.is_relevant_event(event):
            if event.button == plt.MouseButton.LEFT:
                if not self._is_editing:
                    self._label_builder.add_label_point(event.xdata, event.ydata)
                    self._is_editing = True
            if event.button == plt.MouseButton.RIGHT:
                if self._is_editing:
                    self._label_builder.cancel_label()
                    self._is_editing = False

    def on_mouse_released(self, event):
        if self._label_builder.is_relevant_event(event) and event.button == plt.MouseButton.LEFT and self._is_editing:
            self._label_builder.add_label_point(event.xdata, event.ydata)
        else:
            self._label_builder.cancel_label()
        self._is_editing = False

    def on_mouse_moved(self, event):
        if self._is_editing and self._label_builder.is_relevant_event(event):
            self._label_builder.update_label_point(event.xdata, event.ydata)


class Renderer(object):

    def __init__(self, base_path: str, labels: typing.Dict[str, typing.List[lbl.Line]], writer):
        self._base_path = base_path
        self._writer = writer

        # State
        self._labels = labels
        self._index = 0
        self._image = None
        self._new_line = None

        # Ui
        self._image_axis = None
        self._buttons = []

        # Load first image
        self._load_image()

    def _current_file(self) -> str:
        return ui.get_file(self._index, self._labels.keys())

    def _load_image(self):
        image = cv2.imread(self._base_path + self._current_file())
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self._image = image

    def _on_start(self):
        self._index = 0
        self._load_image()
        self._update()

    def _on_previous(self):
        self._index = max(self._index - 1, 0)
        self._load_image()
        self._update()

    def _on_next(self):
        self._index = min(self._index + 1, len(self._labels) - 1)
        self._load_image()
        self._update()

    def _on_end(self):
        self._index = len(self._labels) - 1
        self._load_image()
        self._update()

    def _on_save(self):
        self._writer(create_labels(self._labels))
        print('...saved')

    def _plot_line(self, line: lbl.Line):
        x_data = [line.p1.x, line.p2.x]
        y_data = [line.p1.y, line.p2.y]
        self._image_axis.plot(x_data, y_data, 'r-', linewidth=2)

    def _update(self):
        if self._image_axis:
            self._image_axis.clear()
            self._image_axis.imshow(self._image)
            self._image_axis.xaxis.set_visible(False)
            self._image_axis.yaxis.set_visible(False)

            for line in self._labels[self._current_file()]:
                self._plot_line(line)
            if self._new_line:
                self._plot_line(self._new_line)
            plt.draw()

    def is_relevant_event(self, event):
        return event.inaxes == self._image_axis

    def add_label_point(self, x: float, y: float):
        if self._new_line:
            self._new_line.p2 = lbl.Point(x, y)
            self._labels[self._current_file()].append(self._new_line)
            self._new_line = None
        else:
            self._new_line = lbl.Line(lbl.Point(x, y), lbl.Point(x, y))
        self._update()

    def update_label_point(self, x, y):
        if self._new_line:
            self._new_line.p2 = lbl.Point(x, y)
            self._update()

    def cancel_label(self):
        if self._new_line:
            self._new_line = None
            self._update()

    def clear_labels(self):
        self._labels[self._current_file()] = []
        self._update()

    def show(self):
        fig = plt.figure()
        self._image_axis = fig.gca()

        # Add click listener
        clk_listener = ClickListener(self)
        fig.canvas.mpl_connect('button_press_event', clk_listener.on_mouse_pressed)
        fig.canvas.mpl_connect('button_release_event', clk_listener.on_mouse_released)
        fig.canvas.mpl_connect('motion_notify_event', clk_listener.on_mouse_moved)

        # Add buttons
        plt.subplots_adjust(bottom=0.08)
        self._buttons.append(ui.create_button(0, 8, 'Save', lambda _: self._on_save()))
        self._buttons.append(ui.create_button(1, 8, 'Clear', lambda _: self.clear_labels()))
        self._buttons.append(ui.create_button(4, 8, 'Start', lambda _: self._on_start()))
        self._buttons.append(ui.create_button(5, 8, 'Previous', lambda _: self._on_previous()))
        self._buttons.append(ui.create_button(6, 8, 'Next', lambda _: self._on_next()))
        self._buttons.append(ui.create_button(7, 8, 'End', lambda _: self._on_end()))

        # Show ui
        self._update()
        plt.show()


def create_labels(mapping):
    labels = (lbl.Label(file, lines) for file, lines in mapping.items())
    return lbl.non_empty_labels_to_json(labels)


def main():
    print('Listing images in workspace...')
    base_path = '../assets/'
    files = set(list_image_files(base_path))
    print(f'...{len(files)} images found.')

    print('Loading existing labels...')
    labels = lbl.load_json(base_path + 'labels.json')
    labels = (lbl.Label.from_json(data) for data in labels)
    labels = {label.image: label.lines for label in labels}
    labels = {image: lines for image, lines in labels.items() if image in files}
    print(f'...{len(labels)} labels found.')

    print('Set defaults for unlabeled images...')
    unlabeled = {file: [] for file in files if file not in labels}
    labels.update(unlabeled)
    print(f'...{len(unlabeled)} unlabeled images found.')

    print('Start labeling...')
    renderer = Renderer(base_path, labels, lambda data: lbl.write_json(data, base_path + 'labels.json'))
    renderer.show()
    print('...done!')


if __name__ == '__main__':
    main()
