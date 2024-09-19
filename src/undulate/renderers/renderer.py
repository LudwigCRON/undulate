"""
renderer.py declare the logic to render waveforms
into different format
"""

import re
import copy
import undulate.skin
import undulate.logger as log
from undulate.skin import style_in_kwargs, get_style, SizeUnit, text_bbox
from math import floor
from undulate.bricks.generic import (
    Brick,
    BrickFactory,
    FilterBank,
    NodeBank,
    Point,
    ShapeFactory,
    safe_eval,
    ArrowDescription,
    SplineSegment,
)
from typing import List

# Counter for unique id generation
#: counter of group of wave unique id
_WAVEGROUP_COUNT = 0
#: counter of wave unique id
_WAVE_COUNT = 0

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
        Group some drawable together

        Args:
            callback (callable): function which populate what inside the group
            identifier (str): unique id for the group
        """
        raise NotImplementedError()

    def path(self, vertices: List[Point], **kwargs) -> str:
        """
        Draw line segments to connect consecutive points of 'vertices'
        to represent common signals

        Args:
            vertices (List[Point]): list of points to be connected
        Parameters:
            style_repr (optional str) : css rule, by default 'path'
        """
        raise NotImplementedError()

    def arrow(self, arrow_description: ArrowDescription, **kwargs) -> str:
        """
        Draw an arrow to represent edge trigger on clock signals or to point
        something in an annotation.

        Args:
            arrow_description (ArrowDescription) : position and oriantation
        Parameters:
            style_repr (optional str) : css rule, by default 'arrow'
        """
        raise NotImplementedError()

    def polygon(self, vertices: List[Point], **kwargs) -> str:
        """
        Draw a closed shape for shaded/colored area

        Args:
            vertices (List[Point]): Ordered list of point delimiting the polygon
        Parameters:
            style_repr (optional str) : css rule, by default None
        """
        raise NotImplementedError()

    def spline(self, vertices: List[SplineSegment], **kwargs) -> str:
        """
        Draw a path to represent smooth signals

        Args:
            vertices (List[SplineSegment]): list of SVG path operators and arguments
        Parameters:
            style_repr (optional str) : css rule, by default 'path'
        """
        raise NotImplementedError()

    def text(self, x: float, y: float, text: str = "", **kwargs) -> str:
        """
        Draw a text at a specific position

        Args:
            x      (float) : x coordinate of the text
            y      (float) : y coordinate of the text
            text   (str)   : text to display
        Parameters:
            style_repr (optional str) : css rule, by default 'text'
        """
        raise NotImplementedError()

    def translate(self, x: float, y: float, **kwargs) -> str:
        """
        translation function that is inherited for svg and eps
        """
        raise NotImplementedError()

    def brick(self, symbol: str, b: Brick, **kwargs) -> str:
        """
        Draw the symbol of a given Brick element
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
                arrow.object,
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

    @staticmethod
    def adjust_y(index, brick_height: float = 1.0) -> float:
        """
        Convert an integer expression the index of the waveform
        as a y-coordinate in the drawing context

        Args:
            y (int): index of the waveform
            brick_height (float): height of a brick
        Returns:
            equivalent y-coordinate
        """
        total_y, k, s = 0, 0, 0
        for dy in Renderer.y_steps:
            # 't' means title with potential separation
            if dy == "t":
                k -= 1
                s += 1
            elif k + 1 > floor(index):
                break
            else:
                k += 1
                total_y += dy
        return total_y + (index - k) * brick_height

    @staticmethod
    def from_to_parser(
        s: object,
        width: float,
        height: float,
        brick_width: float = 40.0,
        brick_height: float = 20.0,
    ) -> Point:
        """
        Parse the from and to options of annotations into positions
        for drawing the specified shape or text

        Supported format are:
        - float
        - Tuple[float, float]
        - String "float"
        - String "float unit" where unit is either "" or "%"
        - String "(float unit, float unit)" where unit is either "" or "%"
        - String "node_name"
        - String "node_name + (± float, ± float)"

        Args:
            s (str): value of from or to option
            width (float): width of the image
            height (float): height of the image
            brick_width (float, default=40): brick width
            brick_height (float, default=40): brick height
        Returns:
            Point of x-y coordinate
        """
        ans = Point(0, 0)
        # None, empty str, ...
        if s is None or (isinstance(s, str) and not s.strip()):
            return ans
        re_str_node_tuple = r"(?P<node>\w+)\s*\+\s*\(\s*(?P<dx>[+-]?\s*\d*\.?\d*)\s*,\s*(?P<dy>[+-]?\s*\d*\.?\d*)\s*\)"
        re_str_tuple = r"\(\s*(?P<x>\d*\.?\d*\s*%?)\s*,\s*(?P<y>\d*\.?\d*\s*%?)\s*\)"
        # convert potential tuple and int into python object
        if isinstance(s, str):
            s = s.strip()
            # if s corresponds to a node
            if s in NodeBank.nodes:
                return NodeBank.nodes.get(s)
            # if s corresponds to node_name + (dx, dy)
            match = re.match(re_str_node_tuple, s)
            if match:
                p = NodeBank.nodes.get(match.group("node"))
                if p:
                    ans.x = p.x + float(match.group("dx")) * brick_width
                    ans.y = p.y + float(match.group("dy")) * brick_height
                    return ans
            # if s corresponds to a tuple get x and y coordinate
            match = re.match(re_str_tuple, s)
            if match:
                s = (match.group("x"), match.group("y"))
                # convert percentage into absolute
                if "%" in s[0]:
                    ans.x = float(s[0].replace("%", "")) * width / 100
                else:
                    ans.x = float(s[0]) * brick_width
                if "%" in s[1]:
                    ans.y = float(s[1].replace("%", "")) * height / 100
                else:
                    ans.y = Renderer.adjust_y(float(s[1]), brick_height)
                return ans
            if "%" in s:
                ans.x = float(s.replace("%", "")) * width / 100
                ans.y = float(s.replace("%", "")) * height / 100
                return ans
            s = safe_eval(s)
        # if s is a tuple
        if isinstance(s, tuple):
            ans.x = float(s[0]) * brick_width
            ans.y = Renderer.adjust_y(float(s[1]), brick_height)
            return ans
        # if s is only a number
        if isinstance(s, (int, float)):
            ans.x = s * brick_width
            ans.y = Renderer.adjust_y(s, brick_height)
            return ans
        log.fatal(log.FROM_TO_UNKNOWN_FORMAT % str(s), 8)

    @staticmethod
    def register_y_step(dy, is_title: bool = False):
        if is_title:
            Renderer.y_steps.append("t")
        Renderer.y_steps.append(dy)

    def annotate(self, wavelanes: dict, viewport: tuple, **kwargs) -> str:
        """
        Draw edges, vertical lines, horizontal lines, global time compression, ...
        or any other shape defined in the annotations section of the input file

        Example:
            .. code-block:: json

                {"annotations": [
                    {"shape": "||", "x": 3.5},
                    {"shape": "-~>", "from": "trigger", "to": "event", "text": "ready"}
                ]}

        Args:
            wavelanes (Dict): global signals representations
            viewport (Tuple[float, float, float, float]): the drawable zone (excluding signal names) x, y, width, height
        Parameters:
            edges (Dict): edge section of the input file
            annotations (List[Dict]): annotations section of the input file
            brick_width (float): default width of a brick
            brick_height (float): default height of a brick
        """
        edges_input = wavelanes.get("edges", wavelanes.get("edge", []))
        annotations = wavelanes.get("annotations", [])
        brick_width = kwargs.get("brick_width", 20)
        brick_height = kwargs.get("brick_height", 20)
        # if not empty
        if not annotations and not edges_input:
            return ""
        # transform edges into annotations
        for ei in edges_input:
            match = re.match(Renderer._EDGE_REGEXP, ei)
            if match is not None:
                m = match.groupdict()
                annotations.append(m)

        # create annotations
        def __annotate__(a: dict, viewport: tuple):
            xmin, _, width, height = viewport
            shape = a.get("shape", None)
            x = a.get("x", 0)
            y = a.get("y", 0)
            dx = a.get("dx", 0) * brick_width
            dy = Renderer.adjust_y(a.get("dy", 0), brick_height)
            start = a.get("from", None)
            end = a.get("to", None)
            text = a.get("text", "")
            text_background = a.get("text_background", True)
            ans = ""
            s = Renderer.from_to_parser(start, width, height, brick_width, brick_height)
            e = Renderer.from_to_parser(end, width, height, brick_width, brick_height)
            log.debug(a)
            log.debug(f"Edge from {start}:{s} to {end}:{e}")
            # compatibility support of issue #17
            if s.x == 0 and s.y == 0 and e.x != 0 and e.y != 0:
                s = Point(e.x - brick_width / 2, e.y)
                txt_font_size = get_style("edge-text").get("font-size") or (
                    1.0,
                    SizeUnit.EM,
                )
                txt_font_size = txt_font_size[0] * txt_font_size[1].value
                dx = -len(text) / 2 * txt_font_size
                shape = "->"
            # add offset for delay of data and middle of brick vertical
            s = Point(s.x + xmin, s.y)
            e = Point(e.x + xmin, e.y)
            # draw shapes and surcharge styles
            overload = style_in_kwargs(**a)
            # hline
            if shape == "-":
                y = Renderer.adjust_y(y, brick_height)
                if isinstance(end, (float, int)):
                    xmax = xmin + end * brick_width
                else:
                    xmax = xmin + width
                if isinstance(start, (float, int)):
                    xmin += start * brick_width
                overload["y"] = y
                overload["xmin"] = xmin
                overload["ymax"] = xmax
            # vline or time compression
            elif shape in ["|", "||"]:
                x = xmin + x * brick_width
                ymin = 0
                ymax = height
                if isinstance(start, (float, int)):
                    ymin = Renderer.adjust_y(start, brick_height)
                if isinstance(end, (float, int)):
                    ymax = Renderer.adjust_y(end, brick_height)
                overload["x"] = x
                overload["ymin"] = ymin
                overload["ymax"] = ymax
            else:
                overload["start"] = s
                overload["end"] = e
            if shape:
                ans += ShapeFactory.create(shape, self, **overload)
            if text:
                overload = style_in_kwargs(**a)
                # add white background for the text
                if shape:
                    mx, my = (s.x + e.x) * 0.5, (s.y + e.y) * 0.5
                    overload.update(
                        {
                            "style_repr": "edge-text",
                            "x": mx + dx,
                            "y": my + dy,
                            "text": text,
                        }
                    )
                else:
                    overload.update(
                        {
                            "style_repr": "edge-text",
                            "x": xmin + x * brick_width,
                            "y": Renderer.adjust_y(y, brick_height),
                            "text": text,
                        }
                    )
                if text_background:
                    ox, oy, w, h = undulate.skin.text_bbox(
                        self.ctx, "edge-text", text, self.engine, overload
                    )
                    x = overload.get("x")
                    y = overload.get("y")
                    ans += self.polygon(
                        [
                            Point(x + ox, y + oy),
                            Point(x + ox, y + oy + h),
                            Point(x + ox + w, y + oy + h),
                            Point(x + ox + w, y + oy),
                            Point(x + ox, y + oy),
                        ],
                        style_repr="edge-background",
                    )
                # add the text
                ans += self.text(**overload)
            return ans

        return "\n".join([__annotate__(a, viewport) for a in annotations])

    def wavelane_title(self, name: str, **kwargs) -> str:
        """
        Draw the title in front of a waveform

        Args:
            name (str): name of the waveform print alongside
            order (int): position from 0-4 of the title position along
                the y-axis. This property is important when overlaying signals

                    - 0   : middle of the wavelane height, is the default
                    - 1-4 : quarter from top to bottom of the wavelane
            brick_height (float): height a brick
        """
        extra = kwargs.get("extra")
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

    def _reduce_wavelane(self, name: str, wavelane: str, nodes: List[str], **kwargs):
        """
        Create a Brick by reading the symbols and needed parameters
        for each symbol.

        Args:
            name (str) : name of the wavelane
            wavelane (str) : list of symbol describing the signal
        Parameters:
            repeat (int): number of times the wavelane is repeated
        Returns:
            List[Brick]
        """
        repeat = kwargs.get("repeat", 1)
        # calculate total length of the wavelance
        TOTAL_LENGTH = len(wavelane) * int(repeat)
        # calculate parameters for each brick of a given wavelane
        needed_params = BrickFactory.get_parameters()
        for param in list(needed_params.keys()):
            if isinstance(kwargs.get(param), str):
                kwargs[param] = safe_eval(kwargs[param])
            params = param + "s" if param not in ["data", "analogue"] else param
            # for specific data attribute allow split of space separated string
            if isinstance(kwargs.get(param), str) and param == "data":
                kwargs[param] = kwargs.get(param).split(" ")
            # multiply singular value to create 1 value per brick
            if isinstance(kwargs.get(param), list):
                needed_params[params] = kwargs.get(param) * TOTAL_LENGTH
            else:
                needed_params[params] = [kwargs.get(param)] * TOTAL_LENGTH
            # select if available multiple values variant over repeat singular one
            if params in kwargs:
                if isinstance(kwargs[params], str):
                    kwargs[params] = safe_eval(kwargs[params])
                needed_params[params] = kwargs.get(params) or needed_params[params]
        # computed properties
        follow_data = False
        previous_symbol = " "
        _wavelane = []
        # ensure nodes and wavelane have the same size
        if len(nodes) < len(wavelane) * repeat:
            nodes.extend([None] * (len(wavelane) * repeat - len(nodes)))
        # initialize the waveform
        for i, b in enumerate(wavelane * repeat):
            brick_args = copy.deepcopy(kwargs)
            for param in BrickFactory.params.get(b, []):
                params = param + "s" if param not in ["data", "analogue"] else param
                default = BrickFactory.params.get(b, {}).get(param)
                if needed_params[params]:
                    brick_args[param] = needed_params[params].pop(0)
                else:
                    brick_args[param] = default
                if brick_args[param] is None:
                    brick_args[param] = default
            brick_args["follow_data"] = follow_data
            brick_args["is_first"] = i == 0
            brick_args["repeat"] = 1
            brick_args["name"] = name
            brick_args["node_name"] = nodes.pop(0)
            # generate the brick
            _wavelane.append(BrickFactory.create(b, **brick_args))
            log.debug(f"{name} {b} {_wavelane[-1]!r} {_wavelane[-1].get_last_y()}")
            follow_data = "data" in BrickFactory.tags[previous_symbol]
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
    def wavelane(
        self, name: str, wavelane: str, extra: str = "", y: float = 0, **kwargs
    ) -> str:
        """
        Draw the internal Dict[str, Any] representing a waveform inside a waveform group.

        the internal Dict[str, Any] is expected to have at least the following two keys:

        - name       : name of the waveform
        - wavelane   : string which describes the waveform

        Args:
            name (str): name of the waveform
            wavelane (str): string of symbols describing the waveform
            extra (str): extra information given to self.group()
            y (float): global y position of the wavelane in the drawing context
        """
        # options
        brick_width = kwargs.get("brick_width", 20) * kwargs.get("hscale", 1)
        gap_offset = kwargs.get("gap_offset", brick_width * 0.5)
        phase = kwargs.get("phase", 0.0) * brick_width
        # pre-process nodes
        nodes, *expended_names = kwargs.get("node", "").split(" ")
        nodes = [expended_names.pop(0) if node == "#" else node for node in nodes]

        # preprocess waveform to simplify it
        _wavelane = self._reduce_wavelane(name, wavelane, nodes, **kwargs)

        # generate waveform
        wave, pos = [], 0
        for brick in _wavelane:
            # prune the properties
            x = max(0, pos) - max(0, phase)
            if brick.symbol == "|":
                x = pos - brick_width + gap_offset - brick.slewing
            brick.args.update({"extra": self.translate(x, 0, dont_touch=True), "pos_x": x})
            # add style informations
            brick.args.update(style_in_kwargs(**kwargs))
            # generate the brick
            wave.append(BrickFactory.create(brick.symbol, **brick.args))
            # register node position
            NodeBank.register(
                brick.node_name, Point(x + brick.slewing / 2, y + brick.height / 2)
            )
            # create the new brick
            pos += wave[-1].width

        # rendering
        def _gen_wave():
            ans = []
            for brick in wave:
                ans.append(self.brick(brick.symbol, brick, **brick.args))
            return "".join(ans)

        def _gen():
            ans = self.wavelane_title(name, **kwargs) if name else ""
            ans += self.group(_gen_wave, name + "_wave", classes=["wave"])
            return ans

        # wrap the wavelane
        return self.group(
            _gen,
            name if name else "wavelane_%d_%d" % (_WAVEGROUP_COUNT, _WAVE_COUNT),
            extra=extra,
        )

    def ticks(self, width: int, height: int, step: float, **kwargs) -> str:
        """
        Generates the dotted vertical lines to ease reading of waveforms
        and their respective alignment

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
    def wavegroup(self, name: str, wavelanes, depth: int = 1, **kwargs) -> str:
        """
        Draw a group of waveforms

        Args:
            name (str) : name of the waveform group
            wavelanes (Dict[str, dict]): named waveforms composing the group
            depth (int) : depth of nested groups to represent hierarchy
        Parameters:
            config (Dict[str, Any]): config section of the input file
            brick_width (float): width of a brick, default is 20.0
            brick_height (float): height of a brick, default is 20.0
            width (float): image width
            height (float): image height
        """
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
        separation = config.get("separation", kwargs.get("separation", 0.25))
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

        if not isinstance(wavelanes, dict):
            return (offsety, "")

        def _gen(
            offset: Point,
            width: float,
            height: float,
            brick_width: float,
            brick_height: float,
        ) -> str:
            ans = ""
            # create a label and separator to identify groups of signals
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
                    offset.y + separation + brick_height * 0.9 - grp_font_size,
                    name,
                    style_repr="h%d" % depth,
                    **kwargs,
                )
                # add group separator
                if depth == 2:
                    ans += self.path(
                        [
                            Point(0, offset.y + brick_height),
                            Point(offset.x + width, offset.y + brick_height),
                        ],
                        style_repr="border ctx-y",
                        **kwargs,
                    )
                # some space for group separation if not the root
                offset.y += brick_height + separation
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
                    ans += self.wavelane(
                        wavetitle,
                        wave,
                        self.translate(offset.x, offset.y),
                        offset.y,
                        **args,
                    )
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
                            "offsetx": offset.x,
                            "offsety": offset.y,
                            "no_ticks": True,
                            "gap-offset": gap_offset,
                        }
                    )
                    dy, tmp = self.wavegroup(
                        wavetitle,
                        wavelanes[wavetitle],
                        depth + 1,
                        **args,
                    )
                    ans += tmp
                offset.y += dy
            # add ticks only for the principale group
            if not no_ticks:
                kw = {
                    "offsetx": offset.x,
                    "step": brick_width,
                    "width": width,
                    "height": height,
                    "phase": config.get("ticks_phase", 0),
                }
                ans = "%s\n%s" % (self.ticks(**kw), ans)
            return ans

        # room for displaying names
        start_y, offset = offsety, Point(offsetx, offsety)
        ans = self.group(
            lambda: _gen(offset, width, height, brick_width, brick_height), name
        )
        # finish the group with local annotations
        ans += self.annotate(
            wavelanes, viewport=(offset.x, 0, width, height), depth=depth, **kwargs
        )
        return (offset.y - start_y, ans)

    def size(self, wavelanes, depth: int = 1, **kwargs):
        """
        Pre-estimate the size of the image (duplicate of wavegroup without drawing)

        Args:
            name (str) : name of the waveform group
            wavelanes (Dict[str, dict]): named waveforms composing the group
            depth (int) : depth of nested groups to represent hierarchy
        Parameters:
            config (Dict[str, Any]): config section of the input file
            brick_width (float): width of a brick, default is 20.0
            brick_height (float): height of a brick, default is 20.0
            width (float): image width
            height (float): image height

        .. warning::

            Might be good to implement a parameter no_drawing in wavegroup
            and performs 2 passes to prevent possible discrepency
        """
        if not isinstance(wavelanes, dict):
            return (0, 0, 0, 0)
        # options for size of bricks
        config = wavelanes.get("config", {})
        vscale = config.get("vscale", 1.0)
        hscale = config.get("hscale", 1.0)
        brick_width = kwargs.get("brick_width", 40) * hscale
        brick_height = kwargs.get("brick_height", 20) * vscale
        separation = config.get("separation", kwargs.get("separation", 0.25))
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
                    len(a[-1]) if isinstance(a[-1], list) else 0 if a[-1] is None else 1
                    for a in _attr
                ]
                n = max(n, len(_n))
            else:
                n = max(n, 1)
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
                _, _, tw, _ = text_bbox(None, "title", wavetitle, None)
                keys.append(tw)
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
