#!/usr/bin/env python3

"""
This define the style of the drawing
it follows the principle of the css but accept only a subset:
font: size, style, variant, weight, stretch, align, family
fill: color, opacity
stroke: color, width, opacity, linecap, linejoin, mitterlimit, dasharray, opacity

colors should always be in rgba with value from 0—255
"""
from enum import Enum

class Engine(Enum):
    SVG = 0
    EPS = 1
    CAIRO = 2

class SizeUnit(Enum):
    EM = 16
    PX = 1
    PT = 1.333

class LineCap(Enum):
    BUTT = 0
    ROUND = 1
    SQUARE = 2

class LineJoin(Enum):
    MITER = 0
    ROUND = 1
    BEVEL = 2

class TextAlign(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    JUSTIFY = 3

# style definition for cairo renderer
DEFAULT_STYLE = {
    "title": {
        "fill": (0, 65, 196, 255),
        "font-weight": 500,
        "font-size": (0.7, SizeUnit.EM),
        "font-family": "fira mono",
        "text-align": TextAlign.RIGHT,
        "text-anchor": "end",
        "dominant-baseline": "middle",
        "alignment-baseline": "central"
    },
    "text": {
        "fill": (0, 0, 0, 255),
        "font-size": (0.9, SizeUnit.EM),
        "font-style": "normal",
        "font-variant": "normal",
        "font-weight": 500,
        "font-stretch": "normal",
        "text-align": TextAlign.CENTER,
        "font-family": "fira mono",
    },
    "attr": {
        "fill": (0, 0, 0, 255),
        "font-size": (9, SizeUnit.PX),
        "font-style": "normal",
        "font-variant": "normal",
        "font-weight": 200,
        "font-stretch": "normal",
        "text-align": TextAlign.CENTER,
        "font-family": "fira mono",
        "text-anchor": "middle",
        "dominant-baseline": "middle",
        "alignment-baseline": "central"
    },
    "path": {
        "fill": None,
        "stroke": (0, 0, 0, 255),
        "stroke-width": 1,
        "stroke-linecap": LineCap.ROUND,
        "stroke-linejoin": LineJoin.MITER,
        "stroke-miterlimit": 4,
        "stroke-dasharray": None,
    },
    "stripe": {
        "fill": None,
        "stroke": (0, 0, 0, 255),
        "stroke-width": 0.5,
        "stroke-linecap": LineCap.ROUND,
        "stroke-linejoin": LineJoin.MITER,
        "stroke-miterlimit": 4,
        "stroke-dasharray": None,
    },
    "data": {
        "fill": (0, 0, 0, 255),
        "font-size": (0.4, SizeUnit.EM),
        "font-style": "normal",
        "font-variant": "normal",
        "font-weight": 500,
        "font-stretch": "normal",
        "text-align": TextAlign.CENTER,
        "font-family": "fira mono",
        "text-anchor": "middle",
        "dominant-baseline": "middle",
        "alignment-baseline": "central"
    },
    "arrow": {
        "fill": (0, 0, 0, 255),
        "stroke": None
    },
    "hide": {
        "fill": (255, 255, 255, 255),
        "stroke": (255, 255, 255, 255),
        "stroke-width": 2
    },
    "hash": {
        "fill": (200, 200, 200, 255)
    },
    "s2-polygon": {"fill": (0, 0, 0, 0), "stroke": None},
    "s3-polygon": {"fill": (255, 255, 176, 255), "stroke": None},
    "s4-polygon": {"fill": (255, 224, 185, 255), "stroke": None},
    "s5-polygon": {"fill": (185, 224, 255, 255), "stroke": None},
    "tick": {
        "stroke": (136, 136, 136, 255),
        "stroke-width": 0.5,
        "stroke-dasharray": [1, 3],
    },
    "edge": {
        "fill": None,
        "stroke": (0, 0, 255, 255),
        "stroke-width": 1
    },
    "edge-arrow": {
        "fill": (0, 0, 255, 255),
        "stroke": None,
        "overflow": "visible",
    },
    "edge-text": {
        "font-family": "fira mono",
        "font-size": (0.625, SizeUnit.EM),
        "fill": (0, 0, 0, 255),
        "filter": "#solid",
        "transform": "translate(0, 2.5px)",
        "text-anchor": "middle",
    },
    "edge-background": {
        "fill": (255, 255, 255, 255),
        "stroke": (255, 255, 255, 255),
        "stroke-width": 2
    },
    "border": {"stroke-width": 1.25, "stroke": (0, 0, 0, 255)},
    "h1": {
        "fill": (0, 0, 0, 255),
        "font-size": (18.31/1.2, SizeUnit.PX),
        "font-weight": "bold",
        "font-family": "fira mono",
        "text-align": TextAlign.LEFT,
        "dominant-baseline": "middle",
    },
    "h2": {
        "fill": (0, 0, 0, 255),
        "font-size": (14.65/1.2, SizeUnit.PX),
        "font-weight": "bold",
        "font-family": "fira mono",
        "text-align": TextAlign.LEFT,
        "dominant-baseline": "middle",
    },
    "h3": {
        "fill": (0, 0, 0, 255),
        "font-size": (11.72/1.2, SizeUnit.PX),
        "font-weight": "bold",
        "font-family": "fira mono",
        "text-align": TextAlign.LEFT,
        "dominant-baseline": "middle",
    },
    "h4": {
        "fill": (0, 0, 0, 255),
        "font-size": (9.38/1.2, SizeUnit.PX),
        "font-weight": "bold",
        "font-family": "fira mono",
        "text-align": TextAlign.LEFT,
        "dominant-baseline": "middle",
    },
    "h5": {
        "fill": (0, 0, 0, 255),
        "font-size": (7.5/1.2, SizeUnit.PX),
        "font-weight": "bold",
        "font-family": "fira mono",
        "text-align": TextAlign.LEFT,
        "dominant-baseline": "middle",
    },
    "h6": {
        "fill": (0, 0, 0, 255),
        "font-size": (6/1.2, SizeUnit.PX),
        "font-weight": "bold",
        "font-family": "fira mono",
        "text-align": TextAlign.LEFT,
        "dominant-baseline": "middle",
    },
}

DEFINITION = """
<defs>
    <pattern id="diagonalHatch" width="5" height="5" patternTransform="rotate(45 0 0)" patternUnits="userSpaceOnUse">
        <line x1="0" y1="0" x2="0" y2="5" style="stroke:black; stroke-width:1" />
    </pattern>
    <marker id="arrow" viewBox="0 0 10 10" refX="10" refY="5"
        markerWidth="7" markerHeight="7" markerUnits="userSpaceOnUse"
        orient="auto-start-reverse" style="fill:#00F;">
      <path d="M 0 0 L 10 5 L 0 10 z" />
    </marker>
    <filter x="0" y="0" width="1" height="1" id="solid">
      <feFlood flood-color="white"/>
      <feComposite in="SourceGraphic"/>
    </filter>
</defs>
"""

try:
    import cairo
except ImportError:
    pass
else:

    def apply_cairo_style(context, name: str, overload: dict):
        """
        read the style and apply via cairo functions
        """
        style = get_style(name)
        apply_cairo_font(context, style, overload)
        apply_cairo_fill(context, style, overload)
        apply_cairo_stroke(context, style, overload)

    def apply_cairo_fill(context, style: dict, overload: dict):
        """
        set the fill color found in the style
        """
        style = dict(style)
        style.update(overload)
        # color
        t = style.get("fill", None)
        if not t is None:
            r, g, b, a = t
            context.set_source_rgba(r / 255, g / 255, b / 255, a / 255)

    def apply_cairo_stroke(context, style: dict, overload: dict):
        """
        support width, color, linecap, linejoin, dash
        """
        style = dict(style)
        style.update(overload)
        # color
        t = style.get("stroke", None)
        if not t is None:
            r, g, b, a = t
            context.set_source_rgba(r / 255, g / 255, b / 255, a / 255)
        # width
        w = style.get("stroke-width", 1.0)
        if not w is None:
            context.set_line_width(w)
        # line cap
        lc = style.get("stroke-linecap", LineCap.ROUND)
        if lc == LineCap.SQUARE:
            context.set_line_cap(cairo.LINE_CAP_SQUARE)
        elif lc == LineCap.BUTT:
            context.set_line_cap(cairo.LINE_CAP_BUTT)
        else:
            context.set_line_cap(cairo.LINE_CAP_ROUND)
        # line join
        lj = style.get("stroke-linejoin", LineJoin.MITER)
        if lj == LineJoin.BEVEL:
            context.set_line_join(cairo.LINE_JOIN_BEVEL)
        elif lj == LineJoin.ROUND:
            context.set_line_join(cairo.LINE_JOIN_ROUND)
        else:
            context.set_line_join(cairo.LINE_JOIN_MITER)
        # dash array
        da = style.get("stroke-dasharray", [])
        of = style.get("stroke-dasharray-offset", 0)
        if of is None:
            of = 0
        if da:
            context.set_dash(da, of)

    def cairo_text_align(context, style: dict, text: str):
        """
        offset calculation for text alignment
        """
        ta = style.get("text-align", TextAlign.CENTER)
        ba = style.get("dominant-baseline", "middle")
        # get text width
        ascent, descent, _height, max_x_advance, max_y_advance = context.font_extents()
        xbearing, ybearing, width, height, xadvance, yadvance = context.text_extents(text)
        # apply style
        dy = descent/2+height/4 if ba == "middle" else 0
        if ta == TextAlign.LEFT:
            return (0,-dy)
        if ta == TextAlign.RIGHT:
            return (width,-dy)
        return (width / 2, -dy)

    def cairo_text_bbox(context, style: dict, text: str):
        """
        return size of the text for a given font
        """
        ta = style.get("text-align", TextAlign.CENTER)
        # get text width
        ascent, descent, _height, max_x_advance, max_y_advance = context.font_extents()
        xbearing, ybearing, width, height, xadvance, yadvance = context.text_extents(text)
        if ta == TextAlign.LEFT:
            return (0, -height/2, width, _height)
        elif ta == TextAlign.RIGHT:
            return (-width, -height/2, width, _height)
        return (-width / 2, -descent-height/2, width, _height)

    def apply_cairo_font(context, style: dict, overload: dict):
        """
        get font information from the style and apply
        support font family, bold, italic, normal, size
        """
        style = dict(style)
        style.update(overload)
        # font slant
        font_style = style.get("font-style", "")
        if "it" in font_style:
            font_style = cairo.FONT_SLANT_ITALIC
        elif "ob" in font_style:
            font_style = cairo.FONT_SLANT_OBLIQUE
        else:
            font_style = cairo.FONT_SLANT_NORMAL
        # normal or bold
        w = style.get("font-weight", 200)
        if isinstance(w, str) and "bold" in w:
            font_weight = cairo.FONT_WEIGHT_BOLD
        elif isinstance(w, int) and w > 400:
            font_weight = cairo.FONT_WEIGHT_BOLD
        else:
            font_weight = cairo.FONT_WEIGHT_NORMAL
        # fetch font family
        font_family = style.get("font-family", None)
        if not font_family is None and isinstance(font_family, str):
            context.select_font_face(font_family, font_style, font_weight)
        # font size
        font_size = style.get("font-size", None)
        if not font_size is None:
            s, u = font_size
            context.set_font_size(s * u.value)


def apply_style(context, name: str, engine: Engine, overload: dict = {}):
    """
    apply style from 'name' of the selector
    for the supported engine
    """
    if engine == Engine.CAIRO:
        apply_cairo_style(context, name, overload)
    else:
        raise "Engine selected is not yet supported"


def apply_fill(context, name: str, engine: Engine, overload: dict = {}):
    """
    apply fill from 'name' of the selector
    for the supported engine
    """
    if engine == Engine.CAIRO:
        apply_cairo_fill(context, get_style(name), overload)


def apply_stroke(context, name: str, engine: Engine, overload: dict = {}):
    """
    apply stroke from 'name' of the selector
    for the supported engine
    """
    if engine == Engine.CAIRO:
        apply_cairo_stroke(context, get_style(name), overload)


def apply_font(context, name: str, engine: Engine, overload: dict = {}):
    """
    apply font from 'name' of the selector
    for the supported engine
    """
    if engine == Engine.CAIRO:
        apply_cairo_font(context, get_style(name), overload)


def get_style(name: str, overload: dict = {}) -> dict:
    """
    get the style from the selector rules and
    fallback to a closest match in the default style
    """
    selectors = DEFAULT_STYLE.keys()
    rule = name if name in selectors else \
           name.split(' ')[0] if ' ' in name else ''
    style = dict(DEFAULT_STYLE.get(rule, {}))
    style.update(overload)
    return style


def text_align(context, name: str, text: str, engine: Engine):
    """
    calculate the offset to apply for the text alignment
    """
    if engine == Engine.CAIRO:
        return cairo_text_align(context, get_style(name), text)

def text_bbox(context, name: str, text: str, engine: Engine, overload: dict = {}):
    """
    calculate the bounding box of the text
    """
    if engine == Engine.CAIRO:
        apply_cairo_style(context, name, overload)
        return cairo_text_bbox(context, get_style(name), text)
    return (-len(text)*6/2, -4.5, len(text)*6, 9)

def style_in_kwargs(**kwargs) -> dict:
    ans = {}
    # parse_color
    for e in ["fill", "stroke", "color"]:
        if e in kwargs:
            ans[e] = parse_css_color(kwargs.get(e))
    # parse size
    for e in ["font-size"]:
        if e in kwargs:
            ans[e] = parse_css_size(kwargs.get(e))
    # integer or array
    for e in ["stroke-width", "stroke-dasharray", "font-weight"]:
        if e in kwargs:
            ans[e] = kwargs.get(e)
    return ans

def css_from_style(style: dict):
    """
    generate an equivalent string for only
    one rule of the style
    """
    return '\n'.join((css_from_rule(*item) for item in style.items()))

def css_from_rule(rule: str, style: dict, with_rule: bool = True):
    """
    generate an equivalent string for only
    one rule of the style
    """
    ans = ".%s {" % rule if with_rule else ""
    # create repr of each property
    for prop, value in style.items():
        if value is None:
            ans += "%s: none;" % prop
        # fill or stroke are only color
        elif prop == "fill" and rule == "hash":
            ans += "fill: url(#diagonalHatch);"
        elif prop in ["fill", "stroke", "color"]:
            ans += "%s: rgba(%d, %d, %d, %d);" % (prop, *value)
        # font size
        elif prop in ["font-size"]:
            v, unit = value
            if unit == SizeUnit.EM:
                ans += "%s: %.3fem;" % (prop, v)
            elif unit == SizeUnit.PT:
                ans += "%s: %.3fpt;" % (prop, v)
            else:
                ans += "%s: %.3fpx;" % (prop, v)
        elif prop in ["text-align"]:
            if value == TextAlign.LEFT:
                ans += "%s: left;" % prop
            elif value == TextAlign.RIGHT:
                ans += "%s: right;" % prop
            elif value == TextAlign.CENTER:
                ans += "%s: center;" % prop
            else:
                ans += "%s: justify;" % prop
        elif prop in ["stroke-dasharray"]:
            ans += "%s: %s;" % (prop, ', '.join([str(v) for v in value]))
        elif prop in ["stroke-linecap"]:
            if value == LineCap.ROUND:
                ans += "%s: round;" % prop
            elif value == LineCap.BUTT:
                ans += "%s: butt;" % prop
            else:
                ans += "%s: square;" % prop
        elif prop in ["stroke-linejoin"]:
            if value == LineJoin.BEVEL:
                ans += "%s: bevel;" % prop
            elif value == LineJoin.MITER:
                ans += "%s: miter;" % prop
            else:
                ans += "%s: round;" % prop
        else:
            ans += "%s: %s;" % (prop, value)
    if not with_rule:
        return ans
    return ans + '}'
    
def parse_css_size(S: str) -> tuple:
    """
    convert a css valid representation of a size
    into a value unit tuple
    """
    s = S.strip().lower()
    v = float(''.join([c for c in s if c in "0123456789."]))
    u = SizeUnit.EM if "em" in s else \
        SizeUnit.PT if "pt" in s else SizeUnit.PX
    return (v, u)

def parse_css_color(S: str) -> tuple:
    """
    convert a css valid representation of a color
    into rgba tuple from 0 to 255
    """
    s = S.strip().lower()
    if s.startswith("rgba"):
        return [int(i, 10) for i in s[5:-1].split(',')]
    elif s.startswith("rgb"):
        return [int(i, 10) for i in s[4:-1].split(',')]
    elif s.startswith("#"):
        if len(s) == 3:
            return [int(i, 16) for i in s.split('', 3)]
        else:
            return [int(i, 16) for i in s[1::2]]
    return s
