"""
generic.py declare the basic building block
to generate a waveform
"""

import ast
import copy
from math import nan
from typing import Callable, Any, Dict, List
from dataclasses import dataclass
import undulate.logger as log


@dataclass
class Point:
    """Cartesian coordinate of a point"""

    x: float = 0.0
    y: float = 0.0


@dataclass
class SplineSegment:
    """
    Spline directive as in SVG images

    Attributes:
        order (str): one of the following directive:

            - 'm': relative move to
            - 'l': relative line to
            - 'c': relative cubic bezier curve to
            - 'M': absolute move to
            - 'L': absolute line to
            - 'C': absolute cubic bezier curve to
            - 'z': close path
            - 'Z': close path
            - '': add coordinate to previous directive
        x (float): x-coordinate relative to previous point (relative) or to brick (absolute)
        y (float): y-coordinate relative to previous point (relative) or to brick (absolute)


    .. warning::
        splines are considered to be a list of (type, x or dx, y or dy) tuples
        for more details please look at
        https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths
    """

    order: str = ""
    x: float = 0.0
    y: float = 0.0


@dataclass
class ArrowDescription:
    """
    Position of the center and orientation of the arrow to be drawn
    """

    x: float = 0.0
    y: float = 0.0
    angle: float = 0.0


@dataclass
class Drawable:
    """
    Association of a css class to a List[Point], or List[SplineSegment],
    or ArrowDescription
    """

    style: str
    object: Any


def safe_eval(code: str, ctx: dict = {}):
    """
    propose a safer alternative to eval based on ast to pre-filter possible
    instructions and limiting current variables access

    Args:
        code (str): code to execute
        ctx (dict): predefined variables and functions
    Returns:
        resulting value of the code
    """
    try:
        # ast only accept a subset of python instruction
        # which is safer than eval
        parse_tree = ast.parse(code, mode="eval")
        code_object = compile(parse_tree, filename="<string>", mode="eval")
        # eval is not safe by itself but filtered by ast
        return eval(code_object, ctx)
    except Exception:
        log.note(f"Failed to parse '{code}' consider as normal string")
        return code


@dataclass
class Brick:
    """
    Define the brick as a composition of paths, arrows, and generic polygons
    to fill an area

    Attributes:
        width (float > 0): by default is 40.0
        height (float > 0): by default is 20.0
        slewing (float > 0): by default 0.0

        symbol (str): identification symbol (mostly for debug)
        args (Dict[str, Any]): arguments used to create the brick (allow regeneration of it)
        repeat (int): number consecutive '.' after it for repetition

        ignore_start_transition (bool): by default False for smooth connection
        ignore_end_transition (bool): by default False for smooth connection
        is_first (bool): first brick of a signal, by default False
        last_y (float): last y-coordinate of the previous brick for smooth connection
        first_y (float): first y-coordinate of the next brick for smooth connection

        paths (List[Point]): list of "svg" paths to be drawn
        arrows (List[ArrowDesctiption]): list of arrows to be drawn
        polygons (List[Point]): list of polygons to be drawn
        splines (List[SplineSegment]): list of splines to be drawn
        texts (List[(str, x, y)]): list of textual element to be drawn

        .. warning::
            'paths', 'arrows', 'polygons', 'splines' are List[Drawable] but
            inside a Drawable any object are accepted.

            However, the rendering functions cannot support any object and thus,
            the clear distinction is made here to precise what is the
            expected type of object in the Drawable.
    """

    symbol: str
    paths: List[Drawable]
    arrows: List[ArrowDescription]
    polygons: List[Drawable]
    splines: List[Drawable]
    texts: List[Drawable]
    args: dict
    width: float = 40.0
    height: float = 20.0
    repeat: int = 1
    slewing: float = 0.0
    ignore_start_transition: bool = False
    ignore_end_transition: bool = False
    is_first: bool = False
    first_y: float = nan
    last_y: float = nan

    def __init__(self, **kwargs) -> None:
        self.width = float(kwargs.get("brick_width", 40.0))
        self.height = float(kwargs.get("brick_height", 20.0))
        self.slewing = float(kwargs.get("slewing", 0.0))
        self.first_y = float(kwargs.get("first_y", nan))
        self.last_y = float(kwargs.get("last_y", nan))
        self.node_name = kwargs.get("node_name", "")
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

    def get_last_y(self) -> float:
        """Get last y-coordinate of the brick"""
        last_point_path = max(
            (point for drawable in self.paths for point in drawable.object),
            key=lambda p: p.x,
            default=Point(self.width / 8, self.height),
        )
        last_point_spline = max(
            (point for drawable in self.splines for point in drawable.object),
            key=lambda p: p.x,
            default=Point(self.width / 8, self.height),
        )
        if last_point_path.x >= last_point_spline.x:
            return last_point_path.y
        return last_point_spline.y

    def get_first_y(self) -> float:
        """Get first y-coordinate of the brick"""
        first_point_path = min(
            (point for drawable in self.paths for point in drawable.object),
            key=lambda p: p.x,
            default=Point(self.width / 2, self.height),
        )
        first_point_spline = min(
            (point for drawable in self.splines for point in drawable.object),
            key=lambda p: p.x,
            default=Point(self.width / 2, self.height),
        )
        if first_point_path.x <= first_point_spline.x:
            return first_point_path.y
        return first_point_spline.y


class BrickFactory:
    """
    Create a brick from its symbol once registered

    Attributes:
        funcs (Dict[str, Callable[...,Brick]]): initialization function to create a brick
            from its symbol
        tags (Dict[str, List[str]]): list of categories associated to bricks
        params (Dict[str, Dict[str, Any]]): list of required parameters and their
            default for a given brick
    """

    funcs = {}
    tags = {}
    params = {}

    @staticmethod
    def register(
        symbol: str,
        initializer: Callable,
        tags: List[str] = [],
        params: Dict[str, Any] = {},
    ) -> None:
        """register a new brick called {name} mapped to {symbol}"""
        BrickFactory.funcs[symbol] = initializer
        # symbol can be tagged to later ease filtering on type
        BrickFactory.tags[symbol] = tags
        # register list of needed parameters
        BrickFactory.params[symbol] = params

    @staticmethod
    def create(symbol: str, **kwargs) -> Brick:
        """create a brick from its symbol"""
        if symbol not in BrickFactory.funcs:
            log.fatal(log.BRICK_SYMBOL_UNDEFINED % symbol, 3)
        init = BrickFactory.funcs[symbol]
        brick = init(**kwargs)
        brick.symbol = symbol
        return brick

    @staticmethod
    def get_parameters() -> Dict[str, Any]:
        """list all parameters registered"""
        ans = {}
        for params in BrickFactory.params.values():
            ans.update(params)
        return ans


class FilterBank:
    """List of filters to apply process a waveform"""

    filters = []

    @staticmethod
    def register(filter: Callable):
        FilterBank.filters.append(filter)

    @staticmethod
    def apply(waveform: List[Brick]) -> List[Brick]:
        """apply registered filters on the wavelane"""
        ans = waveform
        for filter in FilterBank.filters:
            if ans:
                log.note(f"Apply {filter.__name__} on {ans[-1].args.get('name', '')}")
            ans = filter(ans)
        return ans


class NodeBank:
    """Register brick position of a given node"""

    nodes = {}

    @staticmethod
    def register(node_name: str, point: Point):
        """save coordinate of a node"""
        NodeBank.nodes[node_name] = point


class ShapeFactory:
    """
    Create an annotation from its shape

    Attributes:
        funcs (Dict[str, Callable[...,str]]): initialization function to create an annotation
            from its shape
    """

    funcs = {}

    @staticmethod
    def register(pattern: str, generator: Callable):
        """save coordinate of a node"""
        ShapeFactory.funcs[pattern] = generator

    @staticmethod
    def create(pattern: str, renderer, **kwargs) -> str:
        """create an annotation from a pattern"""
        if pattern not in ShapeFactory.funcs:
            log.fatal(log.ANNOTATION_PATTERN_UNDEFINED % pattern, 3)
        generator = ShapeFactory.funcs[pattern]
        return generator(renderer, pattern, **kwargs)
