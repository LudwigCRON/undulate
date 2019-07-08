#!/usr/bin/env python3
# spell-checker: disable

"""
renderer.py declare the logic to render waveforms
into different format
"""

import re
import copy
import pywave
from .skin import DEFAULT, DEFINITION
from itertools import count

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
# TODO add support of T curves in svg

def SvgCurveConvert(vertices: list) -> list:
  px, py, pt    =  0, 0, 'm'
  ans, ppx, ppy = [], 0, 0
  for t, x, y in vertices:
    # translate S into C
    if (t in ['s', 'S']) and (pt in ['s', 'S', 'c', 'C']):
      ans.append(('c' if t == 's' else 'C', px+(px-ppx), py+(py-ppy)))
      ans.append(('', x, y))
    # translate Q into C
    elif t in ['q', 'Q'] or (t in ['s', 'S'] and not pt in ['s', 'S', 'c', 'C']):
      ans.append(('c' if t in ['s', 'q'] else 'C', x, y))
      ans.append(('', x, y))
    else:
      ans.append((t, x, y))
    if t in ['m', 'M', 'l', 'L', 's', 'S', 'c', 'C', 'q', 'Q', 't', 'T']:
      pt = t
    px, py = x, y
    ppx, ppy = px, py
  return ans

class Renderer:
  """
  Abstract class of all renderer and define the parsing logic
  """

  _EDGE_REGEXP = r"([\w\.\_]+)([~\|\/\-\>\<]+)([\w\.\_]+)"
  _WAVE_TITLE  = ""
  _DATA_TEXT   = ""
  _GROUP_NAME  = ""
  _SYMBOL_TEMP = None
  _FIRST_TRANSLATION = True

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

  def path(self, vertices: list, extra: str = "", **kwargs) -> str:
    """
    path draw a path to represent common signals
    vertices: list of of x-y coordinates in a tuple
    [extra] : optional attributes for the svg (eg class)
    """
    raise NotImplementedError()

  def arrow(self, x, y, angle, extra: str = "", **kwargs) -> str:
    """
    arrow draw an arrow to represent edge trigger on clock signals
    x       : x coordinate of the arrow center
    y       : y coordinate of the arrow center
    angle   : angle in degree to rotate the arrow
    [extra] : optional attributes for the svg (eg class)
    """
    raise NotImplementedError()

  def polygon(self, vertices: list, extra: str = "", **kwargs) -> str:
    """
    polygon draw a closed shape to represent common data
    vertices: list of of x-y coordinates in a tuple
    [extra] : optional attributes for the svg (eg class)
    """
    raise NotImplementedError()

  def spline(self, vertices: list, extra: str = "", **kwargs) -> str:
    """
    spline draw a path to represent smooth signals
    vertices: list of of type-x-y coordinates in a tuple of control points
              where type is either a moveto (m/M) lineto (l/L) or curveto (c/C)
              svg operator
    [extra] : optional attributes for the svg (eg class)
    """
    raise NotImplementedError()

  def text(self, x: float, y: float, text: str = "", extra: str = "", **kwargs) -> str:
    """
    text draw a text for data
    x       : x coordinate of the text
    y       : y coordinate of the text
    text    : text to display
    """
    raise NotImplementedError()

  def translate(self, x: float, y: float, **kwargs) -> str:
    """
    translation function that is inherited for svg and eps
    """
    raise NotImplementedError()

  def untranslate(self):
    pass

  def brick(self, symbol: str, b: pywave.Brick, height: int = 20, **kwargs) -> str:
    """
    brick generate the symbol for a pywave.Brick element
    (collection of paths, splines, arrows, polygons, text)
    """
    ans, content = "", ""
    for _, poly in enumerate(b.polygons):
      filling = "url(#diagonalHatch)" if symbol == pywave.BRICKS.x else "none"
      content += self.polygon(poly, fill=filling, **kwargs)
    for _, path in enumerate(b.paths):
      content += self.path(path, style_repr="path", **kwargs)
    for _, arrow in enumerate(b.arrows):
      content += self.arrow(*arrow, style_repr="arrow", **kwargs)
    for i, spline in enumerate(b.splines):
      if i == 0 and symbol == pywave.BRICKS.gap:
        content += self.spline(spline, style_repr="hide", **kwargs)
      else:
        content += self.spline(spline, style_repr="path", **kwargs)
    for i, span in enumerate(b.texts):
      if len(str(span[2])) > 0:
        a = copy.deepcopy(kwargs)
        a.update({"extra": self._DATA_TEXT})
        content += self.text(*span, **a)
    if self._SYMBOL_TEMP:
      ans = self._SYMBOL_TEMP(symbol, content, **kwargs)
    return ans

  def wavelane_title(self, name: str, extra: str = "", vscale: float = 1):
    """
    wavelane_title generate the title in front of a waveform
    name: name of the waveform print alongside
    """
    if "spacer" in name or not name.strip():
      return ""
    return self.text(-10, 15 * vscale, name, extra=self._WAVE_TITLE, offset=extra)

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

  def _get_or_eval(self, name: str, default, **kwargs):
    """
    if is a str, evaluate the code or get it in a standard way
    """
    if isinstance(kwargs.get(name), str):
      return eval(kwargs.get(name, ""))
    return kwargs.get(name, default)

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
    [duty_cycles]: A list of duty_cycle for each bricks
    [periods]    : A list of period for each bricks
    """
    # options
    period       = kwargs.get("period", 1)
    phase        = kwargs.get("phase", 0)
    data         = kwargs.get("data", "")
    regpos       = kwargs.get("regpos", "")
    brick_width  = period * kwargs.get("brick_width", 20)
    brick_height = kwargs.get("brick_height", 20) * kwargs.get("vscale", 1)
    gap_offset   = kwargs.get("gap_offset", brick_width*0.75)
    slewing      = kwargs.get("slewing", 3)
    analogue     = self._get_or_eval("analogue", [], **kwargs)
    duty_cycles  = self._get_or_eval("duty_cycles", [], **kwargs)
    periods      = self._get_or_eval("periods", [], **kwargs)
    # in case a string is given reformat it as a list
    if isinstance(data, str):
      data = data.split(' ')
    # generate the waveform
    wave, pos, ignore, last_y = [], 0, False, None
    # look for repetition '.'
    _wavelane = self._reduce_wavelane(name, wavelane, **kwargs)
    # generate bricks
    symbol, data_counter, regpos_counter, is_first, b_counter, ana_counter = None, 0, 0, 0, 0, 0
    for b, k in _wavelane:
      if b != '|':
        # get the final height of the last brick
        last = -2 if symbol == pywave.BRICKS.gap else -1
        if wave:
          s, br, c, style = wave[last]
          last_y = br.get_last_y()
          symbol = pywave.BRICKS.from_str(b)
          ignore = pywave.BRICKS.ignore_transition(wave[last] if wave else None, symbol)
          # adjust transition from data or x
          if s in [pywave.BRICKS.data, pywave.BRICKS.x] and symbol in [pywave.BRICKS.zero, pywave.BRICKS.one, pywave.BRICKS.low, pywave.BRICKS.high]:
            if symbol in [pywave.BRICKS.zero, pywave.BRICKS.low]:
              br.alter_end(3, brick_height)
            else:
              br.alter_end(3, 0)
            wave[last] = (s, br, c, style)
            ignore = True
          # adjust clock symbols
          if symbol in [pywave.BRICKS.low, pywave.BRICKS.Low] and \
             s in [pywave.BRICKS.Pclk, pywave.BRICKS.pclk, pywave.BRICKS.Nclk, pywave.BRICKS.nclk]:
            br.alter_end(0, brick_height)
            wave[last] = (s, br, c, style)
            ignore = True
          last_y = br.get_last_y()
        else:
          last_y = brick_height
          symbol = pywave.BRICKS.from_str(b)
        # adjust the width of a brick depending on the phase and periods
        pmul = max(periods[b_counter], slewing*2/brick_width) if b_counter < len(periods) else 1
        if is_first == 0:
          width_with_phase = pmul*brick_width*(k-phase)
        elif b_counter == len(_wavelane) - 1:
          width_with_phase = max(pmul*brick_width*(k+phase), kwargs.get("width", 0)-pos)
        else:
          width_with_phase = pmul*k*brick_width
        if pos <= 0:
          is_first = 0
        # update the arguments to be passed for the generation
        kwargs.update({
            "brick_width": width_with_phase + pos if pos < 0 else width_with_phase,
            "brick_height": brick_height,
            "ignore_transition": ignore,
            "is_first": is_first == 0,
            "last_y": last_y,
            "slewing": slewing,
            "duty_cycle": max(duty_cycles[b_counter], slewing*2/brick_width) if b_counter < len(duty_cycles) else 0.5,
            "equation": analogue[ana_counter] if ana_counter < len(analogue) else "0",
            "data": data[data_counter] if len(data) > data_counter else "",
            "regpos": regpos[regpos_counter] if len(regpos) > regpos_counter else ""
        })
        # get next equation if analogue
        if symbol in [pywave.BRICKS.ana, pywave.BRICKS.step, pywave.BRICKS.cap]:
          ana_counter += 1
        # get next data
        if symbol in [pywave.BRICKS.data, 
          pywave.BRICKS.field_start, pywave.BRICKS.field_mid,
          pywave.BRICKS.field_end, pywave.BRICKS.field_bit]:
          data_counter += 1
        if symbol in [pywave.BRICKS.field_start, pywave.BRICKS.field_end, pywave.BRICKS.field_bit]:
          regpos_counter += 1
        # create the new brick
        if pos + width_with_phase > 0:
          wave.append((
              symbol,
              pywave.generate_brick(symbol, **kwargs),
              self.translate(max(0, pos), 0, dont_touch=True),
              f"s{b if b.isdigit() and int(b, 10) > 1 else '2'}"
          ))
        pos += width_with_phase
      else:
        # create the gap
        symbol = pywave.BRICKS.gap
        pos -= brick_width
        wave.append((
            symbol,
            pywave.generate_brick(symbol, **kwargs),
            self.translate(pos+gap_offset, 0, dont_touch=True),
            ""
        ))
        pos += brick_width
      is_first  += 1
      b_counter += 1
    # generate waveform
    def _gen():
      ans = self.wavelane_title(name, vscale=kwargs.get("vscale", 1)) if name else ""
      for w in wave:
        symb, b, e, style = w
        kwargs.update({"extra": e, "style": style})
        ans += self.brick(symb, b, **kwargs)
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
      for x in range(0, int(width), step):
        ans += self.path(
          [(x, 0), (x, height-offsety)],
          style_repr="ticks",
          extra=self.translate(offsetx, 0, dont_touch=False, no_acc=True),
          **kwargs)
      return ans
    return self.group(
      _gen,
      f"ticks_{_WAVEGROUP_COUNT}",
      self.translate(offsetx, 0))

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
          _y += brick_height * 1.5 * wavelane.get("vscale", 1)
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
              s = s[0] + 3 + adj.get("start_x", 0), s[1] + brick_height * 0.5 + adj.get("start_y", 0)
              e = e[0] + 3 + adj.get("end_x", 0), e[1] + brick_height * 0.5 + adj.get("end_y", 0)
              style = "edges "
              style += "arrowtail " if _shape[-1] == '>' else ''
              style += "arrowhead " if _shape[0] == '<' else ''
              mx, my = (s[0] + e[0]) * 0.5, (s[1] + e[1]) * 0.5
              if _shape in ['<~', '~', '~>', '<~>']:
                ans += self.spline([('M', s[0], s[1]), ('C', s[0]*0.1+e[0]*0.9, s[1]), ('', s[0]*0.9+e[0]*0.1, e[1]), ('', e[0], e[1])], style_repr=style)
              elif _shape in ['<-~', '-~', '-~>', '<-~>']:
                ans += self.spline([('M', s[0], s[1]), ('C', e[0], s[1]), ('', e[0], e[1]), ('', e[0], e[1])], style_repr=style)
              elif _shape in ['<~-', '~-', '~->', '<~->']:
                ans += self.spline([('M', s[0], s[1]), ('C', s[0], s[1]), ('', s[0], e[1]), ('', e[0], e[1])], style_repr=style)
              elif _shape in ['<-', '-', '->', '<->']:
                ans += self.spline([('M', s[0], s[1]), ('L', e[0], e[1])], style_repr=style)
              elif _shape in ['<-|', '-|', '-|>', '<-|>']:
                ans += self.spline([('M', s[0], s[1]), ('L', e[0], s[1]), ('', e[0], e[1])], style_repr=style)
                mx, my = e[0], s[1]
              elif _shape in ['<|-', '|-', '|->', '<|->']:
                ans += self.spline([('M', s[0], s[1]), ('L', s[0], e[1]), ('', e[0], e[1])], style_repr=style)
                mx, my = s[0], e[1]
              elif _shape in ['<-|-', '-|-', '-|->', '<-|->']:
                ans += self.spline([('M', s[0], s[1]), ('L', mx, s[1]), ('', mx, e[1]), ('', e[0], e[1])], style_repr=style)
                mx, my = mx, e[1]
              ans += self.text(mx+dx, my+dy, text, extra="text-anchor=\"middle\"")
              return ans
            global _EDGE_COUNT
            ans += self.group(lambda: _gen(**adj), f"edge_{_EDGE_COUNT}")
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
    offsetx = kwargs.get("offsetx", max(_default_offset_x, default=0)*9)
    offsety = kwargs.get("offsety", 0)
    translate = kwargs.get("translate", False)
    def _gen(offset):
      # options
      brick_width  = kwargs.get("brick_width", 40)
      brick_height = kwargs.get("brick_height", 20)
      width        = kwargs.get("width", 0)
      height       = kwargs.get("height", 0)
      no_ticks     = kwargs.get("no_ticks", False)
      ox, oy, dy = offset[0], offset[1], 0
      # some space for group separation
      dy = 20 if depth > 1 else 0
      oy += dy
      if translate:
        self.translate(ox if translate and depth == 1 else 0, dy)
      # return value is ans
      if depth > 1:
        # add group name
        ans = self.text(0, oy-10, name, style_repr=f"h{depth}", extra=self._GROUP_NAME, **kwargs)
        # add group separator
        if depth == 2:
          ans += self.path([(0, dy-6), (width+ox, dy-6)], style_repr="border ctx-y", **kwargs)
      else:
        ans = ""
      # look through waveforms data
      for _, wavetitle in enumerate(wavelanes.keys()):
        # signal in a dict
        if isinstance(wavelanes[wavetitle], dict):
          # waveform
          if "wave" in wavelanes[wavetitle]:
            wave, args = wavelanes[wavetitle]["wave"], wavelanes[wavetitle]
            l = len(wave)
            width = l * brick_width if l * brick_width > width else width
            args.update(**kwargs)
            ans += self.wavelane(
                wavetitle,
                wave,
                self.translate(0 if translate else ox, 0 if translate else oy),
                **args
            )
            dy = brick_height * 1.5 * wavelanes[wavetitle].get("vscale", 1)
          # spacer or only for label nodes
          elif Renderer.is_spacer(wavetitle) or "node" in wavelanes[wavetitle]:
            dy = brick_height * 1.5
          # named group
          elif not wavetitle in ["head", "foot", "config"]:
            self._FIRST_TRANSLATION = False
            args = kwargs
            args.update({"offsetx": ox, "offsety": 0, "no_ticks": True})
            dy, tmp = self.wavegroup(
                wavetitle,
                wavelanes[wavetitle],
                self.translate(0, oy, dont_touch=True),
                depth+1,
                **args
            )
            ans += tmp
          oy += dy
          if translate:
            self.translate(0, dy)
        # extra config
        else:
          pass
      # add ticks only for the principale group
      if not no_ticks:
        ans = self.ticks(width, height, brick_width, offsetx=ox) + "\n" + ans
      offset[0], offset[1] = ox, oy
      return ans
    # a useful signal is in a dict
    if isinstance(wavelanes, dict):
      # room for displaying names
      offset = [offsetx, offsety]
      ans = self.group(lambda: _gen(offset), name, extra)
      offsetx, offsety = offset[0], offset[1]
      # finish the group
      ans += self.edges(wavelanes, extra=self.translate(offsetx, 0, dont_touch=True), **kwargs)
      return (offsety, ans)
    # unknown options
    else:
      raise Exception("Unkown wavelane type or option")
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
      x, y, keys = [0], 0, [0]
      for wavetitle in wavelanes.keys():
        if isinstance(wavelanes[wavetitle], dict):
          if "wave" in wavelanes[wavetitle]:
            if not "periods" in wavelanes[wavetitle]:
              _l = len(wavelanes[wavetitle]["wave"])
            else:
              periods = self._get_or_eval("periods", [], **wavelanes[wavetitle])
              _l = sum(periods)
            _l *= brick_width
            _l *= wavelanes[wavetitle].get("repeat", 1)
            _l *= wavelanes[wavetitle].get("period", 1)
            x.append(_l)
            y += brick_height * 1.5 * wavelanes[wavetitle].get("vscale", 1)
            keys.append(len(wavetitle))
          elif Renderer.is_spacer(wavetitle) or "node" in wavelanes[wavetitle]:
            y += brick_height * 1.5
          elif not wavetitle in ["head", "foot", "config"]:
            y += 20
            lkeys, _x, _y = self.size(wavelanes[wavetitle], brick_width, brick_height, depth+1)
            x.append(_x)
            y += _y
            keys.append(lkeys)
        elif isinstance(wavelanes[wavetitle], list):
          if len(wavelanes[wavetitle]) > 0 and \
             isinstance(wavelanes[wavetitle][0], dict) and \
             "wave" in wavelanes[wavetitle][0]:
            y += 20
            lkeys, _x, _y = self.size(wavelanes[wavetitle], brick_width, brick_height, depth+1)
            x.append(_x)
            y += _y
            keys.append(lkeys)
      return (max(keys), max(x), y)

  def draw(self, wavelanes, **kwargs) -> str:
    """
    generate an svg file from wavelanes
    [id]           : identifier for multiple integration
    [brick_width]  : width of a brick
    [brick_height] : height of a brick
    """
    raise NotImplementedError()