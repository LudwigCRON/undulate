#!/usr/bin/env python3
# spell-checker: disable

"""
renderer.py declare the logic to render waveforms
into different format
"""

import re
import copy
import undulate
from ..skin import style_in_kwargs, get_style, SizeUnit
from math import atan2, cos, sin, floor
from itertools import count, accumulate
from undulate.bricks.generic import Brick, BrickFactory, FilterBank, Point
from undulate.generic import safe_eval
import undulate.logger as log

# Counter for unique id generation
#: counter of group of wave unique id
_WAVEGROUP_COUNT = 0
#: counter of wave unique id
_WAVE_COUNT = 0
# error message
ERROR_MSG = {
    "ANNOTATION_MISSING_PTS": (
        "ERROR: For annotation check from/to are defined "
        "(float,float) or float supported only"
    ),
    "WRONG_WAVE_START": "ERROR: %s : cannot repeat None or '|', add a valid brick first",
}

ARROWS_PREFIX = "<*# "
ARROWS_SUFFIX = ">*# "
EXCLUDED_NAMED_GROUPS = ["head", "foot", "config", "edges", "annotations"]


def incr_wavelane(f):
    """
    incr_wavelane is a decorator that increment _WAVE_COUNT in auto.
    This generates a unique id for each wavelane
    """

    def wrapper(*args, **kwargs):
        global _WAVE_COUNT
        _WAVE_COUNT += 1
        return f(*args, **kwargs)

    return wrapper


def incr_wavegroup(f):
    """
    incr_wavegroup is a decorator that increment _WAVEGROUP_COUNT in auto.
    This generates a unique id for each group of wavelanes
    """

    def wrapper(*args, **kwargs):
        global _WAVEGROUP_COUNT
        _WAVEGROUP_COUNT += 1
        return f(*args, **kwargs)

    return wrapper


def arrow_angle(dy: float, dx: float) -> float:
    """
    calculate the angle to align arrows based on
    the derivative of the signal

    Args:
        dy (float)
        dx (float)
    Returns:
        angle in degree
    """
    if dx == 0:
        return 90 if dy > 0 else -90
    return 180 * atan2(dy, dx) / 3.14159


def svg_curve_convert(vertices: list) -> list:
    """
    convert svg path definition to simpler s/c/m/l only mode
    to support eps renderer and other output format

    Args:
        vertices (list): list of (type,x,y) tuples where x,y are coordinates
            and type is the svg operator

            .. warning::
                it does not support T curves
    Returns:
        list of (type,x,y) tuples where type is only cubic bezier curve
    """
    # TODO add support of T curves in svg
    px, py, pt = 0, 0, "m"
    ans, ppx, ppy = [], 0, 0
    for vertice in vertices:
        t, x, y = vertice.order, vertice.x, vertice.y
        # translate S into C
        if (t in ["s", "S"]) and (pt in ["s", "S", "c", "C"]):
            ans.append(("c" if t == "s" else "C", px + (px - ppx), py + (py - ppy)))
            ans.append(("", x, y))
        # translate Q into C
        elif t in ["q", "Q"] or (t in ["s", "S"] and pt not in ["s", "S", "c", "C"]):
            ans.append(("c" if t in ["s", "q"] else "C", x, y))
            ans.append(("", x, y))
        else:
            ans.append((t, x, y))
        if t in ["m", "M", "l", "L", "s", "S", "c", "C", "q", "Q", "t", "T"]:
            pt = t
        px, py = x, y
        ppx, ppy = px, py
    return ans


class Renderer:
    """
    Abstract class of all renderer and define the parsing logic
    """

    _EDGE_REGEXP = (
        r"(?:(?P<from>[\w.#]+)[\t ]*"
        r"(?P<shape>[<*\[#]?[-|\\\/~]+[*\]#>]?)[\t ]*)?"
        r"(?P<to>[\w.#]+)[\t ]*"
        r"(?P<text>[\w \t.]*)$"
    )
    _SYMBOL_TEMP = None
    y_steps = []

    def __init__(self):
        self.ctx = None
        self.engine = None

    @staticmethod
    def is_spacer(name: str) -> bool:
        if name.strip() == "":
            return True
        if "spacer" in name.lower():
            return True
        return False

    def group(self, callback, identifier: str, **kwargs) -> str:
        """
        group define a group

        Args:
            callback (callable): function which populate what inside the group
            identifier (str): unique id for the group
        Returns:
            group of drawable items invoked by callback
        """
        raise NotImplementedError()

    def path(self, vertices: list, **kwargs) -> str:
        """
        draw a path to represent common signals

        Args:
            vertices: list of of x-y coordinates in a tuple
        Parameters:
            style_repr (optional) : class of the skin to apply
                by default apply the class 'path'
        """
        raise NotImplementedError()

    def arrow(self, x, y, angle, **kwargs) -> str:
        """
        draw an arrow to represent edge trigger on clock signals

        Args:
            x      (float) : x coordinate of the arrow center
            y      (float) : y coordinate of the arrow center
            angle  (float) : angle in degree to rotate the arrow
        Parameters:
            style_repr (optional) : class of the skin to apply
                by default apply the class 'arrow'
        """
        raise NotImplementedError()

    def polygon(self, vertices: list, **kwargs) -> str:
        """
        draw a closed shape to represent common data

        Args:
            vertices: list of of (x,y) coordinates in a tuple
        Parameters:
            style_repr (optional) : class of the skin to apply
                by default apply the class None
        """
        raise NotImplementedError()

    def spline(self, vertices: list, **kwargs) -> str:
        """
        draw a path to represent smooth signals

        Args:
            vertices: list of of (type,x,y) coordinates in a tuple of control points
                    where type is either a moveto (m/M) lineto (l/L) or curveto (c/C)
                    svg operators.
        Parameters:
            style_repr (optional) : class of the skin to apply
                by default apply the class 'path'
        """
        raise NotImplementedError()

    def text(self, x: float, y: float, text: str = "", **kwargs) -> str:
        """
        draw a text for data

        Args:
            x      (float) : x coordinate of the text
            y      (float) : y coordinate of the text
            text   (str)   : text to display
        Parameters:
            style_repr (optional) : class of the skin to apply
                by default apply the class 'text'
        """
        raise NotImplementedError()

    def translate(self, x: float, y: float, **kwargs) -> str:
        """
        translation function that is inherited for svg and eps
        """
        raise NotImplementedError()

    def brick(self, symbol: str, b: Brick, **kwargs) -> str:
        """
        brick generate the symbol for a undulate.Brick element
        (collection of paths, splines, arrows, polygons, text)
        """
        ans, content = "", ""
        # display polygons (usually background)
        for _, poly in enumerate(b.polygons):
            content += self.polygon(poly.object, style_repr=poly.style, **kwargs)
        # display path (for borders and edges)
        for _, path in enumerate(b.paths):
            content += self.path(path.object, style_repr=path.style, **kwargs)
        # display arrows
        for _, arrow in enumerate(b.arrows):
            content += self.arrow(
                arrow.object.x,
                arrow.object.y,
                arrow.object.angle,
                style_repr=arrow.style,
                **kwargs,
            )
        # display borders or edges
        for _, spline in enumerate(b.splines):
            content += self.spline(spline.object, style_repr=spline.style, **kwargs)
        # format text and display them
        for _, span in enumerate(b.texts):
            # get style of text
            a = copy.deepcopy(kwargs)
            a.update({"style_repr": span.style})
            content += self.text(*span.object, **a)
        # special function to apply at the end depending on the renderer
        if callable(self._SYMBOL_TEMP):
            ans = self._SYMBOL_TEMP(symbol, content, **kwargs)
        return ans

    def __list_nodes__(self, wavelanes: dict, level: int = 0, depth: int = 0, **kwargs):
        """
        list of named nodes in the signal representation
        and calculate their coordinates

        Args:
            wavelanes (dict): global signals representation
            depth (int): indicates if it is a subgroup or the top level

            .. warning::
                the position is altered by the following parameters:
                    - brick_width
                    - brick_height
                    - period/periods
                    - phase
                    - slewing
                    - vscale
        Returns:
            list of nodes in a dict(name: tuple(x, y))
        """
        # options for size of bricks
        config = wavelanes.get("config", {})
        vscale = config.get("vscale", 1.0) if depth > 0 else 1.0
        hscale = config.get("hscale", 1.0) if depth > 0 else 1.0
        brick_width = kwargs.get("brick_width", 40) * hscale
        brick_height = kwargs.get("brick_height", 20) * vscale
        separation = kwargs.get("separation")
        # Parameters for all wavelane
        first_row_of_group = wavelanes[next(iter(wavelanes))]
        nodes, _y = (
            [],
            (level - 1) * first_row_of_group.get("gap-offset", 0)
            if isinstance(first_row_of_group, dict)
            else 0,
        )
        for name, wavelane in wavelanes.items():
            # read nodes declaration
            if isinstance(wavelane, dict) and name not in EXCLUDED_NAMED_GROUPS:
                if "wave" in wavelane or Renderer.is_spacer(name):
                    if "node" in wavelane:
                        chain = wavelane["node"].split(" ")
                        # brick width of the wavelane
                        periods = [wavelane.get("period", 1)] * len(chain[0])
                        periods = self._get_or_eval("periods", periods, **wavelane)
                        if len(periods) < len(chain[0]):
                            periods = periods + [wavelane.get("period", 1)] * (
                                len(chain[0]) - len(periods)
                            )
                        width = [brick_width * p for p in periods]
                        phase = brick_width * wavelane.get("phase", 0)
                        slewing = wavelane.get("slewing", 3)
                        # calculate the x position
                        x = list(accumulate(width))
                        # parse the chain
                        ni, j = [], 0
                        for i, c in enumerate(chain[0]):
                            j = i if len(width) > i else -1
                            if c != ".":
                                ni.append((x[j] - width[j], width[j], c))
                        j = count(0)
                        # get identifier
                        nodes.extend(
                            [
                                (
                                    s[0] - phase + slewing * 0.5,
                                    _y + brick_height / 2,
                                    chain[1 + next(j)],
                                )
                                if not s[2].isalpha()
                                else (
                                    s[0] - phase + slewing * 0.5,
                                    _y + brick_height / 2,
                                    s[2],
                                )
                                for s in ni
                            ]
                        )
                    _y += brick_height * wavelane.get("vscale", 1) + separation
                # it is a wavegroup
                else:
                    # add group name spacing
                    _y += brick_height + separation
                    dy, n = self.__list_nodes__(wavelane, level, depth + 1, **kwargs)
                    for node in n:
                        x, y, name = node
                        nodes.append((x, _y + y, name))
                    # add size of the group
                    _y += dy
        if depth > 0:
            return (_y, nodes)
        return {n: (x, y) for x, y, n in nodes}

    @staticmethod
    def generate_patterns(prefixs: list, root: str, suffixs: list):
        """
        generate possible pattern prefixs/root/suffixs
        """
        for p in prefixs:
            for s in suffixs:
                pattern = "%s%s%s" % (p, root, s)
                yield pattern.strip()

    @staticmethod
    def adjust_y(y, factor: float = 1.0, separation: float = 0.25):
        total_y, k, s = 0, 0, 0
        for dy in Renderer.y_steps:
            if dy == "t":
                k -= 1
                s += 1
            elif k + 1 > floor(y):
                break
            else:
                k += 1
                total_y += dy
        scale = factor + separation * 0
        return total_y + (y - k) * scale

    @staticmethod
    def from_to_parser(
        s: object,
        width: float,
        height: float,
        brick_width: float = 40.0,
        brick_height: float = 20.0,
        separation: float = 0.25,
        nodes: dict = {},
    ):
        """
        parse the from and to options of annotations into positions
        for drawing the specified shape or text

        Exemple:
            .. code-block:: json

                    {"annotations": [
                        {"shape": "||", "x": 3.5},
                        {"shape": "-~>", "from": "1.5, 3%", "to": "2-0.125, 3", "text": "ready"}
                    ]}

        Args:
            s (str): value string of from or to option
            width (float): width of the image
            height (float): height of the image
            brick_width (float, default=40): brick width
            brick_height (float, default=40): brick height
        """
        # None, empty str, ...
        if s is None or isinstance(s, str) and not s.strip():
            return None
        # if is only a number
        if isinstance(s, (int, float)):
            return s
        # if a string representing a tuple
        if isinstance(s, str) and "," in s:
            s = undulate.safe_eval(s)
        # if a string representing a node
        if isinstance(s, str) and s in nodes:
            return nodes.get(s)
        # if tuple so pre-estimated
        if isinstance(s, tuple):
            return (s[0] * brick_width, Renderer.adjust_y(s[1], brick_height, separation))
        # parse (<number>, <number>)
        matches = list(re.finditer(r"\s*(\d+\.?\d*)\s*(\%|[+-]\s*\d+\.?\d*)?\s*", str(s)))
        if not matches:
            return s
        # % for image based positionning
        # otherwise row based positionning
        xunit = (
            width / 100.0
            if matches[0].group(2) and "%" in matches[0].group(2)
            else brick_width
        )
        x = float(matches[0].group(1))
        # if only one value
        if len(matches) == 1:
            return x * xunit
        yunit = (
            height / 100.0
            if matches[1].group(2) and "%" in matches[1].group(2)
            else brick_height
        )
        y = float(matches[1].group(1))
        # if row based consider the offset if given
        if matches[1].group(2) and "%" not in matches[1].group(2):
            y = Renderer.adjust_y(y, brick_height, separation) + float(matches[1].group(2))
        return (x * xunit, y * yunit)

    @staticmethod
    def register_y_step(dy, is_title: bool = False):
        if is_title:
            Renderer.y_steps.append("t")
        Renderer.y_steps.append(dy)

    def annotate(self, wavelanes: dict, viewport: tuple, depth: int = 0, **kwargs):
        """
        draw edges, vertical lines, horizontal lines, global time compression, ...
        defined in the annotations section of the input file

        Example:
            .. code-block:: json

                {"annotations": [
                    {"shape": "||", "x": 3.5},
                    {"shape": "-~>", "from": "trigger", "to": "event", "text": "ready"}
                ]}

        Args:
            wavelances (dict): global signals representations
            viewport (tuple): the drawable zone (excluding signal names)
        """
        edges_input = wavelanes.get("edges", wavelanes.get("edge", []))
        annotations = wavelanes.get("annotations", [])
        brick_width = kwargs.get("brick_width", 20)
        brick_height = kwargs.get("brick_height", 20)
        separation = kwargs.get("separation", 0.25)
        xmin, _, width, height = viewport
        # if not empty
        if not annotations and not edges_input:
            return ""
        # list nodes and their name
        nodes = self.__list_nodes__(wavelanes, depth, **kwargs)
        # transform edges into annotations
        for ei in edges_input:
            match = re.match(Renderer._EDGE_REGEXP, ei)
            if match is not None:
                m = match.groupdict()
                annotations.append(m)

        # create annotations
        def __annotate__(a: dict):
            shape = a.get("shape", None)
            x = a.get("x", 0)
            y = a.get("y", 0)
            dx = a.get("dx", 0) * brick_width
            dy = Renderer.adjust_y(a.get("dy", 0), brick_height, separation)
            start = a.get("from", None)
            end = a.get("to", None)
            text = a.get("text", "")
            text_background = a.get("text_background", True)
            ans = ""
            start = Renderer.from_to_parser(
                start, width, height, brick_width, brick_height, separation, nodes=nodes
            )
            end = Renderer.from_to_parser(
                end, width, height, brick_width, brick_height, separation, nodes=nodes
            )
            # calculate position of start node
            if isinstance(start, str) and nodes:
                s = [node for node in nodes if start in node]
                s = s[-1] if s else (0, 0)
            elif isinstance(start, tuple):
                s = start
            else:
                s = (0, 0)
            # calculate position of end node
            if isinstance(end, str) and nodes:
                e = [node for node in nodes if end in node]
                e = e[-1] if e else (0, 0)
            elif isinstance(end, tuple):
                e = end
            else:
                e = (0, 0)
            # compatibility support of issue #17
            if s == (0, 0) and e != (0, 0):
                s = (e[0] - brick_width / 2, e[-1])
                txt_font_size = get_style("edge-text").get("font-size") or (
                    1.0,
                    SizeUnit.EM,
                )
                txt_font_size = txt_font_size[0] * txt_font_size[1].value
                dx = -len(text) / 2 * txt_font_size
                shape = "->"
            # add offset for delay of data and middle of brick vertical
            s = s[0] + xmin, s[1]
            e = e[0] + xmin, e[1]
            # if shape and shape[0] == '<':
            #    s = s[0]-3.5, s[1]
            # if shape and shape[-1] == '>':
            #    e = e[0]-3.5, e[1]
            # derivative of edges for arrows: by default ->
            start_dx, start_dy, end_dx, end_dy = s[0] - e[0], 0, e[0] - s[0], 0
            mx, my = (s[0] + e[0]) * 0.5, (s[1] + e[1]) * 0.5
            # draw shapes and surcharge styles
            overload = style_in_kwargs(**a)
            # hline
            if shape == "-":
                y_pos = Renderer.adjust_y(y, brick_height, separation)
                x1 = xmin + start * brick_width if isinstance(start, (float, int)) else xmin
                x2 = (
                    xmin + end * brick_width
                    if isinstance(end, (float, int))
                    else xmin + width
                )
                pts = [("M", x1, y_pos), ("L", x2, y_pos)]
                ans = self.spline(pts, **a)
            # vline
            elif shape == "|":
                x = xmin + x * brick_width
                y1 = (
                    Renderer.adjust_y(start, brick_height, separation)
                    if isinstance(start, (float, int))
                    else 0
                )
                y2 = (
                    Renderer.adjust_y(end, brick_height, separation)
                    if isinstance(end, (float, int))
                    else height
                )
                pts = [("M", x, y1), ("L", x, y2)]
                ans = self.spline(pts, **a)
            # global time compression
            elif shape == "||":
                x = xmin + x * brick_width
                y1 = (
                    Renderer.adjust_y(start, brick_height, separation)
                    if isinstance(start, (float, int))
                    else 0
                )
                y2 = (
                    Renderer.adjust_y(end, brick_height, separation)
                    if isinstance(end, (float, int))
                    else height
                )
                pts_1 = [
                    ("M", x, y1),  # |
                    ("L", x, (y2 + y1) / 2 - 10),  # |
                    ("L", x - 10, (y2 + y1) / 2),  # /
                    ("L", x, (y2 + y1) / 2 + 10),  # \
                    ("L", x, y2),  # |
                ]
                pts_2 = [
                    ("M", x + 5, y1),  # |
                    ("L", x + 5, (y2 + y1) / 2 - 10),  # |
                    ("L", x - 4, (y2 + y1) / 2),  # /
                    ("L", x + 5, (y2 + y1) / 2 + 10),  # \
                    ("L", x + 5, y2),  # |
                ]
                poly = copy.deepcopy(pts_2)
                poly.extend(pts_1[::-1])
                ans = self.polygon([(i, j) for c, i, j in poly], style_repr="hide")
                ans += self.spline(pts_1, style_repr="big_gap")
                ans += self.spline(pts_2, style_repr="big_gap")
            # edges
            elif shape in Renderer.generate_patterns(ARROWS_PREFIX, "~", ARROWS_SUFFIX):
                ans = self.spline(
                    [
                        ("M", s[0], s[1]),
                        ("C", s[0] * 0.1 + e[0] * 0.9, s[1]),
                        ("", s[0] * 0.9 + e[0] * 0.1, e[1]),
                        ("", e[0], e[1]),
                    ],
                    is_edge=True,
                    style_repr="edge",
                    **overload,
                )
            elif shape in Renderer.generate_patterns(ARROWS_PREFIX, "-~", ARROWS_SUFFIX):
                ans = self.spline(
                    [
                        ("M", s[0], s[1]),
                        ("C", e[0], s[1]),
                        ("", e[0], e[1]),
                        ("", e[0], e[1]),
                    ],
                    is_edge=True,
                    style_repr="edge",
                    **overload,
                )
                start_dx, start_dy, end_dx, end_dy = s[0] - e[0], 0, 0, e[1] - s[1]
            elif shape in Renderer.generate_patterns(ARROWS_PREFIX, "~-", ARROWS_SUFFIX):
                ans = self.spline(
                    [
                        ("M", s[0], s[1]),
                        ("C", s[0], s[1]),
                        ("", s[0], e[1]),
                        ("", e[0], e[1]),
                    ],
                    is_edge=True,
                    style_repr="edge",
                    **overload,
                )
                start_dx, start_dy, end_dx, end_dy = 0, s[1] - e[1], e[0] - s[0], 0
            elif shape in Renderer.generate_patterns(ARROWS_PREFIX, "-", ARROWS_SUFFIX):
                ans = self.spline(
                    [("M", s[0], s[1]), ("L", e[0], e[1])],
                    is_edge=True,
                    style_repr="edge",
                    **overload,
                )
                start_dx, start_dy, end_dx, end_dy = (
                    s[0] - e[0],
                    s[1] - e[1],
                    e[0] - s[0],
                    e[1] - s[1],
                )
            elif shape in Renderer.generate_patterns(ARROWS_PREFIX, "-|", ARROWS_SUFFIX):
                ans = self.spline(
                    [("M", s[0], s[1]), ("L", e[0], s[1]), ("", e[0], e[1])],
                    is_edge=True,
                    style_repr="edge",
                    **overload,
                )
                start_dx, start_dy, end_dx, end_dy = s[0] - e[0], 0, 0, e[1] - s[1]
                mx, my = e[0], s[1]
            elif shape in Renderer.generate_patterns(ARROWS_PREFIX, "|-", ARROWS_SUFFIX):
                ans = self.spline(
                    [("M", s[0], s[1]), ("L", s[0], e[1]), ("", e[0], e[1])],
                    is_edge=True,
                    style_repr="edge",
                    **overload,
                )
                start_dx, start_dy, end_dx, end_dy = 0, s[1] - e[1], e[0] - s[0], 0
                mx, my = s[0], e[1]
            elif shape in Renderer.generate_patterns(ARROWS_PREFIX, "-|-", ARROWS_SUFFIX):
                ans = self.spline(
                    [("M", s[0], s[1]), ("L", mx, s[1]), ("", mx, e[1]), ("", e[0], e[1])],
                    is_edge=True,
                    style_repr="edge",
                    **overload,
                )
                start_dx, start_dy, end_dx, end_dy = s[0] - mx, 0, e[0] - mx, 0
                mx, my = mx, e[1]
            # add arrows for edges
            if shape is not None:
                # marker start
                if shape[0] == "<":
                    th = arrow_angle(start_dy, start_dx)
                    ans += self.arrow(
                        0,
                        0,
                        th,
                        extra=self.translate(
                            s[0] - 3 * cos(th * 3.14159 / 180),
                            s[1] - 3 * sin(th * 3.14159 / 180),
                            no_acc=True,
                        ),
                        dy=brick_height,
                        is_edge=True,
                        style_repr="edge-arrow",
                        **overload,
                    )
                elif shape[0] == "*":
                    pass
                elif shape[0] == "#":
                    pass
                # marker end
                if shape[-1] == ">":
                    th = arrow_angle(end_dy, end_dx)
                    ans += self.arrow(
                        0,
                        0,
                        th,
                        extra=self.translate(
                            e[0] - 3 * cos(th * 3.14159 / 180),
                            e[1] - 3 * sin(th * 3.14159 / 180),
                            no_acc=True,
                        ),
                        dy=brick_height,
                        is_edge=True,
                        style_repr="edge-arrow",
                        **overload,
                    )
                elif shape[0] == "*":
                    pass
                elif shape[0] == "#":
                    pass
                # add text is not empty
                if text:
                    # add white background for the text
                    a.update({"style_repr": "edge-text", "x": mx + dx, "y": my + dy})
                    if text_background:
                        ox, oy, w, h = undulate.text_bbox(
                            self.ctx, "edge-text", text, self.engine, overload
                        )
                        ans += self.polygon(
                            [(0, 0), (0, 0 + h), (0 + w, 0 + h), (0 + w, 0), (0, 0)],
                            extra=self.translate(
                                a.get("x") + ox, a.get("y") + oy, no_acc=True
                            ),
                            style_repr="edge-background",
                        )
                    # add the text
                    ans += self.text(**a)
            elif text:
                overload = style_in_kwargs(**a)
                # add white background for the text
                a.update(
                    {
                        "style_repr": "edge-text",
                        "x": xmin + x * brick_width,
                        "y": Renderer.adjust_y(y, brick_height, separation),
                    }
                )
                if text_background:
                    ox, oy, w, h = undulate.text_bbox(
                        self.ctx, "edge-text", text, self.engine, overload
                    )
                    ans += self.polygon(
                        [(0, 0), (0, 0 + h), (0 + w, 0 + h), (0 + w, 0), (0, 0)],
                        extra=self.translate(a.get("x") + ox, a.get("y") + oy, no_acc=True),
                        style_repr="edge-background",
                    )
                # add the text
                ans += self.text(**a)
            return ans

        return "\n".join([__annotate__(a) for a in annotations])

    def wavelane_title(self, name: str, **kwargs):
        """
        generate the title in front of a waveform

        Args:
            name: name of the waveform print alongside
            order: position from 0-4 of the title position along
                the y-axis. This property is important when overlaying signals

                    - 0   : middle of the wavelane height
                    - 1-4 : quarter from top to bottom of the wavelane
            brick_height (float)
        Returns:
            renderer.text
        """
        extra = kwargs.get("extra", "")
        order = kwargs.get("order", 0)
        brick_height = kwargs.get("brick_height", 20) * kwargs.get("vscale", 1)
        kw = {
            k: kwargs.get(k)
            for k in kwargs.keys()
            if k in ["fill", "stroke", "font", "font-weight"]
        }
        if Renderer.is_spacer(name):
            return ""
        if order == 0:
            y = brick_height / 2
        else:
            y = brick_height / 4 * order - brick_height / 8
        return self.text(-10, y, name, offset=extra, style_repr="title", **kw)

    def _reduce_wavelane(self, name: str, wavelane: str, **kwargs):
        """
        Args:
            name (str) : name of the wavelane
            wavelane (str) : list of symbol describing the signal
        Returns:
            list of tuple<brick, kwargs> to ease the wavelance generation
            in kwargs the list of properties are:
            All
                periods             (float)
                phase               (float)
                duty_cycle          (float)
                data                (str)
                slewing             (float)
                follow_data         (bool)
                is_first            (bool)
                ignore_transition   (bool)
            Digital-Only
                up                  (bool, generated for impulse)
                add_arrow           (bool, generated)
            Analog-Only
                equation            (float or str)
                then_one            (bool, generated)
                points              (float or list, generated from equation)
            Register-Only
                attr                (str)
                type                (str)
                pos                 (int)
                styles              (str)

        """
        repeat = kwargs.get("repeat", 1)
        # calculate total length of the wavelance
        TOTAL_LENGTH = len(wavelane) * int(repeat)
        # calculate parameters for each brick of a given wavelane
        needed_params = BrickFactory.get_parameters()
        for param in list(needed_params.keys()):
            params = param + "s" if param != "data" else param
            needed_params[params] = [
                kwargs.get(param) or needed_params[param]
            ] * TOTAL_LENGTH
            if params in kwargs:
                needed_params[params] = kwargs.get(params) or needed_params[params]
            if isinstance(needed_params[params], str) and params == "data":
                needed_params[params] = needed_params[params].split(" ")
            elif isinstance(needed_params[params], str):
                needed_params[params] = safe_eval(needed_params[params], {})
        # computed properties
        follow_data = False
        follow_x = False
        previous_symbol = " "
        _wavelane = []
        # initialize the waveform
        for i, b in enumerate(wavelane * repeat):
            brick_args = copy.deepcopy(kwargs)
            for param in BrickFactory.params.get(b, []):
                params = param + "s" if param != "data" else param
                brick_args[param] = needed_params[params].pop(0)
            brick_args["follow_data"] = follow_data
            brick_args["follow_x"] = follow_x
            brick_args["is_first"] = i == 0
            # generate the brick
            _wavelane.append(BrickFactory.create(b, **brick_args))
            follow_data = "data" in BrickFactory.tags[previous_symbol]
            follow_x = previous_symbol == "X"
            previous_symbol = b
        # apply all registered filters
        return FilterBank.apply(_wavelane)

    def _get_or_eval(self, name: str, default: str = "", **kwargs):
        """
        if is a str, evaluate the code or get it in a standard way
        """
        param = kwargs.get(name) or default
        if isinstance(param, str):
            return safe_eval(param)
        return param

    @incr_wavelane
    def wavelane(self, name: str, wavelane: str, extra: str = "", **kwargs):
        """
        wavelane is the core function which generate a waveform from the string
        name         : name of the waveform
        wavelane     : string which describes the waveform
        [extra]      : optional attributes for the svg (eg class)
        [period]     : time dilatation factor, default is 1
        [phase]      : time shift of the waveform, default is 0
        [gap_offset] : time shift for adjusting the position of a gap, default is 3/4
                    of the tick period
        [data]       : when using either '=', '2', '3', ... symbols the data can be set.
                    A list of string is expected
        [slewing]    : current limitation which limit the transition speed of a signal
                    default is 3
        [duty_cycles]: A list of duty_cycle for each bricks
        [periods]    : A list of period for each bricks
        """
        # options
        brick_width = kwargs.get("brick_width", 20) * kwargs.get("hscale", 1)
        brick_height = kwargs.get("brick_height", 20) * kwargs.get("vscale", 1)
        gap_offset = kwargs.get("gap_offset", brick_width * 0.5)

        # preprocess waveform to simplify it
        _wavelane = self._reduce_wavelane(name, wavelane, **kwargs)

        # generate waveform
        wave, pos = [], 0
        last_valid_brick = None
        for brick in _wavelane:
            # prune the properties
            x = max(0, pos)
            if brick.symbol == "|":
                x = pos - brick_width + gap_offset - brick.slewing
            brick.args.update(
                {
                    "last_y": brick_height
                    if last_valid_brick is None
                    else last_valid_brick.last_y,
                    "extra": self.translate(x, 0, dont_touch=True),
                }
            )
            # add style informations
            brick.args.update(style_in_kwargs(**kwargs))
            # generate the brick
            wave.append(BrickFactory.create(brick.symbol, **brick.args))
            # create the new brick
            pos += wave[-1].width
            if "repeat" not in BrickFactory.tags[brick.symbol]:
                last_valid_brick = brick

        # rendering
        def _gen():
            ans = self.wavelane_title(name, **kwargs) if name else ""
            for brick in wave:
                ans += self.brick(brick.symbol, brick, **brick.args)
            return ans

        # wrap the wavelane
        return self.group(
            _gen,
            name if name else "wavelane_%d_%d" % (_WAVEGROUP_COUNT, _WAVE_COUNT),
            extra=extra,
        )

    def ticks(self, width: int, height: int, step: float, **kwargs) -> str:
        """
        generates the dotted lines to see ticks easily

        Args:
            width    (int) : width of the image
            height   (int) : height of the image
            step     (float) : distance between two ticks
            offsetx (optional): shift all ticks along the x-axis
            offsety (optional): shift to the bottom ticks with exceeding the height
            phase (optional): phase of the first signal on the top level
                this parameter is used to align tick with the rising edges of the first signal
        """
        offsetx = kwargs.get("offsetx", 0)
        offsety = kwargs.get("offsety", 0)
        phase = kwargs.get("phase", 0)

        def _gen():
            ans = ""
            for k in range(0, int(width / step)):
                x = step * k
                ans += self.path(
                    [Point(x, 0), Point(x, height - offsety)],
                    style_repr="tick",
                    extra="",
                    **kwargs,
                )
            return ans

        return self.group(
            _gen,
            "ticks_%d" % _WAVEGROUP_COUNT,
            extra=self.translate(offsetx + phase * width, 0),
        )

    @incr_wavegroup
    def wavegroup(self, name: str, wavelanes, extra: str = "", depth: int = 1, **kwargs):
        """
        wavegroup generate a collection of waveforms
        name           : name of the wavegroup
        wavelanes      : collection of wavelane
        [extra]        : optional attributes for the svg (eg class)
        [brick_width]  : width of a brick, default is 20
        [brick_height] : height a row, default is 20
        [width]        : image width, default is auto
        [height]       : image height, default is 0
        [no_ticks]     : if True does not display any ticks
        """
        if not isinstance(wavelanes, dict):
            return (0, "")
        # prepare the return group
        _default_offset_x = [
            len(s) + 1
            for s in wavelanes.keys()
            if not (Renderer.is_spacer(s) or s in EXCLUDED_NAMED_GROUPS)
        ]
        # options for size of bricks
        config = wavelanes.get("config", {})
        vscale = config.get("vscale", 1.0)
        hscale = config.get("hscale", 1.0)
        brick_width = kwargs.get("brick_width", 40) * hscale
        brick_height = kwargs.get("brick_height", 20) * vscale
        separation = config.get("separation", kwargs.get("separation")) or 0.25
        if depth == 1:
            separation *= brick_height
        # update kwargs
        kwargs.update(
            {
                "brick_width": brick_width,
                "brick_height": brick_height,
                "separation": separation,
            }
        )
        # options for reserved space for signal names
        name_font_size = get_style("text").get("font-size") or (1.0, SizeUnit.EM)
        name_font_size = name_font_size[0] * name_font_size[1].value
        offsetx = kwargs.get("offsetx", max(_default_offset_x, default=0) * name_font_size)
        offsety = kwargs.get("offsety", 0)
        # options for appearance
        # group delimiter (image size)
        width = kwargs.get("width", 0)
        height = kwargs.get("height", 0)
        # ticks
        no_ticks = config.get("no_ticks", depth > 1)
        # position of | symbol
        gap_offset = config.get("gap-offset", brick_width * 0.5)

        def _gen(offset, width, height, brick_width, brick_height):
            ox, oy, dy = offset[0], offset[1], 0
            # some space for group separation if not the root
            oy += (brick_height + separation) if depth > 1 else 0
            # return value is ans
            ans = ""
            if depth > 1:
                # get font size for position estimation
                grp_font_size = get_style("h%d" % depth).get("font-size") or (
                    1.0,
                    SizeUnit.EM,
                )
                grp_font_size = grp_font_size[0] * grp_font_size[1].value
                # add group name
                ans = self.text(
                    0,
                    oy - 0.65 * grp_font_size - separation,
                    name,
                    style_repr="h%d" % depth,
                    **kwargs,
                )
                # add group separator
                if depth == 2:
                    ans += self.path(
                        [Point(0, oy - separation), Point(width + ox, oy - separation)],
                        style_repr="border ctx-y",
                        **kwargs,
                    )
                Renderer.register_y_step(brick_height + separation, is_title=True)
            # look through waveforms data
            for _, wavetitle in enumerate(wavelanes.keys()):
                # annotations, config, edges, ... are list
                # and not parsed on the fly
                if not isinstance(wavelanes[wavetitle], dict):
                    continue
                if wavetitle in EXCLUDED_NAMED_GROUPS:
                    continue
                # signals and registers are in a dict
                # height of a single waveform
                dy = brick_height * wavelanes[wavetitle].get("vscale", 1) + separation
                # waveform generation
                if "wave" in wavelanes[wavetitle]:
                    wave, args = wavelanes[wavetitle]["wave"], wavelanes[wavetitle]
                    # propagate information from hierarchy
                    args.update(**kwargs)
                    args.update({"gap-offset": gap_offset})
                    # generate the waveform of this signal
                    ans += self.wavelane(wavetitle, wave, self.translate(ox, oy), **args)
                    # if the waveform of this signal will be overlayed
                    # do not increment the position
                    overlay = args.get("overlay", False)
                    if overlay:
                        dy = 0
                    width = max(len(wave) * brick_width, width)
                    Renderer.register_y_step(dy)
                # spacer or only for label nodes
                elif Renderer.is_spacer(wavetitle) or "node" in wavelanes[wavetitle]:
                    Renderer.register_y_step(dy)
                # named group
                elif wavetitle not in EXCLUDED_NAMED_GROUPS:
                    args = copy.deepcopy(kwargs)
                    args.update(
                        {
                            "offsetx": ox,
                            "offsety": 0,
                            "no_ticks": True,
                            "gap-offset": gap_offset,
                        }
                    )
                    dy, tmp = self.wavegroup(
                        wavetitle,
                        wavelanes[wavetitle],
                        self.translate(0, oy, dont_touch=True),
                        depth + 1,
                        **args,
                    )
                    ans += tmp
                oy += dy
            # add ticks only for the principale group
            if not no_ticks:
                kw = {
                    "offsetx": ox,
                    "step": brick_width,
                    "width": width,
                    "height": height,
                    "phase": config.get("ticks_phase", 0),
                }
                ans = "%s\n%s" % (self.ticks(**kw), ans)
            offset[0], offset[1] = ox, oy
            return ans

        # room for displaying names
        offset = [offsetx, offsety]
        ans = self.group(
            lambda: _gen(offset, width, height, brick_width, brick_height),
            name,
            extra=extra,
        )
        offsetx, offsety = offset[0], offset[1]
        # finish the group with local annotations
        ans += self.annotate(
            wavelanes, viewport=(offsetx, 0, width, height), depth=depth, **kwargs
        )
        return (offsety, ans)

    def size(self, wavelanes, depth: int = 1, **kwargs):
        """
        size pre-estimate the size of the image

        Args:
            wavelanes (dict): global signals representation
            brick_width (int, optional)  : width of a brick, default is 20
            brick_height (int, optional)  : height of a row, default is 20
            periods   (int)  : list of time dilatation factor, default is 1
            repeat    (int)  : brick repetition factor
            overlay (bool) : overlay the next signal over the current one
        """
        if not isinstance(wavelanes, dict):
            return (0, 0, 0, 0)
        # options for size of bricks
        config = wavelanes.get("config", {})
        vscale = config.get("vscale", 1.0)
        hscale = config.get("hscale", 1.0)
        brick_width = kwargs.get("brick_width", 40) * hscale
        brick_height = kwargs.get("brick_height", 20) * vscale
        separation = config.get("separation", kwargs.get("separation")) or 0.25
        if depth == 1:
            separation *= brick_height
        # update kwargs
        kwargs.update(
            {
                "brick_width": brick_width,
                "brick_height": brick_height,
                "separation": separation,
            }
        )
        # return kind of a viewport
        x, y, n, keys = [0], (brick_height + separation) if depth > 1 else 0, 0, [0]
        # look through all wavelanes
        for wavetitle in wavelanes.keys():
            if not isinstance(wavelanes[wavetitle], dict):
                continue
            # add some extra for attr in registers
            _attr = wavelanes[wavetitle].get("attr", [(0, None)])
            if isinstance(_attr, list):
                _n = [
                    len(_a[1])
                    for _a in _attr
                    if not _a[1] is None and isinstance(_a[1], list)
                ]
                n += max(_n) if _n else 0
            # handle a wavelane
            dy = brick_height * wavelanes[wavetitle].get("vscale", 1) + separation
            if "wave" in wavelanes[wavetitle]:
                # estimate length of the wavelane
                # TODO create a wavelane_size function
                if "periods" not in wavelanes[wavetitle]:
                    _l = len(wavelanes[wavetitle]["wave"])
                else:
                    periods = self._get_or_eval("periods", [], **wavelanes[wavetitle])
                    _l = sum(periods)
                _l *= brick_width
                _l *= wavelanes[wavetitle].get("repeat", 1)
                _l *= wavelanes[wavetitle].get("period", 1)
                x.append(_l)
                # estimate height
                if wavelanes[wavetitle].get("overlay", False):
                    dy = 0
                keys.append(len(wavetitle))
            # if it is only spacers allocate space
            elif Renderer.is_spacer(wavetitle) or "node" in wavelanes[wavetitle]:
                pass
            # otherwise it is a new wavegroup
            # or an old wavegroup
            elif wavetitle not in EXCLUDED_NAMED_GROUPS:
                lkeys, _x, dy, _n = self.size(wavelanes[wavetitle], depth + 1, **kwargs)
                x.append(_x)
                n += _n
                keys.append(lkeys)
            else:
                dy = 0
            y += dy
        return (max(keys), max(x), y, n)

    def draw(self, wavelanes, **kwargs) -> str:
        """
        Business function calling all others

        Args:
            wavelanes (dict): parsed dictionary from the input file
            filename (str, optional)  : file name of the output generated file
            brick_width (int): by default 40
            brick_height (int): by default 20
            is_reg (bool):
                if True `wavelanes` given represents a register
                otherwise it represents a bunch of signals
        """
        raise NotImplementedError()
