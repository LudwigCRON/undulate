"""
svgrenderer.py use the logic of renderer.py to render waveforms
into scalable vector graphics format
"""

import html
from undulate.skin import (
    DEFAULT_STYLE,
    DEFINITION,
    Engine,
    style_in_kwargs,
    css_from_rule,
    css_from_style,
    text_bbox,
    SizeUnit,
    get_style,
)
from undulate.bricks.generic import ArrowDescription, SplineSegment, Point
from undulate.renderers.renderer import Renderer
from typing import List


class SvgRenderer(Renderer):
    """
    Render the wavelanes as an svg
    """

    def __init__(self, **kwargs):
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
        Group some drawable together

        Args:
            callback (callable): function which populate what inside the group
            identifier (str): unique id for the group
        """
        classes = " ".join(kwargs.get("classes", []))
        if classes:
            classes = 'class="' + classes + '"'
        ans = '<g id="%s" %s %s >\n' % (identifier, classes, kwargs.get("extra", ""))
        ans += callback()
        ans += "</g>\n"
        return ans

    def path(self, vertices: List[Point], **kwargs) -> str:
        """
        Draw line segments to connect consecutive points of 'vertices'
        to represent common signals

        Args:
            vertices (List[Point]): list of points to be connected
        Parameters:
            style_repr (optional str) : css rule, by default 'path'
        """
        overload = style_in_kwargs(**kwargs)
        overload["fill"] = None
        path = "".join(["L%f,%f " % (v.x, v.y) for v in vertices])
        path = "M" + path[1:]
        return '<path d="%s" class="%s" style="%s" />\n' % (
            path.strip(),
            kwargs.get("style_repr", ""),
            css_from_rule(None, overload, False),
        )

    def arrow(self, arrow_description: ArrowDescription, **kwargs) -> str:
        """
        Draw an arrow to represent edge trigger on clock signals or to point
        something in an annotation.

        Args:
            arrow_description (ArrowDescription) : position and oriantation
        Parameters:
            style_repr (optional str) : css rule, by default 'arrow'
        """
        style_repr = kwargs.get("style_repr", "arrow")
        overload = style_in_kwargs(**kwargs)
        transform = 'transform="translate(%f, %f) rotate(%f, 0, 0)" ' % (
            arrow_description.x,
            arrow_description.y,
            arrow_description.angle - 90,
        )
        return (
            '<path d="M-3.5 -3.5 L0 3.5 L3.5 -3.5 L0 -2 L-3.5 -3.5" '
            + transform
            + 'class="%s" style="%s"/>\n'
            % (style_repr, css_from_rule(None, overload, False))
        )

    def polygon(self, vertices: List[Point], **kwargs) -> str:
        """
        Draw a closed shape for shaded/colored area

        Args:
            vertices (List[Point]): Ordered list of point delimiting the polygon
        Parameters:
            style_repr (optional str) : css rule, by default None
        """
        extra = kwargs.get("extra")
        style = kwargs.get("style_repr")
        overload = style_in_kwargs(**kwargs)
        if "hatch" in style or "polygon" in style or extra is None:
            extra = ""
        if callable(extra):
            extra = extra()
        ans = '<polygon points="'
        for v in vertices:
            ans += "%f, %f " % (v.x, v.y)
        ans += '" class="%s" style="%s" %s/>\n' % (
            style,
            css_from_rule(None, overload, False),
            extra,
        )
        return ans

    def spline(self, vertices: List[SplineSegment], **kwargs) -> str:
        """
        Draw a path to represent smooth signals

        Args:
            vertices (List[SplineSegment]): list of SVG path operators and arguments
        Parameters:
            style_repr (optional str) : css rule, by default 'path'
        """
        overload = style_in_kwargs(**kwargs)
        if kwargs.get("style_repr") not in ["hide", "edge-arrow"]:
            overload["fill"] = None
        path = "".join(
            ["%s%f,%f " % (v.order, v.x, v.y) if v.order != "z" else "z" for v in vertices]
        )
        return '<path d="%s" class="%s" style="%s"/>\n' % (
            path.strip(),
            kwargs.get("style_repr", "path"),
            css_from_rule(None, overload, False),
        )

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
        filename = kwargs.get("filename", False)
        brick_width = kwargs.get("brick_width", 40)
        brick_height = kwargs.get("brick_height", 20)
        is_reg = kwargs.get("is_reg", False)
        longest_wavename, width, height, n = self.size(wavelanes, **kwargs)
        # remove offset for the name in register
        if is_reg:
            s, u = get_style("attr").get("font-size", (9, SizeUnit.PX))
            height += (n + 1) * 1.5 * s * u.value
        _, _, self.offsetx, _ = text_bbox(None, "title", longest_wavename, Engine.SVG)
        with open(filename, "w+") as fp:
            fp.write(
                '<svg xmlns="http://www.w3.org/2000/svg" width="%f" height="%f" '
                % (width + self.offsetx + 10, height)
            )
            fp.write('viewBox="-1 -1 %f %f">\n' % (width + self.offsetx + 10, height + 2))
            fp.write("<style>\n")
            fp.write(css_from_style(DEFAULT_STYLE))
            fp.write("\n.wave {mask: url(#wavezone);}\n")
            fp.write("</style>\n")
            fp.write(DEFINITION.format(int(self.offsetx + 8), int(width), int(height)))
            fp.write(
                self.wavegroup(
                    _id,
                    wavelanes,
                    brick_width=brick_width,
                    brick_height=brick_height,
                    width=width,
                    height=height,
                    offsetx=self.offsetx + 8,
                )[1]
            )
            fp.write("\n</svg>")
