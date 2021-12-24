"""
digital.py declare the basic building block
to generate a digital waveform
"""
# TODO: migrate Garbage follow_data to generic custom filtering functions
# TODO: migrate Data follow_x to generic custom filtering functions
# TODO: migrate is_first to ignore_start_transition ?

import math
from undulate.bricks.generic import (
    ArrowDescription,
    Brick,
    BrickFactory,
    Drawable,
    Point,
    SplineSegment,
)


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

    def __init__(self, hide_data: bool = False, **kwargs):
        Data.__init__(self, style="hatch", hide_data=hide_data, **kwargs)


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


def initialize() -> None:
    """register defined digital blocks in the rendering system"""
    BrickFactory.register("n", Nclk.__init__, tags=["clock"], params={"duty_cycle": 0.5})
    BrickFactory.register(
        "N", NclkArrow.__init__, tags=["clock"], params={"duty_cycle": 0.5}
    )
    BrickFactory.register("p", Pclk.__init__, tags=["clock"], params={"duty_cycle": 0.5})
    BrickFactory.register(
        "P", PclkArrow.__init__, tags=["clock"], params={"duty_cycle": 0.5}
    )
    BrickFactory.register("l", Low.__init__, tags=["clock"])
    BrickFactory.register("L", LowArrow.__init__, tags=["clock"])
    BrickFactory.register("h", High.__init__, tags=["clock"])
    BrickFactory.register("H", HighArrow.__init__, tags=["clock"])
    BrickFactory.register("z", HighZ.__init__)
    BrickFactory.register("0", Zero.__init__)
    BrickFactory.register("1", One.__init__)
    BrickFactory.register("2", Two.__init__, params={"data": ""})
    BrickFactory.register("3", Three.__init__, params={"data": ""})
    BrickFactory.register("4", Four.__init__, params={"data": ""})
    BrickFactory.register("5", Five.__init__, params={"data": ""})
    BrickFactory.register("6", Six.__init__, params={"data": ""})
    BrickFactory.register("7", Seven.__init__, params={"data": ""})
    BrickFactory.register("8", Eight.__init__, params={"data": ""})
    BrickFactory.register("9", Nine.__init__, params={"data": ""})
    BrickFactory.register("x", Unknown.__init__)
    BrickFactory.register("X", Garbage.__init__)
    BrickFactory.register("=", Two.__init__, params={"data": ""})
    BrickFactory.register("|", Gap.__init__, tags=["repeat"])
    BrickFactory.register("u", Up.__init__)
    BrickFactory.register("d", Down.__init__)
    BrickFactory.register("i", ImpulseUp.__init__, params={"duty_cycle": 0.5})
    BrickFactory.register("I", ImpulseDown.__init__, params={"duty_cycle": 0.5})
    BrickFactory.register(" ", Space.__init__)
    BrickFactory.register(".", None, tags=["repeat"])
