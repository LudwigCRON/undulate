#!/usr/bin/env python3
# spell-checker: disable

"""
bricks.py declare the basic building block
to generate a waveform
"""

from enum import Enum, unique
import math
import random

ANALOG_CONTEXT = {
  "time": [],
  "Tmax": 20,
  "VSSA": 0,
  "VDDA": 1.8,
  "atan2": math.atan2,
  "pi": math.pi,
  "exp": math.exp,
  "sin": math.sin,
  "cos": math.cos,
  "tan": math.tan,
  "tanh": math.tanh,
  "sqrt": math.sqrt,
  "rnd": random.random
}

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
  Meta  = 'M'
  ana   = 'a'
  step  = 's'
  cap   = 'c'

  @staticmethod
  def transform_y(y: float, height: float = 20):
    return height-height*(y-ANALOG_CONTEXT["VSSA"])/(ANALOG_CONTEXT["VDDA"]-ANALOG_CONTEXT["VSSA"])

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
    define special case when transition are skip to prevent
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
  equation           = kwargs.get("equation", None)
  # rendering block size
  s, width = 0, brick_width * is_repeated
  # calculate the angle of the arrow
  arrow_angle = math.atan2(height, slewing) * 180 / math.pi
  # update analogue context
  ANALOG_CONTEXT["Tmax"] = width
  ANALOG_CONTEXT["Ymax"] = height
  ANALOG_CONTEXT["time"] = range(0, int(width+1))
  # create the brick
  b = Brick()
  b.symbol = symbol
  # clock signals description (pPnNlLhH)
  # (N|n)clk: falling edge (with|without) arrow for repeated pattern
  if symbol in [BRICKS.nclk, BRICKS.Nclk]:
    last_y = height/2 if last_y is None else last_y
    dt = (height-last_y) * slewing / height
    b.paths.append([
      (0, last_y), (dt, height), (width*duty_cycle-slewing/2, height),
      (width*duty_cycle+slewing/2, 0), (width-slewing/2, 0), (width, height/2)
    ])
    if symbol == BRICKS.Nclk:
      b.arrows.append((dt * (height/2 - last_y)/height, height/2, arrow_angle))
    s = 1
  # (P|p)clk: rising edge (with|without) arrow for repeated pattern
  elif symbol in [BRICKS.pclk, BRICKS.Pclk]:
    last_y = height/2 if last_y is None else last_y
    dt = last_y * slewing / height
    b.paths.append([
      (0, last_y), (dt, 0), (width*duty_cycle-slewing/2, 0),
      (width*duty_cycle+slewing/2, height), (width-slewing/2, height), (width, height/2)
    ])
    if symbol == BRICKS.Pclk:
      b.arrows.append((-dt * (height/2 - last_y)/height, height/2, -arrow_angle))
    s = 1
  # (L|l)ow: falling edge (with|without) arrow and stuck
  elif symbol == BRICKS.low or symbol == BRICKS.Low:
    last_y = height if last_y is None else last_y
    dt = (height-last_y) * slewing / height
    b.paths.append([(0, last_y), (dt, height), (width, height)])
    if symbol == BRICKS.Low:
      b.arrows.append((dt * (height / 2 - last_y) / height, height / 2, arrow_angle))
  # (H|h)igh: rising edge (with|without) arrow and stuck
  elif symbol == BRICKS.high or symbol == BRICKS.High:
    last_y = 0 if last_y is None else last_y
    dt = last_y * slewing / height
    b.paths.append([(0, last_y), (dt, 0), (width, 0)])
    if symbol == BRICKS.High:
      b.arrows.append((-dt * (height / 2 - last_y) / height, height / 2, -arrow_angle))
  # description for data (z01x=)
  elif symbol == BRICKS.highz:
    last_y = height/2 if last_y is None else last_y
    dt = abs(height/2-last_y)*slewing/height
    b.splines.append([
      ('M', 0, last_y), ('C', dt, height / 2), ('', dt, height / 2),
      ('', min(width, 20), height/2), ('L', width, height/2)])
  elif symbol == BRICKS.zero:
    last_y = height if last_y is None else last_y
    b.paths.append([(0, last_y), (3, last_y), (3+slewing, height), (width, height)])
    s = 1
  elif symbol == BRICKS.one:
    last_y = 0 if last_y is None else last_y
    b.paths.append([(0, last_y), (3, last_y), (3+slewing, 0), (width, 0)])
    s = 1
  elif symbol == BRICKS.data or symbol == BRICKS.x:
    last_y = height if last_y is None else last_y
    b.paths.append([(0, last_y), (slewing, 0), (width-slewing, 0), (width, height/2)])
    b.paths.append([(0, last_y), (slewing, height), (width-slewing, height), (width, height/2)])
    b.polygons.append([
      (0, height/2), (slewing, 0), (width-slewing, 0), (width, height/2),
      (width-slewing, height), (slewing, height), (0, height/2)
    ])
    if symbol == BRICKS.data:
      b.text = (width / 2, height / 2, kwargs.get("data", ""))
  # time compression symbol
  elif symbol == BRICKS.gap:
    b.splines.append([
      ('m', 7, -2), ('', -4, 0), ('c', -5, 0), ('', -5, height + 4),
      ('', -10, height + 4), ('l', 4, 0), ('C', 2, height + 4), ('', 2, -2),
      ('', 7, -2), ('z', '', '')])
    b.splines.append([('M', -7, height+2), ('C', -2, height+2), ('', -2, -2), ('', 3, -2)])
    b.splines.append([('M', -3, height + 2), ('C', 2, height + 2), ('', 2, -2), ('', 7, -2)])
  # capacitive charge to 1
  elif symbol == BRICKS.up:
    b.splines.append([
      ('m', 0, last_y), ('', 3, 0), ('C', 3 + slewing, last_y),
      ('', 3 + slewing, 0), ('', min(width, 20), 0), ('L', width, 0)])
  # capacitive discharge to 0
  elif symbol == BRICKS.down:
    b.splines.append([
      ('m', 0, last_y), ('', 3, 0), ('C', slewing, last_y),
      ('', 3+slewing, height-last_y), ('', min(width, 20), height), ('L', width, height)])
  # metastability to zero
  elif symbol == BRICKS.meta:
    last_y = height/2 if last_y is None else last_y
    dt = abs(last_y-height/2) * slewing / height
    time = range(int(dt), int(width*0.75+1))
    if (int(0.75*width+1)-int(dt)) % 2 == 1:
      time = range(int(dt), int(width*0.75+2))
    _tmp = [('M', 0, last_y)]
    for t in time:
      _tmp.append(('S' if t == dt else '', t, (1+math.exp((t-width)/width)*math.sin(8*math.pi*t/width))*0.5*height))
    _tmp.extend([('S', width*0.75, height), ('', width, height)])
    b.splines.append(_tmp)
  # metastability to one
  elif symbol == BRICKS.Meta:
    last_y = height/2 if last_y is None else last_y
    dt = abs(last_y-height/2) * slewing / height
    time = range(int(dt), int(width*0.75+1))
    if (int(0.75*width+1)-int(dt)) % 2 == 1:
      time = range(int(dt), int(width*0.75+2))
    _tmp = [('M', 0, last_y)]
    for t in time:
      _tmp.append(('S' if t == dt else '', t, (1+math.exp((t-width)/width)*math.cos(8*math.pi*t/width))*0.5*height))
    _tmp.extend([('S', width*0.75, 0), ('', width, 0)])
    b.splines.append(_tmp)
  # full custom analogue bloc
  elif symbol in [BRICKS.step, BRICKS.cap, BRICKS.ana]:
    last_y = height if last_y is None else last_y
    if symbol in [BRICKS.step, BRICKS.cap]:
      y = BRICKS.transform_y(float(equation), height)
      dt = abs(last_y-y) * slewing / height
      print(equation, y, dt)
      if symbol == BRICKS.step:
        b.paths.append([(0, last_y), (dt, y), (width, y)])
      else:
        b.splines.append([
          ('M', 0, last_y), ('C', dt, y), ('', dt, y),
          ('', width, y), ('L', width, y)])
    else:
      try:
        b.paths.append([(0, last_y)] + [(p[0], BRICKS.transform_y(p[1], height)) for p in eval(equation, ANALOG_CONTEXT)])
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
      b.splines[i] = [('M', 0, last_y), (c, x, y)]
    for i, p in enumerate(b.polygons):
      x0, _ = p[0]
      _, y1 = p[1]
      _, y2 = p[-2]
      x3, _ = p[-1]
      b.polygons[i] = [(x0, y1)] + p[2:-2] + [(x3, y2)]
  return b