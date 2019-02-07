#!/usr/bin/env python3
# spell-checker: disable

"""
renderer.py declare the logic to render waveforms
into different format
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
# counter of edge
_EDGE_COUNT = 0

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

def incr_edge(f):
  """
  incr_wavegroup is a decorator that increment _WAVEGROUP_COUNT in auto.
  """
  def wrapper(*args, **kwargs):
    global _EDGE_COUNT
    _EDGE_COUNT += 1
    return f(*args, **kwargs)
  return wrapper

# TODO create an abstract parameter for style
# TODO autoscale or scaling for analogue

class Renderer:
  """
  Abstract class of all renderer and define the parsing logic
  """

  _EDGE_REGEXP = r"([\w\.\_]+)([~\|\/\-\>\<]+)([\w\.\_]+)"
  _WAVE_TITLE  = ""
  _DATA_TEXT   = ""

  def __init__(self):
    pass

  @staticmethod
  def is_spacer(name: str) -> bool:
    if name.strip() == "":
      return True
    if "spacer" in name.lower():
      return True
    return False

  def group(self, callback, id: str = "", extra: str = "") -> str:
    """
    group define a group
    """
    raise NotImplementedError()

  def path(self, vertices: list, extra: str = "") -> str:
    """
    path draw a path to represent common signals
    vertices: list of of x-y coordinates in a tuple
    [extra] : optional attributes for the svg (eg class)
    """
    raise NotImplementedError()

  def arrow(self, x, y, angle, extra: str = "") -> str:
    """
    arrow draw an arrow to represent edge trigger on clock signals
    x       : x coordinate of the arrow center
    y       : y coordinate of the arrow center
    angle   : angle in degree to rotate the arrow
    [extra] : optional attributes for the svg (eg class)
    """
    raise NotImplementedError()

  def polygon(self, vertices: list, extra: str = "") -> str:
    """
    polygon draw a closed shape to represent common data
    vertices: list of of x-y coordinates in a tuple
    [extra] : optional attributes for the svg (eg class)
    """
    raise NotImplementedError()

  def spline(self, vertices: list, extra: str = "") -> str:
    """
    spline draw a path to represent smooth signals
    vertices: list of of type-x-y coordinates in a tuple of control points
              where type is either a moveto (m/M) lineto (l/L) or curveto (c/C)
              svg operator
    [extra] : optional attributes for the svg (eg class)
    """
    raise NotImplementedError()

  def text(self, x: float, y: float, text: str = "", extra: str = "") -> str:
    """
    text draw a text for data
    x       : x coordinate of the text
    y       : y coordinate of the text
    text    : text to display
    """
    raise NotImplementedError()

  def translate(self, x: float, y: float) -> str:
    """
    translation function that is inherited for svg and eps
    """
    raise NotImplementedError()

  def brick(self, symbol: str, b: Brick, extra: str = "", height: int = 20) -> str:
    """
    brick generate the symbol for a Brick element
    (collection of paths, splines, arrows, polygons, text)
    x       : x coordinate of the text
    y       : y coordinate of the text
    text    : text to display
    """
    ans = f"<g data-symbol=\"{symbol}\" {extra}>\n"
    for _, poly in enumerate(b.polygons):
      filling = "url(#diagonalHatch)" if symbol == BRICKS.x else "none"
      ans += self.polygon(poly, f"fill=\"{filling}\"")
    for _, path in enumerate(b.paths):
      ans += self.path(path, "class=\"path\"")
    for _, arrow in enumerate(b.arrows):
      ans += self.arrow(*arrow, "class=\"arrow\"")
    for i, spline in enumerate(b.splines):
      if i == 0 and symbol == BRICKS.gap:
        ans += self.spline(spline, "class=\"hide\"")
      else:
        ans += self.spline(spline, "class=\"path\"")
    if len(b.text[2]) > 0:
      ans += self.text(*b.text, self._DATA_TEXT)
    ans += "</g>"
    return ans

  def wavelane_title(self, name: str, extra: str = ""):
    """
    wavelane_title generate the title in front of a waveform
    name: name of the waveform print alongside
    """
    if "spacer" in name or not name.strip():
      return ""
    return self.text(-10, 15, name, self._WAVE_TITLE)

  def _reduce_wavelane(self, name: str, wavelane: str, **kwargs):
    repeat       = kwargs.get("repeat", 1)
    _wavelane, previous_brick = [], None
    # look for repetition '.'
    for i, b in enumerate(wavelane * repeat):
      if b == '.' and previous_brick in [None, '|'] and i == 0:
        raise f"error in {name}: cannot repeat none or '|', add a valid brick first"
      # do not simplify for clock signal
      if b in '.|' and not previous_brick in ['p', 'n', 'N', 'P']:
        br, num = _wavelane[-1]
        _wavelane[-1] = (br, num + 1)
        if b == '|':
          _wavelane.append((b, 1))
      elif b in '.|':
        _wavelane.append((previous_brick, 1))
        if b == '|':
          _wavelane.append((b, 1))
      elif b == 'x' and previous_brick == 'x':
        br, num = _wavelane[-1]
        _wavelane[-1] = (br, num + 1)
      else:
        _wavelane.append((b, 1))
        previous_brick = b
    return _wavelane

  @incr_wavelane
  def wavelane(self, name: str, wavelane: str, extra: str = "", **kwargs):
    """
    wavelane is the core function which generate a waveform from the string
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
                  default is 3
    """
    # options
    period       = kwargs.get("period", 1)
    phase        = kwargs.get("phase", 0)
    data         = kwargs.get("data", "")
    brick_width  = period * kwargs.get("brick_width", 20)
    brick_height = kwargs.get("brick_height", 20)
    gap_offset   = kwargs.get("gap_offset", brick_width*0.75)
    slewing      = kwargs.get("slewing", 3)
    analogue     = kwargs.get("analogue", [])
    # in case a string is given reformat it as a list
    if isinstance(data, str):
      data = data.strip().split()
    # generate the waveform
    wave, pos, ignore, last_y = [], 0, False, None
    # look for repetition '.'
    _wavelane = self._reduce_wavelane(name, wavelane, **kwargs)
    # generate bricks
    symbol, data_counter, i, Nana = None, 0, 0, 0
    for b, k in _wavelane:
      if b != '|':
        # get the final height of the last brick
        last = -2 if symbol == BRICKS.gap else -1
        if wave:
          s, br, c = wave[last]
          last_y = br.get_last_y()
          symbol = BRICKS.from_str(b)
          ignore = BRICKS.ignore_transition(wave[last] if wave else None, symbol)
          # adjust transition from data or x
          if s in [BRICKS.data, BRICKS.x] and symbol in [BRICKS.zero, BRICKS.one, BRICKS.low, BRICKS.high]:
            if symbol in [BRICKS.zero, BRICKS.low]:
              br.alter_end(3, brick_height)
            else:
              br.alter_end(3, 0)
            wave[last] = (s, br, c)
            ignore = True
          # adjust clock symbols
          if symbol in [BRICKS.low, BRICKS.Low] and \
             s in [BRICKS.Pclk, BRICKS.pclk, BRICKS.Nclk, BRICKS.nclk]:
            br.alter_end(0, brick_height)
            wave[last] = (s, br, c)
            ignore = True
          last_y = br.get_last_y()
        else:
          last_y = brick_height
          symbol = BRICKS.from_str(b)
        # adjust the width of a brick depending on the phase
        if i == 0:
          width_with_phase = brick_width*(k-phase)
        elif i == len(_wavelane) - 1:
          width_with_phase = brick_width*(k+phase)
        else:
          width_with_phase = k*brick_width
        # update the arguments to be passed for the generation
        kwargs.update({
            "brick_width": width_with_phase,
            "ignore_transition": ignore,
            "is_first": i == 0,
            "last_y": last_y,
            "slewing": slewing,
            "equation": analogue[Nana] if Nana < len(analogue) else "0",
            "data": data[data_counter] if len(data) > data_counter else ""
        })
        # get next equation if analogue
        if symbol in [BRICKS.ana, BRICKS.step, BRICKS.cap]:
          Nana += 1
        # create the new brick
        wave.append((
            symbol,
            generate_brick(symbol, **kwargs),
            (self.translate(pos if i > 0 else pos, 0) +
            f"class=\"s{b if b.isdigit() and int(b, 10) > 1 else ''}\"")
        ))
        if symbol == BRICKS.data:
          data_counter += 1
      else:
        # create the gap
        symbol = BRICKS.gap
        pos -= brick_width
        wave.append((
            symbol,
            generate_brick(symbol, **kwargs),
            self.translate(pos+gap_offset, 0)
        ))
      pos += width_with_phase
      i += 1
    # generate waveform
    def _gen():
      ans = self.wavelane_title(name) if name else ""
      for w in wave:
        symb, b, e = w
        ans += self.brick(symb, b, extra=e)
      return ans
    return self.group(
      _gen,
      name if name else f"wavelane_{_WAVEGROUP_COUNT}_{_WAVE_COUNT}",
      extra
    )

  def ticks(self, width: int, height: int, step: int, **kwargs) -> str:
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
    def _gen():
      ans = ""
      for x in range(0, width, step):
        ans += self.spline([('m', x, 0), ('', 0, height-offsety)], "class=\"ticks\"")
      return ans
    return self.group(
      _gen,
      f"ticks_{_WAVEGROUP_COUNT}",
      f"transform=\"translate({offsetx}, 0)\"")

  def edges(self, wavelanes, extra: str = "", **kwargs) -> str:
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
    nodes = []
    def _gen():
      ans, _y = "", 0
      for name, wavelane in wavelanes.items():
        # read nodes declaration
        if isinstance(wavelane, dict):
          if "node" in wavelane:
            chain = wavelane["node"].split(' ')
            n = chain[0].replace('.', '')
            i = [chain[0].find(c) for c in n[::]]
            j = count(0)
            # brick width of the wavelane
            width   = brick_width * wavelane.get("period", 1)
            phase   = width * wavelane.get("phase", 0)
            slewing = wavelane.get("slewing", 4)
            # get identifier
            nodes.extend(
              [ (s[0] * width - phase + slewing * 0.5, _y, chain[1+next(j)]) if not s[1].isalpha()
                else (s[0] * width - phase + slewing * 0.5, _y, s[1]) for s in list(zip(i, n[::]))]
            )
          _y += brick_height * 1.5
        # list edgeds to perform
        elif name == "edge":
          # parse edges declaration
          matches = [(r[0].groups(), r[1]) for r in [(re.match(Renderer._EDGE_REGEXP, s.split(' ', 1)[0]), s.split(' ', 1)[1] if len(s.split(' ', 1)) > 1 else '') for s in wavelane] if not r is None]
          # replace by x position
          edges = list(zip([m[0][1] for m in matches],
                          [b for m in matches for b in nodes if m[0][0] in b],
                          [b for m in matches for b in nodes if m[0][2] in b],
                          [m[1] for m in matches]))
          for i, edge in enumerate(edges):
            adj = {}
            if "adjustment" in wavelanes:
              adj = [a for a in wavelanes["adjustment"] if "edge" in a and a["edge"]==i+1]
              adj = adj[0] if adj else {}
            @incr_edge
            def _gen(**kwargs):
              dx = kwargs.get("dx", 0)
              dy = kwargs.get("dy", 0)
              ans = ""
              _shape, s, e, text = edge
              s = s[0] + 3, s[1] + brick_height * 0.5
              e = e[0] + 3, e[1] + brick_height * 0.5
              style = "edges "
              style += "arrowtail " if _shape[-1] == '>' else ''
              style += "arrowhead " if _shape[0] == '<' else ''
              mx, my = (s[0] + e[0]) * 0.5, (s[1] + e[1]) * 0.5
              if _shape in ['<~', '~', '~>', '<~>']:
                ans += self.spline([('M', s[0], s[1]), ('C', s[0]*0.1+e[0]*0.9, s[1]), ('', s[0]*0.9+e[0]*0.1, e[1]), ('', e[0], e[1])], f"class=\"{style}\"")
              elif _shape in ['<-~', '-~', '-~>', '<-~>']:
                ans += self.spline([('M', s[0], s[1]), ('C', e[0], s[1]), ('', e[0], e[1]), ('', e[0], e[1])], f"class=\"{style}\"")
              elif _shape in ['<~-', '~-', '~->', '<~->']:
                ans += self.spline([('M', s[0], s[1]), ('C', s[0], s[1]), ('', s[0], e[1]), ('', e[0], e[1])], f"class=\"{style}\"")
              elif _shape in ['<-', '-', '->', '<->']:
                ans += self.spline([('M', s[0], s[1]), ('L', e[0], e[1])], f"class=\"{style}\"")
              elif _shape in ['<-|', '-|', '-|>', '<-|>']:
                ans += self.spline([('M', s[0], s[1]), ('L', e[0], s[1]), ('', e[0], e[1])], f"class=\"{style}\"")
              elif _shape in ['<|-', '|-', '|->', '<|->']:
                ans += self.spline([('M', s[0], s[1]), ('L', s[0], e[1]), ('', e[0], e[1])], f"class=\"{style}\"")
              elif _shape in ['<-|-', '-|-', '-|->', '<-|->']:
                ans += self.spline([('M', s[0], s[1]), ('L', mx, s[1]), ('', mx, e[1]), ('', e[0], e[1])], f"class=\"{style}\"")
              ans += self.text(mx+dx, my+dy, text, "text-anchor=\"middle\"")
              return ans
            global _EDGE_COUNT
            ans += self.group(lambda : _gen(**adj), f"edge_{_EDGE_COUNT}")
      return ans
    return self.group(
      _gen,
      "edges",
      extra
    )

  @incr_wavegroup
  def wavegroup(self, name: str, wavelanes, extra: str = "", depth: int = 1, **kwargs):
    """
    wavegroup generate a collection of waveforms
    name           : name of the wavegroup
    wavelanes      : collection of wavelane
    [extra]        : optional attributes for the svg (eg class)
    [brick_width]  : width of a brick, default is 20
    [brick_height] : height a row, default is 20
    [width]        : image width, default is auto
    [height]       : image height, default is 0
    [no_ticks]     : if True does not display any ticks
    """
    if not isinstance(wavelanes, dict):
      return (0, "")
    # prepare the return group
    _default_offset_x = [len(s)+1 for s in wavelanes.keys() if not (Renderer.is_spacer(s) or s in ["edge", "adjustment"])]
    offsetx = kwargs.get("offsetx", max(_default_offset_x)*9)
    offsety = 0
    def _gen(offset):
      # options
      brick_width  = kwargs.get("brick_width", 20)
      brick_height = kwargs.get("brick_height", 20)
      width        = kwargs.get("width", 0)
      height       = kwargs.get("height", 0)
      no_ticks     = kwargs.get("no_ticks", False)
      offsetx, offsety = offset[0], offset[1]
      # return value
      if depth > 1:
        ans = self.text(0, offsety+10, name, f"class=\"h{depth}\"")
        if depth == 2:
          ans += self.path([(0, offsety+14), (width+offsetx, offsety+14)], "class=\"border\"")
        offsety += 20
      else:
        ans = ""
      for _, wavetitle in enumerate(wavelanes.keys()):
        # signal
        if "wave" in wavelanes[wavetitle]:
          wave, args = wavelanes[wavetitle]["wave"], wavelanes[wavetitle]
          l = len(wave)
          width = l * brick_width if l * brick_width > width else width
          args.update(**kwargs)
          ans += self.wavelane(
            wavetitle,
            wave,
            self.translate(offsetx, offsety),
            **args
          )
          offsety += brick_height * 1.5
        # spacer
        elif Renderer.is_spacer(wavetitle) or "node" in wavelanes[wavetitle]:
          offsety += brick_height * 1.5
        # group of signals
        else:
          args = kwargs
          args.update({"offsetx": offsetx, "offsety": offsety, "no_ticks": True})
          j, tmp = self.wavegroup(
            wavetitle,
            wavelanes[wavetitle],
            self.translate(0, offsety),
            depth+1,
            **args
          )
          ans += tmp
          offsety += j
      # add ticks only for the principale group
      if not no_ticks:
        ans = self.ticks(width, height, brick_width, offsetx=offsetx) + "\n" + ans
      offset[0], offset[1] = offsetx, offsety
      return ans
    # a use full signal is in a dict
    if isinstance(wavelanes, dict):
      # room for displaying names
      offset = [offsetx, offsety]
      ans = self.group(lambda : _gen(offset), name, extra)
      offsetx, offsety = offset[0], offset[1]
      # finish the group
      ans += self.edges(wavelanes, extra=self.translate(offsetx, 0), **kwargs)
      return (offsety, ans)
    # unknown options
    else:
      raise "Unkown wavelane type or option"
    return (0, "")

  def size(self, wavelanes, brick_width: int = 20, brick_height: int = 28, depth: int = 1):
    """
    svg_size pre-estimate the size of the image
    wavelanes : data to be parse
    [brick_width]   : width of a brick, default is 20
    [brick_height]  : height of a row, default is 20
    [period]        : time dilatation factor, default is 1
    """
    if isinstance(wavelanes, dict):
      x, y, keys = [], 0, []
      for _, wavetitle in enumerate(wavelanes.keys()):
        if "wave" in wavelanes[wavetitle]:
          _l = len(wavelanes[wavetitle]["wave"]) * brick_width
          if "repeat" in wavelanes[wavetitle]:
            _l *= wavelanes[wavetitle]["repeat"]
          if "period" in wavelanes[wavetitle]:
            _l *= wavelanes[wavetitle]["period"]
          x.append(_l)
          y += brick_height * 1.5
          keys.append(len(wavetitle))
        elif Renderer.is_spacer(wavetitle) or "node" in wavelanes[wavetitle]:
          y += brick_height * 1.5
        elif isinstance(wavelanes[wavetitle], dict):
          y += 20
          lkeys, _x, _y = self.size(wavelanes[wavetitle], brick_width, brick_height, depth+1)
          x.append(_x)
          y += _y
          keys.append(lkeys)
        else:
          pass
      return (max(keys), max(x), y)

  def draw(self, wavelanes, **kwargs) -> str:
    """
    generate an svg file from wavelanes
    [id]           : identifier for multiple integration
    [brick_width]  : width of a brick
    [brick_height] : height of a brick
    """
    raise NotImplementedError()

class SvgRenderer(Renderer):
  """
  Render the wavelanes as an svg
  """
  _WAVE_TITLE  = "class=\"info\" text-anchor=\"end\" xml:space=\"preserve\""
  _DATA_TEXT   = "text-anchor=\"middle\" dominant-baseline=\"middle\" alignment-baseline=\"central\""

  def __init__(self):
    Renderer.__init__(self)

  def group(self, callback, id: str = "", extra: str = "") -> str:
    """
    group define a group
    """
    ans = f"<g id=\"{id}\" {extra} >\n"
    ans += callback()
    ans += "</g>\n"
    return ans

  def path(self, vertices: list, extra: str = "") -> str:
    """
    path draw a path to represent common signals
    vertices: list of of x-y coordinates in a tuple
    [extra] : optional attributes for the svg (eg class)
    """
    path = ''.join([f"L{x},{y} " for x, y in vertices])
    path = 'M' + path[1:]
    return f"<path d=\"{path.strip()}\" {extra} />\n"

  def arrow(self, x, y, angle, extra: str = "") -> str:
    """
    arrow draw an arrow to represent edge trigger on clock signals
    x       : x coordinate of the arrow center
    y       : y coordinate of the arrow center
    angle   : angle in degree to rotate the arrow
    [extra] : optional attributes for the svg (eg class)
    """
    return (f"<path d=\"M 0 0 L 3.5 7 L 7 0 L 3.5 1.5z\" "
            f"transform=\"translate({x-3.5}, {y-3.5}) rotate({angle-90}, 3.5, 3.5)\" "
            f"{extra} />\n")

  def polygon(self, vertices: list, extra: str = "") -> str:
    """
    polygon draw a closed shape to represent common data
    vertices: list of of x-y coordinates in a tuple
    [extra] : optional attributes for the svg (eg class)
    """
    ans = "<polygon points=\""
    for x, y in vertices:
      ans += f"{x},{y} "
    ans += f"\" {extra} />\n"
    return ans

  def spline(self, vertices: list, extra: str = "") -> str:
    """
    spline draw a path to represent smooth signals
    vertices: list of of type-x-y coordinates in a tuple of control points
              where type is either a moveto (m/M) lineto (l/L) or curveto (c/C)
              svg operator
    [extra] : optional attributes for the svg (eg class)
    """
    path = ''.join([f"{v[0]}{v[1]},{v[2]} " for v in vertices])
    return f"<path d=\"{path.strip()}\" {extra} />\n"

  def text(self, x: float, y: float, text: str = "", extra: str = "") -> str:
    """
    text draw a text for data
    x       : x coordinate of the text
    y       : y coordinate of the text
    text    : text to display
    """
    return (f"<text x=\"{x}\" y=\"{y}\" {extra} >{text}</text>\n")

  def translate(self, x: float, y: float) -> str:
    return f" transform=\"translate({x}, {y})\" "

  def draw(self, wavelanes, **kwargs) -> str:
    _id          = kwargs.get("id", "a")
    brick_width  = kwargs.get("brick_width", 40)
    brick_height = kwargs.get("brick_height", 20)
    lkeys, width, height = self.size(wavelanes, brick_width, brick_height)
    return (
      f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width+lkeys*11}\" height=\"{height}\" "
      f"viewBox=\"-1 -1 {width+lkeys*11+2} {height+2}\" overflow=\"hidden\">\n"
      f"<style>{skin.DEFAULT}</style>\n"
      f"{skin.DEFINITION}"
      ""+self.wavegroup(_id, wavelanes, brick_width=brick_width, brick_height=brick_height, width=width, height=height)[1]+""
      "\n</svg>"
    )
