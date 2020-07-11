2.1 Usage
==========

Undulate is command-line utility. By default, without any arguments, usage information
is presented as below:

.. code-block:: bash

    $ undulate
    ERROR: None is not found
    usage: undulate [-h] [-i INPUT] [-f FORMAT] [-r] [-d DPI] [-o OUTPUT]

    waveform generator from textual format

    optional arguments:
    -h, --help            show this help message and exit
    -i INPUT, --input INPUT
                            path to the input text file
    -f FORMAT, --format FORMAT
                            file format of the output
    -r, --is_reg          is register description
    -d DPI, --dpi DPI     resolution of the image for png export
    -o OUTPUT, --output OUTPUT
                            path to the output file

It expect at least:

- an input file,
- the format of the output, 
- and the output path of generated file.

The input file of the textual description is provided by the ``-i`` or ``--input``.
The format of the output is given by the ``-f`` or ``--format``.
The supported format is:

- svg
- cairo-svg
- cairo-ps
- cairo-eps
- cairo-pdf
- cairo-png
- json

The output path of the generated file is provided by the ``-o`` or ``--output``:

For instance, converting a file whose path is ``~/project/doc/wavetest.yaml`` into an svg
image in ``~/project/doc/wavetest.svg`` can be done with

.. code-block:: bash

    $ undulate -f svg -i ~/project/doc/wavetest.yaml -o ~/project/doc/wavetest.svg

.. tip::

    For png images, it is useful to precise the resolution of the image for 
    high-quality documentations.

    The resolution is given by ``-d`` or ``--dpi``.

    .. code-block:: bash

        $ undulate -f cairo-png -d 300 -i ~/project/doc/wavetest.yaml -o ~/project/doc/wavetest.png
