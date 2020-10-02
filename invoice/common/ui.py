import typing

import matplotlib.pyplot as plt


def get_file(index: int, files: typing.Iterable[str]) -> str:
    files = sorted(files)
    return files[index]


def create_button(index: int, num_buttons: int, text: str, click_listener, margin=None, height=None) -> plt.Button:
    margin = margin or 0.01
    height = height or 0.06
    width = (1.0 - margin) / num_buttons - margin
    ax = plt.axes([margin + index * (width + margin), margin, width, height])
    button = plt.Button(ax, text)
    button.on_clicked(click_listener)
    return button
