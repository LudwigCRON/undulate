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
    return (
      "gsave\n"
      f"{x} {y} translate\n"
      f"{-angle-90} rotate\n"
      "newpath\n"
      "-3.5 -3.5 moveto\n"
      "0 3.5 lineto\n"
      "3.5 -3.5 lineto\n"
      "0 -2 lineto\n"
      "closepath\n"
      "fill\n"
      "grestore\n"
    )

  def polygon(self, vertices: list, extra: str = "", **kwargs) -> str:
    """
    polygon draw a closed shape to represent common data
    vertices: list of of x-y coordinates in a tuple
    [extra] : optional attributes for the svg (eg class)
    """
    fill = kwargs.get("fill", "1 1 1 setrgbcolor")
    block_height = kwargs.get("block_height", 20)
    if "Hatch" in fill:
      path = ["gsave", "newpath", "0 0 moveto"]
    elif fill != "none":
      path = ["gsave", "newpath", fill, "0 0 moveto"]
    else:
      return ""
    xmin, xmax, ymin, ymax = 9999, 0, 9999, 0
    px, py = 0, 0
    for v in vertices:
      x, y = v
      y = block_height - y
      xmin = x if x < xmin else xmin
      xmax = x if xmax < x else xmax
      ymin = y if y < ymin else ymin
      ymax = y if ymax < y else ymax
      path.append(f"{x - px} {y - py} rlineto")
      px, py = x, y
    if "Hatch" in fill:
      path[2] = path[2].replace('rlineto', 'rmoveto')
      path.append("closepath")
      path.append("clip")
      path.append("newpath")
      path.append("0.5 setlinewidth")
      for x in range(int(xmin-abs(ymax-ymin)), int(xmax+10), 10):
        path.append(f"{x-10} {ymin} moveto")
        path.append(f"{x+abs(ymax-ymin)} {ymax} lineto")
      path.append("stroke")
    else:
      path[3] = path[3].replace('rlineto', 'rmoveto')
      path.append("closepath")
      path.append("fill")
    path.append("grestore\n")
    return '\n'.join(path)

  def spline(self, vertices: list, **kwargs) -> str:
    """
    spline draw a path to represent smooth signals
    vertices: list of of type-x-y coordinates in a tuple of control points
              where type is either a moveto (m/M) lineto (l/L) or curveto (c/C)
              svg operator
    [extra] : optional attributes for the svg (eg class)
    """
    style        = kwargs.get("style_repr", "")
    block_height = kwargs.get("block_height", 20)
    # ticks are disabled for debug purpose only
    path, c, cmd, line = [], 0, "", ""
    if style == "ticks":
      path = ["gsave", "0.8 setgray", "[1 1] 0 setdash"]
    path.extend(["newpath", "0 0 moveto"])
    px, py = 0, 0
    for v in vertices:
      s, x, y = v
      if not style == "ticks":
        if isinstance(y, (float, int)):
          y = -y
          if not s.startswith('r'):
            y += block_height
      # check the command
      cmd = "rcurveto"  if s in "cqts" else \
            "curveto"   if s in "CQTS" else \
            "rlineto"   if s == "l" else \
            "lineto"    if s == "L" else \
            "rmoveto"   if s == "m" else \
            "moveto"    if s == "M" else \
            "closepath" if s == "z" else cmd
      if c == 0:
        c = 2 if s in "CQTcqt" else \
            1 if s in "Ss"     else c
        if s in "Ss":
          line += f"{x+(x-px)} {y+(y-py)} "
        else:
          line += f"{px} {py} "
      if c > 0:
        c -= 1
        line += f"{x} {y} "
      else:
        path.append(f"{line}{x} {y} {cmd}")
        line = ""
      px, py = x, y
    if style == "ticks":
      path.append("stroke")
      path.append("grestore\n")
    else:
      path.append("stroke\n")
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
    if text.strip():
      if extra == "right-justify":
        ans += f"{self._ox} {self._height - self._oy} moveto ({text}) {x} {y-9} right-justify\n"
      else:
        ans += f"0 0 moveto ({text}) {x} {y-3} center-justify\n"
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
      return f"{self._ox} {self._height - self._oy} translate"
    else:
      return f"{self._ox + x} {self._height - self._oy - y} translate 0 0 moveto"
  
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
    self._height = height - brick_height * 1.25
    return (
      "%!PS-Adobe-3.0\n"
      "%%LanguageLevel: 2\n"
      "%%Pages: 1\n"
      f"<< /PageSize [{width+lkeys*11+2} {height+2}] >> setpagedevice\n"
      #f"%%BoundingBox: 0 0 {width} {height}\n"
      "%%EndComments\n"
      "%%BeginProlog\n"
      "% Use own dictionary to avoid conflicts\n"
      "10 dict begin\n"
      "%%EndProlog\n"
      "%%Page: 1 1\n"
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
      "/center-justify { % stack: string y\n"
      "  /y exch def % handle top of stack: y coord of line\n"
      "  /x exch def % handle top of stack: x coord of line\n"
      "  x y rmoveto % move to right end\n"
      "  dup stringwidth pop 2 div neg 0 rmoveto show"
      "} def\n"
      "0 0 moveto\n"
      "1 1 scale\n"
      ""+self.wavegroup(_id, wavelanes, brick_width=brick_width, brick_height=brick_height, width=width, height=height, offsetx=lkeys*10+10)[1]+""
      "showpage\n"
      "%%Trailer\n"
      "end\n"
      "%%EOF\n"
    )
