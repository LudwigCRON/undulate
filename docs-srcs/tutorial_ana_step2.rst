superposition and style overloading
***********************************

Mixed signal design shall have clear interface definition between analogue and digital.
A common situation is a comparator giving a digital output of the comparison of two analogue
signals.

In order to better convey the relation between the two analogue signals at the input of the
comparator, it is interresting to superpose them with a different color.

Undulate allows a superposition of up to 4 signals. For that, the attribute ``overlay`` should
be set to ``True`` for the first 3 signals. Both signal and signal's name are supperposed.
In order to clarify which signal is which, the position of the signal's name could be adjusted:
the attribute ``order`` accepts a value between 0 and 4:

    - 0: middle (default value)
    - 1: top
    - 2: middle-high
    - 3: middle-low
    - 4: bottom

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
                {name: "mcu_clk", wave: "P", repeat: 10},
                {name: "dac", wave: "c", repeat: 10, slewing: 32, vscale: 4, overlay: true,
                stroke: [0, 0, 255, 255], 
                "stroke-dasharray": [1, 3], 
                fill: [0, 0, 255, 255], 
                "font-size": "9pt", order: 2, analogue: [
                    "VDDA*512/1024",
                    "VDDA*256/1024",
                    "VDDA*384/1024",
                    "VDDA*320/1024",
                    "VDDA*352/1024",
                    "VDDA*336/1024",
                    "VDDA*344/1024",
                    "VDDA*340/1024",
                    "VDDA*342/1024",
                    "VDDA*341/1024"
                ]},
                {name: "vin", wave: "0a........", vscale: 4, overlay: true,
                stroke: "#F00",
                "stroke-dasharray": [5, 3, 1, 5],
                "stroke-width": 1.5,
                fill: "rgb(255, 0, 0)",
                "font-size": "0.4em", order: 3, analogue: ["[(t, (VDDA/3)*(1-exp(-t/3))) for t in time]"]},
                {name: "vmax", wave: "1.........", vscale: 4, order: 1, overlay: true},
                {name: "vmin", wave: "l.........", vscale: 4, order: 4},
                {name: "dac_ref", wave: "s", repeat: 10, slewing: 32, vscale: 4,
                stroke: "#0000FFAA",
                "stroke-dasharray": [1, 3],
                fill: "#0000FF", order: 2, analogue: [
                    "VDDA*512/1024",
                    "VDDA*256/1024",
                    "VDDA*384/1024",
                    "VDDA*320/1024",
                    "VDDA*352/1024",
                    "VDDA*336/1024",
                    "VDDA*344/1024",
                    "VDDA*340/1024",
                    "VDDA*342/1024",
                    "VDDA*341/1024"
                ]}
            ]}
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_2_ana.json -o step_2_ana.svg
        
        .. image:: ./_images/step2_ana-json.svg

    .. container:: tab-content
        :name: step_2_yaml

        set the content of the file to

        .. code-block:: yaml

            # testcase to demonstrate the possibility
            # of overlaying several curves

            mcu_clk:
                wave: "P"
                repeat: 10

            # value of the 10-bits DAC of a SAR
            dac:
                wave: "c"
                repeat: 10
                slewing: 32
                vscale: 4
                overlay: true
                stroke: [0, 0, 255, 255]
                stroke-dasharray: [1, 3]
                fill: [0, 0, 255, 255]
                font-size: "9pt"
                order: 2
                analogue:
                    - "VDDA*512/1024"
                    - "VDDA*256/1024"
                    - "VDDA*384/1024"
                    - "VDDA*320/1024"
                    - "VDDA*352/1024"
                    - "VDDA*336/1024"
                    - "VDDA*344/1024"
                    - "VDDA*340/1024"
                    - "VDDA*342/1024"
                    - "VDDA*341/1024"

            # input  voltage to which compare
            vin:
                wave: "0a........"
                vscale: 4
                overlay: true
                stroke: "#F00"
                stroke-dasharray: [5, 3, 1, 5]
                stroke-width: 1.5
                fill: "rgb(255, 0, 0)"
                font-size: "0.4em"
                order: 3
                analogue:
                    - "[(t, (VDDA/3)*(1-exp(-t/3))) for t in time]"

            # vmax
            vmax:
                wave: "1........."
                vscale: 4
                order: 1
                overlay: true

            # vmin
            vmin:
                wave: "l........."
                vscale: 4
                order: 4

            dac_ref:
                wave: "s"
                repeat: 10
                slewing: 32
                vscale: 4
                stroke: "#0000FFAA"
                stroke-dasharray: [1, 3]
                fill: "#0000FF"
                order: 2
                analogue:
                    - "VDDA*512/1024"
                    - "VDDA*256/1024"
                    - "VDDA*384/1024"
                    - "VDDA*320/1024"
                    - "VDDA*352/1024"
                    - "VDDA*336/1024"
                    - "VDDA*344/1024"
                    - "VDDA*340/1024"
                    - "VDDA*342/1024"
                    - "VDDA*341/1024"
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_2_ana.yaml -o step_2_ana.svg
        
        .. image:: ./_images/step2_ana-yaml.svg

    .. container:: tab-content
        :name: step_2_toml

        set the content of the file to

        .. code-block:: toml

            # testcase to demonstrate the possibility
            # of overlaying several curves

            mcu_clk.wave          = "P"
            mcu_clk.repeat        = 10

            # value of the 10-bits DAC of a SAR
            dac.wave              = "c"
            dac.repeat            = 10
            dac.slewing           = 32
            dac.vscale            = 4
            dac.overlay           = true
            dac.stroke            = [0, 0, 255, 255]
            dac.stroke-dasharray  = [1, 3]
            dac.fill              = [0, 0, 255, 255]
            dac.font-size         = '9pt'
            dac.order             = 2
            dac.analogue          = [
                "VDDA*512/1024",
                "VDDA*256/1024",
                "VDDA*384/1024",
                "VDDA*320/1024",
                "VDDA*352/1024",
                "VDDA*336/1024",
                "VDDA*344/1024",
                "VDDA*340/1024",
                "VDDA*342/1024",
                "VDDA*341/1024"
            ]

            # input  voltage to which compare
            vin.wave              = "0a........"
            vin.vscale            = 4
            vin.overlay           = true
            vin.stroke            = '#F00'
            vin.stroke-dasharray  = [5, 3, 1, 5]
            vin.stroke-width      = 1.5
            vin.fill              = 'rgb(255, 0, 0)'
            vin.font-size         = '0.4em'
            vin.order             = 3
            vin.analogue          = [
                "[(t, (VDDA/3)*(1-exp(-t/3))) for t in time]"
            ]

            # vmax
            vmax.wave             = "1........."
            vmax.vscale           = 4
            vmax.order            = 1
            vmax.overlay          = true

            # vmin
            vmin.wave             = "l........."
            vmin.vscale           = 4
            vmin.order            = 4

            dac_ref.wave              = "s"
            dac_ref.repeat            = 10
            dac_ref.slewing           = 32
            dac_ref.vscale            = 4
            dac_ref.stroke            = '#0000FFAA'
            dac_ref.stroke-dasharray  = [1, 3]
            dac_ref.fill              = '#0000FF'
            dac_ref.order             = 2
            dac_ref.analogue          = [
                "VDDA*512/1024",
                "VDDA*256/1024",
                "VDDA*384/1024",
                "VDDA*320/1024",
                "VDDA*352/1024",
                "VDDA*336/1024",
                "VDDA*344/1024",
                "VDDA*340/1024",
                "VDDA*342/1024",
                "VDDA*341/1024"
            ]
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_2_ana.toml -o step_2_ana.svg
        
        .. image:: ./_images/step2_ana-toml.svg

.. note::

    To enhance the clarity, the following property can be overloaded as in the example:

        - font-size:

            | size of the text (valid css units in em, px, pt)

        - fill:

            | color of area and text (valid css color in hex, rgb, rgba)

        - stroke:

            | color of lines (valid css color in hex, rgb, rgba)

        - stroke-width:

            | thickness of lines

        - stroke-dasharray:

            | pattern of dash to apply described as an array of number representing
            | alternatively line segment length, spacing length

.. tip::

    To enhance lisibility, the line have been made bigger by using ``vscale``. It accepts
    a scaling factor as done in the example.

    It also exists ``hscale`` scaling the x-axis instead of the y-axis as ``vscale`` does.