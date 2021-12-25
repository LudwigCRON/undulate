"""
digital.py declare the basic building block
to generate a digital waveform
"""
# TODO: migrate Garbage follow_data to generic custom filtering functions
# TODO: migrate Data follow_x to generic custom filtering functions
# TODO: migrate is_first to ignore_start_transition ?

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

# ======== Brick Definition ========


class Nclk(Brick):
    """
    Falling edge clock without arrow

    Parameters:
        slewing (float): limit the slope
        duty_cycle (float > 0): between 0 and 1
    """

    def __init__(self, duty_cycle: float = 0.5, **kwargs) -> None:
        Brick.__init__(self, **kwargs)
        self.first_y = self.height
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
                    Point(self.width, self.height / 2),
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
        if self.ignore_start_transition:
            return None
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

    def __init__(self, duty_cycle: float = 0.5, **kwargs):
        Brick.__init__(self, **kwargs)
        self.first_y = 0.0
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
                    Point(self.width, self.height / 2),
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
        if self.is_first or math.isnan(self.last_y):
            self.last_y = self.height
        # add shape
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0.0, self.last_y),
                    Point(
                        self.slewing / 2, self.last_y if self.is_first else self.height / 2
                    ),
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
        elif math.isnan(self.last_y):
            self.last_y = 0.0
        # add shape
        self.paths.append(
            Drawable(
                "path",
                [
                    Point(0.0, self.last_y),
                    Point(
                        self.slewing / 2, self.last_y if self.is_first else self.height / 2
                    ),
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
    """

    def __init__(self, style: str = "s2-polygon", hide_data: bool = False, **kwargs):
        Brick.__init__(self, **kwargs)
        if math.isnan(self.last_y):
            self.last_y = self.height / 2
        follow_x = kwargs.get("follow_x", False)
        # add shape
        if self.is_first:
            self.paths.append(
                Drawable(
                    "path",
                    [
                        Point(0.0, 0.0),
                        Point(self.slewing, 0.0),
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
                        Point(0.0, self.height),
                        Point(self.slewing, self.height),
                        Point(self.width - self.slewing, self.height),
                        Point(
                            self.width,
                            self.height / 2
                            if not self.ignore_end_transition
                            else self.height,
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
                            -self.slewing if follow_x else 0.0,
                            self.last_y if not self.ignore_start_transition else 0.0,
                        ),
                        Point(0.0 if follow_x else self.slewing, 0.0),
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
                            -self.slewing if follow_x else 0,
                            self.last_y
                            if not self.ignore_start_transition
                            else self.height,
                        ),
                        Point(0 if follow_x else self.slewing, self.height),
                        Point(self.width - self.slewing, self.height),
                        Point(
                            self.width,
                            self.height / 2
                            if not self.ignore_end_transition
                            else self.height,
                        ),
                    ],
                )
            )
        # add background
        if self.is_first:
            self.polygons.append(
                Drawable(
                    style,
                    [
                        Point(0.0, 0.0),
                        Point(self.slewing, 0.0),
                        Point(self.width - self.slewing, 0.0),
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
                        Point(self.slewing, self.height),
                        Point(0.0, self.height),
                    ],
                )
            )
        else:
            self.polygons.append(
                Drawable(
                    style,
                    [
                        Point(
                            -self.slewing if follow_x else 0,
                            self.last_y if not self.ignore_start_transition else 0,
                        ),
                        Point(
                            self.slewing
                            if not self.ignore_start_transition and not follow_x
                            else 0,
                            0,
                        ),
                        Point(
                            self.width - self.slewing
                            if not self.ignore_end_transition
                            else self.width,
                            0,
                        ),
                        Point(
                            self.width,
                            self.height / 2 if not self.ignore_end_transition else 0,
                        ),
                        Point(
                            self.width - self.slewing
                            if not self.ignore_end_transition
                            else self.width,
                            self.height,
                        ),
                        Point(
                            self.slewing
                            if not self.ignore_start_transition and not follow_x
                            else 0,
                            self.height,
                        ),
                        Point(
                            -self.slewing if follow_x else 0,
                            self.last_y
                            if not self.ignore_start_transition
                            else self.height,
                        ),
                    ],
                )
            )
        # add text
        if not hide_data:
            self.texts.append(
                Drawable("data", (self.width / 2, self.height / 2, kwargs.get("data", "")))
            )


class Two(Data):
    """
    Variant of Data with s2-polygon
    """

    def __init__(self, hide_data: bool = False, **kwargs):
        Data.__init__(self, style="s2-polygon", hide_data=hide_data, **kwargs)


class Three(Data):
    """
    Variant of Data with s3-polygon
    """

    def __init__(self, hide_data: bool = False, **kwargs):
        Data.__init__(self, style="s3-polygon", hide_data=hide_data, **kwargs)


class Four(Data):
    """
    Variant of Data with s4-polygon
    """

    def __init__(self, hide_data: bool = False, **kwargs):
        Data.__init__(self, style="s4-polygon", hide_data=hide_data, **kwargs)


class Five(Data):
    """
    Variant of Data with s5-polygon
    """

    def __init__(self, hide_data: bool = False, **kwargs):
        Data.__init__(self, style="s5-polygon", hide_data=hide_data, **kwargs)


class Six(Data):
    """
    Variant of Data with s6-polygon
    """

    def __init__(self, hide_data: bool = False, **kwargs):
        Data.__init__(self, style="s6-polygon", hide_data=hide_data, **kwargs)


class Seven(Data):
    """
    Variant of Data with s7-polygon
    """

    def __init__(self, hide_data: bool = False, **kwargs):
        Data.__init__(self, style="s7-polygon", hide_data=hide_data, **kwargs)


class Eight(Data):
    """
    Variant of Data with s8-polygon
    """

    def __init__(self, hide_data: bool = False, **kwargs):
        Data.__init__(self, style="s8-polygon", hide_data=hide_data, **kwargs)


class Nine(Data):
    """
    Variant of Data with s9-polygon
    """

    def __init__(self, hide_data: bool = False, **kwargs):
        Data.__init__(self, style="s9-polygon", hide_data=hide_data, **kwargs)


class Unknown(Data):
    """
    Variant of Data with hatch
    """

    def __init__(self, **kwargs):
        Data.__init__(self, style="hatch", hide_data=True, **kwargs)


class Gap(Brick):
    """
    single line time compression
    """

    def __init__(self, **kwargs):
        Brick.__init__(self, **kwargs)
        # if self.is_first:
        # raise "a gap cannot be first in a wavelane"
        self.splines.append(
            Drawable(
                "hide",
                [
                    SplineSegment("M", 0, self.height + 2),
                    SplineSegment("C", 5, self.height + 2),
                    SplineSegment("", 5, -4),
                    SplineSegment("", 10, -4),
                    SplineSegment("L", 7, 0),
                    SplineSegment("C", 2, 0),
                    SplineSegment("", 2, self.height + 4),
                    SplineSegment("", -3, self.height + 4),
                    SplineSegment("z", "", ""),
                ],
            )
        )
        self.splines.append(
            Drawable(
                "path",
                [
                    SplineSegment("M", 0, self.height + 2),
                    SplineSegment("C", 5, self.height + 2),
                    SplineSegment("", 5, -2),
                    SplineSegment("", 10, -2),
                ],
            )
        )
        self.splines.append(
            Drawable(
                "path",
                [
                    SplineSegment("M", -3, self.height + 2),
                    SplineSegment("C", 2, self.height + 2),
                    SplineSegment("", 2, -2),
                    SplineSegment("", 7, -2),
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
            self.last_y = 0.0
        self.splines.append(
            Drawable(
                "path",
                [
                    SplineSegment("M", 0, self.last_y),
                    SplineSegment("L", 3, self.last_y),
                    SplineSegment("C", 3 + self.slewing, self.last_y),
                    SplineSegment("", 3 + self.slewing, self.height - self.last_y),
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
            self.last_y = self.height
        self.splines.append(
            Drawable(
                "path",
                [
                    SplineSegment("M", 0, self.last_y),
                    SplineSegment("L", 3, self.last_y),
                    SplineSegment("C", 3 + self.slewing, self.last_y),
                    SplineSegment("", 3 + self.slewing, self.height - self.last_y),
                    SplineSegment("", min(self.width, 20), self.height),
                    SplineSegment("L", self.width, self.height),
                ],
            )
        )


class ImpulseUp(Brick):
    """
    pulse to VDD

    Parameters:
        duty_cycle (float): adjust the x position of the impulse
            from 0 to 1, by default 0.5
    """

    def __init__(self, duty_cycle: float = 0.5, **kwargs):
        Brick.__init__(self, **kwargs)
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
    pulse to GND

    Parameters:
        up (bool): True for impulse to up and False for impulse down
        duty_cycle (float): adjust the x position of the impulse
            from 0 to 1, by default 0.5
    """

    def __init__(self, duty_cycle: float = 0.5, **kwargs):
        Brick.__init__(self, **kwargs)
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
    blank
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


# ======== Filtering Functions ========
def filter_width(waveform: list[Brick]) -> list[Brick]:
    ans = []
    for brick in waveform:
        brick_width = brick.args.get("brick_width", 20) * brick.args.get("hscale", 1)
        brick_height = brick.args.get("brick_height", 20) * brick.args.get("vscale", 1)
        brick.args["brick_width"] = brick_width
        brick.args["brick_height"] = brick_height
        ans.append(BrickFactory.create(brick.symbol, **brick.args))
    return ans


def filter_repeat(waveform: list[Brick]) -> list[Brick]:
    ans = []
    previous_brick = BrickFactory.create(" ")
    for i, brick in enumerate(waveform):
        # check validity of the first brick
        if i == 0 and "repeat" in BrickFactory.tags.get(brick.symbol, []):
            log.fatal(log.WRONG_WAVE_START % brick.symbol)
        if "repeat" not in BrickFactory.tags.get(brick.symbol, []):
            ans.append(brick)
            previous_brick = brick
            continue
        # always repeat a clock signal and after gap repeat the last valid symbol
        if (
            "clock" in BrickFactory.tags.get(previous_brick.symbol, [])
            or previous_brick.symbol == "|"
        ):
            ans.append(BrickFactory.create(previous_brick.symbol, **previous_brick.args))
        # extend the width of other symbols
        else:
            ans[-1].repeat += 1
        # a gap symbol overlay the previous one
        if brick.symbol == "|":
            ans.append(brick)
        if "repeat" not in BrickFactory.tags.get(brick.symbol, []):
            previous_brick = brick
    # make repeat info propagate
    for b in ans:
        b.args["repeat"] = b.repeat
    return ans


def filter_phase_pos(waveform: list[Brick]) -> list[Brick]:
    ans = []
    for i, brick in enumerate(waveform):
        phase = brick.args.get("phase", 0.0)
        period = brick.args.get("period", 1.0)
        repeat = brick.args.get("repeat", 1.0)
        slewing = brick.args.get("slewing", 3.0)
        brick_width = brick.args["brick_width"]
        lane_width = brick.args["width"]
        # global scaling of the x-axis
        if brick.symbol == "|":
            pmul = 0
        if "analogue" in BrickFactory.tags[brick.symbol]:
            pmul = period
        else:
            pmul = max(period, slewing * 2 / brick_width)
        # adjust width depending on the brick's index in the the lane
        if i == 0:
            brick.args["brick_width"] = pmul * brick_width * (repeat - phase)
        elif i == len(waveform) - 1:
            position = sum(b.width for b in waveform[:-1])
            brick.args["brick_width"] = max(
                pmul * brick_width * (repeat + phase), lane_width - position
            )
        else:
            brick.args["brick_width"] = pmul * repeat * brick_width
        ans.append(BrickFactory.create(brick.symbol, **brick.args))
    return ans


def filter_transition(waveform: list[Brick]) -> list[Brick]:
    ans = []
    previous_brick = BrickFactory.create(" ")
    for brick in waveform:
        # adjust transistion from data to X
        if "data" in BrickFactory.tags[previous_brick.symbol] and brick.symbol == "X":
            previous_brick.args["brick_width"] += previous_brick.args.get("slewing", 0)
            previous_brick = BrickFactory.create(
                previous_brick.symbol, **previous_brick.args
            )
        # identic consecutive block
        if brick.symbol == previous_brick.symbol:
            # two data brick with same data
            if "data" in BrickFactory.tags[brick.symbol]:
                current_data = str(brick.args.get("data") or "").strip()
                previous_data = str(previous_brick.args.get("data") or "").strip()
                if current_data == previous_data:
                    brick.args["ignore_start_transition"] = True
                    brick.args["hide_data"] = True
                    previous_brick.args["ignore_end_transition"] = True
                    previous_brick = BrickFactory.create(
                        previous_brick.symbol, **previous_brick.args
                    )
            # otherwise join path
            else:
                # fy = brick.get_first_y()
                # alter current brick end
                # nb.alter_end(0, fy)
                # alter next brick start
                # brick.alter_start(0, fy)
                pass
        ans.append(BrickFactory.create(brick.symbol, **brick.args))
        if "repeat" not in BrickFactory.tags[brick.symbol]:
            previous_brick = ans[-1]
    return ans


# ======== Plugin Loading ========


def initialize() -> None:
    """register defined digital blocks in the rendering system"""
    BrickFactory.register("n", Nclk, tags=["clock"], params={"duty_cycle": 0.5})
    BrickFactory.register("N", NclkArrow, tags=["clock"], params={"duty_cycle": 0.5})
    BrickFactory.register("p", Pclk, tags=["clock"], params={"duty_cycle": 0.5})
    BrickFactory.register("P", PclkArrow, tags=["clock"], params={"duty_cycle": 0.5})
    BrickFactory.register("l", Low, tags=["clock"])
    BrickFactory.register("L", LowArrow, tags=["clock"])
    BrickFactory.register("h", High, tags=["clock"])
    BrickFactory.register("H", HighArrow, tags=["clock"])
    BrickFactory.register("z", HighZ)
    BrickFactory.register("0", Zero)
    BrickFactory.register("1", One)
    BrickFactory.register("2", Two, params={"data": "", "slewing": 3})
    BrickFactory.register("3", Three, params={"data": "", "slewing": 3})
    BrickFactory.register("4", Four, params={"data": "", "slewing": 3})
    BrickFactory.register("5", Five, params={"data": "", "slewing": 3})
    BrickFactory.register("6", Six, params={"data": "", "slewing": 3})
    BrickFactory.register("7", Seven, params={"data": "", "slewing": 3})
    BrickFactory.register("8", Eight, params={"data": "", "slewing": 3})
    BrickFactory.register("9", Nine, params={"data": "", "slewing": 3})
    BrickFactory.register("x", Unknown, params={"slewing": 3})
    BrickFactory.register("X", Garbage, params={"slewing": 3})
    BrickFactory.register("=", Two, params={"data": "", "slewing": 3})
    BrickFactory.register("|", Gap, tags=["repeat"])
    BrickFactory.register("u", Up)
    BrickFactory.register("d", Down)
    BrickFactory.register("i", ImpulseUp, params={"duty_cycle": 0.5})
    BrickFactory.register("I", ImpulseDown, params={"duty_cycle": 0.5})
    BrickFactory.register(" ", Space)
    BrickFactory.register(".", Empty, tags=["repeat"])

    FilterBank.register(filter_repeat)
    FilterBank.register(filter_width)
    FilterBank.register(filter_phase_pos)
    FilterBank.register(filter_transition)
