bus
****

It is common for busses to represent only a transition with the new value.
The list of possible characters are the following: ``xX=23456789``

| ``x`` or ``X`` define any unkown value.
| ``=23456789`` are the same symbol with different background color

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_3_jsonml">jsonml</a>
        <a class="tab-button" href="#step_3_yaml">yaml</a>
        <a class="tab-button" href="#step_3_toml">toml</a>

    .. container:: tab-content
        :name: step_3_jsonml

        set the content of the file to

        .. code-block:: javascript

            {signal: [
                {name: "clk", wave: "p.....|..."},
                {name: "data", wave: "x.345x|=.x", data: ["head", "body", "tail", "data"]}
                {},
                {name: 'request', wave: '0.1..0|1.0' },
                {name: 'acknowledge', wave: '1.....|01.' }
            ]}
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_3_dig.json -o step_3_dig.svg
        
        .. image:: ./_images/step3_dig-json.svg

    .. container:: tab-content
        :name: step_3_yaml

        set the content of the file to

        .. code-block:: yaml

            clk:
                wave: "p.....|..."
            data:
                wave: "x.345x|=.x"
                data: "head body tail data"
            "":
                wave: ""
            request:
                wave: "0.1..0|1.0"
            acknowledge:
                wave: "1.....|01."
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_3_dig.yaml -o step_3_dig.svg
        
        .. image:: ./_images/step3_dig-yaml.svg

    .. container:: tab-content
        :name: step_3_toml

        set the content of the file to

        .. code-block:: toml

            clk.wave         = "p.....|..."
            data.wave        = "x.345x|=.x"
            spacer.wave      = ""
            request.wave     = "0.1..0|1.0"
            acknowledge.wave = "1.....|01."

            data.data   = "head body tail data"
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_3_dig.toml -o step_3_dig.svg
        
        .. image:: ./_images/step3_dig-toml.svg

.. note::

    * values of bus is defined in ``data`` attribute

        | data could be either an array or a string where items
        | are delimited by a space character