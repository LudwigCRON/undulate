5. Internal Architecture
========================
[uml bloc diagram of the architecture]
[for each presente all bricks with subsection of which parameters are supported]

BRICKS
------

BRICKS as defined in `undulate/bricks.py` is an enumeration with common methods to apply on a new brick.

The Enumeration is a 1-to-1 map between the charactere in the wave representation and brick to create.

It also define the following methods

.. code-block:: python

   def transform_y(y: float, height: float = 20):
       """
       change y coordinate to represente voltage between VSSA and VDDA
       if current VSSA <-> ISSA / VDDA <-> IDDA
       """

   def from_str(s: str):
       """
       from_str return the corresponding enumeration from a char
       """

   def ignore_transition(from_symb, to_symb):
       """
       define special case when transition are skipped to prevent
       glitches by default
       """

undulate.Brick
--------------
In `undulate/generic.py`, we define the class from which inherit all other bricks.

A brick is a collection of:

- paths
- arrows
- polygons
- splines
- texts

within a given box defined by `weight` and `height` properties.

Two methods have been define to ensure continuity between symbols:

.. code-block:: python3

   def get_last_y(self):
       """
       get last position to preserve continuity
       """

   def alter_end(self, shift: float = 0, next_y: float = -1):
       """
       alter the last coordinate to preserve continuity
       """

Then a final method ensure to load the appropriate context to create a brick

.. code-block:: python3

   def generate_brick(symbol: str, **kwargs) -> dict:
       """
       define the mapping between the symbol and the brick
       """

Description
~~~~~~~~~~~

Annotations
-----------

Edges
~~~~~

Style
-----
[dev-mode only]

Renderer
--------
Renderer is base class from which inherit all rendering engine.

It defines usefull methods

It also define `svg_curve_convert(vertices: list)` method to the svg `path command <https://developer.mozilla.org/en-US/docs/Web/SVG/Tutorial/Paths>`_ into derivative rendering engine.
