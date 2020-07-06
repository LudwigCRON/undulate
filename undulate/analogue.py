#!/usr/bin/env python3
# spell-checker: disable

"""
analogue.py declare the basic building block
to generate an analogue waveform and define
common functions in the analogue context
"""

import math
import random
import undulate

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


class Meta(undulate.Brick):
    """
    Metastable state representation

    This brick is used to depict when a transition as difficulties
    to settled correctly. Therefore the signal is wavering between 0 and 1
    before a settled state either to 0 or 1

    To 0 if 'm'
    To 1 if 'M'
    """

    def __init__(self, **kwargs):
        """
        Create the brick as a sum of path, polygon, spline, ...

        Parameters:
            slewing (float > 0): only for the connection with adjacent bricks
            then_one (bool): select if settle to one (True) or zero (False)
        Returns:
            None
        """
        undulate.Brick.__init__(self, **kwargs)
        then_one = kwargs.get("then_one", False)
        self.last_y = self.height / 2 if self.last_y is None else self.last_y
        dt = abs(self.last_y - self.height / 2) * self.slewing / self.height
        # time range
        time = range(int(dt), int(self.width * 0.75 + 1))
        if (int(0.75 * self.width + 1) - int(dt)) % 2 == 1:
            time = range(int(dt), int(self.width * 0.75 + 2))
        # prepare spline
        _tmp = ["path", ("m", 0, self.last_y)]
        if then_one:
            for i, t in enumerate(time):
                _tmp.append(
                    (
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
            t, x, y = _tmp[-1]
            dx = max(y * self.slewing / self.height, y)
            _tmp.extend([("C", x + dx, 0), ("", x + dx, 0), ("", self.width, 0)])
        else:
            for i, t in enumerate(time):
                _tmp.append(
                    (
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
            t, x, y = _tmp[-1]
            dx = max((self.height - y) * self.slewing / self.height, (self.height - y))
            _tmp.extend(
                [
                    ("C", x + dx, self.height),
                    ("", x + dx, self.height),
                    ("", self.width, self.height),
                ]
            )
        self.splines.append(_tmp)


class Cap(undulate.Brick):
    """
    RC charge/discharge behaviour

    This brick is used to depict a RC charge or discharge to
    the new level.
    """

    def __init__(self, **kwargs):
        """
        Args:
            y: the new level between 0 and height
                if not the case see undulate.BRICKS.transform_y
        Parameters:
            slewing (float > 0): maximum slope of the signal
        Returns:
            None
        """
        undulate.Brick.__init__(self, **kwargs)
        y = undulate.BRICKS.transform_y(kwargs.get("points"), self.height)
        if self.is_first:
            self.last_y = self.height
        else:
            self.last_y = self.height if self.last_y is None else self.last_y
        dt = abs(y - self.last_y) * self.slewing / self.height
        # add shape
        self.splines.append(
            [
                "path",
                ("m", 0, self.last_y),
                ("C", dt, y),
                ("", dt, y),
                ("", self.width, y),
                ("L", self.width, y),
            ]
        )


class Step(undulate.Brick):
    """
    Slewing behaviour

    This brick represents a slewing transitions until the
    desired level is reached. Then the value is locked.

    This behaviour corresponds to a charge-pump or a
    comparator-based integrator
    """

    def __init__(self, **kwargs):
        """
        Args:
            y: the new level between 0 and height
                if not the case see undulate.BRICKS.transform_y
        Parameters:
            slewing (float > 0): maximum slope of the signal
        Returns:
            None
        """
        undulate.Brick.__init__(self, **kwargs)
        y = undulate.BRICKS.transform_y(kwargs.get("points"), self.height)
        if self.is_first:
            self.last_y = self.height
        else:
            self.last_y = self.height if self.last_y is None else self.last_y
        dt = abs(y - self.last_y) * self.slewing / self.height
        # add shape
        self.paths.append(["path", (0, self.last_y), (dt, y), (self.width, y)])


class Analogue(undulate.Brick):
    """
    Arbitrary analogue signal

    This brick is intended to depict an time changing signal
    """

    def __init__(self, **kwargs):
        """
        Args:
            pts: list of points (relative time, y-value)
        Returns:
            None
        """
        undulate.Brick.__init__(self, **kwargs)
        pts = kwargs.get("points") or []
        if self.is_first:
            self.last_y = self.height
        else:
            self.last_y = self.height if self.last_y is None else self.last_y
        # add shape
        self.paths.append(
            ["path", (0, self.last_y)]  # link to the previous block
            + [
                (p[0], undulate.BRICKS.transform_y(p[1], self.height))
                for p in pts  # evaluation fonctions, complex python code
            ]
        )


def generate_analogue_symbol(symbol, **kwargs) -> (bool, object):
    """
    define the mapping between the symbol and the brick

    It fetches needed parameters for the analogue bricks
    and evaluate equations with the appropriate CONTEXT

    Args:
        symbol (undulate.BRICKS): symbol to create
    Parameters:
        brick_height (int): height of the brick in display unit
        equation (str or float): value(s) to be passed to bricks
            if equation is a str, then it is evaluated
            if equation is a float, it given to brick as the y value
    Returns:
        tuple(bool, brick)

        bool
            if True the brick generated is an analogue brick
            if False nothing has been generated
        brick
            the brick created or None
    """
    # get option supported
    equation = kwargs.get("equation", [])
    # mapping
    map_dict = {
        # metastability to zero
        undulate.BRICKS.meta: Meta,
        # metastability to one
        undulate.BRICKS.Meta: Meta,
        # slewing analogue bloc
        undulate.BRICKS.step: Step,
        # capacitive load
        undulate.BRICKS.cap: Cap,
        # full custom analogue bloc
        undulate.BRICKS.ana: Analogue,
    }
    # add parameters
    if symbol == undulate.BRICKS.Meta:
        kwargs.update({"then_one": True})
    kwargs.update(
        {
            "points": undulate.safe_eval(equation, CONTEXT)
            if isinstance(equation, str)
            else equation
        }
    )
    # get factory and generate block
    factory = map_dict.get(symbol, None)
    if callable(factory):
        return factory(**kwargs)
    return None
