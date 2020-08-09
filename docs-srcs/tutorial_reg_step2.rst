Let's suppose in the register, some bits are unused for the sake of
field alignment to ease software writing.

Either one can precise the position of each field with ``regpos``, or
only the position of the field following the unused section.

In the example below, we desired to skip the bit 7 to align "vd" on 
the range [12:8], the field "nf" on the range [34:32].

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_2_jsonml">jsonml</a>
        <a class="tab-button" href="#step_2_yaml">yaml</a>
        <a class="tab-button" href="#step_2_toml">toml</a>

    .. container:: tab-content
        :name: step_2_jsonml

        set the content of the file to

        .. code-block:: javascript

            {control:[
                {bits: 7,  name: 0x07, attr: [
                'VLxU,VLE zero-extended',
                'VLxU,VLE zero-extended, fault-only-first',
                'VLxU sign-extended',
                'VLxU sign-extended, fault-only-first',
                ]},
                {bits: 5,  name: 'vd', attr: 'destination of load', type: 5, regpos:8},
                {bits: 3,  name: 'width'},
                {bits: 5,  name: 'rs1', attr: 'base address', type: 4},
                {bits: 5,  name: 'lumop', attr: [0, 16, 0, 16], type: 3},
                {bits: 1,  name: 'vm'},
                {bits: 3,  name: 'mop', attr: [0, 0, 4, 4]},
                {bits: 3,  name: 'nf', regpos: 32},
            ],
            config: {
                no_ticks: true
            }}
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -r -i step_2_reg.json -o step_2_reg.svg
        
        .. image:: ./_images/step2_reg-json.svg

    .. container:: tab-content
        :name: step_2_yaml

        set the content of the file to

        .. code-block:: yaml

            control:
                - bits: 7
                  name: 0x07
                  attr:
                  - 'VLxU,VLE zero-extended'
                  - 'VLxU,VLE zero-extended, fault-only-first'
                  - 'VLxU sign-extended'
                  - 'VLxU sign-extended, fault-only-first'
                - bits: 5
                  name: 'vd'
                  attr: 'destination of load'
                  type: 5
                  regpos: 8
                - bits: 3
                  name: 'width'
                - bits: 5
                  name: 'rs1'
                  attr: 'base address'
                  type: 4
                - bits: 5
                  name: 'lumop'
                  attr: [0, 16, 0, 16]
                  type: 3
                - bits: 1
                  name: 'vm'
                - bits: 3
                  name: 'mop'
                  attr: [0, 0, 4, 4]
                - bits: 3
                  name: 'nf'
                  regpos: 32

            config:
              no_ticks: true
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -r -i step_2_reg.yaml -o step_2_reg.svg
        
        .. image:: ./_images/step2_reg-yaml.svg

    .. container:: tab-content
        :name: step_2_toml

        set the content of the file to

        .. code-block:: toml

            [[control]]
            bits = 7
            name = 0x07
            attr = [
                'VLxU,VLE zero-extended',
                'VLxU,VLE zero-extended, fault-only-first',
                'VLxU sign-extended',
                'VLxU sign-extended, fault-only-first'
            ]

            [[control]]
            bits = 5
            name = 'vd'
            attr = 'destination of load'
            type = 5
            regpos = 8

            [[control]]
            bits = 3
            name = 'width'

            [[control]]
            bits = 5
            name = 'rs1'
            attr = 'base address'
            type = 4

            [[control]]
            bits = 5
            name = 'lumop'
            attr = [0, 16, 0, 16]
            type = 3

            [[control]]
            bits = 1
            name = 'vm'

            [[control]]
            bits = 3
            name = 'mop'
            attr = [0, 0, 4, 4]

            [[control]]
            bits = 3
            name = 'nf'
            regpos = 32

            config.no_ticks = true
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -r -i step_2_reg.toml -o step_2_reg.svg
        
        .. image:: ./_images/step2_reg-toml.svg
    