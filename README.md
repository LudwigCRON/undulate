
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

### HTML pages

There are three steps to insert **WaveDrom** diagrams directly into your page:

1) Put the following line into your HTML page ```<header>``` or ```<body>```:

```html
<script src="http://wavedrom.com/skins/default.js" type="text/javascript"></script>
<script src="http://wavedrom.com/wavedrom.min.js" type="text/javascript"></script>
```
or from a CDN:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/wavedrom/1.6.2/skins/default.js" type="text/javascript"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/wavedrom/1.6.2/wavedrom.min.js" type="text/javascript"></script>
```

2) Set the ``onload`` event for the HTML body.

```html
<body onload="WaveDrom.ProcessAll()">
```

3) Insert [WaveJSON](https://github.com/drom/wavedrom/wiki/WaveJSON) source inside HTML ``<body>`` wrapped with the ``<script>`` tag:

```html
<script type="WaveDrom">
{ signal : [
  { name: "clk",  wave: "p......" },
  { name: "bus",  wave: "x.34.5x",   data: "head body tail" },
  { name: "wire", wave: "0.1..0." },
]}
</script>
```

The script will find all ``<script type="WaveDrom">`` instances and insert a timing diagram at that point.


 * [jsbin](http://jsbin.com/uderuw/17)
 * [jsfiddle](http://jsfiddle.net/H7nBn/25)


### impress.js

(http://wavedrom.com/impress.html)


### Blogs & Wikis

Blogger integration: (http://wavedrom.blogspot.com/2011/08/wavedrom-digital-timing-diagram-in-your.html)

MediaWiki integration: (https://github.com/Martoni/mediawiki_wavedrom)

## Editor

[WaveDromEditor](http://wavedrom.com/editor.html)
is an online real-time editor of digital timing diagrams based on the **WaveDrom** engine and **WaveJSON** format.

## Standalone WaveDromEditor

### Windows
1. Download latest `wavedrom-editor-v1.5.0-win-{ia32|ia64}.zip` release from here: [releases](https://github.com/wavedrom/wavedrom.github.io/releases)
2. Unzip it into a working directory.
3. Run the editor: `wavedrom-editor.exe`

### Linux
1. Download the latest `wavedrom-editor-v1.6.2-linux-{ia32|x64}.tar.gz` release from here: [releases](https://github.com/wavedrom/wavedrom.github.io/releases)
2. unzip-untar the package: `tar -xvzf wavedrom-editor-v1.6.2-linux-x64.tar.gz`
3. Run the editor: `./WaveDromEditor/linux64/wavedrom-editor`

## OS X
1. Download the latest `wavedrom-editor-v1.6.2-osx-x64.zip` release:
2. Unzip
3. Run

## Community

Please use the [WaveDrom user group](http://groups.google.com/group/wavedrom) for discussions, questions, ideas, or whatever.

## Contributing

[Contributing](./.github/CONTRIBUTING.md)

## License

See [LICENSE](https://github.com/drom/wavedrom/blob/master/LICENSE).
