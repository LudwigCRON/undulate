import undulate.logger as log


class Register:
    """
    define the register as a composition of new kind of bricks
    with field informations
    """

    __slots__ = ["name", "description", "fields", "config"]

    def __init__(self):
        # default value
        self.name = ""
        self.description = ""
        self.fields = []
        self.config = {}

    def push_field(self, field):
        """
        add a new field to the fields stack
        """
        f = None
        # add to the stack
        if isinstance(field, dict):
            f = Field.from_dict(field)
        else:
            log.fatal(log.FIELD_UNSUPPORTED_TYPE % type(field), 5)
        self.fields.append(f)

    def to_wavelane(self):
        """
        convert the description of a register into a wavelane
        """
        # look for unused field and position
        unuseds, pos = [], 0
        for i, f in enumerate(self.fields):
            # start position is given and overwrite
            if f.start and pos > f.start:
                log.fatal(log.FIELD_OVERLAP % f.name, 6)
            # start position and no overlap -> unused field
            if f.start and f.start > 0 and pos < f.start:
                width = f.start - pos
                unuseds.append((i, pos, width))
                pos += width
            # default behaviour
            if not f.start:
                f.start = pos if i > 0 else 0
            pos += f.width
        # insert unused field in fields
        for i, pos, width in unuseds[::-1]:
            self.fields.insert(
                i, Field.from_dict({"description": "unused", "width": width, "regpos": pos})
            )
        # generate wavelane
        wave = "".join([field.wave for field in self.fields[::-1]])
        data = " ".join([field.data for field in self.fields[::-1]])
        attributes = [field.attributes for field in self.fields[::-1]]
        widths = [field.width for field in self.fields[::-1]]
        types, positions, styles = [], [], []
        for field in self.fields[::-1]:
            types.extend([field.type] * field.width)
            if field.width > 1:
                positions.extend([field.start + field.width - 1, field.start])
            else:
                positions.append(field.start)
            styles.extend([field.style] * field.width)
        ans = {"config": self.config}
        ans[self.name] = {
            "wave": wave,
            "data": data,
            "positions": positions,
            "attributes": attributes,
            "types": types,
            "styles": styles,
            "scale_widths": widths,
        }
        return ans


class Field:
    """
    define what is a field inside a register
    from 1-bit to N-bits
    """

    __slots__ = [
        "name",
        "description",
        "start",
        "width",
        "attributes",
        "wave",
        "data",
        "style",
        "type",
    ]

    def __init__(self):
        # default value
        self.name = ""
        self.description = ""
        self.start = -1
        self.width = 1
        self.attributes = []
        self.wave = ""
        self.data = ""
        self.type = ""

    @staticmethod
    def from_dict(d: dict):
        """
        Generate a field from a dict
        given after parsing
        """
        f = Field()
        f.name = str(d.get("name", ""))
        f.description = d.get("description", "")
        f.width = int(d.get("width", d.get("bits", 1)))
        f.attributes = d.get("attributes", d.get("attr", None))
        f.type = d.get("type", 2)
        f.style = (
            "s%s-polygon" % f.type
            if f.type
            else "hatch"
            if f.description == "unused"
            else ""
        )
        f.start = d.get("regpos", None)
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
            f.data = " " * (f.width - 1)
        if f.width > 1:
            f.wave = f"[{':'*(f.width-2)}]"
        else:
            f.wave = "b"
        return f

    def to_dict(self):
        """
        Allow one field per line representation
        """
        return {s: getattr(self, s, None) for s in self.__slots__}


def convert(obj: dict) -> tuple[bool, dict]:
    """
    convert a register definition as a wavelane
    """
    reg = Register()
    # name of the register
    reg.name = [name for name in obj.keys() if name not in ["config", "head", "foot"]][-1]
    for field in obj.get(reg.name, []):
        reg.push_field(field)
    # default value from wavedrom format
    if reg.name == "reg":
        reg.name = ""
    reg.config = obj.get("config", {})
    return (0, reg.to_wavelane())
