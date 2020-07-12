List of bricks
==============

A brick is a collection of:

    - paths
    - arrows
    - polygons
    - splines
    - texts

A brick is thus a combination of drawing element generate a unit symbol in a given context.
Until now, only three context are existing: **Analogue**, **Digital**, and **Register**.

Analogue Bricks
---------------
This section present the available bricks inside the analogue context.

List of bricks
~~~~~~~~~~~~~~
.. |brick-ana-a| image:: ./imgs/bricks/brick_a.yaml.svg
.. |brick-ana-c| image:: ./imgs/bricks/brick_c.yaml.svg
.. |brick-ana-m| image:: ./imgs/bricks/brick_m.yaml.svg
.. |brick-ana-M| image:: ./imgs/bricks/brick_m1.yaml.svg
.. |brick-ana-s| image:: ./imgs/bricks/brick_s.yaml.svg

+--------+------------+----------------------+---------------+
| Symbol |    Class   | Parameters Supported |     Image     |
+========+============+======================+===============+
|    a   |   Analogue |                      | |brick-ana-a| |
+--------+------------+----------------------+---------------+
|    c   | Capacitive |                      | |brick-ana-c| |
+--------+------------+----------------------+---------------+
|    m   | Metastable |                      | |brick-ana-m| |
+--------+------------+----------------------+---------------+
|    M   | Metastable |                      | |brick-ana-M| |
+--------+------------+----------------------+---------------+
|    s   |       Step |                      | |brick-ana-s| |
+--------+------------+----------------------+---------------+

Description
~~~~~~~~~~~
Analogue signal representations are defined in the ``analogue.py``. An analogue signal
being able to go through a multitude of "levels" (voltage,current,charges...), basic
assumptions have been considered.

All signals are considered to be a voltage with a Maximum excursion in
:math:`[V_{SSA};V_{DDA}]` range. For the sake of clarity, x-y coordinates are respectively the
time and the voltage.

A brick is defined as single expression. To simplify the expression, an analogue context
is loaded. This context include the extremum voltage, usual functions, and pi constant.

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


This behaviour corresponds to the `Analogue brick <#List\ of\ bricks>`_ whose symbol is **a**.

Other analogue bricks are an *Analogue brick* with a predefined expression.

Digital Bricks
--------------
This section present the available bricks inside the digital context.

List of bricks
~~~~~~~~~~~~~~

.. |brick-dig-n| image:: ./imgs/bricks/brick_n.yaml.svg
.. |brick-dig-N| image:: ./imgs/bricks/brick_nmaj.yaml.svg
.. |brick-dig-p| image:: ./imgs/bricks/brick_p.yaml.svg
.. |brick-dig-P| image:: ./imgs/bricks/brick_pmaj.yaml.svg
.. |brick-dig-l| image:: ./imgs/bricks/brick_l.yaml.svg
.. |brick-dig-L| image:: ./imgs/bricks/brick_lmaj.yaml.svg
.. |brick-dig-h| image:: ./imgs/bricks/brick_h.yaml.svg
.. |brick-dig-H| image:: ./imgs/bricks/brick_hmaj.yaml.svg
.. |brick-dig-0| image:: ./imgs/bricks/brick_0.yaml.svg
.. |brick-dig-1| image:: ./imgs/bricks/brick_1.yaml.svg
.. |brick-dig-g| image:: ./imgs/bricks/brick_gap.yaml.svg
.. |brick-dig-z| image:: ./imgs/bricks/brick_z.yaml.svg
.. |brick-dig-x| image:: ./imgs/bricks/brick_x.yaml.svg
.. |brick-dig-=| image:: ./imgs/bricks/brick_data.yaml.svg
.. |brick-dig-u| image:: ./imgs/bricks/brick_u.yaml.svg
.. |brick-dig-d| image:: ./imgs/bricks/brick_d.yaml.svg
.. |brick-dig-i| image:: ./imgs/bricks/brick_i.yaml.svg
.. |brick-dig-I| image:: ./imgs/bricks/brick_imaj.yaml.svg

+--------+------------+----------------------+-----------------+
| Symbol |    Class   | Parameters Supported |      Image      |
+========+============+======================+=================+
|    n   |       Nclk |                      |  |brick-dig-n|  |
+--------+------------+----------------------+-----------------+
|    N   |       Nclk |                      |  |brick-dig-N|  |
+--------+------------+----------------------+-----------------+
|    p   |       Pclk |                      |  |brick-dig-p|  |
+--------+------------+----------------------+-----------------+
|    P   |       Pclk |                      |  |brick-dig-P|  |
+--------+------------+----------------------+-----------------+
|    l   |        Low |                      |  |brick-dig-l|  |
+--------+------------+----------------------+-----------------+
|    L   |        Low |                      |  |brick-dig-L|  |
+--------+------------+----------------------+-----------------+
|    h   |       High |                      |  |brick-dig-h|  |
+--------+------------+----------------------+-----------------+
|    H   |       High |                      |  |brick-dig-H|  |
+--------+------------+----------------------+-----------------+
|    0   |       Zero |                      |  |brick-dig-0|  |
+--------+------------+----------------------+-----------------+
|    1   |        One |                      |  |brick-dig-1|  |
+--------+------------+----------------------+-----------------+
|   \|   |        Gap |                      |  |brick-dig-g|  |
+--------+------------+----------------------+-----------------+
|    z   |      HighZ |                      |  |brick-dig-z|  |
+--------+------------+----------------------+-----------------+
|    x   |       Data |                      |  |brick-dig-x|  |
+--------+------------+----------------------+-----------------+
|    =   |       Data |                      |  |brick-dig-=|  |
+--------+------------+----------------------+-----------------+
|    u   |         Up |                      |  |brick-dig-u|  |
+--------+------------+----------------------+-----------------+
|    d   |       Down |                      |  |brick-dig-d|  |
+--------+------------+----------------------+-----------------+
|    i   |    Impulse |                      |  |brick-dig-i|  |
+--------+------------+----------------------+-----------------+
|    I   |    Impulse |                      |  |brick-dig-I|  |
+--------+------------+----------------------+-----------------+


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

.. |brick-reg-start| image:: ./imgs/bricks/field_start.yaml.svg
.. |brick-reg-end|   image:: ./imgs/bricks/field_end.yaml.svg
.. |brick-reg-mid|   image:: ./imgs/bricks/field_mid.yaml.svg
.. |brick-reg-bit|   image:: ./imgs/bricks/field_bit.yaml.svg

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
