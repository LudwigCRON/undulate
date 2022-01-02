digital signal
**************

Let's see how to generate your first digital waveform.
First create a text file in which we will add the textual representation of the
waveform with all possibilities of a digital signal. Each character in the
``wave`` string represents a single time step (clock period).

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
                {name: "digital", wave: "01.zx=ud.2.3.45XziIzmzM"}
            ]}
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_1_dig.json -o step_1_dig.svg
        
        .. image:: ./_images/step_1_dig.json.svg

    .. container:: tab-content
        :name: step_1_yaml

        set the content of the file to

        .. code-block:: yaml

            digital:
                wave: "01.zx=ud.2.3.45XziIzmzM"
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_1_dig.yaml -o step_1_dig.svg
        
        .. image:: ./_images/step_1_dig.yaml.svg

    .. container:: tab-content
        :name: step_1_toml

        set the content of the file to

        .. code-block:: toml

            digital.wave = "01.zx=ud.2.3.45XziIzmzM"
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_1_dig.toml -o step_1_dig.svg
        
        .. image:: ./_images/step_1_dig.toml.svg

.. note::

    * "." extends the previous symbol by one more period.
    * "i" is an impulse 1 -> 0 -> 1
    * "I" is an impulse 0 -> 1 -> 0
    * "m" is a metastability resolved to 0
    * "M" is a metastability resolved to 1
