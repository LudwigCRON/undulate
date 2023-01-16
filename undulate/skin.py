#!/usr/bin/env python3

"""
This define the style of the drawing
it follows the principle of the css but accept only a subset:
font: size, style, variant, weight, stretch, align, family
fill: color, opacity
stroke: color, width, opacity, css.LineCap, css.LineJoin, mitterlimit, dasharray, opacity

colors should always be in rgba with value from 0—255
"""
import os
import sys
from enum import Enum

import undulate.parsers.css as css


class Engine(Enum):
    SVG = 0
    EPS = 1
    CAIRO = 2


# style definition for cairo renderer
DEFAULT_STYLE = css.load(os.path.join(os.path.dirname(__file__), "default.css"))

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
    <mask id="wavezone">
        <rect x="-{0}" y="-8" width="{0}" height="{2}" fill="black" />
        <rect x="0" y="-8" width="{1}" height="{2}" fill="white" />
    </mask>
</defs>
"""

try:
    import cairocffi as cairo
    import pangocffi as pango
    import pangocairocffi as pangocairo
except ImportError:
    pass
else:

    def apply_cairo_style(context, name: str, overload: dict):
        """
        read the style and apply via cairo functions
        """
        style = get_style(name)
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
        if t is None:
            t = (255, 255, 255, 0)
        r, g, b, a = t
        context.set_source_rgba(r / 255, g / 255, b / 255, a / 255)

    def apply_cairo_stroke(context, style: dict, overload: dict):
        """
        support width, color, LineCap, LineJoin, dash
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
        lc = style.get("stroke-linecap", css.LineCap.ROUND)
        if lc == css.LineCap.SQUARE:
            context.set_line_cap(cairo.LINE_CAP_SQUARE)
        elif lc == css.LineCap.BUTT:
            context.set_line_cap(cairo.LINE_CAP_BUTT)
        else:
            context.set_line_cap(cairo.LINE_CAP_ROUND)
        # line join
        lj = style.get("stroke-linejoin", css.LineJoin.MITER)
        if lj == css.LineJoin.BEVEL:
            context.set_line_join(cairo.LINE_JOIN_BEVEL)
        elif lj == css.LineJoin.ROUND:
            context.set_line_join(cairo.LINE_JOIN_ROUND)
        else:
            context.set_line_join(cairo.LINE_JOIN_MITER)
        # dash array
        da = style.get("stroke-dasharray", [])
        of = style.get("stroke-dasharray-offset", 0)
        if da:
            context.set_dash(da, of)

    def cairo_text_align(layout, style: dict, text: str, overload: dict = {}):
        """
        offset calculation for text alignment
        """
        style.update(overload)
        ta = style.get("text-align", css.TextAlign.CENTER)
        ba = style.get("dominant-baseline", "middle")
        # get text width
        _, log_box = layout.get_extents()
        PANGO_SCALE = pango.units_from_double(1)
        width, height = log_box.width / PANGO_SCALE, log_box.height / PANGO_SCALE
        # apply style
        dy = height / 2 if ba == "middle" else 0
        if ta == css.TextAlign.LEFT:
            return (0, dy)
        if ta == css.TextAlign.RIGHT:
            return (width, dy)
        return (width / 2, dy)

    def cairo_text_bbox(layout, style: dict, text: str, overload: dict = {}):
        """
        return size of the text for a given font
        can differ as not using the pango backend
        """
        style.update(overload)
        ta = style.get("text-align", css.TextAlign.CENTER)
        layout.apply_markup(text)
        # get text width
        _, log_box = layout.get_extents()
        PANGO_SCALE = pango.units_from_double(1)
        width, height = log_box.width / PANGO_SCALE, log_box.height / PANGO_SCALE
        width += css.SizeUnit.EM.value / 2
        if ta == css.TextAlign.LEFT:
            return (0, -height / 2, width, height)
        elif ta == css.TextAlign.RIGHT:
            return (-width, -height / 2, width, height)
        return (-width / 2, -height / 2, width, height)

    def apply_cairo_font(layout, style: dict, overload: dict):
        """
        get font information from the style and apply
        support font family, bold, italic, normal, size
        """
        style = dict(style)
        style.update(overload)
        desc = pango.FontDescription()
        # font slant
        font_style = style.get("font-style", "")
        if "it" in font_style:
            desc.style = pango.Style.ITALIC
        elif "ob" in font_style:
            desc.style = pango.Style.OBLIQUE
        else:
            desc.style = pango.Style.NORMAL
        # normal or bold
        w = style.get("font-weight", 200)
        if isinstance(w, str) and "bold" in w:
            desc.weight = 700
        elif isinstance(w, int):
            desc.weight = w
        else:
            desc.weight = 400
        # fetch font family
        font_family = style.get("font-family", "Sans-Serif")
        if font_family is not None and isinstance(font_family, str):
            desc.family = font_family
        # font size
        font_size = style.get("font-size", None)
        if font_size is not None:
            s, u = font_size
            desc.size = int(s * u.value * pango.units_from_double(1))
        layout.alignment = pango.Alignment.CENTER
        layout.font_description = desc


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


def text_align(layout, name: str, text: str, engine: Engine, overload: dict = {}):
    """
    calculate the offset to apply for the text alignment
    """
    if engine == Engine.CAIRO:
        return cairo_text_align(layout, get_style(name), text, overload)


def text_bbox(context, name: str, text: str, engine: Engine, overload: dict = {}):
    """
    calculate the bounding box of the text
    """
    style = get_style(name)
    if engine == Engine.CAIRO:
        apply_cairo_style(context, name, overload)
        dummy_layout = pangocairo.create_layout(context)
        apply_cairo_font(dummy_layout, style, {})
        dummy_layout.alignment = pango.Alignment.CENTER
        return cairo_text_bbox(dummy_layout, style, text, overload)
    val, unit = style.get("font-size", (0.5, css.SizeUnit.EM))
    return (
        -len(text) * 0.333 * val * unit.value,
        -val * unit.value / 2,
        len(text) * 0.667 * val * unit.value,
        val * unit.value,
    )


def style_in_kwargs(**kwargs) -> dict:
    ans = {}
    # parse_color
    for e in ["fill", "stroke", "color"]:
        if e in kwargs:
            ans[e] = css.parse_css_color(kwargs.get(e))
    # parse size
    for e in ["font-size"]:
        if e in kwargs:
            ans[e] = css.parse_css_size(kwargs.get(e))
    # parse text-align
    for e in ["text-align"]:
        if e in kwargs:
            ans[e] = css.parse_text_align(kwargs.get(e))
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
    ans = ":root {" if rule == "root" else ".%s {" % rule if with_rule else ""
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
        elif prop in ["font-size", "padding-top", "padding-bottom"]:
            v, unit = value
            if unit == css.SizeUnit.EM:
                ans += "%s: %.3fem;" % (prop, v)
            elif unit == css.SizeUnit.PT:
                ans += "%s: %.3fpt;" % (prop, v)
            else:
                ans += "%s: %.3fpx;" % (prop, v)
        elif prop in ["text-align"]:
            if value == css.TextAlign.LEFT:
                ans += "%s: left;" % prop
            elif value == css.TextAlign.RIGHT:
                ans += "%s: right;" % prop
            elif value == css.TextAlign.CENTER:
                ans += "%s: center;" % prop
            else:
                ans += "%s: justify;" % prop
        elif prop in ["stroke-dasharray"]:
            ans += "%s: %s;" % (prop, ", ".join([str(v) for v in value]))
        elif prop in ["stroke-linecap"]:
            if value == css.LineCap.ROUND:
                ans += "%s: round;" % prop
            elif value == css.LineCap.BUTT:
                ans += "%s: butt;" % prop
            else:
                ans += "%s: square;" % prop
        elif prop in ["stroke-linejoin"]:
            if value == css.LineJoin.BEVEL:
                ans += "%s: bevel;" % prop
            elif value == css.LineJoin.MITER:
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
        style = css.load(filepath)
    DEFAULT_STYLE.update(style)
