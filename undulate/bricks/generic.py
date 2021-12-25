#!/usr/bin/env python3
# spell-checker: disable

"""
bricks.py declare the basic building block
to generate a waveform
"""

import copy
from math import nan
from typing import Callable, Any
from dataclasses import dataclass
import undulate.logger as log


@dataclass
class Point:
    """cartesian coordinate of a point"""

    x: float = 0.0
    y: float = 0.0


@dataclass
class SplineSegment:
    """spline directive m/l/c/z/M/L/C/Z as for svg"""

    order: str = ""
    x: float = 0.0
    y: float = 0.0


@dataclass
class ArrowDescription:
    """position and orientation of the arrow to be drawn"""

    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0


@dataclass
class Drawable:
    """associate a style class to an object"""

    style: str
    object: Any


class BrickFactory:
    """create a brick from its symbol once registered"""

    funcs = {}
    tags = {}
    params = {}

    @staticmethod
    def register(
        symbol: str,
        initializer: Callable,
        tags: list[str] = [],
        params: dict[str, Any] = {},
    ):
        """register a new brick called {name} mapped to {symbol}"""
        BrickFactory.funcs[symbol] = initializer
        # symbol can be tagged to later ease filtering on type
        BrickFactory.tags[symbol] = tags
        # register list of needed parameters
        BrickFactory.params[symbol] = params

    @staticmethod
    def create(symbol: str, **kwargs):
        """create a brick from its symbol"""
        if symbol not in BrickFactory.funcs:
            log.fatal("The symbol '%s' is not defined" % symbol)
        init = BrickFactory.funcs[symbol]
        brick = init(**kwargs)
        brick.symbol = symbol
        return brick

    @staticmethod
    def get_parameters() -> dict[str, Any]:
        ans = {}
        for params in BrickFactory.params.values():
            ans.update(params)
        return ans


@dataclass
class Brick:
    """
    define the brick as a composition of paths, arrows, and generic polygons
    to fill an area

    Attributes:
        width (float > 0): by default is 40.0
        height (float > 0): by default is 20.0
        slewing (float > 0): by default 0.0
        ignore_start_transition (bool): by default False
        ignore_end_transition (bool): by default False
        is_first (bool): first brick of a wavelance, by default False
        last_y (float): y coordinate of the previous brick
            to make the junction between the two

        paths (list): list of "svg" paths to be drawn
        arrows (list): list of arrows to be drawn
        polygons (list): list of polygons to be drawn

            .. warning::
                polygons are considered to be a list of (x, y) tuples
        splines (list): list of splines to be drawn

            .. warning::
                splines are considered to be a list of (type, x or dx, y or dy) tuples
                for more details please look at
                https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths
    """

    symbol: str
    paths: list[Drawable]
    arrows: list[ArrowDescription]
    polygons: list[Drawable]
    splines: list[Drawable]
    texts: list[Drawable]
    args: dict
    width: float = 40.0
    height: float = 20.0
    repeat: int = 1
    slewing: float = 0.0
    ignore_start_transition: bool = False
    ignore_end_transition: bool = False
    is_first: bool = False
    first_y: float = 0.0
    last_y: float = nan

    def __init__(self, **kwargs) -> None:
        self.width = float(kwargs.get("brick_width", 40.0))
        self.height = float(kwargs.get("brick_height", 20.0))
        self.slewing = float(kwargs.get("slewing", 0.0))
        self.last_y = float(kwargs.get("last_y", nan))
        self.ignore_start_transition = bool(kwargs.get("ignore_start_transition", False))
        self.ignore_end_transition = bool(kwargs.get("ignore_end_transition", False))
        self.is_first = bool(kwargs.get("is_first", False))
        self.args = copy.deepcopy(kwargs)
        self.symbol = None
        self.paths = []
        self.arrows = []
        self.polygons = []
        self.splines = []
        self.texts = []


# def ignore_transition(from_symb, to_symb) -> bool:
#        """
#        define special case when transition are skipped to prevent
#        glitches by default
#
#        Args:
#            from_symb (undulate.BRICKS): symbol from which start the transition
#            to_symb (undulate.BRICKS): target symbol of the transition
#        Returns:
#            boolean result corresponding to the statement
#            'transition should be skipped'
#        """
#        if (from_symb, to_symb) in [
#            (BRICKS.low, BRICKS.Low),
#            (BRICKS.high, BRICKS.High),
#            (BRICKS.Low, BRICKS.low),
#            (BRICKS.High, BRICKS.high),
#            (BRICKS.one, BRICKS.Pclk),
#            (BRICKS.zero, BRICKS.Nclk),
#            (BRICKS.High, BRICKS.Pclk),
#            (BRICKS.high, BRICKS.Pclk),
#            (BRICKS.high, BRICKS.pclk),
#            (BRICKS.High, BRICKS.pclk),
#            (BRICKS.Low, BRICKS.Nclk),
#            (BRICKS.low, BRICKS.Nclk),
#            (BRICKS.low, BRICKS.nclk),
#            (BRICKS.Low, BRICKS.nclk),
#        ]:
#            return True
#        if (
#            to_symb in [undulate.BRICKS.zero, undulate.BRICKS.one]
#            or BRICKS.is_forced_signal(to_symb)
#        ) and from_symb in [undulate.BRICKS.data, undulate.BRICKS.x, undulate.BRICKS.X]:
#            return True
#        if BRICKS.is_forced_signal(to_symb) and BRICKS.is_clock(from_symb):
#            if from_symb.value.lower() == "n" and to_symb.value.lower() == "h":
#                return True
#            if from_symb.value.lower() == "p" and to_symb.value.lower() == "l":
#                return True
#            if from_symb.value.lower() == "h" and to_symb.value.lower() == "p":
#                return True
#            if from_symb.value.lower() == "l" and to_symb.value.lower() == "n":
#                return True
#        return False


class FilterBank:
    """list of filters to apply process a waveform"""

    filters = []

    @staticmethod
    def register(filter: Callable):
        FilterBank.filters.append(filter)

    @staticmethod
    def apply(waveform: list[Brick]) -> list[Brick]:
        """apply registered filters on the wavelane"""
        ans = copy.deepcopy(waveform)
        for filter in FilterBank.filters:
            ans = filter(ans)
        return ans
