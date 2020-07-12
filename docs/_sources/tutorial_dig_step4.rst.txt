groups
******

In order to gather signals in a given context, or of a same protocol, groups can be nested.

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_4_jsonml">jsonml</a>
        <a class="tab-button" href="#step_4_yaml">yaml</a>
        <a class="tab-button" href="#step_4_toml">toml</a>

    .. container:: tab-content
        :name: step_4_jsonml

        set the content of the file to

        .. code-block:: javascript

            {signal: [
                {name: "clk", wave: "p..Pp..P", slewing: 0},
                ["Master",
                    {name: "io_address", wave: "x3.x4..x", data: "A1 A2"},
                    {name: "io_wdata", wave: "x3.x....", data: "D1"},
                    ["control",
                        {name: "io_write", wave: "01.0...."},
                        {name: "io_read", wave: "0...1..0"}
                    ]
                ],
                {},
                ["Slave",
                    {name: "io_rdata", wave: "x.....4x", data: "Q2"},
                    ["control",
                        {name: "io_valid", wave: "x01x0.1x"}
                    ]
                ]
            ]}
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_4_dig.json -o step_4_dig.svg
        
        .. image:: ./_images/step4_dig-json.svg

    .. container:: tab-content
        :name: step_4_yaml

        set the content of the file to

        .. code-block:: yaml

            clk:
                wave: "p..Pp..P"
                slewing: 0
            Master:
                io_address:
                    wave: "x3.x4..x"
                    data:
                        - "A1"
                        - "A2"
                io_wdata:
                    wave: "x3.x...."
                    data: "D1"
                control:
                    io_write:
                        wave: "01.0...."
                    io_read:
                        wave: "0...1..0"
            spacer:
                wave: ""
            Slave:
                io_rdata:
                    wave: "x.....4x"
                    data: "Q2"
                control:
                    io_valid:
                    wave: "x01x0.1x"
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_4_dig.yaml -o step_4_dig.svg
        
        .. image:: ./_images/step4_dig-yaml.svg

    .. container:: tab-content
        :name: step_4_toml

        set the content of the file to

        .. code-block:: toml

            clk.wave = "p..Pp..P"
            clk.slewing = 0

            [Master]
            io_address.wave       = "x3.x4..x"
            io_wdata.wave         = "x3.x...."
            control.io_write.wave = "01.0...."
            control.io_read.wave  = "0...1..0"

            io_address.data = "A1 A2"
            io_wdata.data   = "D1"

            spacer.wave = ""

            [Slave]
            io_rdata.wave         = "x.....4x"
            control.io_valid.wave = "x01x0.1x"

            io_rdata.data = "Q2"
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -i step_4_dig.toml -o step_4_dig.svg
        
        .. image:: ./_images/step4_dig-toml.svg

.. note::

    Notice the conciseness of new languages such as toml or yaml. These languages have
    been designed to be less verbose than json and natively support comments.

    Also notice the difference of implementation in jsonml compare to yaml/toml of groups:
    while in jsonml the name of the group is the first item of an array, in yaml and toml,
    a group is a key:value pair of an HashMap. The key is the name of the group, and the
    value is the content of the group.

.. warning::

    With nested group, the name of the group take one extra row in height instead of
    adding a name beside an accolade delimiting signals of a same group (wavedrom).
    Thus the image grows vertically rather than horizontally.

    Growing horizontally make the image look smaller when integrated inside a document.
    However, signals not being in a group being placed after a group will look as if they
    belong to it.
    