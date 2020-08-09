A register is a combination of flip-flops storing configurations,
flags, or triggers. A particular value in a register is called a field,
and a register is the concatenation of several field.

A common file format for exchange of information
between digital and software teams is needed. Wavedrom made a
proposal by generating an image from a textual representation.

In this section we present the implementation of the Wavedrom proposal.
Each field is described by the following information:

  - a name
  - the number of bits of this field
  - an attribute giving extra information to it
  - a type

And a register is an ordered array of fields as represented below.

.. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#step_1_jsonml">jsonml</a>
        <a class="tab-button" href="#step_1_yaml">yaml</a>
        <a class="tab-button" href="#step_1_toml">toml</a>

    .. container:: tab-content
        :name: step_1_jsonml

        set the content of the file to

        .. code-block:: javascript

            {reg: [
                {bits: 7,  name: 0x37, attr: ['OPIVI']},
                {bits: 5,  name: 'vd', type: 2},
                {bits: 3,  name: 3},
                {bits: 5,  name: 'simm5', type: 5},
                {bits: 5,  name: 'vs2', type: 2},
                {bits: 1,  name: 'vm'},
                {bits: 6,  name: 'funct6'},
            ]}
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -r -i step_1_reg.json -o step_1_reg.svg
        
        .. image:: ./_images/step1_reg-json.svg

    .. container:: tab-content
        :name: step_1_yaml

        set the content of the file to

        .. code-block:: yaml

            reg: 
                - bits: 7
                  name: 0x37
                  attr: ['OPIVI']
                - bits: 5
                  name: 'vd'
                  type: 2
                - bits: 3
                  name: 3
                - bits: 5
                  name: 'simm5'
                  type: 5
                - bits: 5
                  name: 'vs2'
                  type: 2
                - bits: 1
                  name: 'vm'
                - bits: 6
                  name: 'funct6'
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -r -i step_1_reg.yaml -o step_1_reg.svg
        
        .. image:: ./_images/step1_reg-yaml.svg

    .. container:: tab-content
        :name: step_1_toml

        set the content of the file to

        .. code-block:: toml

            [[reg]]
            name = 0x37
            bits = 7
            attr = ['OPIVI']

            [[reg]]
            name = 'vd'
            bits = 5
            type = 2

            [[reg]]
            name = 3
            bits = 3

            [[reg]]
            name = 'simm5'
            bits = 5
            type = 5

            [[reg]]
            name = 'vs2'
            bits = 5
            type = 2

            [[reg]]
            name = 'vm'
            bits = 1

            [[reg]]
            name = 'funct6'
            bits = 6
        
        then generate an image with undulate 

        .. code-block:: bash

            undulate -f svg -r -i step_1_reg.toml -o step_1_reg.svg
        
        .. image:: ./_images/step1_reg-toml.svg

.. note::

  Note that a name set to a number is converted into binary to zero
  padded if necessary to fit the size of a bus.

  However, the use of number as a name is only useful to illustrate
  a specific configuration or state.

.. note::

  For the coloration of a specific field, it is definied by ``type``.
  The number of type and the color used is identical to the data
  representation for a signal (signal.wave = "=23456789").

.. tip::

  If you desire to remove the dashed lines in the background, add a
  config section at the end like as underneath. Note this is also true
  for previous section of the tutorial.

  .. container:: tabs

    .. raw:: html

        <a class="tab-button" href="#tip_1_jsonml">jsonml</a>
        <a class="tab-button" href="#tip_1_yaml">yaml</a>
        <a class="tab-button" href="#tip_1_toml">toml</a>

    .. container:: tab-content
        :name: tip_1_jsonml

        .. code-block:: javascript

          config: {
            no_ticks: true
          }
    
    .. container:: tab-content
        :name: tip_1_yaml

        .. code-block:: yaml

          config:
            no_ticks: true
    
    .. container:: tab-content
        :name: tip_1_toml

        .. code-block:: toml

          config.no_ticks = true
    