"""Definition of Shape in Annotations"""

import copy
from math import cos, sin, atan2
from typing import List
from undulate.bricks.generic import ShapeFactory, SplineSegment, Point
from undulate.renderers.renderer import Renderer

ARROWS_PREFIX = "<*# "
ARROWS_SUFFIX = ">*# "


def scircle(x: float, y: float, r: float) -> List[SplineSegment]:
    """Generate a circle using 4-quadrant bezier curves"""
    return [
        SplineSegment("M", x - r, y),
        SplineSegment("C", x - r, y),
        SplineSegment("", x - r, y - r),
        SplineSegment("", x, y - r),
        SplineSegment("C", x, y - r),
        SplineSegment("", x + r, y - r),
        SplineSegment("", x + r, y),
        SplineSegment("C", x + r, y),
        SplineSegment("", x + r, y + r),
        SplineSegment("", x, y + r),
        SplineSegment("C", x, y + r),
        SplineSegment("", x - r, y + r),
        SplineSegment("", x - r, y),
        SplineSegment("Z", 0, 0),
    ]


def square(x: float, y: float, w: float) -> List[SplineSegment]:
    """Generate a square using a list of points"""
    return [
        SplineSegment("M", x - w / 2, y - w / 2),
        SplineSegment("L", x + w / 2, y - w / 2),
        SplineSegment("L", x + w / 2, y + w / 2),
        SplineSegment("L", x - w / 2, y + w / 2),
    ]


def arrow_angle(dy: float, dx: float) -> float:
    """
    Calculate the angle to align arrows based on
    the derivative of the signal

    Args:
        dy (float)
        dx (float)
    Returns:
        angle in degree
    """
    if dx == 0:
        return 90 if dy > 0 else -90
    return 180 * atan2(dy, dx) / 3.14159


def arrow_markers(renderer: Renderer, pattern: str, ds: Point, de: Point, **kwargs) -> str:
    """Generate markers at extremities of an arrow/edge"""
    ans = ""
    start = kwargs.get("start")
    end = kwargs.get("end")
    kwargs["style_repr"] = "edge-arrow"
    if pattern.startswith("<"):
        angle = arrow_angle(ds.y, ds.x)
        ans += renderer.arrow(
            start.x - 3 * cos(angle * 3.14159 / 180),
            start.y - 3 * sin(angle * 3.14159 / 180),
            angle,
            **kwargs
        )
    elif pattern.startswith("*"):
        ans += renderer.spline(scircle(start.x, start.y, 3), **kwargs)
    elif pattern.startswith("#"):
        ans += renderer.spline(square(start.x, start.y, 6), **kwargs)
    if pattern.endswith(">"):
        angle = arrow_angle(de.y, de.x)
        ans += renderer.arrow(
            end.x - 3 * cos(angle * 3.14159 / 180),
            end.y - 3 * sin(angle * 3.14159 / 180),
            angle,
            **kwargs
        )
    elif pattern.endswith("*"):
        ans += renderer.spline(scircle(end.x, end.y, 3), **kwargs)
    elif pattern.endswith("#"):
        ans += renderer.spline(square(end.x, end.y, 6), **kwargs)
    return ans


def generate_patterns(prefixs: list, root: str, suffixs: list):
    """
    generate possible pattern prefixs/root/suffixs
    """
    for p in prefixs:
        for s in suffixs:
            pattern = "%s%s%s" % (p, root, s)
            yield pattern.strip()


def TimeCompressor(renderer: Renderer, pattern: str, **kwargs) -> str:
    """
    Multiline Time Compressor

    Args:
        x (float): position of the time compressor
        ymin (float): top limit of the time compressor
        ymax (float): bottom limit of the time compressor
    """
    ans = ""
    x = kwargs.get("x", 0)
    ymin = kwargs.get("ymin", 0)
    ymax = kwargs.get("ymax", 10000)
    pts_1 = [
        SplineSegment("M", x, ymin),  # |
        SplineSegment("L", x, (ymax + ymin) / 2 - 10),  # |
        SplineSegment("L", x - 10, (ymax + ymin) / 2),  # /
        SplineSegment("L", x, (ymax + ymin) / 2 + 10),  # \
        SplineSegment("L", x, ymax),  # |
    ]
    pts_2 = [
        SplineSegment("M", x + 5, ymin),  # |
        SplineSegment("L", x + 5, (ymax + ymin) / 2 - 10),  # |
        SplineSegment("L", x - 4, (ymax + ymin) / 2),  # /
        SplineSegment("L", x + 5, (ymax + ymin) / 2 + 10),  # \
        SplineSegment("L", x + 5, ymax),  # |
    ]
    poly = copy.deepcopy(pts_2)
    poly.extend(pts_1[::-1])
    ans = renderer.polygon(poly, style_repr="hide")
    ans += renderer.spline(pts_1, style_repr="big_gap")
    ans += renderer.spline(pts_2, style_repr="big_gap")
    return ans


def HorizontalLine(renderer: Renderer, pattern: str, **kwargs) -> str:
    """
    Horizontal Line

    Args:
        y (float): position of the line
        xmin (float): left limit of the segment
        xmax (float): right limit of the segment
    """
    xmin = kwargs.get("xmin", 0)
    xmax = kwargs.get("xmax", 10000)
    y = kwargs.get("y", 0)
    pts = [SplineSegment("M", xmin, y), SplineSegment("L", xmax, y)]
    return renderer.spline(pts, **kwargs)


def VerticalLine(renderer: Renderer, pattern: str, **kwargs) -> str:
    """
    Vertical Line

    Args:
        x (float): position of the line
        ymin (float): top limit of the segment
        ymax (float): bottom limit of the segment
    """
    ymin = kwargs.get("ymin", 0)
    ymax = kwargs.get("ymax", 10000)
    x = kwargs.get("x", 0)
    pts = [SplineSegment("M", x, ymin), SplineSegment("L", x, ymax)]
    return renderer.spline(pts, **kwargs)


def ArrowStraight(renderer: Renderer, pattern: str, **kwargs) -> str:
    """
    Straight Line Edge

    Args:
        start (Point): coordinate of start extremity
        end (Point): coordinate of end extremity
    """
    start = kwargs.get("start")
    end = kwargs.get("end")
    kwargs["style_repr"] = "edge"
    pts = [
        SplineSegment("M", start.x, start.y),
        SplineSegment("L", end.x, end.y),
    ]
    ans = renderer.spline(pts, is_edge=True, **kwargs)
    # draw markers
    ds = Point(start.x - end.x, start.y - end.y)
    de = Point(end.x - start.x, end.y - start.y)
    ans += arrow_markers(renderer, pattern, ds, de, **kwargs)
    return ans


def ArrowHV(renderer: Renderer, pattern: str, **kwargs) -> str:
    """
    Straight Line Edge with a corner Horizontal -> Vertical

    Args:
        start (Point): coordinate of start extremity
        end (Point): coordinate of end extremity
    """
    start = kwargs.get("start")
    end = kwargs.get("end")
    kwargs["style_repr"] = "edge"
    pts = [
        SplineSegment("M", start.x, start.y),
        SplineSegment("L", end.x, start.y),
        SplineSegment("L", end.x, end.y),
    ]
    ans = renderer.spline(pts, is_edge=True, **kwargs)
    # draw markers
    ds = Point(start.x - end.x, 0)
    de = Point(0, end.y - start.y)
    ans += arrow_markers(renderer, pattern, ds, de, **kwargs)
    return ans


def ArrowVH(renderer: Renderer, pattern: str, **kwargs) -> str:
    """
    Straight Line Edge with corner Vertical -> Horizontal

    Args:
        start (Point): coordinate of start extremity
        end (Point): coordinate of end extremity
    """
    start = kwargs.get("start")
    end = kwargs.get("end")
    kwargs["style_repr"] = "edge"
    pts = [
        SplineSegment("M", start.x, start.y),
        SplineSegment("L", start.x, end.y),
        SplineSegment("L", end.x, end.y),
    ]
    ans = renderer.spline(pts, is_edge=True, **kwargs)
    # draw markers
    ds = Point(0, start.y - end.y)
    de = Point(end.x - start.x, 0)
    ans += arrow_markers(renderer, pattern, ds, de, **kwargs)
    return ans


def ArrowHVH(renderer: Renderer, pattern: str, **kwargs) -> str:
    """
    Straight Line Edge Horizontal -> Vertical -> Horizonal

    Args:
        start (Point): coordinate of start extremity
        end (Point): coordinate of end extremity
    """
    start = kwargs.get("start")
    end = kwargs.get("end")
    kwargs["style_repr"] = "edge"
    pts = [
        SplineSegment("M", start.x, start.y),
        SplineSegment("L", (start.x + end.x) * 0.5, start.y),
        SplineSegment("L", (start.x + end.x) * 0.5, end.y),
        SplineSegment("L", end.x, end.y),
    ]
    ans = renderer.spline(pts, is_edge=True, **kwargs)
    # draw markers
    ds = Point(start.x - end.x, 0)
    de = Point(end.x - start.x, 0)
    ans += arrow_markers(renderer, pattern, ds, de, **kwargs)
    return ans


def ArrowWave(renderer: Renderer, pattern: str, **kwargs) -> str:
    """
    S-Shaped Edge

    Args:
        start (Point): coordinate of start extremity
        end (Point): coordinate of end extremity
    """
    start = kwargs.get("start")
    end = kwargs.get("end")
    kwargs["style_repr"] = "edge"
    pts = [
        SplineSegment("M", start.x, start.y),
        SplineSegment("C", start.x * 0.1 + end.x * 0.9, start.y),
        SplineSegment("", start.x * 0.9 + end.x * 0.1, end.y),
        SplineSegment("", end.x, end.y),
    ]
    ans = renderer.spline(pts, is_edge=True, **kwargs)
    # draw markers
    ds = Point(pts[0].x - pts[1].x, pts[0].y - pts[1].y)
    de = Point(pts[-1].x - pts[-2].x, pts[-1].y - pts[-2].y)
    ans += arrow_markers(renderer, pattern, ds, de, **kwargs)
    return ans


def ArrowHWave(renderer: Renderer, pattern: str, **kwargs) -> str:
    """
    Straight -> Curved Line Edge

    Args:
        start (Point): coordinate of start extremity
        end (Point): coordinate of end extremity
    """
    start = kwargs.get("start")
    end = kwargs.get("end")
    kwargs["style_repr"] = "edge"
    pts = [
        SplineSegment("M", start.x, start.y),
        SplineSegment("C", end.x, start.y),
        SplineSegment("", end.x, end.y),
        SplineSegment("", end.x, end.y),
    ]
    ans = renderer.spline(pts, is_edge=True, **kwargs)
    # draw markers
    ds = Point(pts[0].x - pts[1].x, pts[0].y - pts[1].y)
    de = Point(pts[-1].x - pts[-3].x, pts[-1].y - pts[-3].y)
    ans += arrow_markers(renderer, pattern, ds, de, **kwargs)
    return ans


def ArrowWaveH(renderer: Renderer, pattern: str, **kwargs) -> str:
    """
    Curved -> Straight Line Edge

    Args:
        start (Point): coordinate of start extremity
        end (Point): coordinate of end extremity
    """
    start = kwargs.get("start")
    end = kwargs.get("end")
    kwargs["style_repr"] = "edge"
    pts = [
        SplineSegment("M", start.x, start.y),
        SplineSegment("C", start.x, start.y),
        SplineSegment("", start.x, end.y),
        SplineSegment("", start.x * 0.1 + end.x * 0.9, end.y),
        SplineSegment("L", end.x, end.y),
    ]
    ans = renderer.spline(pts, is_edge=True, **kwargs)
    # draw markers
    ds = Point(pts[1].x - pts[2].x, pts[1].y - pts[2].y)
    de = Point(pts[-1].x - pts[-2].x, pts[-1].y - pts[-2].y)
    ans += arrow_markers(renderer, pattern, ds, de, **kwargs)
    return ans


def initialize() -> None:
    ShapeFactory.register("||", TimeCompressor)
    ShapeFactory.register("-", HorizontalLine)
    ShapeFactory.register("|", VerticalLine)
    for pattern in generate_patterns(ARROWS_PREFIX, "-", ARROWS_SUFFIX):
        if pattern != "-":
            ShapeFactory.register(pattern, ArrowStraight)
    for pattern in generate_patterns(ARROWS_PREFIX, "~", ARROWS_SUFFIX):
        ShapeFactory.register(pattern, ArrowWave)
    for pattern in generate_patterns(ARROWS_PREFIX, "-~", ARROWS_SUFFIX):
        ShapeFactory.register(pattern, ArrowHWave)
    for pattern in generate_patterns(ARROWS_PREFIX, "~-", ARROWS_SUFFIX):
        ShapeFactory.register(pattern, ArrowWaveH)
    for pattern in generate_patterns(ARROWS_PREFIX, "-|", ARROWS_SUFFIX):
        ShapeFactory.register(pattern, ArrowHV)
    for pattern in generate_patterns(ARROWS_PREFIX, "|-", ARROWS_SUFFIX):
        ShapeFactory.register(pattern, ArrowVH)
    for pattern in generate_patterns(ARROWS_PREFIX, "-|-", ARROWS_SUFFIX):
        ShapeFactory.register(pattern, ArrowHVH)
