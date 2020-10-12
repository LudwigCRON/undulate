#!/usr/bin/env python3

"""
This define the style of the drawing
it follows the principle of the css but accept only a subset:
font: size, style, variant, weight, stretch, align, family
fill: color, opacity
stroke: color, width, opacity, linecap, linejoin, mitterlimit, dasharray, opacity

colors should always be in rgba with value from 0—255
"""
import os
import re
import sys
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


class CSSTokenType(Enum):
    RULES = 0
    STRING = 1
    SEP = 2
    END_PROPERTY = 3
    BLOCK_START = 4
    BLOCK_END = 5
    IGNORE = 6
    UNKNOWN = 7
    EOF = 8


def css_tokenizer(stream):
    """
    read a character stream and gather them
    to provide a token to the css parser
    Args:
        character line stream (FileStream/StringIO)

    Returns:
        Tuple(int,CSSTokenType,str):
            line_number (int)
            token_type (CSSTokenType)
            token (str)
    """
    buf = []
    in_string = False
    in_block = False
    in_comment = False
    prev_c = None
    mapping_table = {
        " ": CSSTokenType.IGNORE,
        "\t": CSSTokenType.IGNORE,
        "\n": CSSTokenType.IGNORE,
        ",": CSSTokenType.SEP,
        ":": CSSTokenType.SEP,
        "{": CSSTokenType.BLOCK_START,
        "}": CSSTokenType.BLOCK_END,
        ";": CSSTokenType.END_PROPERTY,
    }
    for i, line in enumerate(stream):
        for c in line:
            token = "".join(buf)
            token_type = CSSTokenType.STRING if in_block else CSSTokenType.RULES
            mc = mapping_table.get(c, CSSTokenType.UNKNOWN)
            if c in "'\"":
                in_string = not in_string
            elif prev_c == "/" and c == "*":
                in_comment = True
                buf = buf[:-1]
            elif prev_c == "*" and c == "/":
                in_comment = False
            elif not in_comment and mc not in [CSSTokenType.IGNORE, CSSTokenType.UNKNOWN]:
                if token and not (c == ":" and not in_block):
                    yield (i, token_type, token)
                    buf = []
                if mc == CSSTokenType.BLOCK_START:
                    in_block = True
                elif mc == CSSTokenType.BLOCK_END:
                    in_block = False
                if not (c == ":" and not in_block):
                    yield (i, mapping_table.get(c), c)
            elif not in_comment and not in_string and mc == CSSTokenType.IGNORE:
                if token:
                    yield (
                        i,
                        token_type,
                        token,
                    )
                    buf = []
            elif not in_comment:
                buf.append(c)
            prev_c = c
        if buf and not in_comment:
            yield (i, CSSTokenType.STRING if in_block else CSSTokenType.RULES, "".join(buf))
            buf = []
    yield (-1, CSSTokenType.EOF, None)


def parse_css_size(S: str) -> tuple:
    """
    convert a css valid representation of a size
    into a value unit tuple
    """
    if isinstance(S, str):
        s = S.strip().lower()
        v = float("".join([c for c in s if c in "0123456789."]))
        u = SizeUnit.EM if "em" in s else SizeUnit.PT if "pt" in s else SizeUnit.PX
        return (v, u)
    return S


def hsl_to_rgb(h, s, l):
    """
    convert hsl([0-359] deg, [0-1] float, [0-1] float) into
    rgb([0-255] int, [0-255] int, [0-255] int)
    """
    c = (2 - 2 * l) * s if l > 0.5 else 2 * l
    y = (h / 60) % 2
    x = (2 - y) * c if y > 1.0 else y
    m = l - c / 2
    rp = c if h < 60 or h >= 300 else x if h < 120 or h >= 240 else 0
    gp = c if h >= 60 and h < 180 else x if h < 240 else 0
    bp = c if h >= 180 and h < 300 else x if h >= 120 else 0
    return [int((rp + m) * 255), int((gp + m) * 255), int((bp + m) * 255)]


def parse_css_color(S: str) -> tuple:
    """
    convert a css valid representation of a color
    into rgba tuple from 0 to 255
    """
    if isinstance(S, list):
        return S
    s = S.strip().lower()
    if s.startswith("rgba"):
        return [int(i, 10) for i in re.split(",| ", s[5:-1]) if i]
    elif s.startswith("rgb"):
        return [int(i, 10) for i in re.split(",| ", s[4:-1]) if i] + [255]
    elif s.startswith("hsla"):
        hsl = [
            float("".join([c for c in i if c in "0123456789."])) / 100
            if i and "%" in i
            else float(i)
            for i in re.split(",| ", s[5:-1])
        ]
        rgba = hsl_to_rgb(*hsl[:3])
        rgba.append(hsl[-1])
        return rgba
    elif s.startswith("hsl"):
        hsl = [
            float("".join([c for c in i if c in "0123456789."])) / 100
            if i and "%" in i
            else float(i)
            for i in re.split(",| ", s[5:-1])
        ]
        return hsl_to_rgb(*hsl[:3])
    elif s.startswith("#"):
        if len(s) == 4:
            return [int(i, 16) * 17 for i in s[1:4]] + [255]
        elif len(s) == 7:
            return [int(s[i : i + 2], 16) for i in range(1, 6, 2)] + [255]
        else:
            return [int(s[i : i + 2], 16) for i in range(1, 8, 2)]
    return s


def css_parser(token_iter):
    """
    construct the style dictionnary from
    an iterator of tokens
    """

    def expect(it, types):
        try:
            line_number, type, token = next(it)
            if type not in types:
                print(
                    "ERROR: unexpected token '%s' at Line %d" % (token, line_number),
                    file=sys.stderr,
                )
                exit(6)
            return token
        except StopIteration:
            return None

    def expect_multiple(it, types, until_types):
        ans = []
        try:
            line_number, type, token = next(it)
            while type in types:
                ans.append(token)
                line_number, type, token = next(it)
            if type not in until_types:
                print(
                    "ERROR: unexpected token '%s' at Line %d" % (token, line_number),
                    file=sys.stderr,
                )
                exit(7)
            return ans, (line_number, type, token)
        except StopIteration:
            return None, None

    def expect_property(it):
        property_name = expect(it, [CSSTokenType.STRING, CSSTokenType.BLOCK_END])
        if property_name is None:
            return None, (-1, CSSTokenType.EOF, "")
        if property_name == "}":
            return None, (-1, CSSTokenType.BLOCK_END, "}")
        expect(it, [CSSTokenType.SEP])
        property_value, b = expect_multiple(
            token_iter,
            [CSSTokenType.STRING, CSSTokenType.SEP],
            [CSSTokenType.END_PROPERTY],
        )
        value = " ".join(property_value)
        # parse number only
        if all([c in "0123456798 " for c in value]):
            property_value = int(value, 10)
        elif all([c in "0123456798. " for c in value]):
            property_value = float(value)
        # parse color
        elif re.match(r"#([0-9A-Fa-f]+)", value):
            property_value = tuple(parse_css_color(value))
        elif property_value[0].startswith("rgb"):
            property_value = tuple(parse_css_color(value))
        elif property_value[0].startswith("hsl"):
            property_value = tuple(parse_css_color(value))
        # parse size
        elif (
            "size" in property_name
            or "padding" in property_name
            or "width" in property_name
        ):
            property_value = parse_css_size(value)
        # align
        elif property_name == "text-align":
            property_value = (
                TextAlign.LEFT
                if "le" in value
                else TextAlign.RIGHT
                if "ri" in value
                else TextAlign.CENTER
                if "ce" in value
                else TextAlign.JUSTIFY
            )
        # linecap
        elif "linecap" in property_name:
            property_value = (
                LineCap.ROUND
                if "ro" in value
                else LineCap.BUTT
                if "bu" in value
                else LineCap.SQUARE
            )
        # linejoin
        elif "linejoin" in property_name:
            property_value = (
                LineJoin.ROUND
                if "ro" in value
                else LineJoin.MITER
                if "mi" in value
                else LineJoin.BEVEL
            )
        # none -> None
        elif "none" in property_value:
            property_value = None
        # array
        elif "," in value and all([c in "0123456789. ," for c in value]):
            property_value = [int(v, 10) for v in property_value if v != ","]
        else:
            property_value = " ".join(value.replace(" ,", ", ").split())
        return (property_name, property_value), b

    def expect_rule(it):
        style = {}
        rule, _ = expect_multiple(
            it,
            [CSSTokenType.RULES, CSSTokenType.SEP],
            [CSSTokenType.BLOCK_START, CSSTokenType.EOF],
        )
        if rule:
            rule = [r for r in rule if r != ","]
        else:
            return None, None
        end_type = CSSTokenType.UNKNOWN
        while end_type != CSSTokenType.BLOCK_END:
            property_or_empty, end_block = expect_property(it)
            if property_or_empty:
                property, value = property_or_empty
                style[property] = value
            if end_block:
                end_type = end_block[1]
        return rule, style

    stylesheet = {}
    rule = ""
    while rule is not None:
        rule, style = expect_rule(token_iter)
        if rule:
            for r in rule:
                rp = r.replace(".", "")
                stylesheet[rp] = style
    return stylesheet


def css_load(filepath: str):
    with open(filepath, "r+") as fp:
        return css_parser(css_tokenizer(fp))


# style definition for cairo renderer
DEFAULT_STYLE = css_load(os.path.join(os.path.dirname(__file__), "default.css"))

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
        if t is not None:
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
        if t is not None:
            r, g, b, a = t
            context.set_source_rgba(r / 255, g / 255, b / 255, a / 255)
        # width
        w = style.get("stroke-width", 1.0)
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
        dy = descent / 2 + height / 4 if ba == "middle" else 0
        if ta == TextAlign.LEFT:
            return (0, -dy)
        if ta == TextAlign.RIGHT:
            return (width, -dy)
        return (width / 2, -dy)

    def cairo_text_bbox(context, style: dict, text: str):
        """
        return size of the text for a given font
        """
        ta = style.get("text-align", TextAlign.CENTER)
        # get text width
        ascent, descent, _height, max_x_advance, max_y_advance = context.font_extents()
        xbearing, ybearing, width, height, xadvance, yadvance = context.text_extents(text)
        width += SizeUnit.EM.value / 2
        if ta == TextAlign.LEFT:
            return (0, -height / 2, width, _height)
        elif ta == TextAlign.RIGHT:
            return (-width, -height / 2, width, _height)
        return (-width / 2, -descent - height / 2, width, _height)

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
        if font_family is not None and isinstance(font_family, str):
            context.select_font_face(font_family, font_style, font_weight)
        # font size
        font_size = style.get("font-size", None)
        if font_size is not None:
            s, u = font_size
            context.set_font_size(s * u.value)


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
    rule = name if name in selectors else name.split(" ")[0] if " " in name else ""
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
    return (-len(text) * 6 / 2, -4.5, len(text) * 6, 9)


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
    return "\n".join((css_from_rule(*item) for item in style.items()))


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
        elif prop == "fill" and rule == "hatch":
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
            ans += "%s: %s;" % (prop, ", ".join([str(v) for v in value]))
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
    return ans + "}"


def update_style(filepath: str):
    if not os.path.exists(filepath):
        print("ERROR: cannot read '%s' as a valid stylesheet" % filepath, file=sys.stderr)
        exit(8)
    with open(filepath, "r+") as fp:
        style = css_load(filepath)
    DEFAULT_STYLE.update(style)