#!/usr/bin/env python3

import skin
import bricks

_WAVEGROUP_COUNT = 0
_WAVE_COUNT = 0
def incr_wavelane(f):
  def wrapper(*args, **kwargs):
    global _WAVE_COUNT
    _WAVE_COUNT += 1
    return f(*args, **kwargs)
  return wrapper

def incr_wavegroup(f):
  def wrapper(*args, **kwargs):
    global _WAVEGROUP_COUNT
    _WAVEGROUP_COUNT += 1
    return f(*args, **kwargs)
  return wrapper

# SVG Drawing
def vertices_to_svgpath(vertices:list, extra:str = "") -> str:
  p = ''.join([f"L{x},{y} " for x, y in vertices])
  p = 'M' + p[1:]
  return f"<path d=\"{p.strip()}\" {extra} />\n"

def svg_arrow(x, y, angle, extra:str = "") -> str:
  return f"<path d=\"M 0 0 L 3.5 7 L 7 0 L 3.5 1.5z\" transform=\"translate({x-3.5}, {y-3.5}) rotate({angle-90}, 3.5, 3.5)\" {extra} />\n"

def svg_polygon(vertices:list, extra:str = "") -> str:
  ans = "<polygon points=\""
  for x, y in vertices:
    ans += f"{x},{y} "
  ans += f"\" {extra} />"
  return ans

def svg_spline(vertices:list, extra:str = "") -> str:
  p = ''.join([f"{v[0]}{v[1]},{v[2]} " for v in vertices])
  return f"<path d=\"{p.strip()}\" {extra} />\n"

def svg_vertical_line(x, size:int = 20, extra:str = ""):
  return f"<path d=\"M {x} 0 L {x} {size}\" {extra} />"

def svg_brick(symbol:str, b:dict, extra:str = "", height:int = 20):
  ans = f"<g data-symbol=\"{symbol}\" {extra}>\n"
  if symbol == bricks.BRICKS.gap or symbol == '|':
    ans += f"<path d=\"m7,-2 -4,0 c -5,0 -5,{height+4} -10,{height+4} l 4,0 C 2,{height+4} 2,-2 7,-2 z\" class=\"hide\"></path>\n"
    ans += f"<path d=\"M-7,{height+2} C -2,{height+2} -2,-2 3,-2\" class=\"path\"></path>\n"
    ans += f"<path d=\"M-3,{height+2} C 2,{height+2} 2,-2 7,-2\" class=\"path\"></path>\n"
  else:
    for _, path in enumerate(b.paths):
      ans += vertices_to_svgpath(path, "class=\"path\"")
    for _, arrow in enumerate(b.arrows):
      ans += svg_arrow(*arrow, "class=\"arrow\"")
    for _, poly in enumerate(b.polygons):
      ans += svg_polygon(poly, "fill=\"url(#diagonalHatch)\"" if symbol == bricks.BRICKS.x else "fill=\"none\"")
    for _, spline in enumerate(b.splines):
      ans += svg_spline(spline, "class=\"path\"")
  ans += "</g>"
  return ans

def svg_wavelane_title(name:str):
  return f"<text x=\"-10\" y=\"15\" class=\"info\" text-anchor=\"end\" xml:space=\"preserve\"><tspan>{name}</tspan></text>\n"

@incr_wavelane
def svg_wavelane(name:str, wavelane:str, extra:str = "", **kwargs):
  no_glitch  = kwargs.get("no_glitch", False)
  width      = kwargs.get("width", 20)
  gap_offset = kwargs.get("gap_offset", width*0.75)
  # generate the waveform
  wave, pos, previous_brick, last_y = [], 0, None, None
  for b in wavelane:
    if b != '|':
      symbol = previous_brick if b == '.' and not previous_brick == bricks.BRICKS.data else bricks.BRICKS.from_str(b)
      ignore = bricks.BRICKS.ignore_transition(previous_brick, '.' if b == '.' else symbol)
      if b == '.' and previous_brick is None:
        raise f"error in {name}: cannot repeat none, add a valid brick first"
      elif b != '.':
        previous_brick = bricks.BRICKS.from_str(b)
      if wave:
        s, br, _ = wave[-1]
        if s == bricks.BRICKS.gap:
          s, br, _ = wave[-2]
        if br.paths:
          _, last_y = br.paths[0][-1]
        elif br.splines:
          _, _, last_y = br.splines[0][-1]
      kwargs.update({"ignore_transition":ignore, "last_y":last_y})
      wave.append(
        (symbol if not b == '.' or symbol == bricks.BRICKS.x else '.',
        bricks.generate_brick(
          previous_brick,
          **kwargs,
        ), f"transform=\"translate({pos*width}, 0)\"")
      )
    else:
      pos -= 1
      wave.append((bricks.BRICKS.gap, bricks.Brick(), f"transform=\"translate({pos*width+gap_offset}, 0)\""))
    pos += 1
  # filter for no_glitch
  if no_glitch:
    for i in range(0, len(wave)-1):
      symb2, b2, e2 = wave[i+1]
      symb1, b1, e1 = wave[i]
      for j in range(min(len(b1.paths), len(b2.paths))):
        dy_dx2 = bricks.start_derivative(b2.paths[j])
        dy_dx1 = bricks.end_derivative(b1.paths[j])
        # spike detected
        if (dy_dx2 > 0 and dy_dx1 < 0) or (dy_dx1 > 0 and dy_dx2 < 0):
          # remove it
          _, y = b2.paths[j][1]
          _, x = b1.paths[j][-2]
          y += x
          x1, y1 = b1.paths[j][-1]
          x2, y2 = b2.paths[j][0]
          b1.paths[j] = b1.paths[j][:-1]+[(x1, y*0.5)]
          b2.paths[j] = [(x2, y*0.5)]+b2.paths[j][1:]
          b2.arrows = b2.arrows[1:]
          wave[i] = (symb1, b1, e1)
  # waveform name
  ans = ""
  if len(name) > 0:
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

@incr_wavegroup
def svg_wavegroup(name:str, wavelanes, extra:str = "", **kwargs):
  height = kwargs.get("height", 20)
  ans = f"<g id=\"{name}\" {extra} >"
  # if no name is given
  if isinstance(wavelanes, list):
    for i, wavelane in enumerate(wavelanes):
      ans += svg_wavelane("", wavelane, f"transform=\"translate(0, {i*height*1.5})\"", **kwargs)
  # otherwise
  elif isinstance(wavelanes, dict):
    # room for displaying names
    offsetx = max(map(len, wavelanes.keys()))*11
    for i, wavetitle in enumerate(wavelanes.keys()):
      wave, args = wavelanes[wavetitle]["wave"], wavelanes[wavetitle]
      args.update(**kwargs)
      ans += svg_wavelane(wavetitle, wave, f"transform=\"translate({offsetx}, {i*height*1.5})\"", **args)
  else:
    raise "Unkown wavelane type"
  ans += "</g>"
  return ans

def svg_size(wavelanes, width:int = 20, height:int = 28):
  if isinstance(wavelanes, dict):
    y = len(wavelanes.keys())
    x = max(map(lambda w: len(w["wave"]), wavelanes.values()))*width
    x += max(map(len, wavelanes.keys()))*11
    return (x, y*height*1.5)
  else:
    y = len(wavelanes)
    x = max(map(len, wavelanes))
    return (x*width, y*height*1.5)

def draw(wavelanes, **kwargs) -> str:
  tile_width  = kwargs.get("tile_width", 40)
  tile_height = kwargs.get("tile_height", 20)
  width, height = svg_size(wavelanes, tile_width, tile_height)
  return (
    f"<svg xmlns=\"http://www.w3.org/2000/svg\" \n width=\"{width}\" height=\"{height}\" viewBox=\"-1 -1 {width+2} {height+2}\">\n"
    f"<style>{skin.DEFAULT}</style>\n"
    f"{skin.PATTERN}"
    ""+svg_wavegroup("a", wavelanes, width=tile_width, height=tile_height)+""
    "\n</svg>"
  )

# test
if __name__ == "__main__":
  import os
  os.makedirs("./svgs", exist_ok=True)
  # test of each elements
  for brick in bricks.BRICKS:
    print(f"./svgs/{brick}.svg")
    try:
      with open(f"./svgs/{brick}.svg", "w+") as fp:
        fp.write(f"<svg xmlns=\"http://www.w3.org/2000/svg\" \n width=\"40\" height=\"20\" viewBox=\"-1 -1 42 22\">\n")
        fp.write(f"<style>{skin.DEFAULT}</style>\n")
        fp.write(skin.PATTERN)
        fp.write(svg_brick(brick, bricks.generate_brick(brick, width=40, height=20)))
        fp.write("\n</svg>")
    except Exception as e:
      print("failed!", e)
  
  # test of a signal line
  wavelanes = ["P........", "pnpnPN....", "lh.ll..h..."]
  size, height = 40, 40
  for i, wavelane in enumerate(wavelanes):
    width = size * len(wavelane)
    print(f"./svgs/wavelane_{i}.svg")
    try:
      with open(f"./svgs/wavelane_{i}.svg", "w+") as fp:
        fp.write(f"<svg xmlns=\"http://www.w3.org/2000/svg\" \n width=\"{width}\" height=\"{height}\" viewBox=\"-1 -1 {width+2} {height+2}\">\n")
        fp.write(f"<style>{skin.DEFAULT}</style>\n")
        fp.write(skin.PATTERN)
        fp.write(svg_wavelane(f"clk_{i}", wavelane, width=size, height=height))
        fp.write("\n</svg>")
    except Exception as e:
      print("failed!", e)
  
  # test for a group
  wavelanes = {
    "clk": {"wave": "P........", "slewing":8},
    "gated_clk_a": {"wave": "pnpnPN....", "slewing":8},
    "gated_clk_b": {"wave": "pnpnPN....", "slewing":8, "no_glitch":True},
    "data_0": {"wave": "lh.ll..h..."},
    "data_1": {"wave": "lh.ll..h...", "slewing":8},
    "data_2": {"wave": "0.1..0|1.0", "slewing":8},
    "data_3": {"wave": "0.1..0|1.0", "slewing":0, "gap_offset": 10},
    "data_4": {"wave": "0.1..0|1.0", "slewing":26, "no_glitch":True},
    "data_5": {"wave": "0.1..0|1.0", "slewing":0, "no_glitch":True, "gap_offset": 16},
    "DQS": {"wave": "z.......0.1010z.", "slewing":8, "no_glitch":True},
    "Data": {"wave": "0..01==...=.", "slewing":8, "no_glitch":True}
  }
  width, height = svg_size(wavelanes, 30, 20)
  i += 1
  print(f"./svgs/wavelane_{i}.svg")
  try:
    with open(f"./svgs/wavelane_{i}.svg", "w+") as fp:
      fp.write(f"<svg xmlns=\"http://www.w3.org/2000/svg\" \n width=\"{width}\" height=\"{height}\" viewBox=\"-1 -1 {width+2} {height+2}\">\n")
      fp.write(f"<style>{skin.DEFAULT}</style>\n")
      fp.write(skin.PATTERN)
      fp.write(svg_wavegroup("a", wavelanes, width=30, height=20))
      fp.write("\n</svg>")
  except Exception as e:
      print("failed!", e)
  
  wavelanes = {
    "clk": {"wave": "P......" },
    "bus": {"wave": "x.==.=x", "data": ["head", "body", "tail", "data"] },
    "wire": {"wave": "0.1..0." }
  }
  width, height = svg_size(wavelanes, 30, 20)
  i += 1
  print(f"./svgs/wavelane_{i}.svg")
  try:
    with open(f"./svgs/wavelane_{i}.svg", "w+") as fp:
      fp.write(f"<svg xmlns=\"http://www.w3.org/2000/svg\" \n width=\"{width}\" height=\"{height}\" viewBox=\"-1 -1 {width+2} {height+2}\">\n")
      fp.write(f"<style>{skin.DEFAULT}</style>\n")
      fp.write(skin.PATTERN)
      fp.write(svg_wavegroup("a", wavelanes, width=30, height=20))
      fp.write("\n</svg>")
  except Exception as e:
      print("failed!", e)
  