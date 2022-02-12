Changelog
=========

For next release:

    - text underline or overline rendering
    - multiline text support
    - verilog stimuli rendering engine

v0.0.6:
    **New:**
      - terminal rendering engine

v0.0.5:
    **New:**
        - css file parser for global style
        - fix `#36 <https://github.com/LudwigCRON/undulate/issues/36>`_ 
        - fix `#37 <https://github.com/LudwigCRON/undulate/issues/37>`_ 
    
    **Change:**
        - architecture change to support brick plugins
        - architecture change to apply filters on wavelanes
        - complete the documentation
        - improve test coverage
        - improve parsing of annotations's from/to properties
        - change from Travis CI to Circle CI

v0.0.4:
*******
    **New:**
        - Wavedrom single node edge for text position
        - arrows, lines, ... and color overloading
        - add from/to properties to delimit global time compression
        - remove background behind text in annotations with text_background: False


    **Change:**
        - rename module from pywave to undulate
        - fix positions wrt to hscale/vscale
        - improve safety wrt to evaluation of equations
        - fix position calculation
        - fix background during signal transition
        - update documentation
        - simplify installation process

v0.0.3:
*******

    **New:**
        - travis CI
        - decomposition into pre/-/post-processing steps
        - enhanced annotations capability
        - add signal overlay
        - add empty brick with ' '
        - add "||" for global time compression annotation
        - add hline, vline and edges as annotations
        - add stroke-dasharray support
        - preparation of the documentation

    **Change:**
        - rename module into pywave
        - update license
        - fix complex Wavedrom script
        - adjust code for sphinx-module creation
        - fix python 3.5 compatibility issues
        - consider period information for node positioning
        - arrows positioning
        - fix cross groups edges

    **Removed:**
        - eps renderer in favor of cairo renderer

v0.0.2:
*******

    **New:**
        - register rendering
        - cairo renderer
        - metastability brick: m (metastable settling to 0) / M (settling to 1)
        - equation evaluation for c and s analogue bricks
        - add attr / data / position attributes for registers

    **Change:**
        - edge position inside nested groups
        - miscellaneous fix inside bricks rendering
        - improved code readability
        - improved tests and code coverage
        - digital brick area filling
        - fix eps discrepency wrt to svg renderer

v0.0.1:
*******

    **New:**
        - slewing option
        - offset dx/dy on edges labels
        - migration from javascript to python
        - abstract renderer inherited

            * svg renderer
            * eps renderer
        - comment support in json
        - analogue waveforms: a (any) / c (capacitive) / s (step with slew)
        - toml support
        - yaml support
        - black & white eps renderer

    **Change:**
        - baseline adjustment in firefox
        - group representation