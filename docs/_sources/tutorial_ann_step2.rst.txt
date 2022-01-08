annotations
***********

Undulate supports more evolved annotations than edges. These are 
defined in a separated section entitled ``annotations``.

These annotations are like special bricks defined by a property
``shape`` associated to extra parameters dedicated to the given
shape.

Time compression
----------------
This one is purely stylistic, and consists in global time
compression. It is a variant of the symbol '|' spanning over
several signals. Its shape is thus ``||``.

This global time compression requires a ``x`` value to place
the annotation at the desired instant.

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_2_jsonml">jsonml</a>
        <a class="tab-button" href="#step_2_yaml">yaml</a>
        <a class="tab-button" href="#step_2_toml">toml</a>

    .. container:: tab-content
        :name: step_2_jsonml

        .. code-block:: javascript

            {
                signal: [
                    {
                        name: "pulses",
                        wave: "lhl...hl.",
                        node: ".a....b.."
                    },
                    {
                        name: "toggle",
                        wave: "l.h....l.",
                        node: "..c....d."
                    }
                ],
                annotations: [
                    {
                        shape: "||",
                        x: 5
                    }
                ]
            }
        
        .. image:: ./_images/step_2_ann.json.svg

    .. container:: tab-content
        :name: step_2_yaml

        .. code-block:: yaml

            pulses:
                wave: "lhl...hl."
                node: ".a....b.."
            toggle:
                wave: "l.h....l."
                node: "..c....d."

            annotations:
            - shape: "||"
              x: 5
              
        .. image:: ./_images/step_2_ann.yaml.svg

    .. container:: tab-content
        :name: step_2_toml

        .. code-block:: toml

            pulses.wave = "lhl...hl."
            pulses.node = ".a....b.."
            toggle.wave = "l.h....l."
            toggle.node = "..c....d."

            [[annotations]]
            shape = "||"
            x = 5
        
        .. image:: ./_images/step_2_ann.toml.svg

.. tip::

    The global time compression annotation is by default drawn
    over the complete image. However, this annotation accepts two
    other properties: ``from`` and ``to``.

    These limit to which waveforms are concerned by the time
    compression.

    For instance one can split the time compression to change the look
    and feel of the following image

    .. image:: ./_images/step_2_ann_tips_1.yaml.svg

    into the following

    .. image:: ./_images/step_2_ann_tips_2.yaml.svg

    ``from`` and ``to`` accept either a floating point number as an index of
    a signal waveform or a percentage in the format ``number %`` where the number
    is a floating point number between 0.0 and 100.0.

Horizontal Line
---------------

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_3_jsonml">jsonml</a>
        <a class="tab-button" href="#step_3_yaml">yaml</a>
        <a class="tab-button" href="#step_3_toml">toml</a>

    .. container:: tab-content
        :name: step_3_jsonml

        .. code-block:: javascript

            {
                signal: [
                    {
                        name: "pulses",
                        wave: "lhl...hl.",
                        node: ".a....b.."
                    },
                    {
                        name: "toggle",
                        wave: "l.h....l.",
                        node: "..c....d."
                    }
                ],
                annotations: [
                    {
                        shape: "-",
                        y: 0.5
                    }
                ]
            }

        .. image:: ./_images/step_3_ann.json.svg

    .. container:: tab-content
        :name: step_3_yaml

        .. code-block:: yaml

            pulses:
                wave: "lhl...hl."
                node: ".a....b.."
            toggle:
                wave: "l.h....l."
                node: "..c....d."

            annotations:
            - shape: "-"
              y: 0.5

        .. image:: ./_images/step_3_ann.yaml.svg

    .. container:: tab-content
        :name: step_3_toml

        .. code-block:: toml

            pulses.wave = "lhl...hl."
            pulses.node = ".a....b.."
            toggle.wave = "l.h....l."
            toggle.node = "..c....d."

            [[annotations]]
            shape = "-"
            y = 0.5

        .. image:: ./_images/step_3_ann.toml.svg

.. tip::

    The horizontal line annotation is by default drawn
    over the complete image. However, this annotation accepts two
    other properties: ``from`` and ``to``.

    These limit to which bricks are concerned by the horizontal line.
    ``from`` and ``to`` accept either a floating point number as an index of
    a signal brick or a percentage in the format ``number %`` where the number
    is a floating point number between 0.0 and 100.0.

Vertical Line
-------------

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_4_jsonml">jsonml</a>
        <a class="tab-button" href="#step_4_yaml">yaml</a>
        <a class="tab-button" href="#step_4_toml">toml</a>

    .. container:: tab-content
        :name: step_4_jsonml

        .. code-block:: javascript

            {
                signal: [
                    {
                        name: "pulses",
                        wave: "lhl...hl.",
                        node: ".a....b.."
                    },
                    {
                        name: "toggle",
                        wave: "l.h....l.",
                        node: "..c....d."
                    }
                ],
                annotations: [
                    {
                        shape: "|",
                        x: 7.5
                    }
                ]
            }

        .. image:: ./_images/step_4_ann.json.svg

    .. container:: tab-content
        :name: step_4_yaml

        .. code-block:: yaml

            pulses:
                wave: "lhl...hl."
                node: ".a....b.."
            toggle:
                wave: "l.h....l."
                node: "..c....d."

            annotations:
            - shape: "|"
              y: 7.5

        .. image:: ./_images/step_4_ann.yaml.svg

    .. container:: tab-content
        :name: step_4_toml

        .. code-block:: toml

            pulses.wave = "lhl...hl."
            pulses.node = ".a....b.."
            toggle.wave = "l.h....l."
            toggle.node = "..c....d."

            [[annotations]]
            shape = "|"
            y = 7.5

        .. image:: ./_images/step_4_ann.toml.svg


.. tip::

    The vertical line annotation is by default drawn
    over the complete image. However, this annotation accepts two
    other properties: ``from`` and ``to``.

    These limit to which waveforms are concerned by the vertical line.
    
    ``from`` and ``to`` accept either a floating point number as an index of
    a signal waveform or a percentage in the format ``number %`` where the number
    is a floating point number between 0.0 and 100.0.

Arrows
------

This annotation is the equivalent of Wavedrom's edges.
To represent an edge ``NODE`` ``PATTERN`` ``NODE`` ``[TEXT]``
the annotation object is represented as follows:

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_5_jsonml">jsonml</a>
        <a class="tab-button" href="#step_5_yaml">yaml</a>
        <a class="tab-button" href="#step_5_toml">toml</a>

    .. container:: tab-content
        :name: step_5_jsonml

        .. code-block:: javascript

            annotations: [
                {
                    shape: ``PATTERN``
                    from: ``NODE``
                    to: ``NODE``
                    text: ``TEXT``
                }
            ]
    
    .. container:: tab-content
        :name: step_5_yaml

        .. code-block:: yaml

            annotations:
            - shape: ``PATTERN``
              from: ``NODE``
              to: ``NODE``
              text: ``TEXT``
    
    .. container:: tab-content
        :name: step_5_toml

        .. code-block:: toml

            [[annotations]]
            shape = ``PATTERN``
            from = ``NODE``
            to = ``NODE``
            text = ``TEXT``

.. tip::

    It is possible to adjust the position of a text with the properties
    ``dx`` and ``dy``.
    They accept a floating point value.

.. tip::

    ``from`` and ``to`` accept either one of the following format:
    
    - (x, y)
    - (x %, y %)
    - node name
    - node name + (dx, dy)

    Where ``x``, ``y``, ``dx`` and ``dy`` are floating point numbers.
    In case of a percentage notation, it is a floating point number between
    0.0 and 100.0.

Text
----

It is also possible to draw only a textual annotation. This annotation object
expect a text and a position. The position is provided by a ``x`` and a ``y``
coordinate. Thus, it can be used as follows:


.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_6_jsonml">jsonml</a>
        <a class="tab-button" href="#step_6_yaml">yaml</a>
        <a class="tab-button" href="#step_6_toml">toml</a>

    .. container:: tab-content
        :name: step_6_jsonml

        .. code-block:: javascript

            annotations: [
                {
                    text: "There is no transition between these data",
                    fill: "rgba(255, 255, 0, 255)",
                    x: 8,
                    y: 4.15
                }
            ]
    
    .. container:: tab-content
        :name: step_6_yaml

        .. code-block:: yaml

            annotations:
            - text: There is no transition between these data
              fill: rgba(255, 255, 0, 255)
              x: 8
              y: 4.15
    
    .. container:: tab-content
        :name: step_6_toml

        .. code-block:: toml

            [[annotations]]
            text = There is no transition between these data
            fill = rgba(255, 255, 0, 255)
            x = 8
            y = 4.15

Stylish annotation
------------------

Fill and Strokes
~~~~~~~~~~~~~~~~

    It is possible to change the color of a line
    by specifying the property ``stroke``.
    
    For example on the vertical line

    .. container:: tabs

        .. raw:: html

            <a class="tab-button" href="#step_7_jsonml">jsonml</a>
            <a class="tab-button" href="#step_7_yaml">yaml</a>
            <a class="tab-button" href="#step_7_toml">toml</a>

        .. container:: tab-content
            :name: step_7_jsonml

            .. code-block:: javascript

                annotations: [
                    {
                        shape: "|",
                        x: 1,
                        stroke: "rgb(10, 200, 240)"
                    }
                ]

        .. container:: tab-content
            :name: step_7_yaml

            .. code-block:: yaml

                annotations:
                - shape: "|"
                x: 1
                stroke: "rgb(10, 200, 240)"
        
        .. container:: tab-content
            :name: step_7_toml

            .. code-block:: toml

                [[annotations]]
                shape = "|"
                x = 1
                stroke = "rgb(10, 200, 240)"

    
    It is also possible to change the color of filled
    arrow by specifying the property ``fill``.

    For example on an arrow

    .. container:: tabs

        .. raw:: html

            <a class="tab-button" href="#step_8_jsonml">jsonml</a>
            <a class="tab-button" href="#step_8_yaml">yaml</a>
            <a class="tab-button" href="#step_8_toml">toml</a>

        .. container:: tab-content
            :name: step_8_jsonml

            .. code-block:: javascript

                annotations: [
                    {
                        shape: "#~>",
                        from: "a",
                        to: "b",
                        fill: "#FFA500",
                        stroke: "#FFA500"
                    }
                ]
        
        .. container:: tab-content
            :name: step_8_yaml

            .. code-block:: yaml

                annotations:
                - shape: "#~>"
                  from: a
                  to: b
                  fill: "#FFA500"
                  stroke: "#FFA500"

        .. container:: tab-content
            :name: step_8_toml

            .. code-block:: toml

                [[annotations]]
                shape = "#~>"
                from = a
                to = b
                fill = "#FFA500"
                stroke = "#FFA500"

    
    The property ``fill`` and ``stroke`` are part of the css for 
    `SVG images <https://developer.mozilla.org/fr/docs/Web/SVG/Tutorial/Fills_and_Strokes>`_.
    
    However, gradient and named colors are not supported by all rendering engines.
    Gradient are not supported.
    Named color is only supported by ``undulate -f svg``

Dashes
~~~~~~

    It is possible to make the line using dashes rather than
    begin solid.

    .. container:: tabs

        .. raw:: html

            <a class="tab-button" href="#step_9_jsonml">jsonml</a>
            <a class="tab-button" href="#step_9_yaml">yaml</a>
            <a class="tab-button" href="#step_9_toml">toml</a>

        .. container:: tab-content
            :name: step_9_jsonml

            .. code-block:: javascript

                annotations: [
                    {
                        shape: "|",
                        x: "1",
                        stroke-dasharray: [1, 3]
                    }
                ]
        
        .. container:: tab-content
            :name: step_9_yaml

            .. code-block:: yaml

                annotations:
                - shape: "|"
                  x: 1
                  stroke-dasharray: [1, 3]

        .. container:: tab-content
            :name: step_9_toml

            .. code-block:: toml

                [[annotations]]
                shape = "|"
                x = 1
                stroke-dasharray = [1, 3]


    The property ``stroke-dasharray`` is part of the css for
    `SVG images <https://developer.mozilla.org/fr/docs/Web/SVG/Attribute/stroke-dasharray>`_.

Text background
~~~~~~~~~~~~~~~

By default, to enhance the visibility, textual annotations (even in arrows)
are drawn on top of a white area as a background.
However, this can hide some key element of your drawing. Thus the background
can be removed by setting the property ``text_background`` to False in 
the annotation.