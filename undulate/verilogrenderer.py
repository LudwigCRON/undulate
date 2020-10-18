#!/usr/bin/env python3
# spell-checker: disable

"""
verilogrenderer.py use the logic of renderer.py to render waveforms
into a verilog module for simulation to generate the waveforms
or check the waveform sequence
"""

import logging
from .renderer import Renderer, svg_curve_convert


class VerilogRenderer(Renderer):
    """
    Render the wavelanes as a verilog module

    only the digital subset is supported for now
    01hlpn.z|x=345
    """

    def __init__(self, **kwargs):
        Renderer.__init__(self)

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
        # cannot generate a register checker or generation
        if is_reg:
            logging.fatal("Cannot generate a register checker or stimuli")
