Supported Syntax
================

Undulate selects the syntax based on the extension of the file. However, each 
file has some specificities. Wavedrom only support json and jsonml file formats.
In those formats, only a restricted set of annotations is supported to be
compatible with Wavedrom ("edges" section). Extra annotations can be added in an
"annotations" section but will be only processed by Undulate. 

+------------------------+------+--------+------+------+
|                        | Json | Jsonml | Yaml | Toml |
+========================+======+========+======+======+
| supported in wavedrom  | Yes  | Yes    | No   |  No  |
+------------------------+------+--------+------+------+
| support extra comments | No   | Yes    | Yes  |  Yes |
+------------------------+------+--------+------+------+
| support annotations    | Yes* | Yes*   | Yes  |  Yes |
+------------------------+------+--------+------+------+

In order to let you choose the most appropriate format for you,
an example of the same plot in the different supported file format is posted below:

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#ff_jsonml">json/jsonml</a>
        <a class="tab-button" href="#ff_yaml">yaml</a>
        <a class="tab-button" href="#ff_toml">toml</a>

    .. container:: tab-content
        :name: ff_json

        .. code-block:: json

            { "signal": [
                    { "name": "clk",  "wave": "p......" },
                    { "name": "bus",  "wave": "x.34.5x",   "data": "head body tail" },
                    { "name": "wire", "wave": "0.1..0." },
            ]}

        In this jsonml format, it is possible to add comments.

        .. code-block:: c

            { signal : [
                // clock signal
                { name: "clk",  wave: "p......" },
                // bus data
                { name: "bus",  wave: "x.34.5x",   data: "head body tail" },
                // request signal
                { name: "wire", wave: "0.1..0." }
            ]}

    .. container:: tab-content
        :name: ff_yaml

        .. code-block:: yaml

            clk:
                wave: p......
            bus:
                wave: x.34.5x
                data: head body tail
            wire:
                wave: 0.1..0.

    .. container:: tab-content
        :name: ff_toml

        .. code-block:: toml

            clk.wave = "p......"
            bus.wave = "x.34.5x"
            wire.wave= "0.1..0."

            bus.data = "head body tail"

.. warning::

    Notice the group "signal" vanishes in yaml and toml syntax.
    Wavedrom used a primary group to discriminate if this file contains signals,
    , registers, or logic.

    However, this increase the indentation level, and is prone to error in 
    yaml file format.

    In toml file format, it increase the notation length as
    ``signal.<name of my signal>.wave``, or using ``[signal]`` section
    without adding any advantages.

.. include:: ./_static/update_tabs.rst