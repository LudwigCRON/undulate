List of Bricks
==============

A brick is a collection of drawing element associated to a symbol. For the sake,
of clarity these have been collected in three different contexts:

- Analogue
- Digital
- Register

Analogue Bricks
---------------
This section present the available bricks inside the analogue context.

List of bricks
~~~~~~~~~~~~~~
.. |brick-ana-a| image:: ./_images/bricks/brick_a.yaml.svg
.. |brick-ana-c| image:: ./_images/bricks/brick_c.yaml.svg
.. |brick-ana-m| image:: ./_images/bricks/brick_m.yaml.svg
.. |brick-ana-M| image:: ./_images/bricks/brick_m1.yaml.svg
.. |brick-ana-s| image:: ./_images/bricks/brick_s.yaml.svg

+--------+------------+----------------------+---------------+
| Symbol |    Class   | Parameters Supported |     Image     |
+========+============+======================+===============+
|    a   |   Analogue | analogue             | |brick-ana-a| |
+--------+------------+----------------------+---------------+
|    c   | Capacitive | slewing, analogue    | |brick-ana-c| |
+--------+------------+----------------------+---------------+
|    m   | Metastable | slewing              | |brick-ana-m| |
+--------+------------+----------------------+---------------+
|    M   | Metastable | slewing              | |brick-ana-M| |
+--------+------------+----------------------+---------------+
|    s   |       Step | slewing, analogue    | |brick-ana-s| |
+--------+------------+----------------------+---------------+

Description
~~~~~~~~~~~
An analogue signal being able to go through a multitude of "levels"
(voltage,current,charges...), basic assumptions have been considered:

- All signals are considered to be a voltagein :math:`[V_{SSA};V_{DDA}]` range.

    Even if it is a current or a charge, for the sake
    of representation a voltage range is equivalent and sufficient.

- A brick is defined with a single expression.

    To simplify the expression, an analogue context is loaded. This context 
    include the extremum voltage, usual functions, and pi constant.

    To be more precise, the context is given below.

    .. code-block:: python3

        CONTEXT = {
            "time": [],
            "Tmax": 20,
            "VSSA": 0,
            "VDDA": 1.8,
            "atan2": math.atan2,
            "pi": math.pi,
            "exp": math.exp,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "tanh": math.tanh,
            "sqrt": math.sqrt,
            "rnd": random.random,
        }

- the expression should return a list of (time, voltage) points fitting
  inside the size of the renderered brick. Thus the value of time and
  voltage should be scaled with respect to ``Tmax`` and ``VDDA``/``VSSA``.

The last point corresponds to only the `Analogue brick <#List\ of\ bricks>`_
whose symbol is **a**. For the **c** and **s**, only the final value can be
defined. For other analogue bricks, they are an *Analogue brick* with a 
predefined expression.

Digital Bricks
--------------
This section present the available bricks inside the digital context.

List of bricks
~~~~~~~~~~~~~~

.. |brick-dig-n| image:: ./_images/bricks/brick_n.yaml.svg
.. |brick-dig-N| image:: ./_images/bricks/brick_nmaj.yaml.svg
.. |brick-dig-p| image:: ./_images/bricks/brick_p.yaml.svg
.. |brick-dig-P| image:: ./_images/bricks/brick_pmaj.yaml.svg
.. |brick-dig-l| image:: ./_images/bricks/brick_l.yaml.svg
.. |brick-dig-L| image:: ./_images/bricks/brick_lmaj.yaml.svg
.. |brick-dig-h| image:: ./_images/bricks/brick_h.yaml.svg
.. |brick-dig-H| image:: ./_images/bricks/brick_hmaj.yaml.svg
.. |brick-dig-0| image:: ./_images/bricks/brick_0.yaml.svg
.. |brick-dig-1| image:: ./_images/bricks/brick_1.yaml.svg
.. |brick-dig-g| image:: ./_images/bricks/brick_gap.yaml.svg
.. |brick-dig-z| image:: ./_images/bricks/brick_z.yaml.svg
.. |brick-dig-x| image:: ./_images/bricks/brick_x.yaml.svg
.. |brick-dig-=| image:: ./_images/bricks/brick_data.yaml.svg
.. |brick-dig-2| image:: ./_images/bricks/brick_data2.yaml.svg
.. |brick-dig-3| image:: ./_images/bricks/brick_data3.yaml.svg
.. |brick-dig-4| image:: ./_images/bricks/brick_data4.yaml.svg
.. |brick-dig-5| image:: ./_images/bricks/brick_data5.yaml.svg
.. |brick-dig-6| image:: ./_images/bricks/brick_data6.yaml.svg
.. |brick-dig-7| image:: ./_images/bricks/brick_data7.yaml.svg
.. |brick-dig-8| image:: ./_images/bricks/brick_data8.yaml.svg
.. |brick-dig-9| image:: ./_images/bricks/brick_data9.yaml.svg
.. |brick-dig-u| image:: ./_images/bricks/brick_u.yaml.svg
.. |brick-dig-d| image:: ./_images/bricks/brick_d.yaml.svg
.. |brick-dig-i| image:: ./_images/bricks/brick_i.yaml.svg
.. |brick-dig-I| image:: ./_images/bricks/brick_imaj.yaml.svg

+--------+------------+----------------------------+-----------------+
| Symbol |    Class   | Parameters Supported       |      Image      |
+========+============+============================+=================+
|    n   |       Nclk | slewing, duty_cyle, period |  |brick-dig-n|  |
+--------+------------+----------------------------+-----------------+
|    N   |  NclkArrow | slewing, duty_cyle, period |  |brick-dig-N|  |
+--------+------------+----------------------------+-----------------+
|    p   |       Pclk | slewing, duty_cyle, period |  |brick-dig-p|  |
+--------+------------+----------------------------+-----------------+
|    P   |  PclkArrow | slewing, duty_cyle, period |  |brick-dig-P|  |
+--------+------------+----------------------------+-----------------+
|    l   |        Low | slewing, period            |  |brick-dig-l|  |
+--------+------------+----------------------------+-----------------+
|    L   |   LowArrow | slewing, period            |  |brick-dig-L|  |
+--------+------------+----------------------------+-----------------+
|    h   |       High | slewing, period            |  |brick-dig-h|  |
+--------+------------+----------------------------+-----------------+
|    H   |  HighArrow | slewing, period            |  |brick-dig-H|  |
+--------+------------+----------------------------+-----------------+
|    0   |       Zero | slewing, period            |  |brick-dig-0|  |
+--------+------------+----------------------------+-----------------+
|    1   |        One | slewing, period            |  |brick-dig-1|  |
+--------+------------+----------------------------+-----------------+
|    z   |      HighZ | period                     |  |brick-dig-z|  |
+--------+------------+----------------------------+-----------------+
|    x   |       Data | slewing, period            |  |brick-dig-x|  |
+--------+------------+----------------------------+-----------------+
|    =   |       Data | slewing, period, data      |  |brick-dig-=|  |
+--------+------------+----------------------------+-----------------+
|    2   |       Data | slewing, period, data      |  |brick-dig-2|  |
+--------+------------+----------------------------+-----------------+
|    3   |       Data | slewing, period, data      |  |brick-dig-3|  |
+--------+------------+----------------------------+-----------------+
|    4   |       Data | slewing, period, data      |  |brick-dig-4|  |
+--------+------------+----------------------------+-----------------+
|    5   |       Data | slewing, period, data      |  |brick-dig-5|  |
+--------+------------+----------------------------+-----------------+
|    6   |       Data | slewing, period, data      |  |brick-dig-6|  |
+--------+------------+----------------------------+-----------------+
|    7   |       Data | slewing, period, data      |  |brick-dig-7|  |
+--------+------------+----------------------------+-----------------+
|    8   |       Data | slewing, period, data      |  |brick-dig-8|  |
+--------+------------+----------------------------+-----------------+
|    9   |       Data | slewing, period, data      |  |brick-dig-9|  |
+--------+------------+----------------------------+-----------------+
|   \|   |        Gap | period                     |  |brick-dig-g|  |
+--------+------------+----------------------------+-----------------+
|    u   |         Up | slewing, period            |  |brick-dig-u|  |
+--------+------------+----------------------------+-----------------+
|    d   |       Down | slewing, period            |  |brick-dig-d|  |
+--------+------------+----------------------------+-----------------+
|    i   |    Impulse | duty_cyle, period          |  |brick-dig-i|  |
+--------+------------+----------------------------+-----------------+
|    I   |    Impulse | duty_cyle, period          |  |brick-dig-I|  |
+--------+------------+----------------------------+-----------------+

Description
~~~~~~~~~~~

Register Bricks
---------------

This section present the available bricks inside the register context.

It is assummed that register description and signals description do not serve the same purpose.
Therefore, register description shall not be mixed with signal description.

Dedicated methods are applied to transform a human textual representation of register into
a waveform for rendering engines.

List of bricks
~~~~~~~~~~~~~~

.. note::

    For the sake of completeness, the list of bricks are given in this section.
    However, the end-user do not have to deal with them

.. |brick-reg-start| image:: ./_images/bricks/field_start.yaml.svg
.. |brick-reg-end|   image:: ./_images/bricks/field_end.yaml.svg
.. |brick-reg-mid|   image:: ./_images/bricks/field_mid.yaml.svg
.. |brick-reg-bit|   image:: ./_images/bricks/field_bit.yaml.svg

+--------+------------+----------------------+-------------------+
| Symbol |    Class   | Parameters Supported |       Image       |
+========+============+======================+===================+
|    [   | FieldStart |                      | |brick-reg-start| |
+--------+------------+----------------------+-------------------+
|    ]   |   FieldEnd |                      | |brick-reg-end|   |
+--------+------------+----------------------+-------------------+
|    :   |   FieldMid |                      | |brick-reg-mid|   |
+--------+------------+----------------------+-------------------+
|    b   |   FieldBit |                      | |brick-reg-bit|   |
+--------+------------+----------------------+-------------------+
