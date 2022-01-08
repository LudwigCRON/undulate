edges
*****

Undulate does support the edge notation of Wavedrom.
Let's see how to declare our first annotations.

In the example below, a section ``edges`` contains a list of strings representing
the desired annotations.

For instance, the first one "a -> c" depicts an arrow from a node ``a`` to a 
node ``c``. Those nodes are defined alongside the waveform.
In the **node** attributes, the character ``.`` means don't care of the associated brick
in the **wave** attribute.
Any other character corresponds to the name given to this node.

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_1_jsonml">jsonml</a>
        <a class="tab-button" href="#step_1_yaml">yaml</a>
        <a class="tab-button" href="#step_1_toml">toml</a>

    .. container:: tab-content
        :name: step_1_jsonml

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
                edges: [
                    "a -> c",
                    "a <-> b 100 us",
                    "b ~> d"
                ]
            }
        
        .. image:: ./_images/step_1_ann.json.svg

    .. container:: tab-content
        :name: step_1_yaml

        .. code-block:: yaml
    
            pulses:
                wave: "lhl...hl."
                node: ".a....b.."
            toggle:
                wave: "l.h....h."
                node: "..c....d."
            edges:
            - "a -> c"
            - "a <-> b 100us"
            - "b ~> d"
        
        .. image:: ./_images/step_1_ann.yaml.svg

    .. container:: tab-content
        :name: step_1_toml

        .. code-block:: toml
    
            pulses.wave = "lhl...hl."
            pulses.node = ".a....b.."
            toggle.wave = "l.h....l."
            toggle.node = "..c....d."
            edges = [
                "a -> c",
                "a <-> b 100us",
                "b ~> d"
            ]
        
        .. image:: ./_images/step_1_ann.toml.svg

.. tip::

    Concerning the naming of the nodes you are limited to 1 character for a node.
    Thus in Wavedrom it is common to use other alphabet in the unicode tables
    to not limit ourselves to the 26 characters of the roman alphabet.

.. warning::

    Compared to Wavedrom, the name of the node is not displayed on the waveform.
    Most of the time, the name of the node is not of importance compared to the
    real information that our graphics shall convey, and this prevents overloading
    the drawing.

For the list of possible patterns of an edge, we can decompose an edge as
``NODE`` ``PATTERN`` ``NODE`` ``[TEXT]``.

``PATTERN`` is composed of ``MARKER`` ``MIDDLE`` ``MARKER``.

The list of available ``MARKER`` is:

- empty
- ``<`` (start arrow)
- ``>`` (end arrow)
- ``#`` (square)
- ``*`` (circle)

The list of available ``MIDDLE`` is:

- ``-`` (straight)
- ``~`` (curve)
- ``-~`` (straight then curve)
- ``~-`` (curve then straight)
- ``-|`` (horizontal then vertical)
- ``|-`` (vertical then horizontal)
- ``-|-`` (horizontal then vertical then horizontal)

.. warning::

    the markers ``#`` and ``*`` are not compatible with Wavedrom.