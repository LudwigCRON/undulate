2.4 Use cases
=============

A great power implies great responsabilities! As each characteres count there combination
could lead to an undesired effect.

To prevent any surprise, this section demonstrate several scenarii.

Glitched Clock
--------------

.. code-block:: yaml

   gated clock n:
       wave: "N0...Nl"

   gated clock p:
       wave: "P0...Pl"

.. image:: ./imgs/use-cases/glitched_clock.yaml.svg

Name with ':' in yaml
---------------------
In yaml the ':' is a delimiter which prevents you to write meaningful signal names as below.

.. error::

    the following code will fail

    .. code-block:: yaml

        bus[15:0]:
            wave: "X=...X=..."

.. tip::
    enclose the signal name by double-quotes

    .. code-block:: yaml

        "bus[15:0]":
            wave: "X=...X=..."