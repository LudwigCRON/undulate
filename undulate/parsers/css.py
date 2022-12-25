import re
from enum import Enum


class SizeUnit(Enum):
    EM = 16
    PX = 1
    PT = 1.333


class LineCap(Enum):
    BUTT = 0
    ROUND = 1
    SQUARE = 2


class LineJoin(Enum):
    MITER = 0
    ROUND = 1
    BEVEL = 2


class TextAlign(Enum):
    LEFT = 0
    CENTER = 1
    RIGHT = 2
    JUSTIFY = 3


class CSSTokenType(Enum):
    RULES = 0
    STRING = 1
    SEP = 2
    END_PROPERTY = 3
    BLOCK_START = 4
    BLOCK_END = 5
    IGNORE = 6
    UNKNOWN = 7
    EOF = 8


def css_tokenizer(stream):
    """
    read a character stream and gather them
    to provide a token to the css parser
    Args:
        character line stream (FileStream/StringIO)

    Returns:
        Tuple(int,CSSTokenType,str):
            line_number (int)
            token_type (CSSTokenType)
            token (str)
    """
    buf = []
    in_string = False
    in_block = False
    in_comment = False
    prev_c = None
    mapping_table = {
        " ": CSSTokenType.IGNORE,
        "\t": CSSTokenType.IGNORE,
        "\n": CSSTokenType.IGNORE,
        ",": CSSTokenType.SEP,
        ":": CSSTokenType.SEP,
        "{": CSSTokenType.BLOCK_START,
        "}": CSSTokenType.BLOCK_END,
        ";": CSSTokenType.END_PROPERTY,
    }
    for i, line in enumerate(stream):
        for c in line:
            token = "".join(buf)
            token_type = CSSTokenType.STRING if in_block else CSSTokenType.RULES
            mc = mapping_table.get(c, CSSTokenType.UNKNOWN)
            if c in "'\"":
                in_string = not in_string
            elif prev_c == "/" and c == "*":
                in_comment = True
                buf = buf[:-1]
            elif prev_c == "*" and c == "/":
                in_comment = False
            elif not in_comment and mc not in [CSSTokenType.IGNORE, CSSTokenType.UNKNOWN]:
                if token and not (c == ":" and not in_block):
                    yield (i, token_type, token)
                    buf = []
                if mc == CSSTokenType.BLOCK_START:
                    in_block = True
                elif mc == CSSTokenType.BLOCK_END:
                    in_block = False
                if not (c == ":" and not in_block):
                    yield (i, mapping_table.get(c), c)
            elif not in_comment and not in_string and mc == CSSTokenType.IGNORE:
                if token:
                    yield (
                        i,
                        token_type,
                        token,
                    )
                    buf = []
            elif not in_comment:
                buf.append(c)
            prev_c = c
        if buf and not in_comment:
            yield (i, CSSTokenType.STRING if in_block else CSSTokenType.RULES, "".join(buf))
            buf = []
    yield (-1, CSSTokenType.EOF, None)


def parse_css_size(S: str) -> tuple:
    """
    convert a css valid representation of a size
    into a value unit tuple
    """
    if isinstance(S, str):
        s = S.strip().lower()
        v = float("".join([c for c in s if c in "0123456789."]))
        u = SizeUnit.EM if "em" in s else SizeUnit.PT if "pt" in s else SizeUnit.PX
        return (v, u)
    return S


def hsl_to_rgb(h, s, l):
    """
    convert hsl([0-359] deg, [0-1] float, [0-1] float) into
    rgb([0-255] int, [0-255] int, [0-255] int)
    """
    c = (2 - 2 * l) * s if l > 0.5 else 2 * l
    y = (h / 60) % 2
    x = (2 - y) * c if y > 1.0 else y
    m = l - c / 2
    rp = c if h < 60 or h >= 300 else x if h < 120 or h >= 240 else 0
    gp = c if h >= 60 and h < 180 else x if h < 240 else 0
    bp = c if h >= 180 and h < 300 else x if h >= 120 else 0
    return [int((rp + m) * 255), int((gp + m) * 255), int((bp + m) * 255)]


def parse_css_color(S: str) -> tuple:
    """
    convert a css valid representation of a color
    into rgba tuple from 0 to 255
    """
    if isinstance(S, list):
        return S
    s = S.strip().lower()
    if s.startswith("rgba"):
        return [int(i, 10) for i in re.split(",| ", s[5:-1]) if i]
    elif s.startswith("rgb"):
        return [int(i, 10) for i in re.split(",| ", s[4:-1]) if i] + [255]
    elif s.startswith("hsla"):
        hsl = []
        for i in re.split(",| ", s[5:-1]):
            if i.strip():
                hsl.append(
                    float("".join([c for c in i if c in "0123456789."])) / 100
                    if "%" in i
                    else float(i)
                )
        rgba = hsl_to_rgb(*hsl[:3])
        rgba.append(hsl[-1] * 255)
        return rgba
    elif s.startswith("hsl"):
        hsl = []
        for i in re.split(",| ", s[4:-1]):
            if i.strip():
                hsl.append(
                    float("".join([c for c in i if c in "0123456789."])) / 100
                    if "%" in i
                    else float(i)
                )
        rgba = hsl_to_rgb(*hsl[:3])
        rgba.append(255)
        return rgba
    elif s.startswith("#"):
        if len(s) == 4:
            return [int(i, 16) * 17 for i in s[1:4]] + [255]
        elif len(s) == 7:
            return [int(s[i : i + 2], 16) for i in range(1, 6, 2)] + [255]
        else:
            return [int(s[i : i + 2], 16) for i in range(1, 8, 2)]
    return s


def css_parser(token_iter):
    """
    construct the style dictionnary from
    an iterator of tokens
    """

    def expect(it, types):
        try:
            line_number, type, token = next(it)
            if type not in types:
                print(
                    "ERROR: unexpected token '%s' at Line %d" % (token, line_number),
                    file=sys.stderr,
                )
                exit(6)
            return token
        except StopIteration:
            return None

    def expect_multiple(it, types, until_types):
        ans = []
        try:
            line_number, type, token = next(it)
            while type in types:
                ans.append(token)
                line_number, type, token = next(it)
            if type not in until_types:
                print(
                    "ERROR: unexpected token '%s' at Line %d" % (token, line_number),
                    file=sys.stderr,
                )
                exit(7)
            return ans, (line_number, type, token)
        except StopIteration:
            return None, None

    def expect_property(it):
        property_name = expect(it, [CSSTokenType.STRING, CSSTokenType.BLOCK_END])
        if property_name is None:
            return None, (-1, CSSTokenType.EOF, "")
        if property_name == "}":
            return None, (-1, CSSTokenType.BLOCK_END, "}")
        expect(it, [CSSTokenType.SEP])
        property_value, b = expect_multiple(
            token_iter,
            [CSSTokenType.STRING, CSSTokenType.SEP],
            [CSSTokenType.END_PROPERTY],
        )
        value = " ".join(property_value)
        # parse number only
        if all([c in "0123456798 " for c in value]):
            property_value = int(value, 10)
        elif all([c in "0123456798. " for c in value]):
            property_value = float(value)
        # parse color
        elif re.match(r"#([0-9A-Fa-f]+)", value):
            property_value = tuple(parse_css_color(value))
        elif property_value[0].startswith("rgb"):
            property_value = tuple(parse_css_color(value))
        elif property_value[0].startswith("hsl"):
            property_value = tuple(parse_css_color(value))
        # parse size
        elif (
            "size" in property_name
            or "padding" in property_name
            or "width" in property_name
        ):
            property_value = parse_css_size(value)
        # align
        elif property_name == "text-align":
            property_value = (
                TextAlign.LEFT
                if "le" in value
                else TextAlign.RIGHT
                if "ri" in value
                else TextAlign.CENTER
                if "ce" in value
                else TextAlign.JUSTIFY
            )
        # linecap
        elif "linecap" in property_name:
            property_value = (
                LineCap.ROUND
                if "ro" in value
                else LineCap.BUTT
                if "bu" in value
                else LineCap.SQUARE
            )
        # linejoin
        elif "linejoin" in property_name:
            property_value = (
                LineJoin.ROUND
                if "ro" in value
                else LineJoin.MITER
                if "mi" in value
                else LineJoin.BEVEL
            )
        # none -> None
        elif "none" in property_value:
            property_value = None
        # array
        elif "," in value and all([c in "0123456789. ," for c in value]):
            property_value = [int(v, 10) for v in property_value if v != ","]
        else:
            property_value = " ".join(value.replace(" ,", ", ").split())
        return (property_name, property_value), b

    def expect_rule(it):
        style = {}
        rule, _ = expect_multiple(
            it,
            [CSSTokenType.RULES, CSSTokenType.SEP],
            [CSSTokenType.BLOCK_START, CSSTokenType.EOF],
        )
        if rule:
            rule = [r for r in rule if r != ","]
        else:
            return None, None
        end_type = CSSTokenType.UNKNOWN
        while end_type != CSSTokenType.BLOCK_END:
            property_or_empty, end_block = expect_property(it)
            if property_or_empty:
                property, value = property_or_empty
                style[property] = value
            if end_block:
                end_type = end_block[1]
        return rule, style

    stylesheet = {}
    rule = ""
    while rule is not None:
        rule, style = expect_rule(token_iter)
        if rule:
            for r in rule:
                rp = r.replace(".", "")
                stylesheet[rp] = style
    return stylesheet


def load(filepath: str):
    with open(filepath, "r+") as fp:
        return css_parser(css_tokenizer(fp))
