Usage
=====

Undulate is command-line utility. Usage information are presented with ``-h`` argument
or ``--help`` as below:

.. code-block:: bash

    $> undulate -h
    usage: undulate [-h] [-i INPUT] [-f FORMAT] [-r] [-d DPI] [-o OUTPUT] [-s STYLE] [mangled_input]

    waveform generator from textual format

    positional arguments:
    mangled_input

    options:
    -h, --help            show this help message and exit
    -i INPUT, --input INPUT
                          path to the input text file
    -f FORMAT, --format FORMAT
                          file format of the output
    -r, --is_reg          is register description
    -d DPI, --dpi DPI     resolution of the image for png export
    -o OUTPUT, --output OUTPUT
                          path to the output file
    -s STYLE, --style STYLE
                          path to custom css file

Undulate expects at least an input file. Otherwise, the tool informs you.

.. code-block:: bash

    $> undulate
    CRITICAL: An input file shall be given

The input file of the textual description is provided by the ``-i`` or 
``--input`` arguments.

.. code-block:: bash

    $> undulate -i ./test.json
    WARNING : No output file given. Generated at ./test.png
    $> undulate --input ./test.json
    WARNING : No output file given. Generated at ./test.png

.. tip::

    For the sake of simplicity, if the default behavior of Undulate suits you
    you can simply forget the ``-i`` or ``--input``. But in that case, the input
    file shall be the last argument provided to Undulate.

    .. code-block:: bash

        $> undulate ./test.json
        WARNING : No output file given. Generated at ./test.png

By default, a PNG file is generated where undulate is called. To change the output
format, you shall provide a format with either ``-f`` or ``--format``.
To get the list of supported formats run in a terminal

.. code-block:: bash

    $> undulate -f h
    CRITICAL: This rendering engine is not yet supported
    choose one of the following:
            - cairo-png
            - cairo-pdf
            - cairo-svg
            - cairo-eps
            - svg
            - json
            - term

.. note::

    The name of the engine is named as follows: ``name of base framework``-``extension``.
    In the case there is no name of base framework, there is no dependency needed to use
    it.

    The rendering engine ``json`` displays in the terminal the internal representation
    of the read file.

    The rendering engine ``term`` displays the waveforms in the terminal.
    However, the supported list of symbol is limited to ``hHnNpPlLz01xudmM=``.

To change where is stored the generated drawing, provide the complete file path
by the ``-o`` or ``--output`` arguments. For instance, converting a file whose
path is ``~/project/doc/wavetest.yaml`` into an svg image in
``~/project/doc/wavetest.svg`` can be done with

.. code-block:: bash

    $ undulate -f svg -i ~/project/doc/wavetest.yaml -o ~/project/doc/wavetest.svg

.. tip::

    For png images, it is useful to precise the resolution of the image for 
    high-quality documentations.

    The resolution is given by ``-d`` or ``--dpi``.

    .. code-block:: bash

        $ undulate -f cairo-png -d 300 -i ~/project/doc/wavetest.yaml -o ~/project/doc/wavetest.png
