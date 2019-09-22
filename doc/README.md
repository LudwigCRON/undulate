# Pywave

Pywave is an utility to transform textual representations of waveforms into images.
Textual representations has the benefit of being compatible with git versionning and diff tools.

> Thanks to the supercalifragilisticexpialidocious work and though of the wavedrom's author, on which this project is based

## Dependencies
By default, pywave only need:
- python3 in version greater than 3.5
- pyyaml
- toml

and allows to export in svg and eps (color less mode).

By adding pycairo, pywave can export in svg, eps, ps, pdf, png.

## Installation

## Usage

## Supported Syntax

[table to compare options (comments, legacy, annotations, ...)

### Json
```json
{ "signal": [
  { "name": "clk",  "wave": "p......" },
  { "name": "bus",  "wave": "x.34.5x",   "data": "head body tail" },
  { "name": "wire", "wave": "0.1..0." },
]}
```

### Jsonml
in json-ml for strict compatibility with Wavedrom
```json
{ signal : [
  // clock signal
  { name: "clk",  wave: "p......" },
  // bus data
  { name: "bus",  wave: "x.34.5x",   data: "head body tail" },
  // request signal
  { name: "wire", wave: "0.1..0." },
]}
```

### Yaml
```yaml
clk:
  wave: p......
bus:
  wave: x.34.5x
  data: head body tail
wire:
  wave: 0.1..0.
```

> *notice the "signal" vanishes in yaml*

### Toml
```toml
clk.wave = "p......"
bus.wave = "x.34.5x"
wire.wave= "0.1..0."

bus.data = "head body tail"
```

> *notice the "signal" vanishes in toml*

## Internal Architecture

[uml bloc diagram of the architecture]
[for each presente all bricks with subsection of which parameters are supported]

### pywave.Brick

### Analogue Bricks

#### List of bricks

| Symbol |    Class   | Parameters Supported |           Image            |
|--------|------------|----------------------|----------------------------|
|    a   |   Analogue |                      | ![a](./imgs/bricks/brick_a.yaml.svg) |
|    c   | Capacitive |                      | ![c](./imgs/bricks/brick_c.yaml.svg) |
|    m   | Metastable |                      | ![m](./imgs/bricks/brick_m.yaml.svg) |
|    M   | Metastable |                      | ![M](./imgs/bricks/brick_m1.yaml.svg) |
|    s   |       Step |                      | ![s](./imgs/bricks/brick_s.yaml.svg) |

#### Description

Analogue signal representations are defined in the ```analogue.py```. An analogue signal being able to go through a multitude of "levels" (voltage,current,charges...), basic assumptions have been considered.

All signals are considered to be a voltage with a Maximum excursion in $[V_{SSA}-V_{DDA}]$ range. For the sake of clarity, x-y coordinates are respectively the time and the voltage.

A brick is defined as single expression. To simplify the expression, an analogue context is loaded. This context include the extremum voltage, usual functions, and pi constant.

To be more precise, the context is given below.

```python {.line-numbers}
CONTEXT = {
    "time": [],
    "Tmax": 20,
    "VSSA": 0,
    "VDDA": 1.8,
    "atan2": math.atan2,
    "pi": math.pi,
    "exp": math.exp,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "tanh": math.tanh,
    "sqrt": math.sqrt,
    "rnd": random.random,
}
```

This behaviour corresponds to the *[Analogue](#List\ of\ bricks)* brick whose symbol is **a**.

Other analogue bricks are an *Analogue brick* with a predefined expression.

### Digital Bricks

#### List of bricks

| Symbol |    Class   | Parameters Supported |                  Image                  |
|--------|------------|----------------------|-----------------------------------------|
|    n   |       Nclk |                      | ![n](./imgs/bricks/brick_n.yaml.svg)    |
|    N   |       Nclk |                      | ![N](./imgs/bricks/brick_nmaj.yaml.svg) |
|    p   |       Pclk |                      | ![p](./imgs/bricks/brick_p.yaml.svg)    |
|    P   |       Pclk |                      | ![P](./imgs/bricks/brick_pmaj.yaml.svg) |
|    l   |        Low |                      | ![l](./imgs/bricks/brick_l.yaml.svg)    |
|    L   |        Low |                      | ![L](./imgs/bricks/brick_lmaj.yaml.svg) |
|    h   |       High |                      | ![h](./imgs/bricks/brick_h.yaml.svg)    |
|    H   |       High |                      | ![H](./imgs/bricks/brick_hmaj.yaml.svg) |
|    0   |       Zero |                      | ![0](./imgs/bricks/brick_0.yaml.svg)    |
|    1   |        One |                      | ![1](./imgs/bricks/brick_1.yaml.svg)    |
|   \|   |        Gap |                      | ![\|](./imgs/bricks/brick_gap.yaml.svg) |
|    z   |      HighZ |                      | ![z](./imgs/bricks/brick_z.yaml.svg)    |
|    x   |       Data |                      | ![x](./imgs/bricks/brick_x.yaml.svg)    |
|    =   |       Data |                      | ![=](./imgs/bricks/brick_data.yaml.svg) |
|    u   |         Up |                      | ![u](./imgs/bricks/brick_u.yaml.svg)    |
|    d   |       Down |                      | ![d](./imgs/bricks/brick_d.yaml.svg)    |
|    i   |    Impulse |                      | ![i](./imgs/bricks/brick_i.yaml.svg)    |
|    I   |    Impulse |                      | ![i](./imgs/bricks/brick_imaj.yaml.svg) |

### Register Bricks

[explain it is assumed that register description is not mixed with signal description]

#### List of bricks
> *For the sake of completeness, the list of bricks are given in this section. However, the end-user do not have to deal with them*

| Symbol |    Class   | Parameters Supported |                  Image                  |
|--------|------------|----------------------|-----------------------------------------|
|    [   | FieldStart |                      | ![n](./imgs/bricks/field_start.yaml.svg)|
|    ]   |   FieldEnd |                      | ![n](./imgs/bricks/field_end.yaml.svg)  |
|    :   |   FieldMid |                      | ![n](./imgs/bricks/field_mid.yaml.svg)  |
|    b   |   FieldBit |                      | ![n](./imgs/bricks/field_bit.yaml.svg)    |

### Style

### BaseRenderer

## Roadmap

For the next release:
- [ ] css loader and parsing for cairo
- [ ] annotations
- [ ] edges to annotations transform
- [ ] analogue signals superposition
- [ ] analogue context personalization

In long term:
- [ ] verilog sequences generation

## Use cases

A great power implies great responsabilities! As each characteres count there combination could lead to an undesired effect.

To avoid an surprise, this section demonstrate several scenarii.

### Glitched Clock
```yaml
gated clock n:
    wave: "N0...Nl"

gated clock p:
    wave: "P0...Pl"
```

![glitched clock](./imgs/use-cases/glitched_clock.yaml.svg)