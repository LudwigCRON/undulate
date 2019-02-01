#!/usr/bin/env python3

"""
bricks.py declare the basic building block
to generate a waveform
"""

from enum import Enum, unique
from math import atan2, pi

@unique
class BRICKS(Enum):
  """
  BRICKS enumerate the different allowed block
  and symbol to describe a waveform
  """
  nclk  = 'n'
  pclk  = 'p'
  Nclk  = 'N'
  Pclk  = 'P'
  low   = 'l'
  Low   = 'L'
  high  = 'h'
  High  = 'H'
  zero  = '0'
  one   = '1'
  gap   = "|"
  highz = 'z'
  x     = 'x'
  data  = '='
  up    = 'u'
  down  = 'd'

  @staticmethod
  def from_str(s: str):
    """
    from_str return the corresponding enumeration from a char
    """
    if s in "23456789":
      return BRICKS.data
    a = [b for b in BRICKS if b.value == s]
    return a[0] if a else None

  @staticmethod
  def ignore_transition(f, t):
    """
    define special case when transistion are skip to prevent
    glitch by default
    """
    if (f, t) in [
      
    ]:
      return True
    return False

def start_derivative(path: list) -> float:
  x21, y21 = path[0]
  x22, y22 = path[1]
  return slope(x21, y21, x22, y22)

def end_derivative(path: list) -> float:
  x21, y21 = path[-2]
  x22, y22 = path[-1]
  return slope(x21, y21, x22, y22)

def slope(x1: float, y1: float, x2: float, y2: float) -> float:
  if (x2-x1) == 0:
    return (y2-y1)
  return (y2-y1)/(x2-x1)

def limit_derivative(path: list, l: float) -> list:
  ans = []
  pX, pY = 0, 0
  for _, p in enumerate(path):
    x, y = p
    s = slope(pX, pY, x, y)
    ans.append((x, pY + s * (x-pX)) if abs(s) > l else (x, y))
    pX, pY = ans[-1]
  return ans

class Brick:
  """
  define the brick as a composition of paths, arrows, and generic polygons
  to fill an area
  """
  __slots__ = ["paths", "arrows", "polygons", "splines", "text"]
  def __init__(self):
    self.paths     = []
    self.arrows    = []
    self.polygons  = []
    self.splines   = []
    self.text      = (10, 10, "") 

def generate_brick(symbol: str, **kwargs) -> dict:
  # get option supported
  brick_width        = kwargs.get("brick_width", 40)
  height             = kwargs.get("brick_height", 20)
  slewing            = kwargs.get("slewing", 0)
  duty_cycle         = kwargs.get("duty_cycle", 0.5)
  ignore_transition  = kwargs.get("ignore_transition", False)
  is_repeated        = kwargs.get("is_repeated", 1)
  last_y             = kwargs.get("last_y", None)
  # calculate the angle of the arrow
  arrow_angle = atan2(height, slewing) * 180 / pi
  s, width = 0, brick_width * is_repeated
  # create the brick
  b = Brick()
  if symbol == BRICKS.nclk:
    last_y = height/2 if last_y is None else last_y
    dt = (height-last_y) * slewing / height
    b.paths.append([
      (0, last_y), (dt, height), (width*duty_cycle-slewing/2, height),
      (width*duty_cycle+slewing/2, 0), (width-slewing/2, 0), (width, height/2)
    ])
    s = 1
  elif symbol == BRICKS.pclk:
    last_y = height/2 if last_y is None else last_y
    dt = last_y * slewing / height
    b.paths.append([
      (0, last_y), (dt, 0), (width*duty_cycle-slewing/2, 0), 
      (width*duty_cycle+slewing/2, height), (width-slewing/2, height), (width, height/2)
    ])
    s = 1
  elif symbol == BRICKS.Nclk:
    last_y = height/2 if last_y is None else last_y
    dt = (height-last_y) * slewing / height
    b.paths.append([
      (0, last_y), (dt, height), (width*duty_cycle-slewing/2, height), 
      (width*duty_cycle+slewing/2, 0), (width-slewing/2, 0), (width, height/2)
    ])
    b.arrows.append((dt * (height/2 - last_y)/height, height/2, arrow_angle))
    s = 1
  elif symbol == BRICKS.Pclk:
    last_y = height/2 if last_y is None else last_y
    dt = last_y * slewing / height
    b.paths.append([
      (0, last_y), (dt, 0), (width*duty_cycle-slewing/2, 0),
      (width*duty_cycle+slewing/2, height), (width-slewing/2, height), (width, height/2)
    ])
    b.arrows.append((-dt * (height/2 - last_y)/height, height/2, -arrow_angle))
    s = 1
  elif symbol == BRICKS.low or symbol == BRICKS.Low:
    last_y = height if last_y is None else last_y
    dt = (height-last_y) * slewing / height
    b.paths.append([(0, last_y), (dt, height), (width, height)])
    if symbol == BRICKS.Low:
      b.arrows.append((dt * (height/2 - last_y)/height, height/2, arrow_angle))
  elif symbol == BRICKS.high or symbol == BRICKS.High:
    last_y = 0 if last_y is None else last_y
    dt = last_y * slewing / height
    b.paths.append([(0, last_y), (dt, 0), (width, 0)])
    if symbol == BRICKS.High:
      b.arrows.append((-dt * (height/2 - last_y)/height, height/2, -arrow_angle))
  elif symbol == BRICKS.zero:
    last_y = height if last_y is None else last_y
    b.paths.append([(0, last_y), (3, last_y), (3+slewing, height), (width, height)])
  elif symbol == BRICKS.one:
    last_y = 0 if last_y is None else last_y
    b.paths.append([(0, last_y), (3, last_y), (3+slewing, 0), (width, 0)])
  elif symbol == BRICKS.highz:
    last_y = height/2 if last_y is None else last_y
    dt = abs(height/2-last_y)*slewing/height
    b.splines.append([('M', 0, last_y), ('C', dt, height/2), ('', dt, height/2), ('', min(width, 20), height/2), ('L', width, height/2)])
  elif symbol == BRICKS.data or symbol == BRICKS.x:
    last_y = height if last_y is None else last_y
    b.paths.append([(0, last_y), (5, 0), (width-5, 0), (width, height/2)])
    b.paths.append([(0, last_y), (5, height), (width-5, height), (width, height/2)])
    b.polygons.append([
      (0, height/2), (5, 0), (width-5, 0), (width, height/2),
      (width-5, height), (5, height), (0, height/2)
    ])
    if symbol == BRICKS.data:
      b.text = (width/2, height/2, kwargs.get("data", ""))
  elif symbol == BRICKS.gap:
    pass
  elif symbol == BRICKS.up:
    b.splines.append([('m', 0, last_y), ('', 3, 0), ('C', 3+slewing, last_y), ('', 3+slewing, 0), ('', min(width, 20), 0), ('L', width, 0)])
  elif symbol == BRICKS.down:
    b.splines.append([('m', 0, last_y), ('', 3, 0), ('C', slewing, last_y), ('', 3+slewing, height-last_y), ('', min(width, 20), height), ('L', width, height)])
  else:
    raise NotImplementedError()
  # filter paths according to options
  if ignore_transition:
    for i, p in enumerate(b.paths):
      x, y = p[1+s]
      b.paths[i] = [(0, y)] + p[1+s:]
    for i, p in enumerate(b.splines):
      c, x, y = p[-1]
      b.splines[i] = [('M', 0, last_y), ('', x, y)]
    for i, p in enumerate(b.polygons):
      x0, y0 = p[0]
      x1, y1 = p[1]
      x2, y2 = p[-2]
      x3, y3 = p[-1]
      b.polygons[i] = [(x0, y1)] + p[2:-2] + [(x3, y2)]
      
  return b
