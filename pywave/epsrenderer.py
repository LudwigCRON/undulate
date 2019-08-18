#!/usr/bin/env python3
# spell-checker: disable

"""
epsrenderer.py use the logic of renderer.py to render waveforms
into encapsulated postcript file or postscript file
"""

# TODO fix position of edges --> seems to be only a y=-y
# TODO fix position of wavelane in group with spacers

import copy
from .skin import DEFAULT, DEFINITION
from .renderer import Renderer, SvgCurveConvert

class EpsRenderer(Renderer):
  """
  Render the wavelanes as an eps
  """
  _WAVE_TITLE = "right-justify bold"
  _DATA_TEXT  = "center-justify abs"
  _GROUP_NAME = "bold group"

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
    return f"gsave\n{extra}\n{callback()}\ngrestore\n"

  def path(self, vertices: list, **kwargs) -> str:
    """
    path draw a path to represent common signals
    vertices: list of of x-y coordinates in a tuple
    [extra] : optional attributes for the svg (eg class)
    """
    style        = kwargs.get("style_repr", "")
    extra        = kwargs.get("extra", "")
    block_height = kwargs.get("block_height", 20)
    height       = kwargs.get("height", 20)
    path, ctx = [], self._offset_stack[-1]
    if "ticks" in style:
      path = ["gsave", "0.5 setlinewidth", "0.8 setgray", "[0.5 0.5] 0 setdash", extra]
    elif "border" in style:
      path = ["gsave", "1.5 setlinewidth", extra]
    path.extend(["newpath"])
    px, py, i = 0, 0, len(path)
    for v in vertices:
      x, y = v
      if "ctx-y" in style:
        x, y = x, height - ctx[1] - y
      elif "ctx-x" in style:
        x, y = ctx[0] + x, height - y
      elif "ctx" in style:
        x, y = ctx[0] + x, height - ctx[1] - y
      else:
        y = block_height - y
      path.append(f"{x - px:.5f} {y - py:.5f} rlineto")
      px, py = x, y
    path[i] = path[i].replace("rlineto", "moveto")
    if any([w in style for w in ["ticks", "border"]]):
      path.append("stroke")
      path.append("grestore\n")
    else:
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
      step = 8
      for x in range(int(xmin-abs(ymax-ymin)), int(xmax+step), step):
        path.append(f"{x-step} {ymin} moveto")
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
    extra        = kwargs.get("extra", "")
    block_height = kwargs.get("block_height", 20)
    # debug spline
    vertices = SvgCurveConvert(vertices)
    # ticks are disabled for debug purpose only
    path, c, cmd, line = [], 0, "moveto", ""
    path.extend(["newpath", "0 0 moveto"])
    px, py = 0, 0
    for i, v in enumerate(vertices):
      s, x, y = v
      # check the command
      cmd = "rcurveto"  if s == "c" else \
            "curveto"   if s == "C" else \
            "rlineto"   if s == "l" else \
            "lineto"    if s == "L" else \
            "rmoveto"   if s == "m" else \
            "moveto"    if s == "M" else \
            "closepath" if s == "z" or s == "Z" else cmd
      if isinstance(y, (float, int)):
        y = -y
        # if not first point of bloc of relative coordinate invert
        if i == 0 or not (cmd[0] == 'r'):
          y += block_height
        # if edges shift them
        if "edges" in style:
          y += self._height
      # gather 3 points to draw a bezier curve
      c = 2 if s in ["C", "c"] else c
      if c == 2:
        line = f"{x} {y} "
        c = 1
      elif c > 0:
        line += f"{x} {y} "
        c -= 1
      else:
        path.append(f"{line}{x} {y} {cmd}")
        line = ""
      # hold last point
      px, py = x, y
    if style == "hide":
      path.append("1 1 1 setrgbcolor")
      path.append("fill\n")
    else:
      path.append("0 0 0 setrgbcolor")
      path.append("stroke\n")
    return '\n'.join(path)

  def text(self, x: float, y: float, text: str = "", **kwargs) -> str:
    """
    text draw a text for data
    x       : x coordinate of the text
    y       : y coordinate of the text
    text    : text to display
    """
    extra      = kwargs.get("extra", "")
    ans = ""
    # set font style
    if "bold" in extra:
      ans = "/Courier-Bold findfont 12 scalefont setfont\n"
    elif "group" in extra:
      ans = "/Courier-Bold findfont 14 scalefont setfont\n"
    else:
      ans = "/Courier findfont 12 scalefont setfont\n"
    # not relative
    if "abs" in extra:
      ox, oy = 0, - 2*y + 20
    else:
      ox, oy = self._ox, self._height - self._oy
    # shift the group name
    if "group" in extra:
      ox, oy = 5, oy+36
    # show text
    if text:
      if "right-justify" in extra:
        ans += f"{ox} {oy} moveto ({text}) {x} {y - 9} right-justify"
      elif "center-justify" in extra:
        ans += f"{ox} {oy} moveto ({text}) {x} {y - 3} center-justify"
      else:
        ans += f"{ox} {oy} moveto ({text}) show"
    return f"gsave\n{ans}\ngrestore\n"

  def translate(self, x: float, y: float, **kwargs) -> str:
    no_acc      = kwargs.get("no_acc", False)
    dont_touch  = kwargs.get("dont_touch", False)
    if not dont_touch:
      self._offset_stack.append((self._ox, self._oy))
      if no_acc:
        self._ox, self._oy = x, y
      else:
        self._ox, self._oy = self._ox + x, self._oy + y
      return f"{self._ox} {self._height - self._oy} translate 0 0 moveto"
    else:
      return f"{self._ox + x} {self._height - self._oy - y} translate 0 0 moveto"
  
  def untranslate(self):
    try:
      self._ox, self._oy = self._offset_stack.pop()
    except IndexError:
      self._ox, self._oy = 0, 0

  def wavelane(self, *args, **kwargs) -> str:
    l = len(self._offset_stack)
    ans = Renderer.wavelane(self, *args, **kwargs)
    while len(self._offset_stack) > l:
      self.untranslate()
    return ans
  
  def wavegroup(self, *args, **kwargs) -> str:
    l = len(self._offset_stack)
    ans = Renderer.wavegroup(self, *args, **kwargs)
    while len(self._offset_stack) > l:
      self.untranslate()
    return ans

  def draw(self, wavelanes, **kwargs) -> str:
    _id          = kwargs.get("id", "a")
    brick_width  = kwargs.get("brick_width", 40)
    brick_height = kwargs.get("brick_height", 20)
    is_reg       = kwargs.get("is_reg", False)
    lkeys, width, height, n = self.size(wavelanes, brick_width, brick_height)
    # remove offset for the name in register
    if is_reg:
      lkeys = -1
      height += n * 12
    self._height = height - brick_height * 1.25
    # update viewport information
    kwargs.update({
      "translate": True, 
      "brick_height":brick_height, 
      "brick_width": brick_width,
      "height": height, 
      "width": width, 
      "offsetx":lkeys*10+10})
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
      "gsave\n"
      ""+self.wavegroup(_id, wavelanes, **kwargs)[1]+""
      "showpage\n"
      "%%Trailer\n"
      "end\n"
      "%%EOF\n"
    )
