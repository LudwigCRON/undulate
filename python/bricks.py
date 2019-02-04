#!/usr/bin/env python3

"""
bricks.py declare the basic building block
to generate a waveform
"""

from enum import Enum, unique
from math import atan2, pi, exp

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
  meta  = 'm'
  ana   = 'a'

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
      (BRICKS.x, BRICKS.low),
      (BRICKS.x, BRICKS.zero),
      (BRICKS.x, BRICKS.high),
      (BRICKS.x, BRICKS.one),
      (BRICKS.data, BRICKS.zero),
      (BRICKS.data, BRICKS.one)
    ]:
      return True
    return False

class Brick:
  """
  define the brick as a composition of paths, arrows, and generic polygons
  to fill an area
  """
  __slots__ = ["symbol", "paths", "arrows", "polygons", "splines", "text"]
  def __init__(self):
    self.symbol    = None
    self.paths     = []
    self.arrows    = []
    self.polygons  = []
    self.splines   = []
    self.text      = (10, 10, "")

  def get_last_y(self):
    last_y = 0
    if self.paths:
      _, last_y = self.paths[0][-1]
    elif self.splines:
      _, _, last_y = self.splines[0][-1]
    return last_y

  def alter_end(self, shift: float = 0, next_y: float = -1):
    if self.symbol == BRICKS.data or self.symbol == BRICKS.x:
      for i, path in enumerate(self.paths):
        x1, y1 = path[-1]
        x2, y2 = path[-2]
        self.paths[i] = path[:-1] + [(x2+shift, y2), (x1+shift, next_y if next_y > -1 else y1)]
      for i, poly in enumerate(self.polygons):
        l = int(len(poly)/2)
        x1, y1 = poly[l-1]
        x2, y2 = poly[l]
        x3, y3 = poly[l+1]
        self.polygons[i] = poly[:l-1] + [(x1+shift, y1), (x2+shift, next_y if next_y > -1 else y2), (x3+shift, y3)] + poly[l+1:]

def generate_brick(symbol: str, **kwargs) -> dict:
  # get option supported
  brick_width        = kwargs.get("brick_width", 40)
  height             = kwargs.get("brick_height", 20)
  slewing            = kwargs.get("slewing", 0)
  duty_cycle         = kwargs.get("duty_cycle", 0.5)
  ignore_transition  = kwargs.get("ignore_transition", False)
  is_repeated        = kwargs.get("is_repeated", 1)
  last_y             = kwargs.get("last_y", None)
  next_y             = kwargs.get("next_y", None)
  equation           = kwargs.get("equation", None)
  # calculate the angle of the arrow
  arrow_angle = atan2(height, slewing) * 180 / pi
  s, width = 0, brick_width * is_repeated
  # create the brick
  b = Brick()
  b.symbol = symbol
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
    s = 1
  elif symbol == BRICKS.one:
    last_y = 0 if last_y is None else last_y
    b.paths.append([(0, last_y), (3, last_y), (3+slewing, 0), (width, 0)])
    s = 1
  elif symbol == BRICKS.highz:
    last_y = height/2 if last_y is None else last_y
    dt = abs(height/2-last_y)*slewing/height
    b.splines.append([('M', 0, last_y), ('C', dt, height/2), ('', dt, height/2), ('', min(width, 20), height/2), ('L', width, height/2)])
  elif symbol == BRICKS.data or symbol == BRICKS.x:
    last_y = height if last_y is None else last_y
    b.paths.append([(0, last_y), (slewing, 0), (width-slewing, 0), (width, height/2)])
    b.paths.append([(0, last_y), (slewing, height), (width-slewing, height), (width, height/2)])
    b.polygons.append([
      (0, height/2), (slewing, 0), (width-slewing, 0), (width, height/2),
      (width-slewing, height), (slewing, height), (0, height/2)
    ])
    if symbol == BRICKS.data:
      b.text = (width/2, height/2, kwargs.get("data", ""))
  elif symbol == BRICKS.gap:
    b.splines.append([('M', -7, height+2), ('C', -2, height+2), ('', -2, -2), ('', 3, -2)])
    b.splines.append([('M', -3, height+2), ('C',  2, height+2), ('',  2, -2), ('', 7, -2)])
  elif symbol == BRICKS.up:
    b.splines.append([('m', 0, last_y), ('', 3, 0), ('C', 3+slewing, last_y), ('', 3+slewing, 0), ('', min(width, 20), 0), ('L', width, 0)])
  elif symbol == BRICKS.down:
    b.splines.append([('m', 0, last_y), ('', 3, 0), ('C', slewing, last_y), ('', 3+slewing, height-last_y), ('', min(width, 20), height), ('L', width, height)])
  elif symbol == BRICKS.meta:
    last_y = height/2 if last_y is None else last_y
    dt = abs(last_y-height/2) * slewing / height
    n = int(32*(width*0.75-dt)/width)
    step = (width*0.75-dt)/n
    _tmp = [('M', 0, last_y)]
    for i in range(n):
      dy = 0 if i%4 in [0, 2] else height if i%4==3 else -height
      _tmp.append(('S' if i==0 else '', dt+i*step, (height+exp(-4*i/n)*dy)*0.5))
    _tmp.extend([('', width*0.75, height/2), ('', width, height/2)])
    b.splines.append(_tmp)
  elif symbol == BRICKS.ana:
    try:
      if equation:
        b.paths.append(eval(equation, locals(), None))
    except Exception as e:
      print(getattr(e, 'message', repr(e)))
  else:
    raise NotImplementedError()
  # filter paths according to options
  if ignore_transition:
    for i, p in enumerate(b.paths):
      x, y = p[1+s]
      b.paths[i] = [(0, last_y)] + p[1+s:]
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