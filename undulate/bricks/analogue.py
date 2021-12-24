"""
analogue.py declare the basic building block
to generate an analogue waveform and define
common functions in the analogue context
"""

import math
import random
from typing import Any
from undulate.bricks.generic import Brick, BrickFactory, Drawable, Point, SplineSegment
from undulate.generic import safe_eval


CONTEXT = {
    "time": [],
    "Tmax": 20,
    "VSSA": 0,
    "VDDA": 1.8,
    "atan2": math.atan2,
    "pi": math.pi,
    "exp": math.exp,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "tanh": math.tanh,
    "sqrt": math.sqrt,
    "rnd": random.random,
}


def transform_y(y: float, height: float = 20):
    """
    change y coordinate to represente voltage between VSSA and VDDA
    if current VSSA <-> ISSA / VDDA <-> IDDA

    Args:
        y: y-coordinate between VSSA and VDDA
        height: height of a brick in the wavelane
    Returns:
        the new y-coordinate between 0 and height
    """
    scaled_value = (y - CONTEXT["VSSA"]) / (CONTEXT["VDDA"] - CONTEXT["VSSA"])
    return height - height * scaled_value


class MetaToZero(Brick):
    """
    Metastable state representation

    This brick is used to depict when a transition as difficulties
    to settled correctly. Therefore the signal is wavering between 0 and 1
    before a settled state to 0.
    """

    def __init__(self, **kwargs):
        """
        Create the brick as a sum of path, polygon, spline, ...

        Parameters:
            slewing (float > 0): only for the connection with adjacent bricks
        Returns:
            None
        """
        Brick.__init__(self, **kwargs)
        if math.isnan(self.last_y):
            self.last_y = self.height / 2
        self.dt = abs(self.last_y - self.height / 2) * self.slewing / self.height
        # time range
        time = range(int(self.dt), int(self.width * 0.75 + 1))
        if (int(0.75 * self.width + 1) - int(self.dt)) % 2 == 1:
            time = range(int(self.dt), int(self.width * 0.75 + 2))
        # prepare spline
        _tmp = [SplineSegment("m", 0.0, self.last_y)]
        for i, t in enumerate(time):
            _tmp.append(
                SplineSegment(
                    "L" if i == 0 else "",
                    t,
                    (
                        1
                        + math.exp(2 * (t - self.width) / self.width)
                        * math.sin(8 * math.pi * t / self.width)
                    )
                    * 0.5
                    * self.height,
                )
            )
            x, y = _tmp[-1].x, _tmp[-1].y
            dx = max((self.height - y) * self.slewing / self.height, (self.height - y))
            _tmp.extend(
                [
                    SplineSegment("C", x + dx, self.height),
                    SplineSegment("", x + dx, self.height),
                    SplineSegment("", self.width, self.height),
                ]
            )
        self.splines.append(Drawable("path", _tmp))


class MetaToOne(Brick):
    """
    Metastable state representation

    This brick is used to depict when a transition as difficulties
    to settled correctly. Therefore the signal is wavering between 0 and 1
    before a settled state to 1
    """

    def __init__(self, **kwargs):
        """
        Create the brick as a sum of path, polygon, spline, ...

        Parameters:
            slewing (float > 0): only for the connection with adjacent bricks
        Returns:
            None
        """
        Brick.__init__(self, **kwargs)
        if math.isnan(self.last_y):
            self.last_y = self.height / 2
        self.dt = abs(self.last_y - self.height / 2) * self.slewing / self.height
        # time range
        time = range(int(self.dt), int(self.width * 0.75 + 1))
        if (int(0.75 * self.width + 1) - int(self.dt)) % 2 == 1:
            time = range(int(self.dt), int(self.width * 0.75 + 2))
        # prepare spline
        _tmp = [SplineSegment("m", 0.0, self.last_y)]
        for i, t in enumerate(time):
            _tmp.append(
                SplineSegment(
                    "L" if i == 0 else "",
                    t,
                    (
                        1
                        + math.exp(2 * (t - self.width) / self.width)
                        * math.sin(math.pi + 8 * math.pi * t / self.width)
                    )
                    * 0.5
                    * self.height,
                )
            )
        x, y = _tmp[-1].x, _tmp[-1].y
        dx = max(y * self.slewing / self.height, y)
        _tmp.extend(
            [
                SplineSegment("C", x + dx, 0.0),
                SplineSegment("", x + dx, 0.0),
                SplineSegment("", self.width, 0.0),
            ]
        )
        self.splines.append(Drawable("path", _tmp))


class Cap(Brick):
    """
    RC charge/discharge behaviour

    This brick is used to depict a RC charge or discharge to
    the new level.
    """

    def __init__(self, equation: Any, **kwargs):
        """
        Args:
            points: the new level between 0 and height
        Parameters:
            slewing (float > 0): maximum slope of the signal
        Returns:
            None
        """
        Brick.__init__(self, **kwargs)
        # pre-process equation
        value = safe_eval(equation, CONTEXT) if isinstance(equation, str) else equation
        y = transform_y(value, self.height)
        # set final value if necessary
        if self.is_first or math.isnan(self.last_y):
            self.last_y = self.height
        self.dt = abs(y - self.last_y) * self.slewing / self.height
        # add shape
        self.splines.append(
            Drawable(
                "path",
                [
                    SplineSegment("m", 0.0, self.last_y),
                    SplineSegment("C", self.dt, y),
                    SplineSegment("", self.dt, y),
                    SplineSegment("", self.width, y),
                    SplineSegment("L", self.width, y),
                ],
            )
        )


class Step(Brick):
    """
    Slewing behaviour

    This brick represents a slewing transitions until the
    desired level is reached. Then the value is locked.

    This behaviour corresponds to a charge-pump or a
    comparator-based integrator
    """

    def __init__(self, equation: Any, **kwargs):
        """
        Args:
            equation: the new level between 0 and height
        Parameters:
            slewing (float > 0): maximum slope of the signal
        Returns:
            None
        """
        Brick.__init__(self, **kwargs)
        # pre-process equation
        value = safe_eval(equation, CONTEXT) if isinstance(equation, str) else equation
        y = transform_y(value, self.height)
        # set final value if necessary
        if self.is_first or math.isnan(self.last_y):
            self.last_y = y
        self.dt = abs(y - self.last_y) * self.slewing / self.height
        # add shape
        self.paths.append(
            Drawable(
                "path",
                [
                    SplineSegment(0, self.last_y),
                    SplineSegment(self.dt, y),
                    SplineSegment(self.width, y),
                ],
            )
        )


class Analogue(Brick):
    """
    Arbitrary analogue signal

    This brick is intended to depict an time changing signal
    """

    def __init__(self, equation: Any, **kwargs):
        """
        Args:
            points: list of points (relative time, y-value)
        Returns:
            None
        """
        Brick.__init__(self, **kwargs)
        # pre-process equation
        points = safe_eval(equation, CONTEXT) if isinstance(equation, str) else equation
        # add shape
        _tmp = [Point(0.0, self.last_y)]
        for point in points:
            _tmp.append(Point(point[0], transform_y(point[1], self.height)))
        # set final point if necessary
        if self.is_first or math.isnan(self.last_y):
            self.last_y = _tmp[-1].y
        self.paths.append(Drawable("path", _tmp))


def initialize() -> None:
    """register defined digital blocks in the rendering system"""
    BrickFactory.register("m", MetaToZero.__init__)
    BrickFactory.register("M", MetaToOne.__init__)
    BrickFactory.register("s", Step.__init__, params={"equation": 0.0})
    BrickFactory.register("c", Cap.__init__, params={"equation": 0.0})
    BrickFactory.register("a", Analogue.__init__, params={"equation": [(0.0, 0.0)]})
