periods, duty cycle, and phase
******************************

Let's suppose you have a frequency divider in your circuits. The description of its signals
can tremendously expand as the frequency ratio grows. The only variation is the ``period``.

For a pwm signal, the duty cycle will change from one cycle to another. It is somehow
convenient to tell the list of ``duty_cycles``.

And for inter-chip communication it is interresting to delay the clock with respect to the
data sent. In other term, it is the ``phase`` of the signal which need to be changed.

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_5_jsonml">jsonml</a>
        <a class="tab-button" href="#step_5_yaml">yaml</a>
        <a class="tab-button" href="#step_5_toml">toml</a>

    .. container:: tab-content
        :name: step_5_jsonml

        set the content of the file to

        .. code-block:: javascript

            {signal: [
                {name: "clk", wave: "P", repeat: 8, period: 2},
                {name: "data", wave: "x.3x=x4x5x=x5x=x", data: "RST NOP CAS INC NOP NOP NOP", phase: 0.5},
                {name: "Q", wave: "p", repeat: 8, period: 2, duty_cycles: [0.5, 0.5, 0.5, 0.25, 0.35, 0.35, 0.35, 0.35]}
            ]}
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_5_dig.json -o step_5_dig.svg
        
        .. image:: ./_images/step5_dig-json.svg

    .. container:: tab-content
        :name: step_5_yaml

        set the content of the file to

        .. code-block:: yaml

            clk:
                wave: "P"
                repeat: 8
                period: 2
            data:
                wave: "x.3x=x4x=x=x=x=x"
                data: "RST NOP CAS INC NOP NOP NOP"
                phase: 0.5
            Q:
                wave: "p"
                repeat: 8
                period: 2
                duty_cycles: [0.5, 0.5, 0.25, 0.35, 0.35, 0.35, 0.35]
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_5_dig.yaml -o step_5_dig.svg
        
        .. image:: ./_images/step5_dig-yaml.svg

    .. container:: tab-content
        :name: step_5_toml

        set the content of the file to

        .. code-block:: toml

            clk.wave   = "P"
            clk.repeat = 8
            clk.period = 2

            data.wave  = "x.3x=x4x=x=x=x=x"
            data.data  = "RST NOP CAS INC NOP NOP NOP"
            data.phase = 0.5

            Q.wave     = "p"
            Q.repeat   = 8
            Q.period   = 2
            Q.duty_cycles = [0.5, 0.5, 0.25, 0.35, 0.35, 0.35, 0.35]
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_5_dig.toml -o step_5_dig.svg
        
        .. image:: ./_images/step5_dig-toml.svg

.. tip::

    For repetitive patterns, use ``repeat`` with the number of repetition you desire.

.. tip::

    you desire to change the period from one cycle to another, use ``periods`` with 
    a list of scaling factor as done for ``duty_cycles``.

    .. code-block:: yaml

        my_signal:
            periods: [0.25, 0.5, 0.75, 1, 1.25, 1.5, 2]

.. tip::

    If you need to advance a signal rather than delaying it, use a negative value for ``phase``.

    .. code-block:: yaml

        my_signal:
            phase: -0.2 
    