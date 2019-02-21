#!/usr/bin/env python3
# spell-checker: disable

"""
epsrenderer.py use the logic of renderer.py to render waveforms
into encapsulated postcript file or postscript file
"""

from .skin import DEFAULT, DEFINITION
from .renderer import Renderer
from .bricks import Brick

class EpsRenderer(Renderer):
  """
  Render the wavelanes as an eps
  """
  _WAVE_TITLE  = "right-justify"

  def __init__(self):
    Renderer.__init__(self)
    self._height = 0
    self._offset_stack = [(0, 0)]
    self._ox     = 0
    self._oy     = 0
  
  def _SYMBOL_TEMP(self, *args, **kwargs):
    symbol, content = args
    extra = kwargs.get("extra", "")
    print(symbol, extra)
    return f"gsave\n{extra}\n{content}\ngrestore\n"

  def group(self, callback, id: str = "", extra: str = "") -> str:
    """
    group define a group
    """
    ans = (
      "gsave\n"
      ""+callback()+""
      "grestore\n"
    )
    return ans

  def path(self, vertices: list, **kwargs) -> str:
    """
    path draw a path to represent common signals
    vertices: list of of x-y coordinates in a tuple
    [extra] : optional attributes for the svg (eg class)
    """
    block_height = kwargs.get("block_height", 20)
    path = ["newpath", "0 0 moveto"]
    px, py = 0, 0
    for v in vertices:
      x, y = v
      y = block_height - y
      path.append(f"{x - px} {y - py} rlineto")
      px, py = x, y
    path[2] = path[2].replace("rlineto", "rmoveto")
    path.append("stroke\n")
    return '\n'.join(path)

  def arrow(self, x, y, angle, extra: str = "", **kwargs) -> str:
    """
    arrow draw an arrow to represent edge trigger on clock signals
    x       : x coordinate of the arrow center
    y       : y coordinate of the arrow center
    angle   : angle in degree to rotate the arrow
    [extra] : optional attributes for the svg (eg class)
    """
    #return (f"<path d=\"M 0 0 L 3.5 7 L 7 0 L 3.5 1.5z\" "
    #        f"transform=\"translate({x-3.5}, {y-3.5}) rotate({angle-90}, 3.5, 3.5)\" "
    #        f"{extra} />\n")
    return ""

  def polygon(self, vertices: list, extra: str = "", **kwargs) -> str:
    """
    polygon draw a closed shape to represent common data
    vertices: list of of x-y coordinates in a tuple
    [extra] : optional attributes for the svg (eg class)
    """
    path = ["newpath"]
    path.extend([f"{x} {y} rlineto" for x, y in vertices])
    path[1] = path[1].replace('rlineto', 'rmoveto')
    path.append("closepath")
    path.append("stroke\n")
    return ""#'\n'.join(path)

  def spline(self, vertices: list, **kwargs) -> str:
    """
    spline draw a path to represent smooth signals
    vertices: list of of type-x-y coordinates in a tuple of control points
              where type is either a moveto (m/M) lineto (l/L) or curveto (c/C)
              svg operator
    [extra] : optional attributes for the svg (eg class)
    """
    style = kwargs.get("style_repr", "")
    block_height = kwargs.get("block_height", 20)
    # ticks are disabled for debug purpose only
    if style == "ticks":
      return ""
    c, cmd, line = 0, "", ""
    path = ["newpath", "0 0 moveto"]
    px, py = 0, 0
    for v in vertices:
      s, x, y = v
      y = -y
      if not s.startswith('r'):
        y += block_height
      # check the command
      cmd = "rcurveto"  if s in ["c", "q", "t", "s"] else \
            "curveto"   if s in ["C", "Q", "T", "S"] else \
            "rlineto"   if s == "l" else \
            "lineto"    if s == "L" else \
            "rmoveto"   if s == "m" else \
            "moveto"    if s == "M" else \
            "closepath" if s == "z" else cmd
      c = 2 if s in ["C", "Q", "T", "S", "c", "q", "t", "s"] else c
      if c == 2:
        c -= 1
        line += f"{px} {py} "
      elif c > 0:
        c -= 1
        line += f"{x} {y} "
      else:
        path.append(f"{line}{x} {y} {cmd}")
        line = ""
      px, py = x, y
    path.append("stroke\n")
    print(path)
    return '\n'.join(path)

  def text(self, x: float, y: float, text: str = "", **kwargs) -> str:
    """
    text draw a text for data
    x       : x coordinate of the text
    y       : y coordinate of the text
    text    : text to display
    """
    extra = kwargs.get("extra", "")
    ans = ""
    print("\n", text, self._ox, self._oy, x, y, extra)
    if text.strip():
      if extra == "right-justify":
        ans += f"{self._ox} {self._oy} moveto ({text}) {x} {y} right-justify\n"
      else:
        ans += f"{x} {y} rmoveto ({text}) show\n"
    return ans

  def translate(self, x: float, y: float, **kwargs) -> str:
    no_acc      = kwargs.get("no_acc", False)
    dont_touch  = kwargs.get("dont_touch", False)
    if not dont_touch:
      self._offset_stack.append((self._ox, self._oy))
      if no_acc:
        self._ox, self._oy = x, y
      else:
        self._ox, self._oy = self._ox + x, self._oy + y
      return f"{self._ox} {self._oy} translate"
    else:
      return f"{self._ox + x} {self._oy + y} translate 0 0 moveto"
  
  def untranslate(self):
    try:
      self._ox, self._oy = self._offset_stack.pop()
    except IndexError:
      self._ox, self._oy = 0, 0

  def wavelane(self, *args, **kwargs) -> str:
    ans = Renderer.wavelane(self, *args, **kwargs)
    self.untranslate()
    return ans
  
  def wavegroup(self, *args, **kwargs) -> str:
    ans = Renderer.wavegroup(self, *args, **kwargs)
    self.untranslate()
    return ans

  def draw(self, wavelanes, **kwargs) -> str:
    _id          = kwargs.get("id", "a")
    brick_width  = kwargs.get("brick_width", 40)
    brick_height = kwargs.get("brick_height", 20)
    lkeys, width, height = self.size(wavelanes, brick_width, brick_height)
    self._height = height
    return (
      "%!PS-Adobe-3.0\n"
      "%%LanguageLevel: 2\n"
      "%%Pages: 1\n"
      f"<< /PageSize [{width} {height}] >> setpagedevice\n"
      #f"%%BoundingBox: 0 0 {width} {height}\n"
      "%%EndComments\n"
      "%%BeginProlog\n"
      "% Use own dictionary to avoid conflicts\n"
      "10 dict begin\n"
      "%%EndProlog\n"
      "%%Page: 1 1\n"
      f"{width} {height} 1\n"
      "/Courier findfont\n"
      "9 scalefont\n"
      "setfont\n"
      "0 0 0 setrgbcolor\n"
      "1 setlinewidth\n"
      "/right-justify { % stack: string y\n"
      "  /y exch def % handle top of stack: y coord of line\n"
      "  /x exch def % handle top of stack: x coord of line\n"
      "  dup stringwidth pop % stack: width string\n"
      "  x y rmoveto % move to right end\n"
      "  neg 0 rmoveto % move to left end\n"
      "  show % print string\n"
      "} def\n"
      f"0 0 moveto\n"
      "1 1 scale\n"
      ""+self.wavegroup(_id, wavelanes, brick_width=brick_width, brick_height=brick_height, width=width, height=height)[1]+""
      "showpage\n"
      "%%Trailer\n"
      "end\n"
      "%%EOF\n"
    )
