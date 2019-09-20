# Pywave

Pywave is an utility to transform textual representations of waveforms into images.
Textual representations has the benefit of being compatible with git versionning and diff tools.

*Supercalifragilisticexpialidocious thanks to the author of wavedrom, on which this project is based*

## Dependencies
By default, pywave only need:
- python3 in version greater than 3.5
- yaml
- toml

and allows to export in svg and eps (color less mode).

By adding pycairo, pywave can export in svg, eps, ps, pdf, png.

## Installation

## Usage

## Supported Syntax

[table to compare options (comments, legacy, annotations, ...)

### Json

### Jsonml

### Yaml

### Toml

## Internal Architecture

[uml bloc diagram of the architecture]
[for each presente all bricks with subsection of which parameters are supported]

### Analogue Bricks

### Digital Bricks

### Register Bricks

### Style

### BaseRenderer

## Roadmap

For the next release:
- [ ] css loader and parsing for cairo
- [ ] annotations
- [ ] edges to annotations transform
- [ ] analogue signals superposition

In long term:
- [ ] verilog sequences generation
