"""
termrenderer.py use the logic of renderer.py to render waveforms
into textual representation in the available space
"""

import os
from itertools import tee, islice, chain
from undulate.renderers.renderer import Renderer
from undulate.bricks.generic import Brick, BrickFactory
from typing import Tuple


class TermRenderer(Renderer):
    """
    Render the wavelanes as UTF8/ASCII text
    based on the trce representation of https://github.com/UCSBarchlab/PyRTL

    .. note::
        For now, only black and white representation is supported
    """

    def __init__(self, **kwargs):
        Renderer.__init__(self)
        self.width, self.height = os.get_terminal_size()

    def brick(self, prv: Brick, cur: Brick, nxt: Brick, **kwargs) -> Tuple[float, str]:
        """
        Draw the symbol of a given Brick element
        """
        min_width = 1 if cur.symbol == "x" else 4
        width = max((self.width - self.offsetx) * cur.width / self.draw_width, min_width)
        error_width, width = (width - round(width)) * 8, round(width)
        half_width = width // 2
        sequence = "".join([prv.symbol, cur.symbol, nxt.symbol])
        data = str(cur.args.get("data", "")) or (" " * (width - 1))
        # fill data
        if len(data) < width - 1:
            spaces_left = " " * ((width - 1 - len(data)) // 2)
            spaces_right = " " * (width - 1 - len(data) - len(spaces_left))
            data = spaces_left + data + spaces_right
        else:
            data = data[: width - 1]
        sequences = {
            "0": "\u2581" * width,
            "z": "\u2500" * width,
            "x": "\u2573" * width,
            "1": "\u2594" * width,
            "u": "\u23A7" + "\u2594" * (width - 1),
            "d": "\u23A9" + "\u2581" * (width - 1),
            "m": "\u223F" * (width - 1) + "\u256E",
            "M": "\u223F" * (width - 1) + "\u256F",
            "p": "\u2571"
            + "\u2594" * (half_width - 1)
            + "\u2572"
            + "\u2581" * (width - half_width - 1),
            "n": "\u2572"
            + "\u2581" * (half_width - 1)
            + "\u2571"
            + "\u2594" * (width - half_width - 1),
            "=": "\u276C" + data,
            "00": "\u2581" * width,
            "0z": "\u256D" + "\u2500" * (width - 1),
            "0x": "\u2571" + "\u2573" * (width - 1),
            "01": "\u2571" + "\u2594" * (width - 1),
            "0m": "\u256D" + "\u223F" * (width - 2) + "\u256E",
            "0M": "\u256D" + "\u223F" * (width - 2) + "\u256F",
            "up": "\u2594"
            + "\u2594" * (half_width)
            + "\u2572"
            + "\u2581" * (width - half_width - 1),
            "d1": "\u2571" + "\u2594" * (width - 1),
            "dn": "\u2581"
            + "\u2581" * (half_width - 1)
            + "\u2571"
            + "\u2594" * (width - half_width - 1),
            "0n": "\u2581"
            + "\u2581" * (half_width)
            + "\u2571"
            + "\u2594" * (width - half_width - 1),
            "0=": "\u2571" + data,
            "z0": "\u256E" + "\u2581" * (width - 1),
            "zx": "\u29FC" + "\u2573" * (width - 1),
            "z1": "\u256F" + "\u2594" * (width - 1),
            "zp": "\u256F"
            + "\u2594" * (half_width - 1)
            + "\u2572"
            + "\u2581" * (width - half_width - 1),
            "zn": "\u256E"
            + "\u2581" * (half_width - 1)
            + "\u2571"
            + "\u2594" * (width - half_width - 1),
            "z=": "\u29FC" + data,
            "x0": "\u2572" + "\u2581" * (width - 1),
            "xz": "\u29FD" + "\u2500" * (width - 1),
            "x1": "\u2571" + "\u2594" * (width - 1),
            "xm": "\u2573" + "\u223F" * (width - 2) + "\u256E",
            "xM": "\u2573" + "\u223F" * (width - 2) + "\u256F",
            "x=": "\u2573" + data,
            "10": "\u2572" + "\u2581" * (width - 1),
            "1z": "\u2570" + "\u2500" * (width - 1),
            "1x": "\u2572" + "\u2573" * (width - 1),
            "1m": "\u2570" + "\u223F" * (width - 2) + "\u256E",
            "1M": "\u2570" + "\u223F" * (width - 2) + "\u256F",
            "11": "\u2594" * width,
            "1p": "\u2594"
            + "\u2594" * (half_width - 1)
            + "\u2572"
            + "\u2581" * (width - half_width - 1),
            "1=": "\u2572" + data,
            "p1": "\u2571" + "\u2594" * (width - 1),
            "pz": "\u256D" + "\u2500" * (width - 1),
            "px": "\u2571" + "\u2573" * (width - 1),
            "pd": "\u2581" * width,
            "pm": "\u256D" + "\u223F" * (width - 2) + "\u256E",
            "pM": "\u256D" + "\u223F" * (width - 2) + "\u256F",
            "pn": "\u2581"
            + "\u2581" * (half_width - 1)
            + "\u2571"
            + "\u2594" * (width - half_width - 1),
            "p=": "\u2571" + data,
            "n0": "\u2572" + "\u2581" * (width - 1),
            "np": "\u2594"
            + "\u2594" * (half_width - 1)
            + "\u2572"
            + "\u2581" * (width - half_width - 1),
            "nx": "\u2572" + "\u2573" * (width - 1),
            "nu": "\u2594" * width,
            "nm": "\u2570" + "\u223F" * (width - 2) + "\u256E",
            "nM": "\u2570" + "\u223F" * (width - 2) + "\u256F",
            "n=": "\u2572" + data,
            "mn": "\u2581"
            + "\u2581" * (half_width - 1)
            + "\u2571"
            + "\u2594" * (width - half_width - 1),
            "Mp": "\u2594"
            + "\u2594" * (half_width - 1)
            + "\u2572"
            + "\u2581" * (width - half_width - 1),
            "=0": "\u2572" + "\u2581" * (width - 1),
            "=z": "\u29FD" + "\u2500" * (width - 1),
            "=x": "\u2573" * width,
            "=1": "\u2571" + "\u2594" * (width - 1),
            "==": "\u2573" + data,
        }
        text = sequences.get(
            sequence,
            sequences.get(
                sequence[0:2],
                sequences.get(" " + sequence[1:], sequences.get(cur.symbol, "")),
            ),
        )
        if cur.symbol == "=":
            text = text[0] + "\u001b[47m\u001b[30m" + text[1:] + "\u001b[49m\u001b[39m"
        return (error_width, text)

    def wavelane(self, name: str, wavelane: str, **kwargs) -> str:
        """
        Draw the internal Dict[str, Any] representing a waveform inside a waveform group.

        the internal Dict[str, Any] is expected to have at least the following two keys:

        - name       : name of the waveform
        - wavelane   : string which describes the waveform

        Args:
            name (str): name of the waveform
            wavelane (str): string of symbols describing the waveform
            extra (str): extra information given to self.group()
            y (float): global y position of the wavelane in the drawing context
        """
        offsetx = kwargs.get("offsetx", 0)
        depth = kwargs.get("depth", 0)
        hier_spaces = "  " * max(depth - 1, 0)
        spaces = " " * max(offsetx - len(name) - len(hier_spaces) + 1, 1)
        # display title
        print(f"{hier_spaces}{name}{spaces}", end="")
        # preprocess waveform to simplify it
        _wavelane = self._reduce_wavelane(name, wavelane, [], **kwargs)
        # normalize symbol
        for i, w in enumerate(_wavelane):
            if w.symbol in "=23456789":
                _wavelane[i].symbol = "="
            if w.symbol in "0lL":
                _wavelane[i].symbol = "0"
            if w.symbol in "1hH":
                _wavelane[i].symbol = "1"
            if w.symbol in "nN":
                _wavelane[i].symbol = "n"
            if w.symbol in "pP":
                _wavelane[i].symbol = "p"

        def previous_and_next(some_iterable):
            prevs, items, nexts = tee(some_iterable, 3)
            prevs = chain([BrickFactory.create(" ")], prevs)
            nexts = chain(islice(nexts, 1, None), [BrickFactory.create(" ")])
            return zip(prevs, items, nexts)

        # generate waveform
        wave = []
        width_error = 0.0
        for prv, cur, nxt in previous_and_next(_wavelane):
            # generate the brick and update the width with error
            # committed due to rounding from float to int as in a sigma delta
            cur.width += width_error
            width_error, text = self.brick(prv, cur, nxt, **kwargs)
            wave.append(text)
        # crop wave and replace last char by ellipsis if needed
        wave = "".join(wave)
        nb_ctrl = sum((1 if c == "\u001b" else 0 for c in wave)) * 4
        if len(wave) - nb_ctrl >= self.width - offsetx - 1:
            print(
                wave[: self.width + nb_ctrl - offsetx - 2],
                "\u22EF",
                sep="",
                end="\u001b[49m\u001b[39m\n",
            )
        else:
            print(wave, end="\u001b[49m\u001b[39m\n")

    def wavegroup(self, name: str, wavelanes, depth: int = 1, **kwargs) -> str:
        """
        Draw a group of waveforms

        Args:
            name (str) : name of the waveform group
            wavelanes (Dict[str, dict]): named waveforms composing the group
            depth (int) : depth of nested groups to represent hierarchy
        Parameters:
            config (Dict[str, Any]): config section of the input file
            brick_width (float): width of a brick, default is 20.0
            brick_height (float): height of a brick, default is 20.0
            width (float): image width
            height (float): image height
        """
        # group name:
        #  <signal name>   XXXXXX
        #  <signal name>   XXXXXX
        #  subgroup name:
        #    <signal name> XXXXXX
        if name.strip():
            hier_spaces = "  " * max(depth - 1, 0)
            print(f"{hier_spaces}{name}:")
        for wavename, wavelane in wavelanes.items():
            if "wave" in wavelane:
                wavelane.update(**kwargs)
                wavelane["depth"] = depth + 1
                self.wavelane(wavename, wavelane.get("wave", []), **wavelane)
            else:
                self.wavegroup(wavename, wavelane, depth=depth + 1, **kwargs)

    def depth(self, d):
        if isinstance(d, dict):
            return 1 + (max(map(self.depth, d.values())) if d else 0)
        return 0

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
        _id = kwargs.get("id", "")
        brick_width = kwargs.get("brick_width", 40)
        brick_height = kwargs.get("brick_height", 20)
        # remove group not used for waveform
        wavelanes.pop("annotations", None)
        wavelanes.pop("edges", None)
        wavelanes.pop("edge", None)
        wavelanes.pop("config", None)
        lkeys, width, height, n = self.size(wavelanes, **kwargs)
        self.draw_width = width
        self.offsetx = lkeys + self.depth(wavelanes) * 2
        self.wavegroup(
            _id,
            wavelanes,
            brick_width=brick_width,
            brick_height=brick_height,
            width=width,
            height=height,
            offsetx=self.offsetx,
        )
