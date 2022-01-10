analogue signal
***************

An analogue signal varies between two limits corresponding to the supply 
:math:`V_{DDA}` and :math:`V_{SSA}`.

At the exception of very specific design, most analogue signals are stepwise
variation (switched-caps circuits, trimming operations, ...). Therefore, only the
final value change with a transition either corresponding to the charge 
(resp. discharge) of a capacitor, or linearly due to current limitation (slewing).

The analogue bricks corresponding to such behavior are ``c`` for capacitive
loading, and ``s`` for slewing. They accept a single value being either a number
or an expression depending on :math:`V_{DDA}`.

For more arbitrary functions, or continuous time functions, the analogue brick to
be used is ``a`` and accepts an array of numbers or an expression resulting into
an array of numbers.

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_1_jsonml">jsonml</a>
        <a class="tab-button" href="#step_1_yaml">yaml</a>
        <a class="tab-button" href="#step_1_toml">toml</a>

    .. container:: tab-content
        :name: step_1_jsonml

        set the content of the file to

        .. code-block:: javascript

            {signal: [
                {name: "gbf", wave: "0ssssccca...msMs", analogue: [
                    "0.5*VDDA", "0.6*VDDA", "0.7*VDDA", "0.9*VDDA", // first 4 's'
                    "0.2*VDDA", "0.8*VDDA", "0.3*VDDA", // 3 'c'
                    "[(t, (VDDA+VSSA)*(1 + sin(2*pi*t*3.5/Tmax))/2) for t in time]", // for 'a'
                    "0.25*VDDA", // for last s
                    "VDDA"
                ]}
            ]}
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_1_ana.json -o step_1_ana.svg
        
        .. image:: ./_images/step_1_ana.json.svg

    .. container:: tab-content
        :name: step_1_yaml

        set the content of the file to

        .. code-block:: yaml

            gbf:
                wave: "0ssssccca...msMs"
                analogue:
                    - "0.5*VDDA" # first 4 's'
                    - "0.6*VDDA"
                    - "0.7*VDDA"
                    - "0.9*VDDA"
                    - "0.2*VDDA" # 3 'c'
                    - "0.8*VDDA"
                    - "0.3*VDDA"
                    - "[(t, (VDDA+VSSA)*(1 + sin(2*pi*t*3.5/Tmax))/2) for t in time]" # for 'a'
                    - "0.25*VDDA" # for last s
                    - "VDDA"
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_1_ana.yaml -o step_1_ana.svg
        
        .. image:: ./_images/step_1_ana.yaml.svg

    .. container:: tab-content
        :name: step_1_toml

        set the content of the file to

        .. code-block:: toml

            gbf.wave = "0ssssccca...msMs"
            gbf.analogue = [
                "0.5*VDDA", # first 4 's'
                "0.6*VDDA",
                "0.7*VDDA",
                "0.9*VDDA",
                "0.2*VDDA", # 3 'c'
                "0.8*VDDA",
                "0.3*VDDA",
                "[(t, (VDDA+VSSA)*(1 + sin(2*pi*t*3.5/Tmax))/2) for t in time]", # for 'a'
                "0.25*VDDA", # for last s
                "VDDA"
            ]
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_1_ana.toml -o step_1_ana.svg
        
        .. image:: ./_images/step_1_ana.toml.svg

.. note::

    Predefined constant and functions are provided in this analogue context. The
    exhaustive list of those is presented in section 2.3.
