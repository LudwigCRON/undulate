#!/usr/bin/env python3
# spell-checker: disable

"""
bricks.py declare the basic building block
to generate a waveform
"""
import pywave

# TODO: removed styles in favor of skin.py

class Brick:
    """
    define the brick as a composition of paths, arrows, and generic polygons
    to fill an area
    """

    __slots__ = [
        "symbol",           # define the char
        "paths",            # list of paths to be drawn
        "arrows",           # list of arrows
        "polygons",         # list of polygons
        "splines",          # list of splines
        "texts",            # list of texts to be printed
        "width",            # width of the brick
        "height",           # height of th brick
        "styles",           # display properties: dict --> to be removed
        "slewing",          # slope limitation
        "duty_cycle",       # duty cycle 0 -> 1: float
        "ignore_transition",# prevent glitches in chain: bool
        "is_first",         # first brick in wavelane: bool
        "last_y",           # last brick y position: float
        "equation",         # equation for analogue brick: str, callable, int, float
    ]

    def __init__(self, **kwargs):
        # get options supported
        # sizing
        self.width = kwargs.get("brick_width", 40) * kwargs.get("is_repeated", 1)
        self.height = kwargs.get("brick_height", 20)
        # physical variants
        self.slewing = kwargs.get("slewing", 0)
        self.duty_cycle = kwargs.get("duty_cycle", 0.5)
        self.ignore_transition = kwargs.get("ignore_transition", False)
        # chaining instance
        self.is_first = kwargs.get("is_first", False)
        self.last_y = kwargs.get("last_y", None)
        # is analogue
        self.equation = kwargs.get("equation", None)
        # items to keep for drawing
        self.symbol = None
        self.paths = []
        self.arrows = []
        self.polygons = []
        self.splines = []
        self.texts = []
        self.styles = {"background": None, "foreground": "#000000"}

    def get_last_y(self):
        """
    get last position to preserve continuity
    """
        last_y = 0
        if self.paths:
            _, last_y = self.paths[0][-1]
        elif self.splines:
            _, _, last_y = self.splines[0][-1]
        return last_y

    def alter_end(self, shift: float = 0, next_y: float = -1):
        """
    alter the last coordinate to preserve continuity
    """
        for i, path in enumerate(self.paths):
            x1, y1 = path[-1]
            x2, y2 = path[-2]
            self.paths[i] = path[:-1] + [
                (x2 + shift, y2),
                (x1 + shift, next_y if next_y > -1 else y1),
            ]
        for i, poly in enumerate(self.polygons):
            l = int(len(poly) / 2)
            x1, y1 = poly[l - 1]
            x2, y2 = poly[l]
            x3, y3 = poly[l + 1]
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
  """
    # get option supported
    width = kwargs.get("brick_width", 40)
    height = kwargs.get("brick_height", 20)
    # update analogue context
    pywave.CONTEXT["Tmax"] = width
    pywave.CONTEXT["Ymax"] = height
    pywave.CONTEXT["time"] = range(0, int(width + 1))
    # create the brick
    block = Brick()
    # Digital Context
    generated, block = pywave.generate_digital_symbol(symbol, **kwargs)
    # Analogue Context
    if not generated:
        generated, block = pywave.generate_analogue_symbol(symbol, **kwargs)
    # Register Context
    if not generated:
        generated, block = pywave.generate_register_symbol(symbol, **kwargs)
    # no more context implemented
    if not generated:
        raise Exception(symbol)
    block.symbol = symbol
    return block
