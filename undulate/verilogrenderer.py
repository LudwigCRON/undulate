#!/usr/bin/env python3
# spell-checker: disable

"""
verilogrenderer.py use the logic of renderer.py to render waveforms
into a verilog module for simulation to generate the waveforms
or check the waveform sequence
"""

import os
from os import stat
import undulate
import logging


class VerilogRenderer(undulate.Renderer):
    """
    Render the wavelanes as a verilog module

    only the digital subset is supported for now
    01hlpn.z|x=345
    """

    def __init__(self, **kwargs):
        undulate.Renderer.__init__(self)
        self.signals = []
        self.buffer = []

    def group(self, callback, identifier: str, **kwargs) -> str:
        """
        group define a group

        Args:
            callback (callable): function which populate what inside the group
            identifier (str): unique id for the group
        Returns:
            group of drawable items invoked by callback
        """
        # exclude ticks used for representation only
        if "ticks" in identifier:
            return ""
        self.buffer = []
        callback()
        # if empty group nothing to checkor generate
        if not self.buffer:
            return ""
        signal = {
            "name": identifier.strip().split(" ")[0],
            "waveform": self.buffer,
            "is_dig_sig": all(
                [undulate.BRICKS.is_digital_signal(b.symbol) for b in self.buffer]
            ),
            "is_dig_bus": all(
                [undulate.BRICKS.is_digital_bus(b.symbol) for b in self.buffer]
            ),
            "is_ana_sig": all(
                [undulate.BRICKS.is_analog_signal(b.symbol) for b in self.buffer]
            ),
            "task": "",
        }
        identifier = signal["name"]
        task = ["\ttask gen_chk_%s ();\n" % identifier]
        task.append("\t\tif (chk_%s) #1;\n" % identifier)
        for block in self.buffer:
            task.append("\t\tif (gen_%s) begin\n" % identifier)
            _, steps = VerilogRenderer.render_bricks(block, generate=True, indent_level=3)
            for step in steps:
                task.append(step % identifier)
            task.append("\t\tend\n")
            task.append("\t\tif (chk_%s && %s != 1'bX) begin\n" % (identifier, identifier))
            dx, steps = VerilogRenderer.render_bricks(block, generate=False, indent_level=3)
            for step in steps:
                task.append(step % (identifier, identifier))
            task.append("\t\tend\n")
            task.append("\t\t#(TICK_PERIOD * %.3f);\n" % (dx / block.width))
        task.append("\tendtask\n\n")
        signal["task"] = task
        # check not data mix between digital and analog
        # if analog follow splines and path
        # if digital follow brick_width and type update at each ticks
        # need a VDDA and VSSA real signals if analog detected
        self.signals.append(signal)
        return ""

    def path(self, vertices: list, **kwargs) -> str:
        """
        draw a path to represent common signals

        Args:
            vertices: list of of x-y coordinates in a tuple
        Parameters:
            style_repr (optional) : class of the skin to apply
                by default apply the class 'path'
        """
        return ""

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
        return ""

    def polygon(self, vertices: list, **kwargs) -> str:
        """
        draw a closed shape to represent common data

        Args:
            vertices: list of of (x,y) coordinates in a tuple
        Parameters:
            style_repr (optional) : class of the skin to apply
                by default apply the class None
        """
        return ""

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
        return ""

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
        return ""

    def translate(self, x: float, y: float, **kwargs) -> str:
        """
        translation function that is inherited for svg and eps
        """
        return ""

    def brick(self, symbol: str, b: undulate.Brick, **kwargs) -> str:
        """
        brick generate the symbol for a undulate.Brick element
        (collection of paths, splines, arrows, polygons, text)
        """
        if not symbol in "=234501hlpn|xXz":
            logging.error("Unsupported symbol '%s' in verilog output" % symbol)
            exit(14)
        self.buffer.append(b)
        return ""

    def annotate(self, wavelanes: dict, viewport: tuple, depth: int = 0, **kwargs):
        return ""

    @staticmethod
    def render_bricks(b: undulate.BRICKS, generate: bool = True, indent_level=0):
        last_x, ans = 0, []
        indent = "".join(["\t"] * indent_level)
        if not b or not b.paths:
            return last_x, ans
        if undulate.BRICKS.is_digital_signal(b.symbol):
            for path in b.paths:
                prev_x = 0.0
                for x, y in path[1:-1]:
                    level = (
                        "1'b1"
                        if y < b.height * 0.333
                        else "1'b0"
                        if y > b.height * 0.666
                        else "1'bZ"
                    )
                    dx = (x - prev_x) / b.width
                    if generate:
                        ans.append(
                            "%s#(TICK_PERIOD * %.3f) %%s = %s;\n" % (indent, dx, level)
                        )
                    else:
                        ans.append(
                            (
                                "%s#(TICK_PERIOD * %.3f);\n"
                                "%s\tassert(%%s == %s)\n"
                                "%s\telse `log_Error(\"expect signal '%%s' to be [%s]\");\n"
                            )
                            % (indent, dx, indent, level, indent, level)
                        )
                    prev_x = x
                    last_x = max(last_x, x)
                break
        elif undulate.BRICKS.is_digital_bus(b.symbol):
            for p in b.paths:
                print(p)
        elif undulate.BRICKS.is_analog_signal(b.symbol):
            for p in b.paths:
                print(p)
        else:
            logging.error("'%s' is not a supported brick by this engine" % b.symbol)
        return (b.width - last_x), ans

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
            exit(13)
        self.wavegroup(
            _id,
            wavelanes,
            brick_width=brick_width,
            brick_height=brick_height,
            width=width,
            height=height,
            offsetx=lkeys * 10 + 10,
        )

        with open(filename, "w+") as fp:
            # header
            file_name, _ = os.path.splitext(filename)
            file_name = os.path.basename(file_name)
            fp.write("module %s (\n" % file_name)
            l = len(self.signals)
            for i, signal in enumerate(self.signals):
                is_last = i >= l - 1
                fp.write("\tinout\twire\t\t\t%s,\n" % signal.get("name"))
                fp.write("\tinput\twire\t\t\tgen_%s,\n" % signal.get("name"))
                fp.write(
                    "\tinput\twire\t\t\tchk_%s%s\n"
                    % (signal.get("name"), "" if is_last else ",")
                )
            fp.write(");\n")

            # task definitions
            for signal in self.signals:
                fp.writelines(signal.get("task"))

            # triggers
            for signal in self.signals:
                fp.write("\twire new_op_%s;\n" % signal["name"])
                fp.write(
                    "\tassign new_op_%s = gen_%s | chk_%s;\n"
                    % (signal["name"], signal["name"], signal["name"])
                )
                fp.write("\talways @(posedge new_op_%s)\n" % signal["name"])
                fp.write("\t\tgen_chk_%s();\n\n" % signal["name"])
            fp.write("endmodule")