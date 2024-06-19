"""
analogue.py declare the basic building block
to generate an analogue waveform and define
common functions in the analogue context
"""

import math
import random
from undulate.bricks.generic import (
    Brick,
    BrickFactory,
    Drawable,
    Point,
    SplineSegment,
    safe_eval,
)

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


def transform_y(y: float, brick_height: float = 20):
    """
    Transform values in the [VSSA;VDDA] range to the internal [0;brick_height]
    range. If need to model a current still use 'VSSA' and 'VDDA'
    a dropin replacement for 'ISSA' and 'IDDA'

    Args:
        y: y-coordinate between VSSA and VDDA
        height: height of a brick in the given signal
    Returns:
        the new y-coordinate between 0 and brick_height
    """
    scaled_value = (y - CONTEXT["VSSA"]) / (CONTEXT["VDDA"] - CONTEXT["VSSA"])
    return brick_height * (1 - scaled_value)


class MetaToZero(Brick):
    """
    Metastable state representation resolving to GND

    This brick is used to depict when a transition as difficulties
    to settled correctly. Therefore the signal is wavering between 0 and 1
    before a settled state to 0.
    """

    def __init__(self, **kwargs):
        """
        Create the brick as a sum of path, polygon, spline, ...

        Parameters:
            slewing (float > 0): only for the connection with adjacent bricks
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
                    "L",
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
    Metastable state representation resolving to VDD

    This brick is used to depict when a transition as difficulties
    to settled correctly. Therefore the signal is wavering between 0 and 1
    before a settled state to 1
    """

    def __init__(self, **kwargs):
        """
        Create the brick as a sum of path, polygon, spline, ...

        Parameters:
            slewing (float > 0): only for the connection with adjacent bricks
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
                    "L",
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
    RC charge/discharge

    This brick is used to depict a RC charge or discharge to
    the new level.
    """

    def __init__(self, **kwargs):
        """
        Parameters:
            slewing (float > 0): maximum slope of the signal
            analogue (float): final value of the settling in the [VSSA;VDDA] range
        """
        Brick.__init__(self, **kwargs)
        # pre-process analogue
        CONTEXT["Tmax"] = self.width
        CONTEXT["time"] = range(int(self.width + 1))
        analogue = kwargs["analogue"]
        value = safe_eval(analogue, CONTEXT) if isinstance(analogue, str) else analogue
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
    Ramping signal from one value to another

    This brick represents a slewing transitions until the
    desired level is reached. Then the value is locked.

    This behaviour corresponds to a charge-pump or a
    comparator-based integrator
    """

    def __init__(self, **kwargs):
        """
        Parameters:
            slewing (float > 0): maximum slope of the signal
            analogue (float): final value of the settling in the [VSSA;VDDA] range
        """
        Brick.__init__(self, **kwargs)
        # pre-process analogue
        CONTEXT["Tmax"] = self.width
        CONTEXT["time"] = range(int(self.width + 1))
        analogue = kwargs["analogue"]
        value = safe_eval(analogue, CONTEXT) if isinstance(analogue, str) else analogue
        y = transform_y(value, self.height)
        # set final value if necessary
        if self.is_first or math.isnan(self.last_y):
            self.last_y = self.height
        self.dt = abs(y - self.last_y) * self.slewing / self.height
        # add shape
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0, self.last_y),
                    Point(self.dt, y),
                    Point(self.width, y),
                ],
            )
        )


class Analogue(Brick):
    """
    Arbitrary analogue signal

    This brick is intended to depict any time changing signal
    """

    def __init__(self, **kwargs):
        """
        Args:
            analogue (List[Tuple[float, float]]): list of points (relative time, voltage in [VSSA;VDDA] range)
        """
        Brick.__init__(self, **kwargs)
        # pre-process analogue
        CONTEXT["Tmax"] = self.width
        CONTEXT["time"] = range(int(self.width + 1))
        analogue = kwargs["analogue"]
        points = safe_eval(analogue, CONTEXT) if isinstance(analogue, str) else analogue
        # set final point if necessary
        if self.is_first or math.isnan(self.last_y):
            self.last_y = self.height
        # add shape
        _tmp = [Point(0.0, self.last_y)]
        for point in points:
            _tmp.append(Point(point[0], transform_y(point[1], self.height)))
        self.paths.append(Drawable("path", _tmp))


def initialize() -> None:
    """register defined digital blocks in the rendering system"""
    BrickFactory.register("m", MetaToZero)
    BrickFactory.register("M", MetaToOne)
    BrickFactory.register("s", Step, tags=["analogue"], params={"analogue": 0.0})
    BrickFactory.register("c", Cap, tags=["analogue"], params={"analogue": 0.0})
    BrickFactory.register("a", Analogue, tags=["analogue"], params={"analogue": [(0, 0)]})
