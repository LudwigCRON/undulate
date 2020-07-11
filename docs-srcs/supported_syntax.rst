2.2 Supported Syntax
====================

Undulate selects the syntax based on the extension of the file
(at the exception of Json/Jsonml). However, each file has some specificities.

+-------------+------+--------+------+------+
|             | Json | Jsonml | Yaml | Toml |
+=============+======+========+======+======+
| legacy      |  Yes | Yes    | No   |  No  |
+-------------+------+--------+------+------+
| comments    |  No  | Yes    | Yes  |  Yes |
+-------------+------+--------+------+------+
| annotations |  Yes | Yes    | Yes  |  Yes |
+-------------+------+--------+------+------+

In order to let you choose the most appropriate format for you, examples are posted below:

Json
----

.. code-block:: json

    { "signal": [
            { "name": "clk",  "wave": "p......" },
            { "name": "bus",  "wave": "x.34.5x",   "data": "head body tail" },
            { "name": "wire", "wave": "0.1..0." },
    ]}

Jsonml
------
in json-ml for strict compatibility with Wavedrom

.. code-block:: c

    { signal : [
        // clock signal
        { name: "clk",  wave: "p......" },
        // bus data
        { name: "bus",  wave: "x.34.5x",   data: "head body tail" },
        // request signal
        { name: "wire", wave: "0.1..0." }
    ]}

Yaml
----

.. code-block:: yaml

    clk:
        wave: p......
    bus:
        wave: x.34.5x
        data: head body tail
    wire:
        wave: 0.1..0.

Toml
----

.. code-block:: toml

    clk.wave = "p......"
    bus.wave = "x.34.5x"
    wire.wave= "0.1..0."

    bus.data = "head body tail"

.. note::

    Notice the group "signal" vanishes in yaml and toml syntax.
    Wavedrom used a primary group telling if this is a waveforms of signals,
    or registers, or logic.

    However, this increase the indentation level,
    and is prone to error in yaml file format.

    In toml file format, it increase the notation length as
    ``signal.<name of my signal>.wave``, or using ``[signal]`` section
    without adding any advantages.
