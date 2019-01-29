#!/usr/bin/env python3

import svg
import unittest

class TestSvgMethods(unittest.TestCase):
  def test_wavedrom_step1(self):
    """
    test supported state of a signal
    """
    wavelanes = {
      "Alfa": {"wave":"01.zx=ud.23.45"},
      "SAlfa": {"wave":"01.zx=ud.23.45", "slewing":8, "no_glitch":True},
    }
    with open("./test/wavedrom_step1.svg", "w+") as fp:
      fp.write(svg.draw(wavelanes))
  
  def test_wavedrom_step2(self):
    """
    test clock generation
    """
    wavelanes = {
      "pclk":{ "wave": "p......." },
      "Pclk":{ "wave": "P......." },
      "nclk":{ "wave": "n......." },
      "Nclk":{ "wave": "N......." },
      "clk0":{ "wave": "phnlPHNL" },
      "clk1":{ "wave": "xhlhLHl." },
      "clk2":{ "wave": "hpHplnLn" },
      "clk3":{ "wave": "nhNhplPl" },
      "clk4":{ "wave": "xlh.L.Hx" },
    }
    with open("./test/wavedrom_step2.svg", "w+") as fp:
      fp.write(svg.draw(wavelanes))
  
  def test_wavedrom_step3(self):
    """
    small bus example
    """
    wavelanes = {
      "clk": {"wave": "P......" },
      "bus": {"wave": "x.==.=x", "data": ["head", "body", "tail", "data"]},
      "wire": {"wave": "0.1..0." }
    }
    with open("./test/wavedrom_step3.svg", "w+") as fp:
      fp.write(svg.draw(wavelanes))
  
  def test_wavedrom_step4(self):
    """
    spacer and gaps
    """
    wavelanes = {
      "clk":{"wave": "p.....|..." },
      "Data":{"wave": "x.345x|=.x", "data": ["head", "body", "tail", "data"] },
      "Request":{"wave": "0.1..0|1.0" },
      " ":{"wave":""},
      "Acknowledge":{"wave": "1.....|01." }
    }
    with open("./test/wavedrom_step4.svg", "w+") as fp:
      fp.write(svg.draw(wavelanes))
  
  def test_wavedrom_step5(self):
    """
    groups support
    """
    wavelanes = {
      "clk": {"wave": "p..Pp..P"},
      "Master": {
        "ctrl": {
          "write": {"wave": "01.0...."},
          "read": {"wave": "0...1..0"}
        },
        "addr":{"wave": "x3.x4..x", "data": "A1 A2"},
        "wdata":{"wave": "x3.x....", "data": "D1"}
      },
      " ":{"wave":""},
      "Slave": {
        "ctrl": {
          "ack": {"wave": "x01x0.1x"}
        },
        "rdata": {"wave": "x.....4x", "data": "Q2"}
      }
    }
    with open("./test/wavedrom_step5.svg", "w+") as fp:
      fp.write(svg.draw(wavelanes))

if __name__ == "__main__":
  unittest.main()