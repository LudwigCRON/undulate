#!/usr/bin/env python3

"""
svg.py is a composition of functions to generate
an svg diagram from the WaveDrom-like format
"""
import re
import skin
from itertools import count
from bricks import BRICKS, Brick, generate_brick

# Counter for unique id generation
# counter of group of wave
_WAVEGROUP_COUNT = 0
# counter of wave
_WAVE_COUNT = 0

def incr_wavelane(f):
  """
  incr_wavelane is a decorator that increment _WAVE_COUNT in auto.
  """
  def wrapper(*args, **kwargs):
    global _WAVE_COUNT
    _WAVE_COUNT += 1
    return f(*args, **kwargs)
  return wrapper

def incr_wavegroup(f):
  """
  incr_wavegroup is a decorator that increment _WAVEGROUP_COUNT in auto.
  """
  def wrapper(*args, **kwargs):
    global _WAVEGROUP_COUNT
    _WAVEGROUP_COUNT += 1
    return f(*args, **kwargs)
  return wrapper

_EDGE_REGEXP = r"([\w\.\_]+)([~\|\/\-\>\<]+)([\w\.\_]+)"

def is_spacer(name: str) -> bool:
  if name.strip() == "":
    return True
  if "spacer" in name.lower():
    return True
  return False

# SVG Drawing
# basic function for drawing
def svg_path(vertices: list, extra: str = "") -> str:
  """
  svg_path draw a path to represent common signals
  vertices: list of of x-y coordinates in a tuple
  [extra] : optional attributes for the svg (eg class)
  """
  path = ''.join([f"L{x},{y} " for x, y in vertices])
  path = 'M' + path[1:]
  return f"<path d=\"{path.strip()}\" {extra} />\n"

def svg_arrow(x, y, angle, extra: str = "") -> str:
  """
  svg_arrow draw an arrow to represent edge trigger on clock signals
  x       : x coordinate of the arrow center
  y       : y coordinate of the arrow center
  angle   : angle in degree to rotate the arrow
  [extra] : optional attributes for the svg (eg class)
  """
  return (f"<path d=\"M 0 0 L 3.5 7 L 7 0 L 3.5 1.5z\" "
          f"transform=\"translate({x-3.5}, {y-3.5}) rotate({angle-90}, 3.5, 3.5)\" "
          f"{extra} />\n")

def svg_polygon(vertices: list, extra: str = "") -> str:
  """
  svg_polygon draw a closed shape to represent common data
  vertices: list of of x-y coordinates in a tuple
  [extra] : optional attributes for the svg (eg class)
  """
  ans = "<polygon points=\""
  for x, y in vertices:
    ans += f"{x},{y} "
  ans += f"\" {extra} />\n"
  return ans

def svg_spline(vertices: list, extra: str = "") -> str:
  """
  svg_spline draw a path to represent smooth signals
  vertices: list of of type-x-y coordinates in a tuple of control points
            where type is either a moveto (m/M) lineto (l/L) or curveto (c/C)
            svg operator
  [extra] : optional attributes for the svg (eg class)
  """
  path = ''.join([f"{v[0]}{v[1]},{v[2]} " for v in vertices])
  return f"<path d=\"{path.strip()}\" {extra} />\n"

def svg_text(x: float, y: float, text: str = "") -> str:
  """
  svg_text draw a text at the position specified for data
  x       : x coordinate of the text
  y       : y coordinate of the text
  text    : text to display
  """
  return (f"<text x=\"{x}\" y=\"{y}\" text-anchor=\"middle\" "
          f"alignment-baseline=\"central\">{text}</text>\n")

# TODO: move the gap symbol into bricks.py
def svg_brick(symbol: str, b: Brick, extra: str = "", height: int = 20) -> str:
  """
  svg_brick generate the symbol for a Brick element
  (collection of paths, splines, arrows, polygons, text)
  x       : x coordinate of the text
  y       : y coordinate of the text
  text    : text to display
  """
  ans = f"<g data-symbol=\"{symbol}\" {extra}>\n"
  if symbol == BRICKS.gap:
    ans += f"<path d=\"m7,-2 -4,0 c -5,0 -5,{height+4} -10,{height+4} l 4,0 C 2,{height+4} 2,-2 7,-2 z\" class=\"hide\"></path>\n"
  for _, poly in enumerate(b.polygons):
    filling = "url(#diagonalHatch)" if symbol == BRICKS.x else "none"
    ans += svg_polygon(poly, f"fill=\"{filling}\"")
  for _, path in enumerate(b.paths):
    ans += svg_path(path, "class=\"path\"")
  for _, arrow in enumerate(b.arrows):
    ans += svg_arrow(*arrow, "class=\"arrow\"")
  for _, spline in enumerate(b.splines):
    ans += svg_spline(spline, "class=\"path\"")
  if len(b.text[2]) > 0:
    ans += svg_text(*b.text)
  ans += "</g>"
  return ans

def svg_wavelane_title(name: str):
  """
  svg_wavelane_title generate the title in front of a waveform
  name: name of the waveform print alongside
  """
  if "spacer" in name or not name.strip():
    return ""
  return (f"<text x=\"-10\" y=\"15\" class=\"info\" text-anchor=\"end\" "
          f"xml:space=\"preserve\"><tspan>{name}</tspan></text>\n")

@incr_wavelane
def svg_wavelane(name: str, wavelane: str, extra: str = "", **kwargs):
  """
  svg_wavelane is the core function which generate a waveform from the string
  name         : name of the waveform
  wavelane     : string which describes the waveform
  [extra]      : optional attributes for the svg (eg class)
  [period]     : time dilatation factor, default is 1
  [phase]      : time shift of the waveform, default is 0
  [gap_offset] : time shift for adjusting the position of a gap, default is 3/4
                 of the tick period
  [data]       : when using either '=', '2', '3', ... symbols the data can be set.
                 A list of string is expected
  [slewing]    : current limitation which limit the transition speed of a signal
                default is 4
  """
  # options
  period      = kwargs.get("period", 1)
  phase       = kwargs.get("phase", 0)
  data        = kwargs.get("data", "")
  brick_width = period * kwargs.get("brick_width", 20)
  gap_offset  = kwargs.get("gap_offset", brick_width*0.75)
  slewing     = kwargs.get("slewing", 4)
  # in case a string is given reformat it as a list
  if isinstance(data, str):
    data = data.strip().split()
  # generate the waveform
  _wavelane, wave, pos, previous_brick, last_y = [], [], 0, None, None
  # look for repetition '.'
  for i, b in enumerate(wavelane):
    if b == '.' and previous_brick in [None, '|'] and i == 0:
      raise f"error in {name}: cannot repeat none or '|', add a valid brick first"
    if b in '.|' and not previous_brick in ['p', 'n', 'N', 'P']:
      br, num = _wavelane[-1]
      _wavelane[-1] = (br, num + 1)
      if b == '|':
        _wavelane.append((b, 1))
    elif b in '.|':
      _wavelane.append((previous_brick, 1))
      if b == '|':
        _wavelane.append((b, 1))
    else:
      _wavelane.append((b, 1))
      previous_brick = b
  # generate bricks
  previous_brick = BRICKS.zero
  data_counter, i = 0, 0
  for b, k in _wavelane:
    if b != '|':
      symbol = BRICKS.from_str(b)
      ignore = BRICKS.ignore_transition(previous_brick, symbol)
      # get the final height of the last brick
      if wave:
        s, br, _ = wave[-1]
        if s == BRICKS.gap:
          s, br, _ = wave[-2]
        if br.paths:
          _, last_y = br.paths[0][-1]
        elif br.splines:
          _, _, last_y = br.splines[0][-1]
      # adjust the width of a brick depending on the phase
      if i == 0:
        width_with_phase = brick_width*(1-phase/k)
      elif i == len(_wavelane) - 1:
        width_with_phase = brick_width*(1+2*phase)
      else:
        width_with_phase = brick_width
      # update the arguments to be passed for the generation
      kwargs.update({
          "brick_width": width_with_phase,
          "ignore_transition": ignore,
          "last_y": last_y,
          "is_repeated": k,
          "slewing": slewing,
          "data": data[data_counter] if len(data) > data_counter else ""
      })
      # create the new brick
      wave.append((
          symbol,
          generate_brick(symbol, **kwargs),
          (f"transform=\"translate({pos-brick_width*phase*(i>0)}, 0)\" "
           f"class=\"s{b if b.isdigit() and int(b, 10) > 1 else ''}\"")
      ))
      previous_brick = symbol
      if symbol == BRICKS.data:
        data_counter += 1
    else:
      # create the gap
      pos -= brick_width
      wave.append((
          BRICKS.gap,
          generate_brick(BRICKS.gap, **kwargs),
          f"transform=\"translate({pos-brick_width*phase+gap_offset}, 0)\""
      ))
    pos += brick_width*k
    i += 1
  # waveform name
  ans = ""
  if name:
    ans  = f"<g id=\"{name}\" {extra} >\n"
    ans += svg_wavelane_title(name)
  else:
    ans  = f"<g id=\"wavelane_{_WAVEGROUP_COUNT}_{_WAVE_COUNT}\" {extra} >\n"
  # generate waveform
  for w in wave:
    symb, b, e = w
    ans += svg_brick(symb, b, extra=e)
  ans += "</g>"
  return ans

def svg_ticks(width: int, height: int, step: int, **kwargs) -> str:
  """
  svg_ticks generates the dotted lines to see ticks easily
  width     : width of the image
  height    : height of the image
  step      : distance between two ticks
  [offsetx] : shift all ticks along the x-axis
  [offsety] : shift to the bottom ticks with exceeding the height
  """
  offsetx = kwargs.get("offsetx", 0)
  offsety = kwargs.get("offsety", 0)
  ans = f"<g id=\"ticks_{_WAVEGROUP_COUNT}\" transform=\"translate({offsetx}, 0)\">\n"
  for x in range(0, width, step):
    ans += f"<path d=\"m {x},0 0,{height-offsety}\" class=\"ticks\"/>"
  ans += "</g>"
  return ans

def svg_edges(wavelanes, extra: str = "", **kwargs) -> str:
  """
  svg_edges generate the connectors between edges
  wavelanes      : string which describes the waveform
  [extra]        : optional attributes for the svg (eg class)
  [period]       : time dilatation factor, default is 1
  [phase]        : time shift of the waveform, default is 0
  [slewing]      : current limitation which limit the transition speed of a signal
                   default is 4
  [brick_width]  : width of a brick
  [brick_height] : height of a brick
  """
  brick_width  = kwargs.get("brick_width", 20)
  brick_height = kwargs.get("brick_height", 20)
  slewing      = kwargs.get("slewing", 4)
  nodes = []
  ans = f"<g id=\"edges\" {extra} >\n"
  _y = 0
  for name, wavelane in wavelanes.items():
    # read nodes declaration
    if isinstance(wavelane, dict):
      if "node" in wavelane:
        chain = wavelane["node"].split(' ')
        n = chain[0].replace('.', '')
        i = [chain[0].find(c) for c in n[::]]
        j = count(0)
        # brick width of the wavelane
        width = brick_width * wavelane["period"] if "period" in wavelane \
                else brick_width
        phase = brick_width * wavelane["phase"] if "phase" in wavelane \
                else 0
        # get identifier
        nodes.extend(
          [ (s[0] * width - phase, _y, chain[1+next(j)]) if not s[1].isalpha() 
            else (s[0] * width - phase, _y, s[1]) for s in list(zip(i, n[::]))]
        )
        _y += brick_height * 1.5
    # list edgeds to perform
    elif name == "edge":
      # parse edges declaration
      matches = [(r[0].groups(), r[1]) for r in [(re.match(_EDGE_REGEXP, s.split(' ', 1)[0]), s.split(' ', 1)[-1]) for s in wavelane] if not r is None]
      # replace by x position
      edges = list(zip([m[0][1] for m in matches],
                       [b for m in matches for b in nodes if m[0][0] in b],
                       [b for m in matches for b in nodes if m[0][2] in b],
                       [m[1] for m in matches]))
      for edge in edges:
        _shape, s, e, text = edge
        s = s[0] + 3 + slewing * 0.5, s[1] + brick_height * 0.5
        e = e[0] + 3 + slewing * 0.5, e[1] + brick_height * 0.5
        style = "edges "
        style += "arrowtail " if _shape[-1] == '>' else ''
        style += "arrowhead " if _shape[0] == '<' else ''
        if _shape in ['<~', '~', '~>', '<~>']:
          mx = (s[0] + e[0]) * 0.5
          ans += f"<path d=\"M{s[0]},{s[1]} C {mx},{s[1]} {mx},{e[1]} {e[0]},{e[1]}\" class=\"{style}\"/>\n"
        elif _shape in ['<-~', '-~', '-~>', '<-~>']:
          ans += f"<path d=\"M{s[0]},{s[1]} C {e[0]},{s[1]} {e[0]},{e[1]} {e[0]},{e[1]}\" class=\"{style}\"/>\n"
        elif _shape in ['<~-', '~-', '~->', '<~->']:
          ans += f"<path d=\"M{s[0]},{s[1]} C {s[0]},{s[1]} {s[0]},{e[1]} {e[0]},{e[1]}\" class=\"{style}\"/>\n"
        elif _shape in ['<-', '-', '->', '<->']:
          ans += f"<path d=\"M{s[0]},{s[1]} L {e[0]},{e[1]}\" class=\"{style}\"/>\n"
        elif _shape in ['<-|', '-|', '-|>', '<-|>']:
          ans += f"<path d=\"M{s[0]},{s[1]} L {e[0]},{s[1]} {e[0]},{e[1]}\" class=\"{style}\"/>\n"
        elif _shape in ['<|-', '|-', '|->', '<|->']:
          ans += f"<path d=\"M{s[0]},{s[1]} L {s[0]},{e[1]} {e[0]},{e[1]}\" class=\"{style}\"/>\n"
        elif _shape in ['<-|-', '-|-', '-|->', '<-|->']:
          mx = (s[0] + e[0]) * 0.5
          ans += f"<path d=\"M{s[0]},{s[1]} L {mx},{s[1]} {mx},{e[1]} {e[0]},{e[1]}\" class=\"{style}\"/>\n"
  return ans+"</g>\n"

@incr_wavegroup
def svg_wavegroup(name: str, wavelanes, extra: str = "", **kwargs):
  """
  svg_wavegroup generate a collection of waveforms
  name           : name of the wavegroup
  wavelanes      : collection of wavelane
  [extra]        : optional attributes for the svg (eg class)
  [brick_width]  : width of a brick, default is 20
  [brick_height] : height a row, default is 20
  [width]        : image width, default is auto
  [height]       : image height, default is 0
  [no_ticks]     : if True does not display any ticks
  """
  # options
  brick_width  = kwargs.get("brick_width", 20)
  brick_height = kwargs.get("brick_height", 20)
  width        = kwargs.get("width", 0)
  height       = kwargs.get("height", 0)
  no_ticks     = kwargs.get("no_ticks", False)
  # prepare the return svg group
  header       = f"<g id=\"{name}\" {extra} >"
  ans          = ""
  # a use full signal is in a dict
  if isinstance(wavelanes, dict):
    # room for displaying names
    offsetx = kwargs.get("offsetx", max(map(lambda s: len(s) if not is_spacer(s) else 0, wavelanes.keys()))*11)
    offsety = 0
    for _, wavetitle in enumerate(wavelanes.keys()):
      # signal
      if "wave" in wavelanes[wavetitle]:
        wave, args = wavelanes[wavetitle]["wave"], wavelanes[wavetitle]
        l = len(wave)
        width = l * brick_width if l * brick_width > width else width
        args.update(**kwargs)
        ans += svg_wavelane(
          wavetitle,
          wave,
          f"transform=\"translate({offsetx}, {offsety})\"",
          **args
        )
        offsety += brick_height * 1.5
      # spacer
      elif is_spacer(wavetitle) or "node" in wavelanes[wavetitle]:
        offsety += brick_height * 1.5
      # group of signals
      else:
        args = kwargs
        args.update({"offsetx": offsetx, "offsety": offsety, "no_ticks": True})
        j, tmp = svg_wavegroup(
          wavetitle,
          wavelanes[wavetitle],
          f"transform=\"translate(0, {offsety})\"",
          **args
        )
        ans += tmp
        offsety += j
    # add ticks only for the principale group
    if no_ticks:
      ans = header + ans
    else:
      ans = header + svg_ticks(width, height, brick_width, offsetx=offsetx) + "\n" + ans
    # finish the group
    ans += "</g>"
    ans += svg_edges(wavelanes, extra=f"transform=\"translate({offsetx}, 0)\"", **kwargs)
    return (offsety, ans)
  # otherwise this is an option
  elif name == "edge":
    pass
  # unknown options
  else:
    raise "Unkown wavelane type or option"
  return (0, "")

def svg_size(wavelanes, brick_width: int = 20, brick_height: int = 28):
  """
  svg_size pre-estimate the size of the image
  wavelanes : data to be parse
  [brick_width]   : width of a brick, default is 20
  [brick_height]  : height of a row, default is 20
  """
  if isinstance(wavelanes, dict):
    x, y, keys = [], 0, []
    for _, wavetitle in enumerate(wavelanes.keys()):
      if "wave" in wavelanes[wavetitle]:
        x.append(len(wavelanes[wavetitle]["wave"]) * brick_width)
        y += brick_height * 1.5
        keys.append(len(wavetitle))
      elif is_spacer(wavetitle) or "node" in wavelanes[wavetitle]:
        y += brick_height * 1.5
      elif isinstance(wavelanes[wavetitle], dict):
        lkeys, _x, _y = svg_size(wavelanes[wavetitle], brick_width, brick_height)
        x.append(_x)
        y += _y
        keys.append(lkeys)
      else:
        pass
    return (max(keys), max(x), y)

def draw(wavelanes, **kwargs) -> str:
  """
  generate an svg file from wavelanes
  [id]           : identifier for multiple integration
  [brick_width]  : width of a brick
  [brick_height] : height of a brick
  """
  _id          = kwargs.get("id", "a")
  brick_width  = kwargs.get("brick_width", 40)
  brick_height = kwargs.get("brick_height", 20)
  lkeys, width, height = svg_size(wavelanes, brick_width, brick_height)
  return (
    f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width+lkeys*11}\" height=\"{height}\" "
    f"viewBox=\"-1 -1 {width+lkeys*11+2} {height+2}\">\n"
    f"<style>{skin.DEFAULT}</style>\n"
    f"{skin.PATTERN}"
    ""+svg_wavegroup(_id, wavelanes, brick_width=brick_width, brick_height=brick_height, width=width, height=height)[1]+""
    "\n</svg>"
  )
