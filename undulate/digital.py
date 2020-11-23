#!/usr/bin/env python3
# spell-checker: disable

"""
digital.py declare the basic building block
to generate a digital waveform
"""

import math
import undulate


class Nclk(undulate.Brick):
    """
    Falling edge clock with/without arrow

    Parameters:
        add_arrow (bool): by default False
        slewing (float): limit the slope
        duty_cycle (float > 0): between 0 and 1
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        self.first_y = self.height
        if self.is_first:
            self.last_y = 0
        else:
            self.last_y = self.height / 2 if self.last_y is None else self.last_y
        dt = abs(self.height - self.last_y) * self.slewing / self.height
        # add shape
        self.paths.append(
            [
                "path",
                (0, self.last_y),
                (dt, self.height),
                (self.width * self.duty_cycle - self.slewing / 2, self.height),
                (self.width * self.duty_cycle + self.slewing / 2, 0),
                (self.width - self.slewing / 2, 0),
                (self.width, self.height / 2),
            ]
        )
        # add arrow
        if kwargs.get("add_arrow", False) and not self.ignore_transition:
            arrow_angle = -math.atan2(-self.height, self.slewing) * 180 / math.pi
            self.arrows.append(
                (
                    "arrow",
                    dt * (self.height / 2 - self.last_y) / self.height,
                    self.height / 2,
                    arrow_angle,
                )
            )


class Pclk(undulate.Brick):
    """
    Rising edge clock with arrow

    Parameters:
        add_arrow (bool): by default False
        slewing (float): limit the slope
        duty_cycle (float > 0): between 0 and 1
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        self.first_y = 0
        if self.is_first:
            self.last_y = self.height
        else:
            self.last_y = self.last_y if self.last_y else self.height / 2
        dt = self.last_y * self.slewing / self.height
        # add shape
        self.paths.append(
            [
                "path",
                (0, self.last_y),
                (dt, 0),
                (self.width * self.duty_cycle - self.slewing / 2, 0),
                (self.width * self.duty_cycle + self.slewing / 2, self.height),
                (self.width - self.slewing / 2, self.height),
                (self.width, self.height / 2),
            ]
        )
        # add arrow
        if kwargs.get("add_arrow", False) and not self.ignore_transition:
            arrow_angle = math.atan2(-self.height, self.slewing) * 180 / math.pi
            self.arrows.append(
                (
                    "arrow",
                    dt * (self.last_y - self.height / 2) / self.height,
                    self.height / 2,
                    arrow_angle,
                )
            )


class Low(undulate.Brick):
    """
    Falling edge clock with arrow and rest at zero

    Parameters:
        add_arrow (bool): by default False
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        self.first_y = self.height
        if self.is_first:
            self.last_y = self.height
            self.slewing = 0
        else:
            self.last_y = self.height if self.last_y is None else self.last_y
        dt = abs(self.height - self.last_y) * self.slewing / self.height
        self.width = max(self.width, dt)
        # add shape
        self.paths.append(
            ["path", (0, self.last_y), (dt, self.height), (self.width, self.height)]
        )
        # add arrow
        if kwargs.get("add_arrow", False) and not self.is_first:
            arrow_angle = -math.atan2(-self.height, self.slewing) * 180 / math.pi
            self.arrows.append(
                (
                    "arrow",
                    dt * (self.height / 2 - self.last_y) / self.height,
                    self.height / 2,
                    arrow_angle,
                )
            )


class High(undulate.Brick):
    """
    Rising edge clock with arrow and rest at one

    Parameters:
        add_arrow (bool): by default False
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        self.first_y = 0
        if self.is_first:
            self.last_y = 0
            self.slewing = 0
        else:
            self.last_y = 0 if self.last_y is None else self.last_y
        dt = self.last_y * self.slewing / self.height
        self.width = max(self.width, dt)
        # add shape
        self.paths.append(["path", (0, self.last_y), (dt, 0), (self.width, 0)])
        # add arrow
        if kwargs.get("add_arrow", False) and not self.is_first:
            arrow_angle = math.atan2(-self.height, self.slewing) * 180 / math.pi
            self.arrows.append(("arrow", dt / 2, self.height / 2, arrow_angle))


class HighZ(undulate.Brick):
    """
    High impedance mode with a reset close to VDD/2

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        self.first_y = self.height / 2
        if self.is_first:
            self.last_y = self.height / 2
        else:
            self.last_y = self.height / 2 if self.last_y is None else self.last_y
        dt = abs(self.height - self.last_y) * self.slewing / self.height
        # add shape
        self.splines.append(
            [
                "path",
                ("M", 0, self.last_y),
                ("C", dt, self.height / 2),
                ("", dt, self.height / 2),
                ("", min(self.width, 20), self.height / 2),
                ("L", self.width, self.height / 2),
            ]
        )


class Zero(undulate.Brick):
    """
    Zero level

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        self.first_y = self.height
        if self.is_first:
            self.last_y = self.height
        else:
            self.last_y = self.height if self.last_y is None else self.last_y
        # add shape
        self.paths.append(
            [
                "path",
                (0, self.last_y),
                (self.slewing / 2, self.last_y if self.is_first else self.height / 2),
                (self.slewing, self.height),
                (self.width, self.height),
            ]
        )


class One(undulate.Brick):
    """
    One level

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        self.first_y = 0
        if self.is_first:
            self.last_y = 0
        else:
            self.last_y = 0 if self.last_y is None else self.last_y
        # add shape
        self.paths.append(
            [
                "path",
                (0, self.last_y),
                (self.slewing / 2, self.last_y if self.is_first else self.height / 2),
                (self.slewing, 0),
                (self.width, 0),
            ]
        )


class Garbage(undulate.Brick):
    """
    Unknown state for data

    Parameters:
        slewing (float): limit the slope
        follow_data (bool): data '=' occurs before this brick
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        follow_data = kwargs.get("follow_data", False)
        self.last_y = self.height / 2 if self.last_y is None else self.last_y
        if self.ignore_transition:
            self.ignore_start_transition = True
            self.ignore_end_transition = True
        # add shape
        if follow_data:
            self.paths.append(
                [
                    "path",
                    (self.slewing, self.last_y if not self.ignore_start_transition else 0),
                    (0, 0),
                    (self.width - self.slewing, 0),
                    (self.width, self.height / 2 if not self.ignore_end_transition else 0),
                ]
            )
            self.paths.append(
                [
                    "path",
                    (
                        self.slewing,
                        self.last_y if not self.ignore_start_transition else self.height,
                    ),
                    (0, self.height),
                    (self.width - self.slewing, self.height),
                    (self.width, self.height / 2 if not self.ignore_end_transition else 0),
                ]
            )
        else:
            self.paths.append(
                [
                    "path",
                    (0, self.last_y if not self.ignore_start_transition else 0),
                    (self.slewing if not self.ignore_start_transition else 0, 0),
                    (self.width, 0),
                    (
                        self.width - self.slewing,
                        self.height / 2 if not self.ignore_end_transition else 0,
                    ),
                ]
            )
            self.paths.append(
                [
                    "path",
                    (0, self.last_y if not self.ignore_start_transition else self.height),
                    (self.slewing if not self.ignore_start_transition else 0, self.height),
                    (self.width, self.height),
                    (
                        self.width - self.slewing,
                        self.height / 2 if not self.ignore_end_transition else 0,
                    ),
                ]
            )
        # add background
        if follow_data:
            self.polygons.append(
                [
                    "hatch",
                    (self.slewing, self.last_y),
                    (0, 0),
                    (
                        self.width - self.slewing
                        if not self.ignore_end_transition
                        else self.width,
                        0,
                    ),
                    (self.width, self.height / 2 if not self.ignore_end_transition else 0),
                    (
                        self.width - self.slewing
                        if not self.ignore_end_transition
                        else self.width,
                        self.height,
                    ),
                    (0, self.height),
                    (self.slewing, self.last_y),
                ]
            )
        else:
            self.polygons.append(
                [
                    "hatch",
                    (0, self.last_y),
                    (self.slewing if not self.ignore_start_transition else 0, 0),
                    (self.width if not self.ignore_end_transition else self.width, 0),
                    (
                        self.width - self.slewing,
                        self.height / 2 if not self.ignore_end_transition else 0,
                    ),
                    (
                        self.width if not self.ignore_end_transition else self.width,
                        self.height,
                    ),
                    (self.slewing if not self.ignore_start_transition else 0, self.height),
                    (0, self.last_y),
                ]
            )


class Data(undulate.Brick):
    """
    Multibits value such as a Bus

    Parameters:
        slewing (float): limit the slope
        style (str): from 2 to 5, by default s2
            it applies a specific background color
        unknown (bool): if unknown apply specific background
            typical use case if for 'x'
    """

    def __init__(self, unknown: bool = False, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        self.last_y = self.height / 2 if self.last_y is None else self.last_y
        if self.ignore_transition:
            self.ignore_start_transition = True
            self.ignore_end_transition = True
        follow_x = kwargs.get("follow_x", False)
        # add shape
        if self.is_first:
            self.paths.append(
                [
                    "path",
                    (0, 0),
                    (self.slewing, 0),
                    (self.width - self.slewing, 0),
                    (self.width, self.height / 2 if not self.ignore_end_transition else 0),
                ]
            )
            self.paths.append(
                [
                    "path",
                    (0, self.height),
                    (self.slewing, self.height),
                    (self.width - self.slewing, self.height),
                    (
                        self.width,
                        self.height / 2 if not self.ignore_end_transition else self.height,
                    ),
                ]
            )
        else:
            self.paths.append(
                [
                    "path",
                    (
                        -self.slewing if follow_x else 0,
                        self.last_y if not self.ignore_start_transition else 0,
                    ),
                    (0 if follow_x else self.slewing, 0),
                    (self.width - self.slewing, 0),
                    (self.width, self.height / 2 if not self.ignore_end_transition else 0),
                ]
            )
            self.paths.append(
                [
                    "path",
                    (
                        -self.slewing if follow_x else 0,
                        self.last_y if not self.ignore_start_transition else self.height,
                    ),
                    (0 if follow_x else self.slewing, self.height),
                    (self.width - self.slewing, self.height),
                    (
                        self.width,
                        self.height / 2 if not self.ignore_end_transition else self.height,
                    ),
                ]
            )
        # add background
        style = "hatch" if unknown else "%s-polygon" % kwargs.get("style", "")
        if self.is_first:
            self.polygons.append(
                [
                    style,
                    (0, 0),
                    (self.slewing, 0),
                    (self.width - self.slewing, 0),
                    (self.width, self.height / 2 if not self.ignore_end_transition else 0),
                    (
                        self.width - self.slewing
                        if not self.ignore_end_transition
                        else self.width,
                        self.height,
                    ),
                    (self.slewing, self.height),
                    (0, self.height),
                ]
            )
        else:
            self.polygons.append(
                [
                    style,
                    (
                        -self.slewing if follow_x else 0,
                        self.last_y if not self.ignore_start_transition else 0,
                    ),
                    (
                        self.slewing
                        if not self.ignore_start_transition and not follow_x
                        else 0,
                        0,
                    ),
                    (
                        self.width - self.slewing
                        if not self.ignore_end_transition
                        else self.width,
                        0,
                    ),
                    (self.width, self.height / 2 if not self.ignore_end_transition else 0),
                    (
                        self.width - self.slewing
                        if not self.ignore_end_transition
                        else self.width,
                        self.height,
                    ),
                    (
                        self.slewing
                        if not self.ignore_start_transition and not follow_x
                        else 0,
                        self.height,
                    ),
                    (
                        -self.slewing if follow_x else 0,
                        self.last_y if not self.ignore_start_transition else self.height,
                    ),
                ]
            )
        # add text
        if not unknown and not kwargs.get("hide_data", False):
            self.texts.append(
                ("data", self.width / 2, self.height / 2, kwargs.get("data", ""))
            )


class Gap(undulate.Brick):
    """
    single line time compression
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        # if self.is_first:
        # raise "a gap cannot be first in a wavelane"
        self.splines.append(
            [
                "hide",
                ("M", 0, self.height + 2),
                ("C", 5, self.height + 2),
                ("", 5, -4),
                ("", 10, -4),
                ("L", 7, 0),
                ("C", 2, 0),
                ("", 2, self.height + 4),
                ("", -3, self.height + 4),
                ("z", "", ""),
            ]
        )
        self.splines.append(
            [
                "path",
                ("M", 0, self.height + 2),
                ("C", 5, self.height + 2),
                ("", 5, -2),
                ("", 10, -2),
            ]
        )
        self.splines.append(
            [
                "path",
                ("M", -3, self.height + 2),
                ("C", 2, self.height + 2),
                ("", 2, -2),
                ("", 7, -2),
            ]
        )


class Up(undulate.Brick):
    """
    RC charging to VDD

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        self.first_y = self.height
        self.last_y = 0.0 if self.last_y is None else self.last_y
        self.splines.append(
            [
                "path",
                ("M", 0, self.last_y),
                ("L", 3, self.last_y),
                ("C", 3 + self.slewing, self.last_y),
                ("", 3 + self.slewing, self.height - self.last_y),
                ("", min(self.width, 20), 0),
                ("L", self.width, 0),
            ]
        )


class Down(undulate.Brick):
    """
    RC discharge to GND

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        self.first_y = self.height
        self.last_y = self.height if self.last_y is None else self.last_y
        self.splines.append(
            [
                "path",
                ("M", 0, self.last_y),
                ("L", 3, self.last_y),
                ("C", 3 + self.slewing, self.last_y),
                ("", 3 + self.slewing, self.height - self.last_y),
                ("", min(self.width, 20), self.height),
                ("L", self.width, self.height),
            ]
        )


class Impulse(undulate.Brick):
    """
    pulse

    Parameters:
        up (bool): True for impulse to up and False for impulse down
        duty_cycle (float): adjust the x position of the impulse
            from 0 to 1, by default 0.5
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        up_pulse = kwargs.get("up", True)
        duty_cycle = kwargs.get("duty_cycle") or 0.0
        self.first_y = self.height if up_pulse else 0
        self.last_y = self.first_y if self.last_y is None or self.is_first else self.last_y
        dt = abs(self.first_y - self.last_y) * self.slewing / self.height
        dt = min(dt, duty_cycle * self.width)
        # add shape
        self.paths.append(
            [
                "path",
                (0, self.last_y),
                (dt, self.first_y),
                (duty_cycle * self.width, self.first_y),
                (duty_cycle * self.width, self.height - self.first_y),
                (duty_cycle * self.width, self.first_y),
                (self.width, self.first_y),
            ]
        )


class Space(undulate.Brick):
    """
    blank
    """

    def __init__(self, **kwargs):
        undulate.Brick.__init__(self, **kwargs)
        self.last_y = self.height if self.last_y is None or self.is_first else self.last_y


def generate_digital_symbol(symbol: str, **kwargs) -> (bool, object):
    """
    define the mapping between the symbol and the brick
    """
    # mapping
    map_dict = {
        # clock signals description (pPnNlLhH)
        # (N|n)clk: falling edge (with|without) arrow for repeated pattern
        undulate.BRICKS.nclk: Nclk,
        undulate.BRICKS.Nclk: Nclk,
        # (P|p)clk: rising edge (with|without) arrow for repeated pattern
        undulate.BRICKS.pclk: Pclk,
        undulate.BRICKS.Pclk: Pclk,
        # (L|l)ow: falling edge (with|without) arrow and stuck
        undulate.BRICKS.low: Low,
        undulate.BRICKS.Low: Low,
        # (H|h)igh: rising edge (with|without) arrow and stuck
        undulate.BRICKS.high: High,
        undulate.BRICKS.High: High,
        # description for data (z01=x)
        undulate.BRICKS.highz: HighZ,
        undulate.BRICKS.zero: Zero,
        undulate.BRICKS.one: One,
        undulate.BRICKS.data: Data,
        undulate.BRICKS.x: lambda **k: Data(unknown=True, **k),
        undulate.BRICKS.X: Garbage,
        # time compression symbol
        undulate.BRICKS.gap: Gap,
        # capacitive charge to 1 or 0
        undulate.BRICKS.up: Up,
        undulate.BRICKS.down: Down,
        # impulse symbol
        undulate.BRICKS.imp: Impulse,
        undulate.BRICKS.Imp: Impulse,
        # space to skip one step
        undulate.BRICKS.space: Space,
    }
    # add arrow and parameters
    if undulate.BRICKS.has_arrow_on_edge(symbol):
        kwargs.update({"add_arrow": True})
    if symbol == undulate.BRICKS.imp:
        kwargs.update({"up": False})
    if symbol == undulate.BRICKS.Imp:
        kwargs.update({"up": True})
    # get factory and generate block
    factory = map_dict.get(symbol, None)
    if callable(factory):
        return factory(**kwargs)
    return None
