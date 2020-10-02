import json
import math
import typing

PointJson = typing.Mapping[str, float]
LineJson = typing.Mapping[str, PointJson]
LabelJson = typing.Mapping[str, typing.Union[str, LineJson]]


class Point(object):
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    @staticmethod
    def from_json(data: PointJson) -> 'Point':
        return Point(data['x'], data['y'])

    def to_json(self) -> PointJson:
        return {'x': self.x, 'y': self.y}


class Line(object):
    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    @staticmethod
    def from_json(data: LineJson):
        line = Line(Point.from_json(data['p1']), Point.from_json(data['p2']))
        return line.to_ordered_line()

    def to_ordered_line(self) -> 'Line':
        if self.p2.x < self.p1.x:
            return Line(self.p2, self.p1)
        return self

    def to_angle(self) -> float:
        line = self.to_ordered_line()
        dx = line.p2.x - line.p1.x
        dy = line.p2.y - line.p1.y
        return math.atan2(dy, dx)

    def to_json(self) -> LineJson:
        line = self.to_ordered_line()
        return {'p1': line.p1.to_json(), 'p2': line.p2.to_json()}


class Label(object):
    def __init__(self, image: str, lines: typing.List[Line]):
        self.image = image
        self.lines = lines

    @property
    def min_angle(self):
        return min((line.to_angle() for line in self.lines), default=0.0)

    @property
    def max_angle(self):
        return max((line.to_angle() for line in self.lines), default=0.0)

    @property
    def mean_angle(self):
        return sum(line.to_angle() for line in self.lines) / len(self.lines)

    @staticmethod
    def from_json(data: LabelJson) -> 'Label':
        return Label(data['image'], [Line.from_json(line) for line in data['lines']])

    def to_json(self) -> LabelJson:
        return {'image': self.image, 'lines': [line.to_json() for line in self.lines]}


def non_empty_labels_to_json(labels: typing.Iterable[Label]) -> typing.List[LabelJson]:
    return [label.to_json() for label in labels if label.lines]


def load_json(filename: str) -> typing.List[LabelJson]:
    with open(filename) as file:
        return json.load(file)


def write_json(data: typing.List[LabelJson], filename: str):
    with open(filename, 'w') as file:
        return json.dump(data, file, indent=2)
