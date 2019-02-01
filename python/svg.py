#!/usr/bin/env python3

"""
svg.py is a composition of functions to generate
an svg diagram from the WaveDrom-like format
"""

import skin
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
  # generate a gap symbol (time compression)
  if symbol == BRICKS.gap or symbol == '|':
    ans += f"<path d=\"m7,-2 -4,0 c -5,0 -5,{height+4} -10,{height+4} l 4,0 C 2,{height+4} 2,-2 7,-2 z\" class=\"hide\"></path>\n"
    ans += f"<path d=\"M-7,{height+2} C -2,{height+2} -2,-2 3,-2\" class=\"path\"></path>\n"
    ans += f"<path d=\"M-3,{height+2} C 2,{height+2} 2,-2 7,-2\" class=\"path\"></path>\n"
  # generate other bricks
  else:
    for _, poly in enumerate(b.polygons):
      filling = "url(#diagonalHatch)" if symbol == BRICKS.x else "none"
      ans += svg_polygon(poly, f"fill=\"{filling}\"")
    for _, path in enumerate(b.paths):
      ans += svg_path(path, "class=\"path\"")
    for _, arrow in enumerate(b.arrows):
      ans += svg_arrow(*arrow, "class=\"arrow\"")
    for _, spline in enumerate(b.splines):
      ans += svg_spline(spline, "class=\"path\"")
    if b.text:
      ans += svg_text(*b.text)
  ans += "</g>"
  return ans

def svg_wavelane_title(name: str):
  """
  svg_wavelane_title generate the title in front of a waveform
  name: name of the waveform print alongside
  """
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
          Brick(),
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
    offsetx = kwargs.get("offsetx", max(map(len, wavelanes.keys()))*11)
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
