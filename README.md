
# Undulate
![](https://img.shields.io/badge/license-MIT-blue)
![](https://img.shields.io/badge/python-3.8+-blue)
![](https://64-166642218-gh.circle-artifacts.com/0/tests/outputs/cov_badge.svg)
[![CircleCI](https://circleci.com/gh/LudwigCRON/undulate/tree/master.svg?style=shield)](https://circleci.com/gh/LudwigCRON/undulate/tree/master)<br/>

## Introduction

**WaveDrom** is a Free and Open Source online digital
timing diagram (waveform) rendering engine that uses javascript,
HTML5 and SVG to convert a
[WaveJSON](https://github.com/drom/wavedrom/wiki/WaveJSON)
input text description into SVG vector graphics.

[WaveJSON](https://github.com/drom/wavedrom/wiki/WaveJSON) is an
application of the [JSON](http://json.org/) format. The purpose of
[WaveJSON](https://github.com/drom/wavedrom/wiki/WaveJSON) 
is to provide a compact exchange format for digital timing
diagrams utilized by digital HW / IC engineers.

However, this great tool need either a headless web browser
or node.js to generate documentations. Python being mainstream
and cross-platform why not leverage its power?

This version is not a mere copy of the original one. The goals
are to ensure the compatibility and to add new features. To
name a few:
- long name for nodes for creating edges from one specific point to another
- metastability wave
- analogue waveforms (step, capacitive step, slewing, arbitrary waves, overlay up to 4 waves)
- add annotations (global time compression, vertical/horizontal lines)
- style overloading (font-size, fill color, stroke color, stroke-width, stroke-dasharray, ...)

The inputs could be either:
- json
- WaveJSON (cson)
- yaml
- toml 

while outputs would be:
- svg _for web pages_
- postscript _for latex documentation_
- pdf _for pdflatex documentation_
- png _for word, libreoffice, ..._

## Documentation
The complete documentation is available [here](https://ludwigcron.github.io/undulate/)

## License

See [LICENSE](https://github.com/drom/wavedrom/blob/master/LICENSE).

## Installation
It is recommended to create a python environment to not pollute the python of your operating
system.

> :interrobang: some OS relies on specific version of python 
> packages. One use a workflow with specific tools. To not break
> this vital components, the environment boxes in a specific 
> location packages and dependencies.<br/>
> Tools: [pyenv](https://github.com/pyenv/pyenv-virtualenv)
> [virtualenv](https://pypi.org/project/virtualenv/)
> [lmod](https://lmod.readthedocs.io/en/latest/)

If it's intended, or you do it on purpose, you can skip directly to step #3.

**1. create a new environment**

With pyenv:
``` bash
pyenv virtualenv <name-of-the-environment>
```

with virtualenv package:
```bash
python3 -m venv <path where to store the environments>
```

**2. Activate the newly created environment**

With pyenv:
```bash
pyenv activate <name-of-the-environment>
```

with virtualenv package:
```bash
source <path where to store the environments>/bin/activate
```

**3. Finally, install it**

```bash
python3 -m pip install git+https://github.com/LudwigCRON/undulate.git
```

**4. Use it!**

From now on, in the environment, you can call the script directly wherever you are
```bash
cd ${HOME}/projects/my-fancy-thing/documents/
undulate -f cairo-png --dpi 300 -i input.yaml -o output.png
```

To deactivate your environment call in the terminal
```bash
deactivate
```
