clocks
******

However, most digital design are synchronous. The reference being a clock let's see
how to define a clock.

At first a clock is normal digital signal with specific bricks for rising edge clocks or
falling edge clocks.

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_2_jsonml">jsonml</a>
        <a class="tab-button" href="#step_2_yaml">yaml</a>
        <a class="tab-button" href="#step_2_toml">toml</a>

    .. container:: tab-content
        :name: step_2_jsonml

        set the content of the file to

        .. code-block:: javascript

            {signal: [
                {name: "pclk", wave: "p........"},
                {name: "Pclk", wave: "P........"},
                {name: "nclk", wave: "n........"},
                {name: "Nclk", wave: "N........"},
                {},
                {name: 'clk0', wave: 'phnlPHNL' },
                {name: 'clk1', wave: 'xhlhLHl.' },
                {name: 'clk2', wave: 'hpHplnLn' },
                {name: 'clk3', wave: 'nhNhplPl' },
                {name: 'clk4', wave: 'xlh.L.Hx' },
            ]}
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_2_dig.json -o step_2_dig.svg
        
        .. image:: ./_images/step2_dig-json.svg

    .. container:: tab-content
        :name: step_2_yaml

        set the content of the file to

        .. code-block:: yaml

            pclk:
                wave: "p......."
            Pclk:
                wave: "P......."
            nclk:
                wave: "n......."
            Nclk:
                wave: "N......."
            spacer:
                wave: ""
            clk0:
                wave: "phnlPHNL"
            clk1:
                wave: "xhlhLHl."
            clk2:
                wave: "hpHplnLn"
            clk3:
                wave: "nhNhplPl"
            clk4:
                wave: "xlh.L.Hx"
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_2_dig.yaml -o step_2_dig.svg
        
        .. image:: ./_images/step2_dig-yaml.svg

    .. container:: tab-content
        :name: step_2_toml

        set the content of the file to

        .. code-block:: toml

            pclk.wave   = "p......."
            Pclk.wave   = "P......."
            nclk.wave   = "n......."
            Nclk.wave   = "N......."
            spacer.wave = ""
            clk0.wave   = "phnlPHNL"
            clk1.wave   = "xhlhLHl."
            clk2.wave   = "hpHplnLn"
            clk3.wave   = "nhNhplPl"
            clk4.wave   = "xlh.L.Hx"
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_2_dig.toml -o step_2_dig.svg
        
        .. image:: ./_images/step2_dig-toml.svg

.. note::

    * Upper case characters has an arrow on the edge of reference
    * notice the spacing with ``{}``, ``spacer:``, or ``spacer.wave = ""``

        | In yaml spacer can be an empty string or a string starting with ``spacer``.
        | For toml any string starting with ``spacer`` is considered as a spacer.
    
    * slewing is considered even for clock signals

.. tip::

    try to modify the slew of signal by adding ``slewing: 18`` attribute or ``slewing: 0``
