#!/usr/bin/env python3

from enum import Enum, unique
from math import atan2, pi

@unique
class BRICKS(Enum):
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
  def from_str(s:str):
    if s in "23456789":
      return BRICKS.data
    a = [b for b in BRICKS if b.value == s]
    return a[0] if len(a) > 0 else None
    
  @staticmethod
  def ignore_transition(f, t):
    if (f, t) in [
      (BRICKS.low, BRICKS.low),
      (BRICKS.high, BRICKS.high),
      (BRICKS.zero, BRICKS.one),
      (BRICKS.one, BRICKS.zero),
      (BRICKS.high, BRICKS.one),
      (BRICKS.high, BRICKS.zero),
      (BRICKS.zero, BRICKS.low),
      (BRICKS.low, BRICKS.one),
      (BRICKS.x, BRICKS.x),
      (BRICKS.x, '.'),
      (BRICKS.data, BRICKS.data),
      (BRICKS.down, '.'),
      (BRICKS.up, '.')
    ]:
      return True
    return False

def start_derivative(path):
  x21, y21 = path[0]
  x22, y22 = path[1]
  return slope(x21, y21, x22, y22)

def end_derivative(path):
  x21, y21 = path[-2]
  x22, y22 = path[-1]
  return slope(x21, y21, x22, y22)

def slope(x1, y1, x2, y2):
  if (x2-x1) == 0:
    return (y2-y1)
  return (y2-y1)/(x2-x1)


def limit_derivative(path, l):
  ans = []
  pX, pY = 0, 0
  for i, p in enumerate(path):
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
  __slots__ = ["paths", "arrows", "polygons", "splines"]
  def __init__(self):
    self.paths     = []
    self.arrows    = []
    self.polygons  = []
    self.splines   = []  

def generate_brick(symbol:str, **kwargs) -> dict:
  # get option supported
  width              = kwargs.get("width", 40)
  height             = kwargs.get("height", 20)
  slewing            = kwargs.get("slewing", 0)
  duty_cycle         = kwargs.get("duty_cycle", 0.5)
  ignore_transition  = kwargs.get("ignore_transition", False)
  last_y             = kwargs.get("last_y", None)
  # calculate the angle of the arrow
  arrow_angle = atan2(height, slewing) * 180 / pi
  s = 0
  # create the brick
  b = Brick()
  if symbol == BRICKS.nclk:
    last_y = height/2 if last_y is None else last_y
    b.paths.append([
      (0, last_y), (slewing/2, height), (width*duty_cycle-slewing/2, height),
      (width*duty_cycle+slewing/2, 0), (width-slewing/2, 0), (width, height/2)
    ])
    s = 1
  elif symbol == BRICKS.pclk:
    last_y = height/2 if last_y is None else last_y
    b.paths.append([
      (0, last_y), (slewing/2, 0), (width*duty_cycle-slewing/2, 0), 
      (width*duty_cycle+slewing/2, height), (width-slewing/2, height), (width, height/2)
    ])
    s = 1
  elif symbol == BRICKS.Nclk:
    last_y = height/2 if last_y is None else last_y
    b.paths.append([
      (0, last_y), (slewing/2, height), (width*duty_cycle-slewing/2, height), 
      (width*duty_cycle+slewing/2, 0), (width-slewing/2, 0), (width, height/2)
    ])
    b.arrows.append((0, height/2, arrow_angle))
    s = 1
  elif symbol == BRICKS.Pclk:
    last_y = height/2 if last_y is None else last_y
    b.paths.append([
      (0, last_y), (slewing/2, 0), (width*duty_cycle-slewing/2, 0),
      (width*duty_cycle+slewing/2, height), (width-slewing/2, height), (width, height/2)
    ])
    b.arrows.append((0, height/2, -arrow_angle))
    s = 1
  elif symbol == BRICKS.low or symbol == BRICKS.Low:
    last_y = height if last_y is None else last_y
    b.paths.append([(0, last_y), (slewing, height), (width, height)])
    if symbol == BRICKS.Low:
      b.arrows.append((0, height/2, arrow_angle))
  elif symbol == BRICKS.high or symbol == BRICKS.High:
    last_y = 0 if last_y is None else last_y
    b.paths.append([(0, last_y), (slewing, 0), (width, 0)])
    if symbol == BRICKS.High:
      b.arrows.append((0, height/2, -arrow_angle))
  elif symbol == BRICKS.zero:
    dt = min(slewing, width*0.15)
    dy = min(height*dt/slewing if slewing > 0 else height, height)
    last_y = 0 if last_y is None else last_y
    dt2 = (height-max(last_y-dy, 0))*slewing/height
    b.paths.append([
      (0, last_y), (dt, max(last_y-dy, 0)), (width*0.15, max(last_y-dy, 0)),
      (width*0.15+dt2, height), (width, height)
    ])
  elif symbol == BRICKS.one:
    dt = min(slewing, width*0.15)
    dy = min(height*dt/slewing if slewing > 0 else height, height)
    last_y = height if last_y is None else last_y
    dt2 = min(last_y+dy, height)*slewing/height
    b.paths.append([
      (0, last_y), (dt, min(last_y+dy, height)), (width*0.15, min(last_y+dy, height)),
      (width*0.15+dt2, 0), (width, 0)
    ])
  elif symbol == BRICKS.highz:
    last_y = height/2 if last_y is None else last_y
    dt = abs(height/2-last_y)*slewing/height
    b.paths.append([(0, last_y), (dt, height/2), (width, height/2)])
  elif symbol == BRICKS.data or symbol == BRICKS.x:
    last_y = height if last_y is None else last_y
    b.paths.append([(0, last_y), (5, 0), (width-5, 0), (width, height/2)])
    b.paths.append([(0, last_y), (5, height), (width-5, height), (width, height/2)])
    b.polygons.append([
      (0, height/2), (5, 0), (width-5, 0), (width, height/2),
      (width-5, height), (5, height), (0, height/2)
    ])
    s = -1
  elif symbol == BRICKS.gap:
    pass
  elif symbol == BRICKS.up:
    b.splines.append([('m', 0, last_y), ('', 3, 0), ('C', 3+slewing, last_y), ('', 3+slewing, 0), ('', width, 0)])
  elif symbol == BRICKS.down:
    b.splines.append([('m', 0, last_y), ('', 3, 0), ('C', slewing, last_y), ('', 3+slewing, height-last_y), ('', width, height)])
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
  return b
