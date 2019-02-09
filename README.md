
[EDITOR](http://wavedrom.com/editor.html) | [TUTORIAL](http://wavedrom.com/tutorial.html)

## Introduction

**WaveDrom** is a Free and Open Source online digital timing diagram (waveform) rendering engine that uses javascript, HTML5 and SVG to convert a [WaveJSON](https://github.com/drom/wavedrom/wiki/WaveJSON) input text description into SVG vector graphics.

[WaveJSON](https://github.com/drom/wavedrom/wiki/WaveJSON) is an application of the [JSON](http://json.org/) format. The purpose of [WaveJSON](https://github.com/drom/wavedrom/wiki/WaveJSON) is to provide a compact exchange format for digital timing diagrams utilized by digital HW / IC engineers.

However, this great tool need either a headless web browser or node to generate documentations. Python being mainstream and cross-platform why not leverage its power?

This version is not a mere copy of the original one. The goals are to ensure the compatibility and to add new features. To name a few:
- long name for nodes for creating edges
- metastability wave
- analogue waveforms (step, capacitive step, slewing, arbitrary waves)

The inputs could be either json, cson, or yaml while outputs would be avg, postscript, and libreoffice draw.

## Screenshot
pywave is compatible with pydrom...

![Alt text](/test/output/wavedrom_step4.svg?sanitize=true "screenshot")

...with a slight variation on the group representation...

![Alt text](/test/output/wavedrom_step5.svg?sanitize=true "screenshot")

...aligning signal start and end when phase is used...

![Alt text](/test/output/wavedrom_step6.svg?sanitize=true "screenshot")

...can adjust the text position of edges...

![Alt text](/test/output/wavedrom_step7.svg?sanitize=true "screenshot")

...and represents analogue signals, impulses, and more...

![Alt text](/test/output/wavedrom_step10.svg?sanitize=true "screenshot")

## Architecture

### File Formats
**[WaveJSON](https://github.com/drom/wavedrom/wiki/WaveJSON)**

json-ml
```json
{ signal : [
  { name: "clk",  wave: "p......" },
  { name: "bus",  wave: "x.34.5x",   data: "head body tail" },
  { name: "wire", wave: "0.1..0." },
]}
```
json
```json
{ "signal": [
  { "name": "clk",  "wave"":" "p......" },
  { "name": "bus",  "wave"":" "x.34.5x",   "data"":" "head body tail" },
  { "name": "wire", "wave"":" "0.1..0." },
]}
```
and then notice the "signal" vanishes
yaml
```yaml
clk:
  wave: p......
bus:
  wave: x.34.5x
  data: head body tail
wire:
  wave: 0.1..0.
````

toml
```toml
clk.wave = "p......"
bus.wave = "x.34.5x"
wire.wave= "0.1..0."

bus.data = "head body tail"
```

## Standalone WaveDromEditor
Not yet

## License

See [LICENSE](https://github.com/drom/wavedrom/blob/master/LICENSE).
