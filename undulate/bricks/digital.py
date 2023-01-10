"""
digital.py declare the basic building block
to generate a digital waveform
"""
# TODO: migrate Garbage follow_data to generic custom filtering functions

import math
import undulate.logger as log
from undulate.bricks.generic import (
    ArrowDescription,
    Brick,
    BrickFactory,
    Drawable,
    FilterBank,
    Point,
    SplineSegment,
)
from typing import List

# ======== Brick Definition ========


class Nclk(Brick):
    """
    Falling edge clock without arrow

    Parameters:
        slewing (float): limit the slope
        duty_cycle (float > 0): between 0 and 1
    """

    def __init__(self, **kwargs) -> None:
        Brick.__init__(self, **kwargs)
        duty_cycle = kwargs.get("duty_cycle", 0.5)
        if self.ignore_end_transition:
            self.first_y = 0.0
        elif math.isnan(self.first_y):
            self.first_y = self.height / 2
        if self.is_first:
            self.last_y = 0.0
        elif math.isnan(self.last_y):
            self.last_y = self.height / 2
        self.dt = abs(self.height - self.last_y) * self.slewing / self.height
        # add shape
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0.0, self.last_y),
                    Point(self.dt, self.height),
                    Point(self.width * duty_cycle - self.slewing / 2, self.height),
                    Point(self.width * duty_cycle + self.slewing / 2, 0.0),
                    Point(self.width - self.slewing / 2, 0),
                    Point(self.width, self.first_y),
                ],
            )
        )


class NclkArrow(Nclk):
    """
    Falling edge clock with arrow

    Parameters:
        slewing (float): limit the slope
        duty_cycle (float > 0): between 0 and 1
    """

    def __init__(self, **kwargs) -> None:
        Nclk.__init__(self, **kwargs)
        # add arrow
        arrow_angle = -math.atan2(-self.height, self.slewing) * 180 / math.pi
        self.arrows.append(
            Drawable(
                "arrow",
                ArrowDescription(
                    self.dt * (self.height / 2 - self.last_y) / self.height,
                    self.height / 2,
                    arrow_angle,
                ),
            )
        )


class Pclk(Brick):
    """
    Rising edge clock without arrow

    Parameters:
        slewing (float): limit the slope
        duty_cycle (float > 0): between 0 and 1
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        duty_cycle = kwargs.get("duty_cycle", 0.5)
        if self.ignore_end_transition:
            self.first_y = self.height
        elif math.isnan(self.first_y):
            self.first_y = self.height / 2
        if self.is_first:
            self.last_y = self.height
        elif math.isnan(self.last_y):
            self.last_y = self.height / 2
        self.dt = self.last_y * self.slewing / self.height
        # add shape
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0.0, self.last_y),
                    Point(self.dt, 0.0),
                    Point(self.width * duty_cycle - self.slewing / 2, 0.0),
                    Point(self.width * duty_cycle + self.slewing / 2, self.height),
                    Point(self.width - self.slewing / 2, self.height),
                    Point(self.width, self.first_y),
                ],
            )
        )


class PclkArrow(Pclk):
    """
    Rising edge clock with arrow

    Parameters:
        slewing (float): limit the slope
        duty_cycle (float > 0): between 0 and 1
    """

    def __init__(self, **kwargs) -> None:
        Pclk.__init__(self, **kwargs)
        # add arrow
        if self.ignore_start_transition:
            return None
        arrow_angle = math.atan2(-self.height, self.slewing) * 180 / math.pi
        self.arrows.append(
            Drawable(
                "arrow",
                ArrowDescription(
                    self.dt * (self.last_y - self.height / 2) / self.height,
                    self.height / 2,
                    arrow_angle,
                ),
            )
        )


class Low(Brick):
    """
    Falling edge clock and rest at zero

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs) -> None:
        Brick.__init__(self, **kwargs)
        self.first_y = self.height
        if self.is_first:
            self.last_y = self.height
        elif self.ignore_start_transition:
            self.last_y = self.height
        elif math.isnan(self.last_y):
            self.last_y = self.height
        self.dt = abs(self.height - self.last_y) * self.slewing / self.height
        # add shape
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0, self.last_y),
                    Point(self.dt, self.height),
                    Point(self.width, self.height),
                ],
            )
        )


class LowArrow(Low):
    """
    Falling edge clock with arrow and rest at zero

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs) -> None:
        Low.__init__(self, **kwargs)
        # add arrow
        if self.is_first or self.ignore_start_transition:
            return None
        arrow_angle = -math.atan2(-self.height, self.slewing) * 180 / math.pi
        self.arrows.append(
            Drawable(
                "arrow",
                ArrowDescription(
                    self.dt * (self.height / 2 - self.last_y) / self.height,
                    self.height / 2,
                    arrow_angle,
                ),
            )
        )


class High(Brick):
    """
    Rising edge clock and rest at one

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        self.first_y = 0.0
        if self.is_first:
            self.last_y = 0.0
        elif self.ignore_start_transition:
            self.last_y = 0.0
        elif math.isnan(self.last_y):
            self.last_y = 0.0
        self.dt = self.last_y * self.slewing / self.height
        # add shape
        self.paths.append(
            Drawable(
                "path",
                [Point(0.0, self.last_y), Point(self.dt, 0.0), Point(self.width, 0.0)],
            )
        )


class HighArrow(High):
    """
    Rising edge clock with arrow and rest at one

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        High.__init__(self, **kwargs)
        # add arrow
        if self.is_first or self.ignore_start_transition:
            return None
        arrow_angle = math.atan2(-self.height, self.slewing) * 180 / math.pi
        self.arrows.append(
            Drawable("arrow", ArrowDescription(self.dt / 2, self.height / 2, arrow_angle))
        )


class HighZ(Brick):
    """
    High impedance mode with a reset close to VDD/2

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        self.first_y = self.height / 2
        if self.is_first or math.isnan(self.last_y):
            self.last_y = self.height / 2
        self.dt = abs(self.height - self.last_y) * self.slewing / self.height
        # add shape
        self.splines.append(
            Drawable(
                "path",
                [
                    SplineSegment("M", 0.0, self.last_y),
                    SplineSegment("C", self.dt, self.height / 2),
                    SplineSegment("", self.dt, self.height / 2),
                    SplineSegment("", min(self.width, 20.0), self.height / 2),
                    SplineSegment("L", self.width, self.height / 2),
                ],
            )
        )


class Zero(Brick):
    """
    Zero level

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        self.first_y = self.height
        if self.is_first:
            self.last_y = self.height
        elif self.ignore_start_transition:
            self.last_y = self.height
        elif math.isnan(self.last_y):
            self.last_y = self.height / 2
        # add shape
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0.0, self.last_y),
                    Point(self.slewing / 2, self.last_y),
                    Point(self.slewing, self.height),
                    Point(self.width, self.height),
                ],
            )
        )


class One(Brick):
    """
    One level

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        self.first_y = 0.0
        if self.is_first:
            self.last_y = 0.0
        elif self.ignore_start_transition:
            self.last_y = 0.0
        elif math.isnan(self.last_y):
            self.last_y = self.height / 2
        # add shape
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0.0, self.last_y),
                    Point(self.slewing / 2, self.last_y),
                    Point(self.slewing, 0.0),
                    Point(self.width, 0.0),
                ],
            )
        )


class Garbage(Brick):
    """
    Unknown state for data

    Parameters:
        slewing (float): limit the slope
        follow_data (bool): data '=' occurs before this brick
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        follow_data = kwargs.get("follow_data", False)
        if math.isnan(self.last_y):
            self.last_y = self.height / 2
        # add shape
        if follow_data:
            self.paths.append(
                Drawable(
                    "path",
                    [
                        Point(
                            self.slewing,
                            self.last_y if not self.ignore_start_transition else 0.0,
                        ),
                        Point(0.0, 0.0),
                        Point(self.width - self.slewing, 0.0),
                        Point(
                            self.width,
                            self.height / 2 if not self.ignore_end_transition else 0.0,
                        ),
                    ],
                )
            )
            self.paths.append(
                Drawable(
                    "path",
                    [
                        Point(
                            self.slewing,
                            self.last_y
                            if not self.ignore_start_transition
                            else self.height,
                        ),
                        Point(0.0, self.height),
                        Point(self.width - self.slewing, self.height),
                        Point(
                            self.width,
                            self.height / 2 if not self.ignore_end_transition else 0.0,
                        ),
                    ],
                )
            )
        else:
            self.paths.append(
                Drawable(
                    "path",
                    [
                        Point(
                            0.0, self.last_y if not self.ignore_start_transition else 0.0
                        ),
                        Point(
                            self.slewing if not self.ignore_start_transition else 0.0, 0.0
                        ),
                        Point(self.width, 0.0),
                        Point(
                            self.width - self.slewing,
                            self.height / 2 if not self.ignore_end_transition else 0.0,
                        ),
                    ],
                )
            )
            self.paths.append(
                Drawable(
                    "path",
                    [
                        Point(
                            0.0,
                            self.last_y
                            if not self.ignore_start_transition
                            else self.height,
                        ),
                        Point(
                            self.slewing if not self.ignore_start_transition else 0.0,
                            self.height,
                        ),
                        Point(self.width, self.height),
                        Point(
                            self.width - self.slewing,
                            self.height / 2 if not self.ignore_end_transition else 0.0,
                        ),
                    ],
                )
            )
        # add background
        if follow_data:
            self.polygons.append(
                Drawable(
                    "hatch",
                    [
                        Point(self.slewing, self.last_y),
                        Point(0.0, 0.0),
                        Point(
                            self.width - self.slewing
                            if not self.ignore_end_transition
                            else self.width,
                            0.0,
                        ),
                        Point(
                            self.width,
                            self.height / 2 if not self.ignore_end_transition else 0.0,
                        ),
                        Point(
                            self.width - self.slewing
                            if not self.ignore_end_transition
                            else self.width,
                            self.height,
                        ),
                        Point(0.0, self.height),
                        Point(self.slewing, self.last_y),
                    ],
                )
            )
        else:
            self.polygons.append(
                Drawable(
                    "hatch",
                    [
                        Point(0.0, self.last_y),
                        Point(
                            self.slewing if not self.ignore_start_transition else 0.0, 0.0
                        ),
                        Point(
                            self.width if not self.ignore_end_transition else self.width,
                            0.0,
                        ),
                        Point(
                            self.width - self.slewing,
                            self.height / 2 if not self.ignore_end_transition else 0.0,
                        ),
                        Point(
                            self.width if not self.ignore_end_transition else self.width,
                            self.height,
                        ),
                        Point(
                            self.slewing if not self.ignore_start_transition else 0.0,
                            self.height,
                        ),
                        Point(0, self.last_y),
                    ],
                )
            )


class Data(Brick):
    """
    Multibits value such as a Bus

    Parameters:
        slewing (float): limit the slope
        style (str): from s2 to s9-polygon or hatch, by default s2-polygon
        hide_data (bool): prevent the display of the associated data
    """

    def __init__(self, style: str = "s2-polygon", **kwargs):
        Brick.__init__(self, **kwargs)
        hide_data = kwargs.get("hide_data", False)
        if math.isnan(self.first_y):
            self.first_y = self.height / 2
        if math.isnan(self.last_y):
            self.last_y = self.height / 2
        # add shape
        _tmp = []
        if self.is_first:
            _tmp = [
                Point(0.0, 0.0),
                Point(self.width - self.slewing, 0.0),
                Point(
                    self.width,
                    0.0 if self.ignore_end_transition else self.first_y,
                ),
                Point(self.width - self.slewing, self.height),
                Point(0.0, self.height),
            ]
        else:
            _tmp = [
                Point(
                    0.0,
                    self.last_y if not self.ignore_start_transition else 0.0,
                ),
                Point(self.slewing, 0.0),
                Point(self.width - self.slewing, 0.0),
                Point(
                    self.width,
                    0.0 if self.ignore_end_transition else self.first_y,
                ),
                Point(
                    self.width,
                    self.height if self.ignore_end_transition else self.first_y,
                ),
                Point(self.width - self.slewing, self.height),
                Point(self.slewing, self.height),
                Point(
                    0.0,
                    self.last_y if not self.ignore_start_transition else self.height,
                ),
            ]
        if self.ignore_end_transition:
            self.paths.append(Drawable("path", _tmp[: len(_tmp) // 2]))
            self.paths.append(Drawable("path", _tmp[len(_tmp) // 2 :]))
        else:
            self.paths.append(Drawable("path", _tmp))
        # add background
        self.polygons.append(Drawable(style, _tmp))
        # add text
        if not hide_data:
            self.texts.append(
                Drawable("data", (self.width / 2, self.height / 2, kwargs.get("data", "")))
            )


class Two(Data):
    """
    Variant of Data with a css rule '.s2-polygon'
    """

    def __init__(self, **kwargs):
        Data.__init__(self, style="s2-polygon", **kwargs)


class Three(Data):
    """
    Variant of Data with a css rule '.s3-polygon'
    """

    def __init__(self, **kwargs):
        Data.__init__(self, style="s3-polygon", **kwargs)


class Four(Data):
    """
    Variant of Data with a css rule '.s4-polygon'
    """

    def __init__(self, **kwargs):
        Data.__init__(self, style="s4-polygon", **kwargs)


class Five(Data):
    """
    Variant of Data with a css rule '.s5-polygon'
    """

    def __init__(self, **kwargs):
        Data.__init__(self, style="s5-polygon", **kwargs)


class Six(Data):
    """
    Variant of Data with a css rule '.s6-polygon'
    """

    def __init__(self, **kwargs):
        Data.__init__(self, style="s6-polygon", **kwargs)


class Seven(Data):
    """
    Variant of Data with a css rule '.s7-polygon'
    """

    def __init__(self, **kwargs):
        Data.__init__(self, style="s7-polygon", **kwargs)


class Eight(Data):
    """
    Variant of Data with a css rule '.s8-polygon'
    """

    def __init__(self, **kwargs):
        Data.__init__(self, style="s8-polygon", **kwargs)


class Nine(Data):
    """
    Variant of Data with a css rule '.s9-polygon'
    """

    def __init__(self, **kwargs):
        Data.__init__(self, style="s9-polygon", **kwargs)


class Unknown(Data):
    """
    Variant of Data with a css rule '.hatch'
    """

    def __init__(self, **kwargs):
        kwargs.update({"hide_data": True})
        Data.__init__(self, style="hatch", **kwargs)


class Gap(Brick):
    """
    single line time compression

    Its position inside a brick, similarly to a duty cycle for a clock,
    can be adjusted globally with the property 'gap_offset' in the
    'config' section. The a value is a float in the ]0-1[ range.

    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        # if self.is_first:
        # raise "a gap cannot be first in a wavelane"
        self.splines.append(
            Drawable(
                "hide",
                [
                    SplineSegment("M", -4, self.height + 2),
                    SplineSegment("C", -4, self.height + 2),
                    SplineSegment("", -2, self.height + 2),
                    SplineSegment("", -2, self.height / 2),
                    SplineSegment("C", -2, self.height / 2),
                    SplineSegment("", -2, -2),
                    SplineSegment("", 0, -2),
                    SplineSegment("L", 4, -2),
                    SplineSegment("C", 4, -2),
                    SplineSegment("", 2, -2),
                    SplineSegment("", 2, self.height / 2),
                    SplineSegment("C", 2, self.height / 2),
                    SplineSegment("", 2, self.height + 2),
                    SplineSegment("", 0, self.height + 2),
                    SplineSegment("z", 0, 0),
                ],
            )
        )
        self.splines.append(
            Drawable(
                "path",
                [
                    SplineSegment("M", -4, self.height + 2),
                    SplineSegment("C", -4, self.height + 2),
                    SplineSegment("", -2, self.height + 2),
                    SplineSegment("", -2, self.height / 2),
                    SplineSegment("C", -2, self.height / 2),
                    SplineSegment("", -2, -2),
                    SplineSegment("", 0, -2),
                ],
            )
        )
        self.splines.append(
            Drawable(
                "path",
                [
                    SplineSegment("M", 0, self.height + 2),
                    SplineSegment("C", 0, self.height + 2),
                    SplineSegment("", 2, self.height + 2),
                    SplineSegment("", 2, self.height / 2),
                    SplineSegment("C", 2, self.height / 2),
                    SplineSegment("", 2, -2),
                    SplineSegment("", 4, -2),
                ],
            )
        )


class Up(Brick):
    """
    RC charging to VDD

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        self.first_y = self.height
        if math.isnan(self.last_y):
            self.last_y = self.height / 2
        self.dt = abs(self.first_y - self.last_y) * self.slewing / self.height
        self.splines.append(
            Drawable(
                "path",
                [
                    SplineSegment("M", 0, self.last_y),
                    SplineSegment("C", 0, self.last_y),
                    SplineSegment("", self.dt, 0),
                    SplineSegment("", min(self.width, 20), 0),
                    SplineSegment("L", self.width, 0),
                ],
            )
        )


class Down(Brick):
    """
    RC discharge to GND

    Parameters:
        slewing (float): limit the slope
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        self.first_y = self.height
        if math.isnan(self.last_y):
            self.last_y = self.height / 2
        self.dt = abs(self.first_y - self.last_y) * self.slewing / self.height
        self.splines.append(
            Drawable(
                "path",
                [
                    SplineSegment("M", 0, self.last_y),
                    SplineSegment("C", 0, self.last_y),
                    SplineSegment("", self.dt, self.height),
                    SplineSegment("", min(self.width, 20), self.height),
                    SplineSegment("L", self.width, self.height),
                ],
            )
        )


class ImpulseUp(Brick):
    """
    pulse from GND to VDD

    Parameters:
        duty_cycle (float): adjust the x position of the impulse
            from 0 to 1, by default 0.5
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        duty_cycle = kwargs.get("duty_cycle", 0.5)
        self.first_y = 0.0
        if self.is_first or math.isnan(self.last_y):
            self.last_y = self.first_y
        self.dt = abs(self.first_y - self.last_y) * self.slewing / self.height
        self.dt = min(self.dt, duty_cycle * self.width)
        # add shape
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0.0, self.last_y),
                    Point(self.dt, self.first_y),
                    Point(duty_cycle * self.width, self.first_y),
                    Point(duty_cycle * self.width, self.height - self.first_y),
                    Point(duty_cycle * self.width, self.first_y),
                    Point(self.width, self.first_y),
                ],
            )
        )


class ImpulseDown(Brick):
    """
    pulse from VDD to GND

    Parameters:
        duty_cycle (float): adjust the x position of the impulse
            from 0 to 1, by default 0.5
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        duty_cycle = kwargs.get("duty_cycle", 0.5)
        self.first_y = self.height
        if self.is_first or math.isnan(self.last_y):
            self.last_y = self.first_y
        self.dt = abs(self.first_y - self.last_y) * self.slewing / self.height
        self.dt = min(self.dt, duty_cycle * self.width)
        # add shape
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0.0, self.last_y),
                    Point(self.dt, self.first_y),
                    Point(duty_cycle * self.width, self.first_y),
                    Point(duty_cycle * self.width, self.height - self.first_y),
                    Point(duty_cycle * self.width, self.first_y),
                    Point(self.width, self.first_y),
                ],
            )
        )


class Space(Brick):
    """
    blank (area without any drawing)
    This block can be used in coordination of the overlay possibility
    to create even more complex signal or apply a specific color for
    a portion of the signal.
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        if self.is_first or math.isnan(self.last_y):
            self.last_y = self.height


class Empty(Brick):
    """
    empty brick with zero width
    """

    def __init__(self, **kwargs) -> None:
        Brick.__init__(self, **kwargs)
        self.width = 0
        if self.is_first or math.isnan(self.last_y):
            self.last_y = self.height


class Filler(Brick):
    """
    filling brick to draw an horizontal line
    in front of a waveform
    """

    def __init__(self, **kwargs) -> None:
        Brick.__init__(self, **kwargs)
        self.first_y = kwargs.get("y", self.height / 2)
        self.last_y = kwargs.get("y", self.height / 2)
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0.0, self.first_y),
                    Point(self.width, self.first_y),
                ],
            )
        )


# ======== Filtering Functions ========
def filter_width(waveform: List[Brick]) -> List[Brick]:
    """
    Compute the width/height of each brick considering the following properties:

    - brick_width
    - brick_height
    - hscale
    - vscale
    - period
    """
    ans = []
    for brick in waveform:
        brick_width = (
            brick.args.get("brick_width", 20.0)
            * brick.args.get("hscale", 1.0)
            * brick.args.get("period", 1.0)
        )
        brick_height = brick.args.get("brick_height", 20.0) * brick.args.get("vscale", 1.0)
        brick.args["brick_width"] = brick_width
        brick.args["brick_height"] = brick_height
        ans.append(BrickFactory.create(brick.symbol, **brick.args))
    return ans


def filter_repeat(waveform: List[Brick]) -> List[Brick]:
    """
    Compute the number of size expension for a given brick (using '.' symbol) at
    the exception of clock signals where the brick '.' means duplication.
    """
    ans = []
    previous_symbol = " "
    previous_index = 0
    for i, brick in enumerate(waveform):
        # check validity of the first brick
        if i == 0 and "repeat" in BrickFactory.tags.get(brick.symbol, []):
            log.fatal(log.SIGNAL_WRONG_START % brick.symbol)
        if "repeat" not in BrickFactory.tags.get(brick.symbol, []):
            ans.append(brick)
            previous_symbol = brick.symbol
            previous_index = len(ans) - 1
            continue
        # always repeat a clock signal and after gap repeat the last valid symbol
        if "clock" in BrickFactory.tags.get(previous_symbol, []) or previous_symbol == "|":
            ans.append(BrickFactory.create(previous_symbol, **brick.args))
        # extend the width of other symbols
        else:
            ans[previous_index].repeat += 1
        # a gap symbol overlay the previous one
        if brick.symbol == "|":
            ans.append(brick)
    # make repeat info propagate
    for b in ans:
        b.args["repeat"] = b.repeat
    return ans


def filter_phase_pos(waveform: List[Brick]) -> List[Brick]:
    """
    Adjust the size of the first and last brick of signal based on the following
    properties:

    - phase
    - repeat
    - slewing
    - brick_width
    - width

    A signal should always have a width equal to 'width'
    """
    ans = []
    position = 0
    for i, brick in enumerate(waveform):
        phase = brick.args.get("phase", 0.0)
        repeat = brick.args.get("repeat", 1.0)
        slewing = brick.args.get("slewing", 3.0)
        brick_width = brick.args["brick_width"]
        lane_width = brick.args["width"]
        # global scaling of the x-axis
        if brick.symbol == "|":
            pmul = 0
        elif "analogue" in BrickFactory.tags[brick.symbol]:
            pmul = 1
        else:
            pmul = max(1, slewing * 2 / max(brick_width, 1))
        # consider phase at the beginning
        if i == 0:
            position = -brick_width * phase
        # adjust width depending on the brick's index in the the lane
        if i >= len(waveform) - 1:
            brick.args["brick_width"] = max(0, lane_width - position)
        else:
            brick.args["brick_width"] = pmul * repeat * brick_width
        position += brick.args["brick_width"]
        # update size of the first visible brick
        if position > 0 and not ans:
            brick.args["is_first"] = True
            brick.args["brick_width"] = position
        # prevent monstruosity with phase larger than several block width
        if position > 0:
            # consider the case when the phase is positive
            # extend the first symbol
            if phase > 0.0 and brick.args["is_first"]:
                brick.args["brick_width"] += brick_width * phase
            ans.append(BrickFactory.create(brick.symbol, **brick.args))
    return ans


def filter_transition(waveform: List[Brick]) -> List[Brick]:
    """
    Smooth abutment of different brick to prevent glitches
    and fusion data brick of the same symbol with the same 'data' value
    """
    ans = []
    previous_brick = BrickFactory.create(" ")
    for brick in waveform:
        # clocks combination
        if previous_brick.symbol.lower() + brick.symbol.lower() in [
            "ll",
            "hh",
            "hp",
            "hn",
            "nh",
            "ln",
            "pl",
            "pn",
            "np",
        ]:
            brick.args["ignore_start_transition"] = True
            previous_brick.args["ignore_end_transition"] = True
            previous_brick = BrickFactory.create(
                previous_brick.symbol, **previous_brick.args
            )
        # join consecutive brick
        brick.args["last_y"] = previous_brick.get_last_y()
        # adjust transistion from data to non-data
        if (
            "data" in BrickFactory.tags[previous_brick.symbol]
            and "data" not in BrickFactory.tags[brick.symbol]
        ):
            brick.args["ignore_start_transition"] = True
        # identic consecutive block
        if brick.symbol == previous_brick.symbol:
            # two data brick with same data
            if "data" in BrickFactory.tags[brick.symbol]:
                current_data = str(brick.args.get("data") or "")
                previous_data = str(previous_brick.args.get("data") or "")
                if brick.symbol != "x" and (current_data == previous_data):
                    brick.args["ignore_start_transition"] = True
                    brick.args["hide_data"] = True
                    previous_brick.args["ignore_end_transition"] = True
                    previous_brick = BrickFactory.create(
                        previous_brick.symbol, **previous_brick.args
                    )
        ans.append(BrickFactory.create(brick.symbol, **brick.args))
        if "repeat" not in BrickFactory.tags[brick.symbol]:
            if (
                "data" in BrickFactory.tags[previous_brick.symbol]
                and "data" not in BrickFactory.tags[brick.symbol]
            ):
                previous_brick.args["first_y"] = ans[-1].get_first_y()
                previous_brick = BrickFactory.create(
                    previous_brick.symbol, **previous_brick.args
                )
            previous_brick = ans[-1]
    return ans


# ======== Plugin Loading ========
def initialize() -> None:
    """register defined digital blocks in the rendering system"""
    BrickFactory.register(
        "n", Nclk, tags=["clock"], params={"duty_cycle": 0.5, "slewing": 0, "period": 1}
    )
    BrickFactory.register(
        "N",
        NclkArrow,
        tags=["clock"],
        params={"duty_cycle": 0.5, "slewing": 0, "period": 1},
    )
    BrickFactory.register(
        "p", Pclk, tags=["clock"], params={"duty_cycle": 0.5, "slewing": 0, "period": 1}
    )
    BrickFactory.register(
        "P",
        PclkArrow,
        tags=["clock"],
        params={"duty_cycle": 0.5, "slewing": 0, "period": 1},
    )
    BrickFactory.register("l", Low, tags=["clock"], params={"slewing": 0, "period": 1})
    BrickFactory.register("L", LowArrow, tags=["clock"], params={"slewing": 0, "period": 1})
    BrickFactory.register("h", High, tags=["clock"], params={"slewing": 0, "period": 1})
    BrickFactory.register(
        "H", HighArrow, tags=["clock"], params={"slewing": 0, "period": 1}
    )
    BrickFactory.register("z", HighZ, params={"period": 1})
    BrickFactory.register("0", Zero, params={"slewing": 0, "period": 1})
    BrickFactory.register("1", One, params={"slewing": 0, "period": 1})
    BrickFactory.register(
        "2", Two, tags=["data"], params={"data": "", "slewing": 3, "period": 1}
    )
    BrickFactory.register(
        "3", Three, tags=["data"], params={"data": "", "slewing": 3, "period": 1}
    )
    BrickFactory.register(
        "4", Four, tags=["data"], params={"data": "", "slewing": 3, "period": 1}
    )
    BrickFactory.register(
        "5", Five, tags=["data"], params={"data": "", "slewing": 3, "period": 1}
    )
    BrickFactory.register(
        "6", Six, tags=["data"], params={"data": "", "slewing": 3, "period": 1}
    )
    BrickFactory.register(
        "7", Seven, tags=["data"], params={"data": "", "slewing": 3, "period": 1}
    )
    BrickFactory.register(
        "8", Eight, tags=["data"], params={"data": "", "slewing": 3, "period": 1}
    )
    BrickFactory.register(
        "9", Nine, tags=["data"], params={"data": "", "slewing": 3, "period": 1}
    )
    BrickFactory.register("x", Unknown, tags=["data"], params={"slewing": 3, "period": 1})
    BrickFactory.register("X", Garbage, tags=["data"], params={"slewing": 3, "period": 1})
    BrickFactory.register(
        "=", Two, tags=["data"], params={"data": "", "slewing": 3, "period": 1}
    )
    BrickFactory.register("|", Gap, tags=["repeat"], params={"period": 1})
    BrickFactory.register("u", Up, params={"slewing": 0, "period": 1})
    BrickFactory.register("d", Down, params={"slewing": 0, "period": 1})
    BrickFactory.register("i", ImpulseUp, params={"duty_cycle": 0.5, "period": 1})
    BrickFactory.register("I", ImpulseDown, params={"duty_cycle": 0.5, "period": 1})
    BrickFactory.register(" ", Space)
    BrickFactory.register(
        ".", Empty, tags=["repeat"], params={"duty_cycle": 0.5, "slewing": 0, "period": 1}
    )
    BrickFactory.register("f", Filler, params={"period": 1})
    FilterBank.register(filter_repeat)
    FilterBank.register(filter_width)
    FilterBank.register(filter_phase_pos)
    FilterBank.register(filter_transition)
