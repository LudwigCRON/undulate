#!/usr/bin/env python3
# spell-checker: disable

"""
bricks.py declare the basic building block
to generate a waveform
"""
import pywave

class Brick:
    """
    define the brick as a composition of paths, arrows, and generic polygons
    to fill an area

    Attributes:
        width (float > 0): by default is 40
        height (float > 0): by default is 20
        slewing (float > 0): by default 0
        duty_cycle (float > 0): between 0.0 and 1.0 by default 0.5
        ignore_transition (bool): by default False
        is_first (bool): first brick of a wavelance, by default False
        last_y (float): y coordinate of the previous brick 
            to make the junction between the two
        equation (str or float): analogue value(s)
        
        paths (list): list of "svg" paths to be drawn
        arrows (list): list of arrows to be drawn
        polygons (list): list of polygons to be drawn

            .. warning::
                polygons are considered to be a list of (x, y) tuples
        splines (list): list of splines to be drawn

            .. warning::
                splines are considered to be a list of (type, x or dx, y or dy) tuples
                for more details please look at https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths
    """

    __slots__ = [
        "symbol",
        "paths",
        "arrows",
        "polygons",
        "splines",
        "texts",
        "width",
        "height",
        "slewing",
        "duty_cycle",
        "ignore_transition",
        "is_first",
        "last_y",
    ]

    def __init__(self, **kwargs):
        # get options supported
        # sizing
        #: width of the brick
        self.width = kwargs.get("brick_width", 40) * kwargs.get("is_repeated", 1)
        #: height of the brick
        self.height = kwargs.get("brick_height", 20)
        # physical variants
        #: slope limitation
        self.slewing = kwargs.get("slewing", 0)
        #: duty cycle 0 -> 1: float
        self.duty_cycle = kwargs.get("duty_cycle", 0.5)
        #: prevent glitches in chain: bool
        self.ignore_transition = kwargs.get("ignore_transition", False)
        # chaining instance
        #: first brick in wavelane: bool
        self.is_first = kwargs.get("is_first", False)
        #: last brick y position: float
        self.last_y = kwargs.get("last_y", None)
        # items to keep for drawing
        #: define the char
        self.symbol = None
        #: list of paths to be drawn
        self.paths = []
        #: list of arrows
        self.arrows = []
        #: list of polygons
        self.polygons = []
        #: list of splines
        self.splines = []
        #: list of texts to be printed
        self.texts = []

    def get_last_y(self):
        """
        get last position of the current brick to preserve continuity

        Returns:
            last_y (float)
        """
        last_y = 0
        if self.paths:
            _, last_y = self.paths[0][-1]
        elif self.splines:
            _, _, last_y = self.splines[0][-1]
        return last_y

    def alter_end(self, shift: float = 0, next_y: float = -1):
        """
        alter the last coordinates to preserve continuity

        Args:
            shift (float): adjust the x position of the end, by default 0
            next_y (float): adjust the y position of the end, by default -1
        """
        for i, path in enumerate(self.paths):
            x1, y1 = path[-1]
            x2, y2 = path[-2]
            if isinstance(next_y, list):
                self.paths[i] = path[:-1] + [
                    (x2 + shift, y2),
                    (x1 + shift, next_y[i] if next_y[i] > -1 else y1),
                ]
            else:
                self.paths[i] = path[:-1] + [
                    (x2 + shift, y2),
                    (x1 + shift, next_y if next_y > -1 else y1),
                ]
        for i, poly in enumerate(self.polygons):
            l = int(len(poly) / 2)
            x1, y1 = poly[l - 1]
            x2, y2 = poly[l]
            x3, y3 = poly[l + 1]
            if isinstance(next_y, list):
                self.polygons[i] = (
                    poly[: l - 1]
                    + [
                        (x1 + shift, y1),
                        (x2 + shift, next_y[i] if next_y[i] > -1 else y2),
                        (x3 + shift, y3),
                    ]
                    + poly[l + 1 :]
                )
            else:
                self.polygons[i] = (
                    poly[: l - 1]
                    + [
                        (x1 + shift, y1),
                        (x2 + shift, next_y if next_y > -1 else y2),
                        (x3 + shift, y3),
                    ]
                    + poly[l + 1 :]
                )


def generate_brick(symbol: str, **kwargs) -> dict:
    """
    define the mapping between the symbol and the brick

    It fetches needed parameters for the bricks
    and prepare the analogue CONTEXT

    then ask for each contexts which can interpret the symbol

    Args:
        symbol (pywave.BRICKS): symbol to create
    Parameters:
        brick_width (int): height of the brick in display unit
        brick_height (int): height of the brick in display unit
    Returns:
        brick
            the brick created
    """
    # get option supported
    width = kwargs.get("brick_width", 40)
    height = kwargs.get("brick_height", 20)
    # update analogue context
    pywave.CONTEXT["Tmax"] = width
    pywave.CONTEXT["Ymax"] = height
    pywave.CONTEXT["time"] = range(0, int(width + 1))
    # create the brick
    brick = Brick()
    # Digital Context
    generated, brick = pywave.generate_digital_symbol(symbol, **kwargs)
    # Analogue Context
    if not generated:
        generated, brick = pywave.generate_analogue_symbol(symbol, **kwargs)
    # Register Context
    if not generated:
        generated, brick = pywave.generate_register_symbol(symbol, **kwargs)
    # no more context implemented
    if not generated:
        raise Exception(symbol)
    brick.symbol = symbol
    return brick
