#!/usr/bin/env python3
# spell-checker: disable

"""
register.py declare the basic building block
to represent a register
"""

from typing import Any

from undulate.bricks.generic import Drawable, Brick, BrickFactory, Point, SplineSegment


class FieldStart(Brick):
    """
    [
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        print(kwargs)
        scale_width = float(kwargs.get("scale_width", 1.0))
        position = int(kwargs.get("position", 0))
        data = kwargs.get("data", "")
        attributes = kwargs.get("attribute", None)
        style = kwargs.get("style", None)
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(self.width, self.height),
                    Point(0, self.height),
                    Point(0, self.height / 4),
                    Point(self.width, self.height / 4),
                ],
            )
        )
        if style is not None:
            self.polygons.append(
                Drawable(
                    style,
                    [
                        Point(self.width * scale_width, self.height),
                        Point(0, self.height),
                        Point(0, self.height / 4),
                        Point(self.width * scale_width, self.height / 4),
                    ],
                )
            )
        # add attributes
        if isinstance(attributes, str):
            attributes = [attributes]
        for i, attr in enumerate(attributes):
            self.texts.append(
                Drawable(
                    "attr",
                    ((self.width * scale_width) / 2, self.height + 12 * (i + 1), attr),
                )
            )
        # add centered text
        center_x = self.width / 2
        top_y = self.height * 0.125
        bottom_y = self.height * 0.625
        self.texts.append(Drawable("reg-data", (center_x, bottom_y, data)))
        self.texts.append(Drawable("reg-pos", (center_x, top_y, str(position))))


class FieldMid(Brick):
    """
    :
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        data = kwargs.get("data", "")
        self.splines.append(
            Drawable(
                "path",
                [
                    SplineSegment("M", self.width, self.height * 0.875),
                    SplineSegment("l", 0.0, self.height * 0.125),
                    SplineSegment("l", -self.width, 0),
                    SplineSegment("l", 0.0, -self.height * 0.125),
                ],
            )
        )
        self.splines.append(
            Drawable(
                "path",
                [
                    SplineSegment("M", self.width, self.height * 0.375),
                    SplineSegment("l", 0, -self.height * 0.125),
                    SplineSegment("l", -self.width, 0),
                    SplineSegment("l", 0, self.height * 0.125),
                ],
            )
        )
        # add text
        self.texts.append(Drawable("reg-data", (self.width / 2, self.height * 0.625, data)))


class FieldEnd(Brick):
    """
    ]
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        position = int(kwargs.get("position", 0))
        data = kwargs.get("data", "")
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0.0, self.height),
                    Point(self.width, self.height),
                    Point(self.width, self.height / 4),
                    Point(0.0, self.height / 4),
                ],
            )
        )
        # add centered text
        center_x = self.width / 2
        top_y = self.height * 0.125
        bottom_y = self.height * 0.625
        self.texts.append(Drawable("reg-data", (center_x, bottom_y, data)))
        self.texts.append(Drawable("reg-pos", (center_x, top_y, str(position))))


class FieldBit(Brick):
    """
    b
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        position = int(kwargs.get("position", 0))
        data = kwargs.get("data", "")
        style = kwargs.get("style")
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0.0, self.height / 4),
                    Point(0.0, self.height),
                    Point(self.width, self.height),
                    Point(self.width, self.height / 4),
                    Point(0.0, self.height / 4),
                ],
            )
        )
        if style is not None:
            self.polygons.append(
                Drawable(
                    style,
                    [
                        Point(self.width, self.height),
                        Point(0.0, self.height),
                        Point(0.0, self.height / 4),
                        Point(self.width, self.height / 4),
                    ],
                )
            )
        # add centered text
        center_x = self.width / 2
        top_y = self.height * 0.125
        bottom_y = self.height * 0.625
        self.texts.append(Drawable("reg-data", (center_x, bottom_y, data)))
        self.texts.append(Drawable("reg-pos", (center_x, top_y, str(position))))


def initialize() -> None:
    BrickFactory.register(
        "[",
        FieldStart,
        tags=["reg"],
        params={"data": "", "position": 0, "attribute": "", "style": "", "type": None},
    )
    BrickFactory.register(
        ":", FieldMid, tags=["reg"], params={"data": "", "style": "", "type": None}
    )
    BrickFactory.register(
        "]",
        FieldEnd,
        tags=["reg"],
        params={"data": "", "position": 0, "style": "", "type": None},
    )
    BrickFactory.register(
        "b",
        FieldBit,
        tags=["reg"],
        params={"data": "", "position": 0, "attribute": "", "style": "", "type": None},
    )
