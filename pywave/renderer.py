#!/usr/bin/env python3
# spell-checker: disable

"""
renderer.py declare the logic to render waveforms
into different format
"""

import re
import copy
import pywave
from .skin import style_in_kwargs
from math import atan2, cos, sin, floor
from itertools import count, accumulate, zip_longest

# Counter for unique id generation
#: counter of group of wave unique id
_WAVEGROUP_COUNT = 0
#: counter of wave unique id
_WAVE_COUNT = 0
# error message
ERROR_MSG = {
    "ANNOTATION_MISSING_PTS":
        "ERROR: For annotation check from/to are defined (float,float) or float supported only",
    "WRONG_WAVE_START":
        "ERROR: %s : cannot repeat None or '|', add a valid brick first"
}

ARROWS_PREFIX = "<*# "
ARROWS_SUFFIX = ">*# "

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

def arrow_angle(dy: float, dx:float) -> float:
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
    return 180*atan2(dy, dx)/3.14159

# TODO autoscale or scaling for analogue
# TODO add support of T curves in svg

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
    px, py, pt    =  0, 0, 'm'
    ans, ppx, ppy = [], 0, 0
    for t, x, y in vertices:
        # translate S into C
        if (t in ['s', 'S']) and (pt in ['s', 'S', 'c', 'C']):
            ans.append(('c' if t == 's' else 'C', px+(px-ppx), py+(py-ppy)))
            ans.append(('', x, y))
        # translate Q into C
        elif t in ['q', 'Q'] or (t in ['s', 'S'] and not pt in ['s', 'S', 'c', 'C']):
            ans.append(('c' if t in ['s', 'q'] else 'C', x, y))
            ans.append(('', x, y))
        else:
            ans.append((t, x, y))
        if t in ['m', 'M', 'l', 'L', 's', 'S', 'c', 'C', 'q', 'Q', 't', 'T']:
            pt = t
        px, py = x, y
        ppx, ppy = px, py
    return ans

class Renderer:
    """
    Abstract class of all renderer and define the parsing logic
    """

    _EDGE_REGEXP = r"([\w\.\_]+)\s*([~\|\/\-\>\<]+)\s*([\w\.\_]+)"
    _WAVE_TITLE  = ""
    _DATA_TEXT   = ""
    _GROUP_NAME  = ""
    _SYMBOL_TEMP = None

    def __init__(self):
        self.cr = None
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

    def untranslate(self):
        pass

    def brick(self, symbol: str, b: pywave.Brick, height: int = 20, **kwargs) -> str:
        """
        brick generate the symbol for a pywave.Brick element
        (collection of paths, splines, arrows, polygons, text)
        """
        ans, content = "", ""
        # display polygons (usually background)
        for _, poly in enumerate(b.polygons):
            content += self.polygon(poly[1:], style_repr=poly[0], **kwargs)
        # display path (for borders and edges)
        for _, path in enumerate(b.paths):
            content += self.path(path[1:], style_repr=path[0], **kwargs)
        # display arrows
        for _, arrow in enumerate(b.arrows):
            content += self.arrow(*arrow[1:], style_repr=arrow[0], **kwargs)
        # display borders or edges
        for i, spline in enumerate(b.splines):
            content += self.spline(spline[1:], style_repr=spline[0], **kwargs)
        # format text and display them
        for i, span in enumerate(b.texts):
            # get style of text
            a = copy.deepcopy(kwargs)
            a.update({"style_repr": span[0]})
            content += self.text(*span[1:], **a)
        # special function to apply at the end depending on the renderer
        if self._SYMBOL_TEMP:
            ans = self._SYMBOL_TEMP(symbol, content, **kwargs)
        return ans

    def __list_nodes__(self, wavelanes: dict, level: int=0, depth: int=0, **kwargs):
        """
        list of named nodes in the signal representation
        and calculate the coordinates

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
            list of nodes in a tuple(x, y, name)
        """
        brick_width  = kwargs.get("brick_width", 20)
        brick_height = kwargs.get("brick_height", 20)
        # Parameters for all wavelane
        excluded_sections = ["edges", "edge", "head", "config", "adjustements", "annotations"]
        first_row_of_group = wavelanes[next(iter(wavelanes))]
        nodes, _y = [], (level-1)*first_row_of_group.get("gap-offset", 0) if isinstance(first_row_of_group, dict) else 0
        for name, wavelane in wavelanes.items():
            # read nodes declaration
            if isinstance(wavelane, dict) and not name in excluded_sections:
                if "wave" in wavelane or Renderer.is_spacer(name):
                    if "node" in wavelane:
                        chain = wavelane["node"].split(' ')
                        # brick width of the wavelane
                        periods = [wavelane.get("period", 1)] * len(chain[0])
                        periods = self._get_or_eval("periods", periods, **wavelane)
                        if len(periods) < len(chain[0]):
                            periods = periods + [wavelane.get("period", 1)] * (len(chain[0])-len(periods))
                        width   = [brick_width * p for p in periods]
                        phase   = brick_width * wavelane.get("phase", 0)
                        slewing = wavelane.get("slewing", 3)
                        # calculate the x position
                        x = list(accumulate(width))
                        # parse the chain
                        ni, j = [], 0
                        for i, c in enumerate(chain[0]):
                            j = i if len(width) > i else -1
                            if c != '.':
                                ni.append((x[j]-width[j], width[j], c))
                        j = count(0)
                        # get identifier
                        nodes.extend(
                        [ (s[0] - phase + slewing * 0.5, _y, chain[1+next(j)]) if not s[2].isalpha()
                            else (s[0] - phase + slewing * 0.5, _y, s[2]) for s in ni]
                        )
                    _y += brick_height * (wavelane.get("vscale", 1) + 0.5)
                # it is a wavegroup
                else:
                    dy, n = self.__list_nodes__(wavelane, level, depth+1, **kwargs)
                    _y += brick_height
                    for node in n:
                        x, y, name = node
                        nodes.append((x, _y + y, name))
                    _y += dy
        if depth > 0:
            return (_y, nodes)
        return nodes

    def __gen_patterns__(prefixs: list, root: str, suffixs: list):
        """
        generate possible pattern prefixs/root/suffixs
        """
        for p in prefixs:
            for s in suffixs:
                pattern = "%s%s%S" % (p, root, s)
                yield pattern.strip()
        return None

    def annotations(self, wavelanes:dict, viewport:tuple, depth:int = 0, **kwargs):
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
        xmin, _, width, height = viewport
        # if not empty
        if not annotations and not edges_input:
            return ''
        # adjust y coordinate
        def adjust_y(y):
            return floor(y)*brick_height*1.5+(y-floor(y))*brick_height
        # list nodes and their name
        nodes = self.__list_nodes__(wavelanes, depth, **kwargs)
        # transform edges into annotations
        for ei in edges_input:
            match = re.match(Renderer._EDGE_REGEXP, ei)
            if not match is None:
                m = match.group()
                f, s, t = match.groups()
                txt = "" if len(m) == len(ei.strip()) else ei.strip()[len(m)+1:]
                annotations.append({
                    "shape": s,
                    "from": f,
                    "to": t,
                    "text": txt
                })
        # create annotations
        def __annotate__(a: dict):
            shape = a.get("shape", None)
            x     = a.get("x", 0)
            y     = a.get("y", 0)
            dx    = a.get("dx", 0)*brick_width
            dy    = adjust_y(a.get("dy", 0))
            start = a.get("from", None)
            end   = a.get("to", None)
            text  = a.get("text", "")
            ans   = ""
            # parse from to
            if start:
                if isinstance(start, str) and "," in start:
                    start = eval(start)
            if isinstance(start, tuple):
                x, y = start
                start = (x*brick_width, adjust_y(y))
            if end:
                if isinstance(end, str) and "," in end:
                    end = eval(end)
            if isinstance(end, tuple):
                x, y = end
                end = (x*brick_width, adjust_y(y))
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
            # add offset for delay of data and middle of brick vertical
            s = s[0]+xmin, s[1]+brick_height*0.5
            e = e[0]+xmin, e[1]+brick_height*0.5
            #if shape and shape[0] == '<':
            #    s = s[0]-3.5, s[1]
            #if shape and shape[-1] == '>':
            #    e = e[0]-3.5, e[1]
            # derivative of edges for arrows: by default ->
            start_dx, start_dy, end_dx, end_dy = s[0]-e[0], 0, e[0]-s[0], 0
            mx, my = (s[0] + e[0]) * 0.5, (s[1] + e[1]) * 0.5
            # draw shape
            overload = style_in_kwargs(**a)
            # hline
            if shape == "-":
                y_pos = adjust_y(y)
                x1 = xmin+start*brick_width if isinstance(start, (float, int)) else xmin
                x2 = xmin+end*brick_width if isinstance(end, (float, int)) else xmin+width
                c = a.get("color", (0, 0, 0, 255))
                pts = [("M", x1, y_pos), ("L", x2, y_pos)]
                ans = self.spline(pts, **a)
            # vline
            elif shape == "|":
                x = xmin+x*brick_width
                y1 = adjust_y(start) if isinstance(start, (float, int)) else 0
                y2 = adjust_y(end) if isinstance(end, (float, int)) else height
                c = a.get("color", (0, 0, 0, 255))
                pts = [("M", x, y1), ("L", x, y2)]
                ans = self.spline(pts, **a)
            # global time compression
            elif shape == "||":
                x = xmin+x*brick_width
                y1 = adjust_y(start) if isinstance(start, (float, int)) else 0
                y2 = adjust_y(end) if isinstance(end, (float, int)) else height
                pts_1 = [
                    ("M", x, y1),            # |
                    ("L", x, (y2+y1)/2-10),  # |
                    ("L", x-10, (y2+y1)/2),  # /
                    ("L", x, (y2+y1)/2+10),  # \
                    ("L", x, y2),       # |
                ]
                pts_2 = [
                    ("M", x+5, y1),            # |
                    ("L", x+5, (y2+y1)/2-10),  # |
                    ("L", x-4, (y2+y1)/2),     # /
                    ("L", x+5, (y2+y1)/2+10),  # \
                    ("L", x+5, y2),       # |
                ]
                poly = copy.deepcopy(pts_2)
                poly.extend(pts_1[::-1])
                ans = self.polygon([(i, j) for c, i, j in poly], style_repr="hide")
                ans+= self.spline(pts_1, style_repr="big_gap")
                ans+= self.spline(pts_2, style_repr="big_gap")
            # edges
            elif shape in Renderer.__gen_patterns__(ARROWS_PREFIX, "~", ARROWS_SUFFIX):
                ans = self.spline([('M', s[0], s[1]), ('C', s[0]*0.1+e[0]*0.9, s[1]), ('', s[0]*0.9+e[0]*0.1, e[1]), ('', e[0], e[1])], is_edge=True, style_repr="edge", **overload)
            elif shape in Renderer.__gen_patterns__(ARROWS_PREFIX, "-~", ARROWS_SUFFIX):
                ans = self.spline([('M', s[0], s[1]), ('C', e[0], s[1]), ('', e[0], e[1]), ('', e[0], e[1])], is_edge=True, style_repr="edge", **overload)
                start_dx, start_dy, end_dx, end_dy = s[0]-e[0], 0, 0, e[1]-s[1]
            elif shape in Renderer.__gen_patterns__(ARROWS_PREFIX, "~-", ARROWS_SUFFIX):
                ans = self.spline([('M', s[0], s[1]), ('C', s[0], s[1]), ('', s[0], e[1]), ('', e[0], e[1])], is_edge=True, style_repr="edge", **overload)
                start_dx, start_dy, end_dx, end_dy = 0, s[1]-e[1], e[0]-s[0], 0
            elif shape in Renderer.__gen_patterns__(ARROWS_PREFIX, "-", ARROWS_SUFFIX):
                ans = self.spline([('M', s[0], s[1]), ('L', e[0], e[1])], is_edge=True, style_repr="edge", **overload)
                start_dx, start_dy, end_dx, end_dy = s[0]-e[0], s[1]-e[1], e[0]-s[0], e[1]-s[1]
            elif shape in Renderer.__gen_patterns__(ARROWS_PREFIX, "-|", ARROWS_SUFFIX):
                ans = self.spline([('M', s[0], s[1]), ('L', e[0], s[1]), ('', e[0], e[1])], is_edge=True, style_repr="edge", **overload)
                start_dx, start_dy, end_dx, end_dy = s[0]-e[0], 0, 0, e[1]-s[1]
                mx, my = e[0], s[1]
            elif shape in Renderer.__gen_patterns__(ARROWS_PREFIX, "|-", ARROWS_SUFFIX):
                ans = self.spline([('M', s[0], s[1]), ('L', s[0], e[1]), ('', e[0], e[1])], is_edge=True, style_repr="edge", **overload)
                start_dx, start_dy, end_dx, end_dy = 0, s[1]-e[1], e[0]-s[0], 0
                mx, my = s[0], e[1]
            elif shape in Renderer.__gen_patterns__(ARROWS_PREFIX, "-|-", ARROWS_SUFFIX):
                ans = self.spline([('M', s[0], s[1]), ('L', mx, s[1]), ('', mx, e[1]), ('', e[0], e[1])], is_edge=True, style_repr="edge", **overload)
                start_dx, start_dy, end_dx, end_dy = s[0]-mx, 0, e[0]-mx, 0
                mx, my = mx, e[1]
            # add arrows for edges
            if not shape is None:
                # marker start
                if shape[0] == '<':
                    th = arrow_angle(start_dy, start_dx)
                    ans += self.arrow(0, 0, th,
                            extra=self.translate(s[0]-3*cos(th*3.14159/180), s[1]-3*sin(th*3.14159/180),
                            no_acc=True),
                        dy=brick_height,
                        is_edge=True,
                        style_repr="edge-arrow", **overload)
                elif shape[0] == '*':
                    pass
                elif shape[0] == '#':
                    pass
                # marker end
                if shape[-1] == '>':
                    th = arrow_angle(end_dy, end_dx)
                    ans += self.arrow(0, 0, th,
                            extra=self.translate(e[0]-3*cos(th*3.14159/180), e[1]-3*sin(th*3.14159/180),
                            no_acc=True),
                        dy=brick_height,
                        is_edge=True,
                        style_repr="edge-arrow", **overload)
                elif shape[0] == '*':
                    pass
                elif shape[0] == '#':
                    pass
                # add text is not empty
                if text:
                    # add white background for the text
                    a.update({"style_repr": "edge-text", "x": mx+dx, "y": my+dy})
                    ox, oy, w, h = pywave.text_bbox(self.cr, "edge-text", text, self.engine, overload)
                    ans += self.polygon([
                        (0, 0),
                        (0, 0+h),
                        (0+w, 0+h),
                        (0+w, 0),
                        (0, 0)], extra=self.translate(a.get("x")+ox, a.get("y")+oy, no_acc=True), style_repr="edge-background")
                    # add the text
                    ans += self.text(**a)
            elif text:
                overload = style_in_kwargs(**a)
                # add white background for the text
                a.update({"style_repr": "edge-text", "x": xmin+x*brick_width, "y": adjust_y(y)})
                ox, oy, w, h = pywave.text_bbox(self.cr, "edge-text", text, self.engine, overload)
                ans += self.polygon([
                    (0, 0),
                    (0, 0+h),
                    (0+w, 0+h),
                    (0+w, 0),
                    (0, 0)], extra=self.translate(a.get("x")+ox, a.get("y")+oy, no_acc=True), style_repr="edge-background")
                # add the text
                ans += self.text(**a)
            return ans
        return '\n'.join([__annotate__(a) for a in annotations])

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
        extra        = kwargs.get("extra", "")
        order        = kwargs.get("order", 0)
        brick_height = kwargs.get("brick_height", 20) * kwargs.get("vscale", 1)
        kw           = {k: kwargs.get(k) for k in kwargs.keys() if k in ["fill", "stroke", "font", "font-weight"]}
        if "spacer" in name or not name.strip():
            return ""
        if order == 0:
            y = brick_height / 2
        else:
            y = brick_height / 4 * order - brick_height / 8
        return self.text(-10, y, name, extra=self._WAVE_TITLE, offset=extra, style_repr="title", **kw)

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
            Analog-Only
                equation            (float or str)
            Register-Only
                attr                (str)
                type                (str)
                pos                 (int)

        """
        # calculate total length of the wavelance
        repeat      = kwargs.get("repeat", 1)
        TOTAL_LENGTH= len(wavelane) * int(repeat)
        # Parameters for all wavelane
        periods     = [kwargs.get("period", 1)] * TOTAL_LENGTH
        duty_cycles = [kwargs.get("duty_cycle", 0.5)] * TOTAL_LENGTH
        phases      = [kwargs.get("phase", 0)]+[0] * (TOTAL_LENGTH-1)
        slewings    = [kwargs.get("slewing", 3)] * TOTAL_LENGTH
        # Parameters specific for each bricks
        periods     = self._get_or_eval("periods", periods, **kwargs)
        duty_cycles = self._get_or_eval("duty_cycles", duty_cycles, **kwargs)
        analogue    = self._get_or_eval("analogue", [], **kwargs)
        data        = kwargs.get("data", [])
        attributes  = kwargs.get("attr", [])
        reg_pos     = kwargs.get("regpos", [])
        reg_types   = kwargs.get("types", [])
        # computed properties
        ign_trans   = []
        follows_data = []
        da, ana, att, rp, tr = [], [], [], [], []
        # in case a string is given reformat it as a list
        if isinstance(data, str):
            data = data.split(' ')
        if isinstance(reg_pos, str):
            reg_pos = reg_pos.split(' ')
        # prepare output
        _wavelane, prev_brick = [], None
        last_valid_brick, last_valid_brick_idx = None, 0
        last_valid_symbol = ' '
        # look for repetition '.' and for '|' time compression
        for i, b in enumerate(wavelane * repeat):
            brick = pywave.BRICKS.from_char(b)
            is_duplicate = False
            new_brick = 0
            # check validity of the first brick
            if  i == 0 and brick == pywave.BRICKS.repeat and \
                prev_brick in [None, pywave.BRICKS.gap]:
                raise Exception(ERROR_MSG["WRONG_WAVE_START"] % name)
            # increment last symbol repetition number
            if pywave.BRICKS.is_repeating_symbol(brick):
                # always repeat a clock signal and after gap repeat the last valid symbol
                if pywave.BRICKS.is_clock(last_valid_brick) or prev_brick == pywave.BRICKS.gap:
                    _wavelane.append((last_valid_brick, 1, last_valid_symbol))
                    new_brick += 1
                    is_duplicate = True
                # extend the width of other symbols
                else:
                    br, num, c = _wavelane[-1]
                    _wavelane[-1] = (br, num + 1, c)
                # a time compression overlay the previous one
                if brick == pywave.BRICKS.gap:
                    _wavelane.append((brick, 1, b))
                    new_brick += 1
            # merge all successive x
            elif brick == prev_brick and brick in [pywave.BRICKS.x, pywave.BRICKS.X]:
                br, num, c = _wavelane[-1]
                _wavelane[-1] = (br, num + 1, c)
            # add the new symbol
            else:
                _wavelane.append((brick, 1, b))
                new_brick += 1
            # update parameters
            if new_brick > 0:
                # pre-processing
                ign_trans.append(pywave.BRICKS.ignore_transition(last_valid_brick, brick))
                if last_valid_brick == pywave.BRICKS.data:
                    follows_data.append(True)
                else:
                    follows_data.append(False)
                # get data if needed
                da.append(
                    data[0] if data and pywave.BRICKS.need_data(brick) else \
                    da[-2] if is_duplicate and len(da) > 2 else None)
                # get equation if needed
                ana.append(
                    analogue[0] if analogue and pywave.BRICKS.need_equation(brick) else
                    ana[-2] if is_duplicate and len(ana) > 2 else None)
                # get attribute if needed
                att.append(
                    attributes[0] if attributes and pywave.BRICKS.need_attribute(brick) else
                    att[-2] if is_duplicate and len(att) > 2 else None)
                # get position if needed
                rp.append(
                    reg_pos[0] if reg_pos and pywave.BRICKS.need_position(brick) else
                    rp[-2] if is_duplicate and len(rp) > 2 else None)
                # remove values consummed
                if pywave.BRICKS.need_data(brick):
                    data = data[1:]
                if pywave.BRICKS.need_equation(brick):
                    analogue = analogue[1:]
                if pywave.BRICKS.need_attribute(brick):
                    attributes = attributes[1:]
                if pywave.BRICKS.need_position(brick):
                    reg_pos = reg_pos[1:]
                #print(brick, last_valid_brick, is_duplicate,
                #      data, last_valid_brick_idx, sep='\t')
                for k in range(1, new_brick):
                    periods.insert(last_valid_brick_idx,
                            None if not is_duplicate else periods[last_valid_brick_idx])
                    duty_cycles.insert(last_valid_brick_idx,
                            None if not is_duplicate else duty_cycles[last_valid_brick_idx])
                    slewings.insert(last_valid_brick_idx,
                            None if not is_duplicate else slewings[last_valid_brick_idx])
                #print(new_brick, last_valid_brick_idx, data)
            # update last valid brick
            if not pywave.BRICKS.is_repeating_symbol(brick):
                last_valid_brick = brick
                last_valid_brick_idx += 1
                last_valid_symbol = b
            # update last brick
            prev_brick = brick
        # distribute parameters
        param_order = ["period", "duty_cycle", "equation", "data", "attribute",
                       "reg_pos", "reg_type", "phase", "slewing", "ignore_transition",
                       "follow_data"]
        params = zip_longest(periods, duty_cycles, ana, da, att,
                     rp, reg_types, phases, slewings, ign_trans,
                     follows_data)
        kws = [dict(zip(param_order, t)) for t in params]
        return list(zip(_wavelane, kws))

    def _get_or_eval(self, name: str, default, **kwargs):
        """
        if is a str, evaluate the code or get it in a standard way
        """
        if isinstance(kwargs.get(name), str):
            return eval(kwargs.get(name, ""))
        return kwargs.get(name, default)

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
        brick_width  = kwargs.get("brick_width", 20) * kwargs.get("hscale", 1)
        brick_height = kwargs.get("brick_height", 20) * kwargs.get("vscale", 1)
        gap_offset   = kwargs.get("gap_offset", brick_width*0.5)
        order        = kwargs.get("order", 0)
        # look for repetition '.'
        _wavelane = self._reduce_wavelane(name, wavelane, **kwargs)
        # util functions
        def __select_style(b, **k):
            reg_type = k.get("reg_type", None)
            if b is None:
                return 's2'
            if b.isdigit() and int(b, 10) > 1:
                return 's' + b
            if reg_type:
                return 's' + str(reg_type)
            return 's2'
        def __new_brick_width(idx, b, repeat, pos, **k):
            phase = k.get("phase", 0)
            period = k.get("period", 1)
            slewing = k.get("slewing", 3)
            # set minimum width
            pmul = max(period, 0 if b in "csa" else slewing*2/brick_width)
            if b == '|':
                return 0
            if idx == 0:
                return pmul*brick_width*(repeat-phase)
            elif idx == -1:
                return max(pmul*brick_width*(repeat+phase), kwargs.get("width", 0)-pos)
            return pmul*repeat*brick_width
        # generate waveform
        wave, pos = [], 0
        last_valid_brick = None
        last_valid_index = 0
        for i, w in enumerate(_wavelane):
            br, kw = w
            br, repeat, symbol = br
            # prune the properties
            kw = {k: kw.get(k) for k in kw if not kw.get(k) is None}
            new_width = __new_brick_width(i if not i == len(_wavelane)-1 else -1, symbol, repeat, pos, **kw)
            x = max(0, pos)
            if br == pywave.BRICKS.gap:
                x = pos-brick_width+gap_offset-kw.get("slewing", 3)
            kw.update({
                "style":        __select_style(symbol, **kw),
                "last_y":       brick_height if last_valid_brick is None else last_valid_brick.get_last_y(),
                "is_first":     i == 0,
                "brick_width":  new_width,
                "brick_height": brick_height,
                "follow_X":     isinstance(last_valid_brick, pywave.digital.Garbage),
                "extra":        self.translate(x, 0, dont_touch=True)
            })
            # add style informations
            kw.update(style_in_kwargs(**kwargs))
            # create the new brick
            pos += new_width
            # generate the brick
            brick = pywave.generate_brick(br, **kw)
            wave.append((symbol, brick, kw))
            if not pywave.BRICKS.is_repeating_symbol(br):
                last_valid_brick = brick
        # post-process
        last_valid_index = 0
        for i, w in enumerate(wave):
            symbol, brick, kw = w
            ps, pb, pkw = wave[i-1]
            ns, nb, nkw = wave[last_valid_index]
            # adjust transistion from data to X
            if ns in "=23456789" and symbol in "X":
                nkw.update({"brick_width": nkw.get("brick_width")+nkw.get("slewing")});
                nb.__init__(ns in "xX", **nkw)
            # define how to connect two data block together
            def __update_data_or_garbage():
                kw.update({"ignore_start_transition": True, "hide_data": True});
                nkw.update({"ignore_end_transition": True});
                brick.__init__(symbol in "xX", **kw)
                nb.__init__(ns in "xX", **nkw)
            # check conditions to apply
            if i > 0 and ns == symbol:
                # two consecutive data bricks with same value
                if symbol in "=23456789xX":
                    txt1, txt2 = nkw.get("data", "").strip(), kw.get("data", "").strip()
                    if txt1 == txt2:
                        __update_data_or_garbage()
                # brick before and after a gap of the same type
                elif brick.ignore_transition or isinstance(pb, pywave.digital.Gap):
                    # when it is data or unknown data
                    if symbol in "=23456789xX":
                        txt1, txt2 = nkw.get("data", "").strip(), kw.get("data", "").strip()
                        if txt1 == txt2:
                            __update_data_or_garbage()
                    # arbitrary other brick
                    else:
                        fy, ly = brick.get_first_y(), nb.get_last_y()
                        dy = ly - fy
                        # alter current brick end
                        nb.alter_end(0, fy)
                        # alter next brick start
                        brick.alter_start(0, fy)
                        # update the bricks
                        wave[i] = (symbol, brick, kw)
                        wave[last_valid_index] = (ns, nb, nkw)
            # arbitrary other brick
            elif i > 0 and brick.ignore_transition:
                fy, ly = brick.get_first_y(), nb.get_last_y()
                dy = ly - fy
                # alter current brick end
                nb.alter_end(0, fy)
                # alter next brick start
                brick.alter_start(0, fy)
                # update the bricks
                wave[i] = (symbol, brick, kw)
                wave[last_valid_index] = (ns, nb, nkw)
            if not pywave.BRICKS.is_repeating_symbol(symbol):
                last_valid_index = i
        # rendering
        def _gen():
            ans = self.wavelane_title(name, **kwargs) if name else ""
            pos = 0
            for i, w in enumerate(wave):
                s, b, kw = w
                ans += self.brick(s, b, brick_height, **kw)
            return ans
        # wrap the wavelane
        return self.group(
            _gen,
            name if name else "wavelane_%d_%d" % (_WAVEGROUP_COUNT, _WAVE_COUNT),
            extra=extra
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
        phase   = kwargs.get("phase", 0)
        def _gen():
            ans = ""
            for k in range(0, int(width/step)):
                x = step * k
                ans += self.path(
                    [(x, 0), (x, height-offsety)],
                    style_repr="tick",
                    extra="",
                    **kwargs)
            return ans
        return self.group(
        _gen,
        "ticks_%d" % _WAVEGROUP_COUNT,
        extra=self.translate(offsetx + phase * width, 0))

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
        _default_offset_x = [len(s)+1 for s in wavelanes.keys() if not (Renderer.is_spacer(s) or s in ["edge", "adjustment"])]
        # options
        offsetx      = kwargs.get("offsetx", max(_default_offset_x, default=0)*9)
        offsety      = kwargs.get("offsety", 0)
        translate    = kwargs.get("translate", False)
        brick_width  = kwargs.get("brick_width", 40)
        brick_height = kwargs.get("brick_height", 20)
        width        = kwargs.get("width", 0)
        height       = kwargs.get("height", 0)
        config       = wavelanes.get("config", {})
        no_ticks     = config.get("no_ticks", depth > 1)
        gap_offset   = config.get("gap-offset", brick_width * 0.5);
        def _gen(offset, width, height, brick_width, brick_height):
            ox, oy, dy = offset[0], offset[1], 0
            # some space for group separation
            dy = 20 if depth > 1 else 0
            oy += dy
            if translate:
                self.translate(ox if translate and depth == 1 else 0, dy)
            # return value is ans
            if depth > 1:
                # add group name
                ans = self.text(0, oy-16, name, style_repr="h%d" % depth, extra=self._GROUP_NAME, **kwargs)
                # add group separator
                if depth == 2:
                    ans += self.path([(0, dy-6), (width+ox, dy-6)], style_repr="border ctx-y", **kwargs)
            else:
                ans = ""
            # look through waveforms data
            for _, wavetitle in enumerate(wavelanes.keys()):
                # signal in a dict
                if isinstance(wavelanes[wavetitle], dict):
                    # waveform
                    if "wave" in wavelanes[wavetitle]:
                        wave, args = wavelanes[wavetitle]["wave"], wavelanes[wavetitle]
                        args.update(**kwargs)
                        args.update({"gap-offset": gap_offset})
                        overlay = args.get("overlay", False)
                        ans += self.wavelane(
                            wavetitle,
                            wave,
                            "" if translate else self.translate(ox, oy),
                            **args
                        )
                        l = len(wave)
                        if not overlay:
                            dy = brick_height * (wavelanes[wavetitle].get("vscale", 1) + 0.5)
                        else:
                            dy = 0
                        width = l * brick_width if l * brick_width > width else width
                    # spacer or only for label nodes
                    elif Renderer.is_spacer(wavetitle) or "node" in wavelanes[wavetitle]:
                        dy = brick_height * (wavelanes[wavetitle].get("vscale", 1) + 0.5)
                    # named group
                    elif not wavetitle in ["head", "foot", "config", "edges", "annotations"]:
                        args = copy.deepcopy(kwargs)
                        args.update({"offsetx": ox, "offsety": 0,
                                     "no_ticks": True, "gap-offset": gap_offset})
                        dy, tmp = self.wavegroup(
                            wavetitle,
                            wavelanes[wavetitle],
                            "" if translate else self.translate(0, oy, dont_touch=True),
                            depth+1,
                            **args
                        )
                        ans += tmp
                    oy += dy
                    if translate:
                        self.translate(0, dy)
                # extra config
                else:
                    pass
            # add ticks only for the principale group
            if not no_ticks:
                kw = {
                    "offsetx": ox,
                    "step": brick_width,
                    "width": width,
                    "height": height,
                    "phase": config.get("ticks_phase", 0)
                }
                ans = "%s\n%s" % (self.ticks(**kw), ans)
            offset[0], offset[1] = ox, oy
            return ans
        # a useful signal is in a dict
        if isinstance(wavelanes, dict):
            # room for displaying names
            offset = [offsetx, offsety]
            ans = self.group(lambda: _gen(offset, width, height, brick_width, brick_height), name, extra=extra)
            offsetx, offsety = offset[0], offset[1]
            # finish the group
            ans += self.annotations(wavelanes, viewport=(offsetx, 0, width, height), depth=depth, **kwargs)
            return (offsety, ans)
        # unknown options
        else:
            raise Exception("Unkown wavelane type or option")
        return (0, "")

    def size(self, wavelanes, brick_width: int = 20, brick_height: int = 28, depth: int = 1):
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
        if isinstance(wavelanes, dict):
            x, y, n, keys = [0], 0, 0, [0]
            for wavetitle in wavelanes.keys():
                if isinstance(wavelanes[wavetitle], dict):
                    # add some extra for attr in registers
                    _attr = wavelanes[wavetitle].get("attr", [(0, None)] )
                    if isinstance(_attr, list):
                        _n = [len(_a[1]) for _a in _attr if not _a[1] is None and isinstance(_a[1], list)]
                        n += max(_n) if _n else 0
                    # handle a wavelane
                    if "wave" in wavelanes[wavetitle]:
                        # estimate length of the wavelane
                        if not "periods" in wavelanes[wavetitle]:
                            _l = len(wavelanes[wavetitle]["wave"])
                        else:
                            periods = self._get_or_eval("periods", [], **wavelanes[wavetitle])
                            _l = sum(periods)
                        _l *= brick_width
                        _l *= wavelanes[wavetitle].get("repeat", 1)
                        _l *= wavelanes[wavetitle].get("period", 1)
                        x.append(_l)
                        # estimate height
                        if not wavelanes[wavetitle].get("overlay", False):
                            y += brick_height * (wavelanes[wavetitle].get("vscale", 1) + 0.5)
                        keys.append(len(wavetitle))
                    # if it is only spacers allocate space
                    elif Renderer.is_spacer(wavetitle) or "node" in wavelanes[wavetitle]:
                        y += brick_height * 1.5
                    # otherwise it is a new wavegroup
                    elif not wavetitle in ["head", "foot", "config", "edges", "annotations"]:
                        y += 20
                        lkeys, _x, _y, _n = self.size(wavelanes[wavetitle], brick_width, brick_height, depth+1)
                        x.append(_x)
                        y += _y
                        n += _n
                        keys.append(lkeys)
                    # or an old wavegroup
                    elif isinstance(wavelanes[wavetitle], list):
                        if len(wavelanes[wavetitle]) > 0 and \
                            isinstance(wavelanes[wavetitle][0], dict) and \
                            "wave" in wavelanes[wavetitle][0]:
                            y += 20
                            lkeys, _x, _y, _n = self.size(wavelanes[wavetitle], brick_width, brick_height, depth+1)
                            x.append(_x)
                            y += _y
                            n += _n
                            keys.append(lkeys)
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
