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
  imp   = 'i'
  Imp   = 'I'

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
      (BRICKS.data, BRICKS.one),
      (BRICKS.Nclk, BRICKS.Low),
      (BRICKS.nclk, BRICKS.Low),
      (BRICKS.Pclk, BRICKS.Low),
      (BRICKS.pclk, BRICKS.Low),
    ]:
      return True
    return False

class Brick:
  """
  define the brick as a composition of paths, arrows, and generic polygons
  to fill an area
  """
  __slots__ = [
    "symbol", "paths", "arrows", "polygons", "splines", "text",
    "width", "height",
    "slewing", "duty_cycle", "ignore_transition",
    "is_first", "last_y",
    "equation"]
  def __init__(self, **kwargs):
    # get options supported
    # sizing
    self.width  = kwargs.get("brick_width" , 40) * kwargs.get("is_repeated" , 1)
    self.height = kwargs.get("brick_height", 20)
    # physical variants
    self.slewing           = kwargs.get("slewing"          , 0)
    self.duty_cycle        = kwargs.get("duty_cycle"       , 0.5)
    self.ignore_transition = kwargs.get("ignore_transition", False)
    # chaining instance
    self.is_first = kwargs.get("is_first", False)
    self.last_y   = kwargs.get("last_y"  , None)
    # is analogue
    self.equation = kwargs.get("equation", None)
    # items to keep for drawing
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

class Nclk(Brick):
  def __init__(self, **kwargs):
    Brick.__init__(self, **kwargs)
    if self.is_first:
      self.last_y = 0
    else:
      self.last_y = self.height/2 if self.last_y is None else self.last_y
    dt = self.last_y * self.slewing / self.height
    # add shape
    self.paths.append([
      (0, self.last_y), (dt, 0), (self.width*self.duty_cycle-self.slewing/2, 0),
      (self.width*self.duty_cycle+self.slewing/2, self.height), (self.width-self.slewing/2, self.height), (self.width, self.height/2)
    ])
    if self.ignore_transition:
      self.paths[0] = self.paths[0][0] + self.paths[0][2:]
    # add arrow
    if kwargs.get("add_arrow", False):
      arrow_angle = - math.atan2(-self.height, self.slewing) * 180 / math.pi
      self.arrows.append((dt * (self.height/2 - self.last_y)/self.height + self.width*self.duty_cycle, self.height/2, arrow_angle))

class Pclk(Brick):
  def __init__(self, **kwargs):
    Brick.__init__(self, **kwargs)
    if self.is_first:
      self.last_y = self.height
    else:
      self.last_y = self.height/2 if self.last_y is None else self.last_y
    dt = self.last_y * self.slewing / self.height
    # add shape
    self.paths.append([
      (0, self.last_y), (dt, 0), (self.width*self.duty_cycle-self.slewing/2, 0),
      (self.width*self.duty_cycle+self.slewing/2, self.height), (self.width-self.slewing/2, self.height), (self.width, self.height/2)
    ])
    if self.ignore_transition:
      self.paths[0] = self.paths[0][0] + self.paths[0][2:]
    # add arrow
    if kwargs.get("add_arrow", False):
      arrow_angle = math.atan2(-self.height, self.slewing) * 180 / math.pi
      self.arrows.append((dt/2, self.height/2, arrow_angle))

class Low(Brick):
  def __init__(self, **kwargs):
    Brick.__init__(self, **kwargs)
    if self.is_first:
      self.last_y = self.height
    else:
      self.last_y = self.height if self.last_y is None else self.last_y
    dt = abs(self.height - self.last_y) * self.slewing / self.height
    # add shape
    self.paths.append([(0, self.last_y), (dt, self.height), (self.width, self.height)])
    # add arrow
    if kwargs.get("add_arrow", False) and not self.is_first:
      arrow_angle = - math.atan2(-self.height, self.slewing) * 180 / math.pi
      self.arrows.append((dt * (self.height/2 - self.last_y)/self.height, self.height/2, arrow_angle))

class High(Brick):
  def __init__(self, **kwargs):
    Brick.__init__(self, **kwargs)
    if self.is_first:
      self.last_y = self.height
    else:
      self.last_y = self.height if self.last_y is None else self.last_y
    dt = self.last_y * self.slewing / self.height
    # add shape
    self.paths.append([(0, self.last_y), (dt, 0), (self.width, 0)])
    # add arrow
    if kwargs.get("add_arrow", False):
      arrow_angle = math.atan2(-self.height, self.slewing) * 180 / math.pi
      self.arrows.append((dt/2, self.height/2, arrow_angle))

class HighZ(Brick):
  def __init__(self, **kwargs):
    Brick.__init__(self, **kwargs)
    if self.is_first:
      self.last_y = self.height/2
    else:
      self.last_y = self.height/2 if self.last_y is None else self.last_y
    dt = abs(self.height - self.last_y) * self.slewing / self.height
    # add shape
    self.splines.append([
      ('M', 0, self.last_y), ('C', dt, self.height / 2), ('', dt, self.height / 2),
      ('', min(self.width, 20), self.height/2), ('L', self.width, self.height/2)])

class Zero(Brick):
  def __init__(self, **kwargs):
    Brick.__init__(self, **kwargs)
    if self.is_first:
      self.last_y = self.height
    else:
      self.last_y = self.height if self.last_y is None else self.last_y
    dt = (self.height - self.last_y) * self.slewing / self.height
    # add shape
    self.paths.append([
      (0, self.last_y), (3, self.last_y),
      (3+self.slewing, self.height), (self.width, self.height)])

class One(Brick):
  def __init__(self, **kwargs):
    Brick.__init__(self, **kwargs)
    if self.is_first:
      self.last_y = 0
    else:
      self.last_y = self.height if self.last_y is None else self.last_y
    dt = (self.height - self.last_y) * self.slewing / self.height
    # add shape
    self.paths.append([
      (0, self.last_y), (3, self.last_y),
      (3+self.slewing, 0), (self.width, 0)])

class Data(Brick):
  def __init__(self, **kwargs):
    Brick.__init__(self, **kwargs)
    self.last_y = self.height/2 if self.last_y is None else self.last_y
    # add shape
    if self.is_first:
      self.paths.append([
        (0, 0), (self.slewing, 0),
        (self.width-self.slewing, 0), (self.width, self.height/2)])
      self.paths.append([
        (0, self.height), (self.slewing, self.height),
        (self.width-self.slewing, self.height), (self.width, self.height/2)])
    else:
      self.paths.append([
        (0, self.last_y), (self.slewing, 0),
        (self.width-self.slewing, 0), (self.width, self.height/2)])
      self.paths.append([
        (0, self.last_y), (self.slewing, self.height),
        (self.width-self.slewing, self.height), (self.width, self.height/2)])
    # add background
    if self.is_first:
      self.polygons.append([
        (0, 0), (self.slewing, 0), (self.width-self.slewing, 0), (self.width, self.height/2),
        (self.width-self.slewing, self.height), (self.slewing, self.height), (0, self.height)
      ])
    else:
      self.polygons.append([
        (0, self.height/2), (self.slewing, 0), (self.width-self.slewing, 0), (self.width, self.height/2),
        (self.width-self.slewing, self.height), (self.slewing, self.height), (0, self.height/2)
      ])
    # add text
    self.text = (self.width / 2, self.height / 2, kwargs.get("data", ""))

class Gap(Brick):
  def __init__(self, **kwargs):
    Brick.__init__(self, **kwargs)
    #if self.is_first:
    #raise "a gap cannot be first in a wavelane"
    self.splines.append([
      ('M', 0, self.height + 2), ('C', 5, self.height + 2), ('', 5, -4), ('', 10, -4),
      ('L', 7, 0), ('C', 2, 0), ('', 2, self.height+4), ('', -3, self.height+4), ('z', '', '')])
    self.splines.append([('M', 0, self.height + 2), ('C', 5, self.height + 2), ('', 5, -2), ('', 10, -2)])
    self.splines.append([('M', -3, self.height + 2), ('C', 2, self.height + 2), ('', 2, -2), ('', 7, -2)])

class Up(Brick):
  def __init__(self, **kwargs):
    Brick.__init__(self, **kwargs)
    self.last_y = self.height if self.last_y is None else self.last_y
    self.splines.append([
      ('M', 0, self.last_y), ('L', 3, self.last_y), ('C', 3 + self.slewing, self.last_y),
      ('', 3 + self.slewing, 0), ('', min(self.width, 20), 0), ('L', self.width, 0)])

class Down(Brick):
  def __init__(self, **kwargs):
    Brick.__init__(self, **kwargs)
    self.last_y = self.height if self.last_y is None else self.last_y
    self.splines.append([
      ('M', 0, self.last_y), ('L', 3, self.last_y), ('C', 3 + self.slewing, self.last_y),
      ('', 3 + self.slewing, self.height - self.last_y), ('', min(self.width, 20), self.height),
      ('L', self.width, self.height)])

class Meta(Brick):
  def __init__(self, **kwargs):
    Brick.__init__(self, **kwargs)
    self.last_y = self.height / 2 if self.last_y is None else self.last_y
    dt = abs(self.last_y-self.height/2) * self.slewing / self.height
    time = range(int(dt), int(self.width*0.75+1))
    if (int(0.75*self.width+1)-int(dt)) % 2 == 1:
      time = range(int(dt), int(self.width*0.75+2))
    _tmp = [('m', 0, self.last_y)]
    if kwargs.get("then_one", False):
      for t in time:
        _tmp.append(('L' if t == dt else '', t, (1+math.exp(2*(t-self.width)/self.width)*math.sin(math.pi+8*math.pi*t/self.width))*0.5*self.height))
      t, x, y = _tmp[-1]
      dx = max(y*self.slewing/self.height, y)
      _tmp.extend([('C', x+dx, 0), ('', x+dx, 0), ('', self.width, 0)])
    else:
      for t in time:
        _tmp.append(('L' if t == dt else '', t, (1+math.exp(2*(t-self.width)/self.width)*math.sin(8*math.pi*t/self.width))*0.5*self.height))
      t, x, y = _tmp[-1]
      dx = max((self.height-y)*self.slewing/self.height, (self.height-y))
      _tmp.extend([('C', x + dx, self.height), ('', x+dx, self.height), ('', self.width, self.height)])
    self.splines.append(_tmp)

class Cap(Brick):
  def __init__(self, y, **kwargs):
    Brick.__init__(self, **kwargs)
    if self.is_first:
      self.last_y = self.height
    else:
      self.last_y = self.height if self.last_y is None else self.last_y
    dt = abs(y - self.last_y) * self.slewing / self.height
    # add shape
    self.splines.append([
          ('m', 0, self.last_y), ('C', dt, y), ('', dt, y),
          ('', self.width, y), ('L', self.width, y)])

class Step(Brick):
  def __init__(self, y, **kwargs):
    Brick.__init__(self, **kwargs)
    if self.is_first:
      self.last_y = self.height
    else:
      self.last_y = self.height if self.last_y is None else self.last_y
    dt = abs(y - self.last_y) * self.slewing / self.height
    # add shape
    self.paths.append([(0, self.last_y), (dt, y), (self.width, y)])

class Impulse(Brick):
  def __init__(self, y, **kwargs):
    Brick.__init__(self, **kwargs)
    if self.is_first:
      self.last_y = self.height
    else:
      self.last_y = self.height if self.last_y is None else self.last_y
    # add shape
    self.paths.append([(0, self.height-y), (0, y), (0, self.height-y), (self.width, self.height-y)])

def generate_brick(symbol: str, **kwargs) -> dict:
  # get option supported
  # sizing
  width              = kwargs.get("brick_width", 40)
  height             = kwargs.get("brick_height", 20)
  last_y             = kwargs.get("last_y", None)
  equation           = kwargs.get("equation", None)
  ignore_transition  = kwargs.get("ignore_transition", False)
  # rendering block size
  s = 0
  # update analogue context
  ANALOG_CONTEXT["Tmax"] = width
  ANALOG_CONTEXT["Ymax"] = height
  ANALOG_CONTEXT["time"] = range(0, int(width+1))
  # create the brick
  b = Brick()
  # add arrow
  if symbol in [BRICKS.Nclk, BRICKS.Pclk, BRICKS.Low, BRICKS.High] and not ignore_transition:
    kwargs.update({"add_arrow": True})
  # clock signals description (pPnNlLhH)
  # (N|n)clk: falling edge (with|without) arrow for repeated pattern
  if symbol in [BRICKS.nclk, BRICKS.Nclk]:
    b = Nclk(**kwargs)
  # (P|p)clk: rising edge (with|without) arrow for repeated pattern
  elif symbol in [BRICKS.pclk, BRICKS.Pclk]:
    b = Pclk(**kwargs)
  # (L|l)ow: falling edge (with|without) arrow and stuck
  elif symbol == BRICKS.low or symbol == BRICKS.Low:
    b = Low(**kwargs)
  # (H|h)igh: rising edge (with|without) arrow and stuck
  elif symbol == BRICKS.high or symbol == BRICKS.High:
    b = High(**kwargs)
  # description for data (z01=x)
  elif symbol == BRICKS.highz:
    b = HighZ(**kwargs)
  elif symbol == BRICKS.zero:
    b = Zero(**kwargs)
  elif symbol == BRICKS.one:
    b = One(**kwargs)
  elif symbol == BRICKS.data:
    b = Data(**kwargs)
  elif symbol == BRICKS.x:
    if "data" in kwargs:
      kwargs["data"] = ''
    b = Data(**kwargs)
  # time compression symbol
  elif symbol == BRICKS.gap:
    b = Gap(**kwargs)
  # capacitive charge to 1
  elif symbol == BRICKS.up:
    b = Up(**kwargs)
  # capacitive discharge to 0
  elif symbol == BRICKS.down:
    b = Down(**kwargs)
  # metastability to zero
  elif symbol == BRICKS.meta:
    b = Meta(**kwargs)
  # metastability to one
  elif symbol == BRICKS.Meta:
    kwargs.update({"then_one": True})
    b = Meta(**kwargs)
  # impulse symbol
  elif symbol == BRICKS.imp:
    b = Impulse(height, **kwargs)
  elif symbol == BRICKS.Imp:
    b = Impulse(0, **kwargs)
  # full custom analogue bloc
  elif symbol == BRICKS.step:
    b = Step(BRICKS.transform_y(float(equation), height), **kwargs)
  elif symbol == BRICKS.cap:
    b = Cap(BRICKS.transform_y(float(equation), height), **kwargs)
  elif symbol == BRICKS.ana:
    last_y = height if last_y is None else last_y
    try:
      b.paths.append([(0, last_y)] + [(p[0], BRICKS.transform_y(p[1], height)) for p in eval(equation, ANALOG_CONTEXT)])
    except Exception as e:
      print(getattr(e, 'message', repr(e)))
  else:
    raise NotImplementedError()
  b.symbol = symbol
  return b
