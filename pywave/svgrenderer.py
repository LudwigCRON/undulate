#!/usr/bin/env python3
# spell-checker: disable

"""
svgrenderer.py use the logic of renderer.py to render waveforms
into scalable vector graphics format
"""

from .skin import (
    DEFAULT_STYLE,
    DEFINITION,
    Engine,
    style_in_kwargs,
    get_style,
    css_from_rule,
    css_from_style
)
from .renderer import Renderer

class SvgRenderer(Renderer):
    """
    Render the wavelanes as an svg
    """

    _WAVE_TITLE = 'text-anchor="end" xml:space="preserve"'
    _DATA_TEXT = (
        'text-anchor="middle" dominant-baseline="middle" alignment-baseline="central"'
    )

    def __init__(self):
        Renderer.__init__(self)
        self.engine = Engine.SVG

    def _SYMBOL_TEMP(self, *args, **kwargs):
        symbol, content = args
        extra = kwargs.get("extra", "")
        style = kwargs.get("style", "")
        return f'<g data-symbol="{symbol}" {extra} class="{style}">\n{content}</g>\n'

    def group(self, callback, id: str = "", extra: str = "") -> str:
        """
        group define a group
        """
        ans = f'<g id="{id}" {extra} >\n'
        ans += callback()
        ans += "</g>\n"
        return ans

    def path(self, vertices: list, style_repr: str = "", **kwargs) -> str:
        """
        path draw a path to represent common signals
        vertices: list of of x-y coordinates in a tuple
        [style_repr] : optional attributes for the svg (eg class)
        """
        overload = style_in_kwargs(**kwargs)
        overload["fill"] = None
        path = "".join([f"L{x},{y} " for x, y in vertices])
        path = "M" + path[1:]
        return f'<path d="{path.strip()}" class="{style_repr}" style="{css_from_rule(None, overload, False)}" />\n'

    def arrow(self, x, y, angle, **kwargs) -> str:
        """
        arrow draw an arrow to represent edge trigger on clock signals
        x       : x coordinate of the arrow center
        y       : y coordinate of the arrow center
        angle   : angle in degree to rotate the arrow
        [style_repr] : optional attributes for the svg (eg class)
        """
        extra = kwargs.get("extra", None)
        style_repr = kwargs.get("style_repr", "arrow")
        is_edge = kwargs.get("is_edge", False)
        transform = f'transform="translate({x}, {y}) rotate({angle-90}, 0, 0)" '
        if is_edge:
            transform = f'{extra[:-2]} rotate({angle-90}, 0, 0)" '
        return (
            f'<path d="M-3.5 -3.5 L0 3.5 L3.5 -3.5 L0 -2 L-3.5 -3.5" '
            f'{transform}'
            f'class="{style_repr}" />\n'
        )

    def polygon(self, vertices: list, **kwargs) -> str:
        """
        polygon draw a closed shape to represent common data
        vertices: list of of x-y coordinates in a tuple
        [extra] : optional attributes for the svg (eg class)
        """
        extra = kwargs.get("extra", None)
        style = kwargs.get("style_repr", None)
        if "hash" in style or "polygon" in style:
            extra = ""
        if callable(extra):
            extra = extra()
        ans = '<polygon points="'
        for x, y in vertices:
            ans += f"{x},{y} "
        ans += f'" class="{style}" {extra}/>\n'
        return ans

    def spline(self, vertices: list, style_repr: str = "path", **kwargs) -> str:
        """
        spline draw a path to represent smooth signals
        vertices: list of of type-x-y coordinates in a tuple of control points
                where type is either a moveto (m/M) lineto (l/L) or curveto (c/C)
                svg operator
        [style_repr] : optional attributes for the svg (eg class)
        """
        overload = style_in_kwargs(**kwargs)
        overload["fill"] = None
        path = "".join(
            [f"{v[0]}{v[1]},{v[2]} " if v[0] is not "z" else "z" for v in vertices]
        )
        return f'<path d="{path.strip()}" class="{style_repr}" style="{css_from_rule(None, overload, False)}"/>\n'

    def text(self, x: float, y: float, text: str = "", **kwargs) -> str:
        """
        text draw a text for data
        x       : x coordinate of the text
        y       : y coordinate of the text
        text    : text to display
        """
        extra = kwargs.get("extra", "")
        css = kwargs.get("style_repr", "text")
        overload = style_in_kwargs(**kwargs)
        style = get_style(css, overload)
        style["color"] = style.get("fill", style.get("color"))
        if css:
            css = f'class="{css}"'
        return f'<text x="{x}" y="{y}" {extra} {css} style="{css_from_rule(None, style, False)}" >{text}</text>\n'

    def translate(self, x: float, y: float, **kwargs) -> str:
        return f' transform="translate({x}, {y})" '

    def draw(self, wavelanes, **kwargs) -> str:
        _id = kwargs.get("id", "a")
        brick_width = kwargs.get("brick_width", 40)
        brick_height = kwargs.get("brick_height", 20)
        is_reg = kwargs.get("is_reg", False)
        lkeys, width, height, n = self.size(wavelanes, brick_width, brick_height)
        # remove offset for the name in register
        if is_reg:
            lkeys = -1
            height += n * 12
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width+lkeys*11+11}" height="{height}" '
            f'viewBox="-1 -1 {width+lkeys*11+12} {height+2}" overflow="hidden">\n'
            "<style>\n"
            + css_from_style(DEFAULT_STYLE)
            + "</style>\n"
            + DEFINITION
            + self.wavegroup(
                _id,
                wavelanes,
                brick_width=brick_width,
                brick_height=brick_height,
                width=width,
                height=height,
                offsetx=lkeys * 10 + 10,
            )[1]
            + ""
            "\n</svg>"
        )
