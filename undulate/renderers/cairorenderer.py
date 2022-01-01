"""
cairorenderer.py use the logic of renderer.py to render waveforms
into scalable vector graphics format
"""

import cairo
import undulate.logger as log
from undulate.bricks.generic import ArrowDescription, SplineSegment, Point
from undulate.skin import (
    SizeUnit,
    apply_fill,
    apply_stroke,
    apply_font,
    text_align,
    Engine,
    style_in_kwargs,
    get_style,
)
from undulate.renderers.renderer import Renderer, svg_curve_convert
from typing import List


class CairoRenderer(Renderer):
    """
    Render the wavelanes as an svg, png, eps, ps, or pdf
    by using the pycairo module

    .. note::
        make sure pycairo is installed to use this renderer
        Not knowing how to install it ? Please refer to the
        `Installation <./installation.html>`_ section
    """

    def __init__(self, **kwargs):
        Renderer.__init__(self)
        self.engine = Engine.CAIRO
        self.ctx = None
        self.surface = None
        self.extension = kwargs.get("extension", "svg").lower()
        self.dpi = kwargs.get("dpi", 300)

    def group(self, callback, identifier: str, **kwargs) -> str:
        """
        Group some drawable together

        Args:
            callback (callable): function which populate what inside the group
            identifier (str): unique id for the group
        """
        extra = kwargs.get("extra")
        self.ctx.push_group()
        if callable(extra):
            extra()
        callback()
        self.ctx.pop_group_to_source()
        self.ctx.paint_with_alpha(1)
        return ""

    def path(self, vertices: List[Point], **kwargs) -> str:
        """
        Draw line segments to connect consecutive points of 'vertices'
        to represent common signals

        Args:
            vertices (List[Point]): list of points to be connected
        Parameters:
            style_repr (optional str) : css rule, by default 'path'
        """
        extra = kwargs.get("extra")
        style = kwargs.get("style_repr", "path")
        overload = style_in_kwargs(**kwargs)
        self.ctx.save()
        if callable(extra):
            extra()
        apply_stroke(self.ctx, style, Engine.CAIRO, overload)
        self.ctx.new_path()
        for i, v in enumerate(vertices):
            if i == 0:
                self.ctx.move_to(v.x, v.y)
            else:
                self.ctx.line_to(v.x, v.y)
        self.ctx.stroke()
        self.ctx.restore()
        return ""

    def arrow(self, arrow_description: ArrowDescription, **kwargs) -> str:
        """
        Draw an arrow to represent edge trigger on clock signals or to point
        something in an annotation.

        Args:
            arrow_description (ArrowDescription) : position and oriantation
        Parameters:
            style_repr (optional str) : css rule, by default 'arrow'
        """
        extra = kwargs.get("extra")
        style = kwargs.get("style_repr", "arrow")
        overload = style_in_kwargs(**kwargs)
        self.ctx.save()
        if callable(extra):
            extra()
        apply_fill(self.ctx, style, Engine.CAIRO, overload)
        self.ctx.translate(arrow_description.x, arrow_description.y)
        self.ctx.rotate((arrow_description.angle - 90) * 3.14159 / 180)
        self.ctx.new_path()
        self.ctx.move_to(-3.5, -3.5)
        self.ctx.line_to(0, 3.5)
        self.ctx.line_to(3.5, -3.5)
        self.ctx.line_to(0, -2)
        self.ctx.line_to(-3.5, -3.5)
        self.ctx.fill()
        self.ctx.restore()
        return ""

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
        self.ctx.save()
        if callable(extra):
            extra()
        apply_fill(self.ctx, style, Engine.CAIRO, overload)
        self.ctx.new_path()
        for i, v in enumerate(vertices):
            if i == 0:
                self.ctx.move_to(v.x, v.y)
            else:
                self.ctx.line_to(v.x, v.y)
        self.ctx.fill_preserve()
        apply_stroke(self.ctx, style, Engine.CAIRO, overload)
        self.ctx.stroke()
        self.ctx.restore()
        return ""

    def spline(self, vertices: List[SplineSegment], **kwargs) -> str:
        """
        Draw a path to represent smooth signals

        Args:
            vertices (List[SplineSegment]): list of SVG path operators and arguments
        Parameters:
            style_repr (optional str) : css rule, by default 'path'
        """
        extra = kwargs.get("extra")
        style = kwargs.get("style_repr", "path")
        overload = style_in_kwargs(**kwargs)
        vertices = svg_curve_convert(vertices)
        c, stack = 0, []

        self.ctx.save()
        if callable(extra):
            extra()
        self.ctx.new_path()
        self.ctx.move_to(0, 0)
        previous_cmd = self.ctx.move_to
        map_cmd = {
            "c": self.ctx.rel_curve_to,
            "C": self.ctx.curve_to,
            "l": self.ctx.rel_line_to,
            "L": self.ctx.line_to,
            "m": self.ctx.rel_move_to,
            "M": self.ctx.move_to,
            "z": self.ctx.close_path,
            "Z": self.ctx.close_path,
        }
        for v in vertices:
            t, x, y = v
            # check the command
            cmd = map_cmd.get(t, previous_cmd)
            # gather 3 points to draw a bezier curve
            c = 2 if t in ["c", "C"] else c
            if c > 0:
                stack.extend([x, y])
                c -= 1
            else:
                stack.extend([x, y])
                if t in ["z", "Z"]:
                    cmd()
                else:
                    cmd(*stack)
                stack = []
            # store last cmd
            previous_cmd = cmd
        if style in ["hide", "edge-arrow"]:
            apply_fill(self.ctx, style, Engine.CAIRO, overload)
            self.ctx.fill()
        else:
            apply_stroke(self.ctx, style, Engine.CAIRO, overload)
            self.ctx.stroke()
        self.ctx.restore()
        return ""

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
        extra = kwargs.get("extra")
        style = kwargs.get("style_repr", "text")
        overload = style_in_kwargs(**kwargs)
        self.ctx.save()
        if callable(extra):
            extra()
        apply_fill(self.ctx, style, Engine.CAIRO, overload)
        apply_font(self.ctx, style, Engine.CAIRO, overload)
        ox, oy = text_align(self.ctx, style, str(text), Engine.CAIRO)
        self.ctx.move_to(x - ox, y - oy)
        self.ctx.show_text(str(text))
        self.ctx.restore()
        return ""

    def translate(self, x: float, y: float, **kwargs) -> str:
        def _():
            self.ctx.translate(x, y)

        return _

    def draw(self, wavelanes: dict, **kwargs) -> str:
        """
        Business function calling all others

        Args:
            wavelanes (dict): parsed dictionary from the input file
            filename (str)  : file name of the output generated file
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
        lkeys, width, height, n = self.size(wavelanes, **kwargs)
        # remove offset for the name in register
        if is_reg:
            height += (n + 1) * 12
        # consider padding of root
        root_style = get_style("root")
        val_top, unit_top = root_style.get("padding-top", (0.0, SizeUnit.PX))
        val_bot, unit_bot = root_style.get("padding-bottom", (0.0, SizeUnit.PX))
        height += (val_top * unit_top.value) + (val_bot * unit_bot.value)
        # select appropriate surface
        w, h = (width + lkeys * 6.5 + 11), height
        if self.extension == "svg":
            self.surface = cairo.SVGSurface(filename, w, h)
        elif self.extension == "png":
            self.surface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32, int(w * self.dpi / 72), int(h * self.dpi / 72)
            )
            sx, sy = self.surface.get_device_scale()
            sx, sy = sx * self.dpi / 72, sy * self.dpi / 72
            self.surface.set_device_scale(sx, sy)
        elif self.extension == "ps":
            self.surface = cairo.PSSurface(filename, w, h)
            self.surface.set_eps(False)
        elif self.extension == "eps":
            self.surface = cairo.PSSurface(filename, w, h)
            self.surface.set_eps(True)
        elif self.extension == "pdf":
            self.surface = cairo.PDFSurface(filename, w, h)
        else:
            log.critical(log.CAIRO_FORMAT % self.extension)
        # offset painting for padding emulation
        self.surface.set_device_offset(0.0, val_top * unit_top.value)
        self.ctx = cairo.Context(self.surface)
        # set background for png image
        if self.extension == "png":
            self.ctx.set_source_rgb(1, 1, 1)
            self.ctx.paint()
        # paint waveforms
        self.wavegroup(
            _id,
            wavelanes,
            brick_width=brick_width,
            brick_height=brick_height,
            width=width,
            height=height,
            offsetx=lkeys * 6.5 + 10,
        )
        self.ctx.show_page()
        # write to an external file for png images
        if self.extension == "png":
            self.surface.write_to_png(filename)
        # otherwise close the file pointer
        else:
            self.surface.finish()
        return ""
