#!/usr/bin/env python3
# spell-checker: disable

"""
svgrenderer.py use the logic of renderer.py to render waveforms
into scalable vector graphics format
"""

import html
from .skin import (
    DEFAULT_STYLE,
    DEFINITION,
    Engine,
    style_in_kwargs,
    get_style,
    css_from_rule,
    css_from_style,
)
from .renderer import Renderer


class SvgRenderer(Renderer):
    """
    Render the wavelanes as an svg
    """

    def __init__(self):
        Renderer.__init__(self)
        self.engine = Engine.SVG

    def _SYMBOL_TEMP(self, *args, **kwargs):
        symbol, content = args
        extra = kwargs.get("extra", "")
        style = kwargs.get("style", "")
        return '<g data-symbol="%s" %s class="%s">\n%s</g>\n' % (
            symbol,
            extra,
            style,
            content,
        )

    def group(self, callback, identifier: str, **kwargs) -> str:
        """
        group define a group

        Args:
            callback (callable): function which populate what inside the group
            identifier (str): unique id for the group
        Returns:
            group of drawable items invoked by callback
        """
        ans = '<g id="%s" %s >\n' % (identifier, kwargs.get("extra", ""))
        ans += callback()
        ans += "</g>\n"
        return ans

    def path(self, vertices: list, **kwargs) -> str:
        """
        draw a path to represent common signals

        Args:
            vertices: list of of x-y coordinates in a tuple
        Parameters:
            style_repr (optional) : class of the skin to apply
                by default apply the class 'path'
        """
        overload = style_in_kwargs(**kwargs)
        overload["fill"] = None
        path = "".join(["L%f,%f " % (x, y) for x, y in vertices])
        path = "M" + path[1:]
        return '<path d="%s" class="%s" style="%s" />\n' % (
            path.strip(),
            kwargs.get("style_repr", ""),
            css_from_rule(None, overload, False),
        )

    def arrow(self, x, y, angle, **kwargs) -> str:
        """
        draw an arrow to represent edge trigger on clock signals

        Args:
            x      (float) : x coordinate of the arrow center
            y      (float) : y coordinate of the arrow center
            angle  (float) : angle in degree to rotate the arrow
        Parameters:
            is_edge (bool)
            style_repr (optional) : class of the skin to apply
                by default apply the class 'arrow'
        """
        extra = kwargs.get("extra", None)
        style_repr = kwargs.get("style_repr", "arrow")
        is_edge = kwargs.get("is_edge", False)
        overload = style_in_kwargs(**kwargs)
        transform = 'transform="translate(%f, %f) rotate(%f, 0, 0)" ' % (x, y, angle - 90)
        if is_edge:
            transform = '%s rotate(%f, 0, 0)" ' % (extra[:-2], angle - 90)
        return (
            '<path d="M-3.5 -3.5 L0 3.5 L3.5 -3.5 L0 -2 L-3.5 -3.5" '
            + transform
            + 'class="%s" style="%s"/>\n'
            % (style_repr, css_from_rule(None, overload, False))
        )

    def polygon(self, vertices: list, **kwargs) -> str:
        """
        draw a closed shape to represent common data

        Args:
            vertices: list of of (x,y) coordinates in a tuple
        Parameters:
            style_repr (optional) : class of the skin to apply
                by default apply the class None
        """
        extra = kwargs.get("extra", None)
        style = kwargs.get("style_repr", None)
        overload = style_in_kwargs(**kwargs)
        if "hatch" in style or "polygon" in style or extra is None:
            extra = ""
        if callable(extra):
            extra = extra()
        ans = '<polygon points="'
        for x, y in vertices:
            ans += "%f, %f " % (x, y)
        ans += '" class="%s" style="%s" %s/>\n' % (
            style,
            css_from_rule(None, overload, False),
            extra,
        )
        return ans

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
        overload = style_in_kwargs(**kwargs)
        overload["fill"] = None
        path = "".join(
            ["%s%f,%f " % (v[0], v[1], v[2]) if v[0] != "z" else "z" for v in vertices]
        )
        return '<path d="%s" class="%s" style="%s"/>\n' % (
            path.strip(),
            kwargs.get("style_repr", "path"),
            css_from_rule(None, overload, False),
        )

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
        css = kwargs.get("style_repr", "text")
        overload = style_in_kwargs(**kwargs)
        overload["stroke"] = None
        if css:
            css = 'class="%s"' % css
        return '<text x="%f" y="%f" %s style="%s">%s</text>\n' % (
            x,
            y,
            css,
            css_from_rule(None, overload, False),
            html.escape(str(text)),
        )

    def translate(self, x: float, y: float, **kwargs) -> str:
        return ' transform="translate(%f, %f)" ' % (x, y)

    def draw(self, wavelanes, **kwargs) -> str:
        """
        Business function calling all others

        Args:
            wavelanes (dict): parsed dictionary from the input file
            id (str)  : file name of the output generated file
            brick_width (int): by default 40
            brick_height (int): by default 20
            is_reg (bool):
                if True `wavelanes` given represents a register
                otherwise it represents a bunch of signals
        """
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
            '<svg xmlns="http://www.w3.org/2000/svg" width="%f" height="%f" '
            % (width + lkeys * 11 + 11, height)
            + 'viewBox="-1 -1 %f %f">\n' % (width + lkeys * 11 + 12, height + 2)
            + "<style>\n"
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
