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
        self.signals = {}
        self.buffer = []

    @staticmethod
    def _get_signal_width(s: str = "") -> int:
        """
        get width of bus signal in the form
        signal_name[max:min] or
        signal_name[min:max]
        Args:
            s (str): signal name
        Returns:
            int: max-min+1
        """
        if not s or s is None:
            return 0
        if "[" not in s:
            return 1
        i = s.index("[")
        j = s.find(":")
        k = s.find("]")
        a = int(s[i + 1 : j], 10)
        b = int(s[j + 1 : k], 10)
        return max(a, b) - min(a, b) + 1

    @staticmethod
    def _nb_bits(i: int) -> int:
        t, k = i, 0
        while t > 0:
            t = t >> 1
            k += 1
        return k

    @staticmethod
    def _get_data_width(s: str) -> object:
        """
        parse number in the following form:
        - 0x[A-Fa-f0-9]+
        - [A-Fa-f0-9]+h
        - [0-9]*'h[A-Fa-f0-9]+
        - [0-9]+d?
        - 0d[0-9]
        - [0-9]*'d[0-9]+
        - 0b[0-1]+
        - [0-1]+b
        - [0-9]*'b[0-1]+
        Args:
            s (str): data to be parsed
        Returns:
            width (int): number of bits
            data (int): parsed data in decimal format
        """
        s = s.strip()
        start, end, base = 0, 0, 10
        data, width = 0, 0
        if not s or s is None:
            return width, data
        if "'b" in s:
            start, base = s.find("'b") + 2, 2
        elif "'h" in s:
            start, base = s.find("'h") + 2, 16
        elif "'d" in s:
            start, base = s.find("'d") + 2, 10
        elif s[-1] == "d":
            end, base = -1, 10
        elif s[-1] == "b":
            end, base = -1, 2
        elif s[-1] == "h":
            end, base = -1, 16
        if "0b" in s[:2]:
            start, base = 2, 2
        elif "0h" in s[:2] or "0x" in s[:2]:
            start, base = 2, 16
        elif "0d" in s[:2]:
            start, base = 2, 10
        data = int(s[start:end], base) if end != 0 else int(s[start:], base)
        width = int(s[: start - 2], 10) if start > 2 else VerilogRenderer._nb_bits(data)
        return width, data

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
            "width": 1,
            "task": "",
        }
        identifier = signal["name"]
        width = VerilogRenderer._get_signal_width(identifier)
        for block in self.buffer:
            if block.texts:
                w, _ = VerilogRenderer._get_data_width(block.texts[-1][-1])
                width = max(width, w)
        signal["width"] = width
        signal["is_dig_bus"] = signal["is_dig_bus"] or (width > 1)
        # generate the needed task
        task = ["\ttask gen_chk_%s;\n\tbegin\n" % identifier]
        task.append("\t\tif (chk_%s) #1;\n" % identifier)
        for block in self.buffer:
            task.append("\t\tif (gen_%s)\n\t\tbegin\n" % identifier)
            _, steps = VerilogRenderer.render_bricks(block, generate=True, indent_level=3)
            for step in steps:
                l = step.count("%s")
                task.append(step % tuple(identifier for _ in range(l)))
            task.append("\t\tend")
            task.append(
                " else if (chk_%s && %s != 1'bX)\n\t\tbegin\n" % (identifier, identifier)
            )
            dx, steps = VerilogRenderer.render_bricks(block, generate=False, indent_level=3)
            for step in steps:
                l = step.count("%s")
                task.append(step % tuple(identifier for _ in range(l)))
            task.append("\t\tend\n")
            task.append("\t\t#(TICK_PERIOD * %.3f);\n" % (dx / block.width))
        task.append("\tend\n\tendtask\n\n")
        signal["task"] = task
        # check not data mix between digital and analog
        # if analog follow splines and path
        # if digital follow brick_width and type update at each ticks
        # need a VDDA and VSSA real signals if analog detected
        self.signals[signal["name"]] = signal
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
        b.symbol = undulate.BRICKS.from_char(symbol)
        self.buffer.append(b)
        return ""

    def annotate(self, wavelanes: dict, viewport: tuple, depth: int = 0, **kwargs):
        return ""

    @staticmethod
    def render_dig_sig_brick(
        b: undulate.BRICKS, generate: bool = True, indent_level: int = 0
    ):
        """
        Provide the expected sequence to generate the brick in verilog
        or to check the expected sequence.

        Last point of a brick can be changed on fly to ensure a correct
        transition from one brick to another. So provide the penultimate
        x value to allows x-compensation to preserve the correct timing.

        Args:
            b (undulate.BRICKS) : brick with paths and symbol information
            generate (boolean)  : sequence generation or assertion
            indent_level (int)  : number of \\t for pretty printing
        Returns:
            last_x (float): for x-compensation
            ans (list[str]): verilog description
        """
        last_x, ans = 0, []
        indent = "".join(["\t"] * indent_level)
        # process the first and only path
        prev_x = 0.0
        for x, y in b.paths[0][1:-1]:
            level = (
                "1'b1"
                if y < b.height * 0.333
                else "1'b0"
                if y > b.height * 0.666
                else "1'bZ"
            )
            dx = (x - prev_x) / b.width
            if generate:
                ans.append("%s#(TICK_PERIOD * %.3f) %%s_o = %s;\n" % (indent, dx, level))
            else:
                ans.append(
                    (
                        "%s#(TICK_PERIOD * %.3f);\n"
                        "%s\tif (%%s !== %s)\n"
                        "%s\t\t`log_Error(\"expect signal '%%s' to be [%s]\");\n"
                    )
                    % (indent, dx, indent, level, indent, level)
                )
            prev_x = x
            last_x = max(last_x, x)
        return last_x, ans

    @staticmethod
    def render_dig_bus_brick(
        b: undulate.BRICKS,
        bus_width: int = 16,
        generate: bool = True,
        indent_level: int = 0,
    ):
        """
        Provide the expected sequence to generate the brick in verilog
        or to check the expected sequence.

        Last point of a brick can be changed on fly to ensure a correct
        transition from one brick to another. So provide the penultimate
        x value to allows x-compensation to preserve the correct timing.

        Args:
            b (undulate.BRICKS) : brick with data and symbol information
            bus_width (int)     : width of the bus for data size
            generate (boolean)  : sequence generation or assertion
            indent_level (int)  : number of \\t for pretty printing
        Returns:
            last_x (float): for x-compensation
            ans (list[str]): verilog description
        """
        last_x, ans = 0, []
        indent = "".join(["\t"] * indent_level)
        # get the maximum width
        dx = 999.0
        for p in b.paths:
            for x, _ in p[1:]:
                last_x = max(last_x, x)
                dx = min(dx, x)
        # get the data or set it to X
        level = "%d'h" % bus_width
        level += "".join(["X"] * max(1, bus_width // 4))
        if b.texts:
            _, d = w, _ = VerilogRenderer._get_data_width(b.texts[-1][-1])
            level = "%d'h%s" % (bus_width, hex(d)[2:])
        if generate:
            ans.append("%s#(TICK_PERIOD * %.3f) %%s_o = %s;\n" % (indent, dx, level))
        else:
            ans.append("%s#(TICK_PERIOD * %.3f);\n" % (indent, dx))
            if "x" not in level and "X" not in level:
                ans.append(
                    (
                        "%s\tif (%%s !== %s)\n"
                        "%s\t\t`log_Error(\"expect data '%%s' to be [%s]\");\n"
                    )
                    % (indent, level, indent, level)
                )
        return last_x, ans

    @staticmethod
    def render_bricks(
        b: undulate.BRICKS, bus_width: int = 1, generate: bool = True, indent_level=0
    ):
        last_x, ans = 0, []
        # if the brick is not supported return an empty sequence
        if not b or not b.paths:
            return last_x, ans
        if undulate.BRICKS.is_digital_signal(b.symbol) and bus_width <= 1:
            last_x, ans = VerilogRenderer.render_dig_sig_brick(b, generate, indent_level)
        elif undulate.BRICKS.is_digital_bus(b.symbol):
            last_x, ans = VerilogRenderer.render_dig_bus_brick(
                b, bus_width, generate, indent_level
            )
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
            fp.write("module %s #(\n" % file_name)
            fp.write("\tparameter realtime TICK_PERIOD = 16ns\n")
            fp.write(") (\n")
            l = len(self.signals.keys())
            for i, signal_name in enumerate(self.signals.keys()):
                is_last = i >= l - 1
                fp.write("\tinout\twire\t\t\t%s,\n" % signal_name)
                fp.write("\tinput\twire\t\t\tgen_%s,\n" % signal_name)
                fp.write(
                    "\tinput\twire\t\t\tchk_%s%s\n" % (signal_name, "" if is_last else ",")
                )
            fp.write(");\n")

            # output definition
            fp.write("\n\t//==== output register ====\n")
            for signal_name in self.signals.keys():
                fp.write("\treg %s_o;\n" % signal_name)

            # inout connection
            fp.write("\n\t//==== inout connections ====\n")
            for signal_name in self.signals.keys():
                fp.write(
                    "\tassign %s = (gen_%s) ? %s_o : 'z;\n"
                    % (signal_name, signal_name, signal_name)
                )

            # task definitions
            fp.write("\n\t//==== tasks ====\n")
            for signal in self.signals.values():
                fp.writelines(signal.get("task"))

            # triggers
            fp.write("\n\t//==== triggers ====\n")
            for signal_name in self.signals.keys():
                fp.write("\twire new_op_%s;\n" % signal_name)
                fp.write(
                    "\tassign new_op_%s = gen_%s | chk_%s;\n"
                    % (signal_name, signal_name, signal_name)
                )
                fp.write("\talways @(posedge new_op_%s)\n" % signal_name)
                fp.write("\t\tgen_chk_%s();\n\n" % signal_name)
            fp.write("endmodule")