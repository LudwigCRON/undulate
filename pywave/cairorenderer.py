#!/usr/bin/env python3
# spell-checker: disable

"""
cairorenderer.py use the logic of renderer.py to render waveforms
into scalable vector graphics format
"""

import cairo
from .skin import (
    apply_fill,
    apply_stroke,
    apply_font,
    text_align,
    Engine,
    style_in_kwargs
)
from .renderer import Renderer, svg_curve_convert


class CairoRenderer(Renderer):
    """
    Render the wavelanes as an svg
    """

    def __init__(self, **kwargs):
        Renderer.__init__(self)
        self.engine = Engine.CAIRO
        self.cr = None
        self.surface = None
        self.extension = kwargs.get("extension", "svg").lower()

    def group(self, callback, identifier: str, **kwargs) -> str:
        """
        group define a group
        """
        extra = kwargs.get("extra", None)
        self.cr.push_group()
        if callable(extra):
            extra()
        callback()
        self.cr.pop_group_to_source()
        self.cr.paint_with_alpha(1)
        return ""

    def path(self, vertices: list, **kwargs) -> str:
        """
        path draw a path to represent common signals
        vertices: list of of x-y coordinates in a tuple
        [style_repr] : optional attributes for the svg (eg class)
        """
        extra = kwargs.get("extra", None)
        style = kwargs.get("style_repr", "path")
        overload = style_in_kwargs(**kwargs)
        self.cr.save()
        if callable(extra):
            extra()
        apply_stroke(self.cr, style, Engine.CAIRO, overload)
        self.cr.new_path()
        for i, v in enumerate(vertices):
            if i == 0:
                self.cr.move_to(*v)
            else:
                self.cr.line_to(*v)
        self.cr.stroke()
        self.cr.restore()
        return ""

    def arrow(self, x, y, angle, **kwargs) -> str:
        """
        arrow draw an arrow to represent edge trigger on clock signals
        x       : x coordinate of the arrow center
        y       : y coordinate of the arrow center
        angle   : angle in degree to rotate the arrow
        [style_repr] : optional attributes for the svg (eg class)
        """
        extra = kwargs.get("extra", None)
        style = kwargs.get("style_repr", "arrow")
        self.cr.save()
        if callable(extra):
            extra()
        apply_fill(self.cr, style, Engine.CAIRO)
        self.cr.translate(x, y)
        self.cr.rotate((angle - 90) * 3.14159 / 180)
        self.cr.new_path()
        self.cr.move_to(-3.5, -3.5)
        self.cr.line_to(0, 3.5)
        self.cr.line_to(3.5, -3.5)
        self.cr.line_to(0, -2)
        self.cr.line_to(-3.5, -3.5)
        self.cr.fill()
        self.cr.restore()
        return ""

    def polygon(self, vertices: list, **kwargs) -> str:
        """
        polygon draw a closed shape to represent common data
        vertices: list of of x-y coordinates in a tuple
        [extra] : optional attributes for the svg (eg class)
        """
        extra = kwargs.get("extra", None)
        style = kwargs.get("style_repr", None)
        overload = style_in_kwargs(**kwargs)
        self.cr.save()
        if callable(extra):
            extra()
        apply_fill(self.cr, style, Engine.CAIRO, overload)
        self.cr.new_path()
        for i, v in enumerate(vertices):
            if i == 0:
                self.cr.move_to(*v)
            else:
                self.cr.line_to(*v)
        self.cr.fill_preserve()
        apply_stroke(self.cr, style, Engine.CAIRO, overload)
        self.cr.stroke()
        self.cr.restore()
        return ""

    def spline(self, vertices: list, **kwargs) -> str:
        """
        spline draw a path to represent smooth signals
        vertices: list of of type-x-y coordinates in a tuple of control points
                where type is either a moveto (m/M) lineto (l/L) or curveto (c/C)
                svg operator
        [style_repr] : optional attributes for the svg (eg class)
        """
        style = kwargs.get("style_repr", "path")
        extra = kwargs.get("extra", "")
        overload = style_in_kwargs(**kwargs)
        vertices = svg_curve_convert(vertices)
        c, px, py, stack = 0, 0, 0, []

        self.cr.save()
        if callable(extra):
            extra()
        self.cr.new_path()
        self.cr.move_to(px, py)

        for i, v in enumerate(vertices):
            s, x, y = v
            # check the command
            cmd = (
                "rcurveto"
                if s == "c"
                else "curveto"
                if s == "C"
                else "rlineto"
                if s == "l"
                else "lineto"
                if s == "L"
                else "rmoveto"
                if s == "m"
                else "moveto"
                if s == "M"
                else "closepath"
                if s == "z" or s == "Z"
                else cmd
            )
            # gather 3 points to draw a bezier curve
            c = 2 if s in ["C", "c"] else c
            if c == 2:
                stack.extend([x, y])
                c = 1
            elif c > 0:
                stack.extend([x, y])
                c -= 1
            else:
                stack.extend([x, y])
                if cmd.startswith("rc"):
                    self.cr.rel_curve_to(*stack)
                elif cmd.startswith("rl"):
                    self.cr.rel_line_to(*stack)
                elif cmd.startswith("rm"):
                    self.cr.rel_move_to(*stack)
                elif cmd.startswith("l"):
                    self.cr.line_to(*stack)
                elif cmd.startswith("m"):
                    self.cr.move_to(*stack)
                elif cmd == "closepath":
                    self.cr.close_path()
                else:
                    self.cr.curve_to(*stack)
                stack = []
            # hold last point
            px, py = x, y
        if style == "hide":
            apply_fill(self.cr, style, Engine.CAIRO, overload)
            self.cr.fill()
        else:
            apply_stroke(self.cr, style, Engine.CAIRO, overload)
            self.cr.stroke()
        self.cr.restore()
        return ""

    def text(self, x: float, y: float, text: str = "", **kwargs) -> str:
        """
        text draw a text for data
        x       : x coordinate of the text
        y       : y coordinate of the text
        text    : text to display
        """
        extra = kwargs.get("extra", "")
        style = kwargs.get("style_repr", "text")
        overload = style_in_kwargs(**kwargs)
        self.cr.save()
        if callable(extra):
            extra()
        apply_fill(self.cr, style, Engine.CAIRO, overload)
        apply_font(self.cr, style, Engine.CAIRO)
        ox, oy = text_align(self.cr, style, str(text), Engine.CAIRO)
        self.cr.move_to(x - ox, y - oy)
        self.cr.show_text(str(text))
        self.cr.restore()
        return ""

    def translate(self, x: float, y: float, **kwargs) -> str:
        def _():
            self.cr.translate(x, y)

        return _

    def draw(self, wavelanes, **kwargs) -> str:
        filename = kwargs.get("filename", False)
        _id = kwargs.get("id", "a")
        brick_width = kwargs.get("brick_width", 40)
        brick_height = kwargs.get("brick_height", 20)
        is_reg = kwargs.get("is_reg", False)
        lkeys, width, height, n = self.size(wavelanes, brick_width, brick_height)
        # remove offset for the name in register
        if is_reg:
            lkeys = -1
            height += n * 12
        # select appropriate surface
        if self.extension == "svg":
            self.surface = cairo.SVGSurface(filename, (width + lkeys * 11 + 11), height)
        elif self.extension == "png":
            self.surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width + lkeys * 11 + 11), int(height))
        elif self.extension == "ps":
            self.surface = cairo.PSSurface(filename, (width + lkeys * 11 + 11), height)
            self.surface.set_eps(False)
        elif self.extension == "eps":
            self.surface = cairo.PSSurface(filename, (width + lkeys * 11 + 11), height)
            self.surface.set_eps(True)
        elif self.extension == "pdf":
            self.surface = cairo.PDFSurface(filename, (width + lkeys * 11 + 11), height)
        else:
            raise "Not supported format"
        self.cr = cairo.Context(self.surface)
        # set background for png image
        if self.extension == "png":
            self.cr.set_source_rgb(1, 1, 1)
            self.cr.paint()
        # paint waveforms
        self.wavegroup(
            _id,
            wavelanes,
            brick_width=brick_width,
            brick_height=brick_height,
            width=width,
            height=height,
            offsetx=lkeys * 10 + 10,
        )
        self.cr.show_page()
        # write to an external file for png images
        if self.extension == "png":
            self.surface.write_to_png(filename)
        # otherwise close the file pointer
        else:
            self.surface.finish()
        return ""

