4. Supported Syntax
===================
[table to compare options (comments, legacy, annotations, ...)

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


> *notice the "signal" vanishes in yaml*

Toml
----

.. code-block:: toml

   clk.wave = "p......"
   bus.wave = "x.34.5x"
   wire.wave= "0.1..0."

   bus.data = "head body tail"

> *notice the "signal" vanishes in toml*
