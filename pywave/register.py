#!/usr/bin/env python3
# spell-checker: disable

"""
register.py declare the basic building block
to represent a register
"""

import pywave
from itertools import accumulate


class Register:
    """
    define the register as a composition of new kind of bricks
    with field informations
    """

    __slots__ = ["name", "description", "fields", "__counter"]

    def __init__(self):
        # default value
        self.name = ""
        self.description = ""
        self.fields = []
        # for auto increment field start position
        self.__counter = 0

    def push_field(self, field):
        """
        add a new field to the fields stack
        """
        f = None
        # add to the stack
        if isinstance(field, dict):
            f = Field.from_dict(field)
            f.start = self.__counter
            self.fields.append(f)
        elif isinstance(field, Field):
            f = field
            f.start = self.__counter
            self.fields.append(f)
        else:
            raise Exception(f"Unsupported {type(field)} of field")
        # increment counter
        if f:
            self.__counter += f.width

    def to_wavelane(self):
        """
        convert the description of a register into a wavelane
        """
        wave = "".join([field.wave for field in self.fields[::-1]])
        data = " ".join([field.data for field in self.fields[::-1]])
        attr = [(field.width, field.attributes) for field in self.fields[::-1]]
        # calculate position of extremities
        pos = [0]
        for f in self.fields:
            if f.width > 1:
                pos.append(f.width - 1)
            pos.append(1)
        pos = list(accumulate(pos[:-1]))[::-1]
        ans = {}
        ans[self.name] = {"wave": wave, "data": data, "regpos": pos, "attr": attr}
        return ans


class FieldStart(pywave.Brick):
    """
    [
    """

    def __init__(self, **kwargs):
        pywave.Brick.__init__(self, **kwargs)
        self.paths.append(
            [
                "path",
                (self.width, self.height),
                (0, self.height),
                (0, self.height / 4),
                (self.width, self.height / 4),
            ]
        )
        if not kwargs.get("fill", None) is None:
            self.polygons.append(
                [
                    "%s-polygon" % kwargs.get("style", ""),
                    (self.width, self.height),
                    (0, self.height),
                    (0, self.height / 4),
                    (self.width, self.height / 4),
                ]
            )
        # add attributes
        _attrs = kwargs.get("attr", None)
        attrs = None
        if not _attrs is None and isinstance(_attrs, tuple):
            width, attrs = _attrs
            if not attrs is None:
                for i, attr in enumerate(attrs):
                    self.texts.append(
                        (
                            "attr", 
                            (self.width * width) / 2,
                            self.height + 12 * (i + 1),
                            attr,
                        )
                    )
        # add text
        self.texts.append(
            (
                "data",
                self.width / 2,
                self.height * 0.625,
                kwargs.get("data", ""),
            )
        )
        self.texts.append(
            (
                "data",
                self.width / 2,
                self.height * 0.125,
                kwargs.get("regpos", ""),
            )
        )


class FieldMid(pywave.Brick):
    """
    :
    """

    def __init__(self, **kwargs):
        pywave.Brick.__init__(self, **kwargs)
        self.splines.append(
            [
                "path",
                ("M", self.width, self.height * 0.875),
                ("l", 0, self.height * 0.125),
                ("l", -self.width, 0),
                ("l", 0, -self.height * 0.125),
            ]
        )
        self.splines.append(
            [
                "path",
                ("M", self.width, self.height * 0.375),
                ("l", 0, -self.height * 0.125),
                ("l", -self.width, 0),
                ("l", 0, self.height * 0.125),
            ]
        )
        if not kwargs.get("fill", None) is None:
            self.polygons.append(
                [
                    "%s-polygon" % kwargs.get("style", ""),
                    (self.width, self.height),
                    (0, self.height),
                    (0, self.height / 4),
                    (self.width, self.height / 4),
                ]
            )
        # add text
        self.texts.append(
            (
                "data",
                self.width / 2,
                self.height * 0.625,
                kwargs.get("data", ""),
            )
        )


class FieldEnd(pywave.Brick):
    """
    ]
    """

    def __init__(self, **kwargs):
        pywave.Brick.__init__(self, **kwargs)
        self.paths.append(
            [
                "path",
                (0, self.height),
                (self.width, self.height),
                (self.width, self.height / 4),
                (0, self.height / 4),
            ]
        )
        if not kwargs.get("fill", None) is None:
            self.polygons.append(
                [
                    "%s-polygon" % kwargs.get("style", ""),
                    (self.width, self.height),
                    (0, self.height),
                    (0, self.height / 4),
                    (self.width, self.height / 4),
                ]
            )
        # add text
        self.texts.append(
            (
                "data",
                self.width / 2,
                self.height * 0.625,
                kwargs.get("data", ""),
            )
        )
        self.texts.append(
            (
                "data",
                self.width / 2,
                self.height * 0.125,
                kwargs.get("regpos", ""),
            )
        )


class FieldBit(pywave.Brick):
    """
    b
    """

    def __init__(self, **kwargs):
        pywave.Brick.__init__(self, **kwargs)
        self.paths.append(
            [
                "path",
                (0, self.height / 4),
                (0, self.height),
                (self.width, self.height),
                (self.width, self.height / 4),
                (0, self.height / 4),
            ]
        )
        if not kwargs.get("fill", None) is None:
            self.polygons.append(
                [
                    "%s-polygon" % kwargs.get("style", ""),
                    (self.width, self.height),
                    (0, self.height),
                    (0, self.height / 4),
                    (self.width, self.height / 4),
                ]
            )
        # add text
        self.texts.append(
            (
                "data",
                self.width / 2,
                self.height * 0.625,
                kwargs.get("data", ""),
            )
        )
        self.texts.append(
            (
                "data",
                self.width / 2,
                self.height * 0.125,
                kwargs.get("regpos", ""),
            )
        )


class Field:
    """
    define what is a field inside a register
    from 1-bit to N-bits
    """

    __slots__ = ["name", "description", "start", "width", "attributes", "wave", "data"]

    def __init__(self):
        # default value
        self.name = ""
        self.description = ""
        self.start = 0
        self.width = 1
        self.attributes = []
        self.wave = ""
        self.data = ""

    @staticmethod
    def from_dict(d: dict):
        """
        Generate a field from a dict
        given after parsing
        """
        f = Field()
        f.name = str(d.get("name", ""))
        f.description = d.get("description", "")
        f.width = d.get("width", d.get("bits", 1))
        f.attributes = d.get("attributes", d.get("attr", None))
        # convert attributes for string and int
        if isinstance(f.attributes, str):
            f.attributes = [f.attributes]
        elif isinstance(f.attributes, list):
            f.attributes = [
                ("{0:0" + (str(f.width)) + "b}").format(a) if isinstance(a, int) else a
                for a in f.attributes
            ]
        if isinstance(d.get("name", ""), int):
            # convert number to bits
            f.data = ("{0:0" + (str(f.width)) + "b}").format(d.get("name", ""))
            # split for each bits
            f.data = " ".join([c for c in f.data])
        elif isinstance(d.get("name", ""), str):
            # center the name in the middle
            l = (f.width - 1) // 2
            e = (f.width - 1) / 2 - l
            f.data = "".join([" "] * l if e == 0 else [" "] * (l + 1))
            f.data += d.get("name", "")
            f.data += "".join([" "] * l)
        else:
            # skip the field
            f.data = " ".join([""] * f.width)
        if f.width > 1:
            f.wave = (
                pywave.BRICKS.field_start.value
                + "".join([pywave.BRICKS.field_mid.value] * (f.width - 2))
                + pywave.BRICKS.field_end.value
            )
        else:
            f.wave = pywave.BRICKS.field_bit.value
        return f

    def to_dict(self):
        """
        Allow one field per line representation
        """
        return {s: getattr(self, s, None) for s in self.__slots__}


def generate_register_symbol(symbol: str, **kwargs) -> (bool, object):
    """
    define the mapping between the symbol and the brick
    """
    # get option supported
    block = None
    if symbol == pywave.BRICKS.field_start:
        block = FieldStart(**kwargs)
    elif symbol == pywave.BRICKS.field_mid:
        block = FieldMid(**kwargs)
    elif symbol == pywave.BRICKS.field_end:
        block = FieldEnd(**kwargs)
    elif symbol == pywave.BRICKS.field_bit:
        block = FieldBit(**kwargs)
    return (not block is None, block)

