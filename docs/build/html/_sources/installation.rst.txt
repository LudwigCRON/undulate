2. Installation
===============

The recommended way to install dependencies is by typing in your shell

.. code-block:: bash

   $> pip3 install PyYAML
   $> pip3 install toml
   $> pip3 install pycairo

To install Pywave, it is recommended the following:

- download a stable release from `github <https://github.com/LudwigCRON/pywave/releases/latest>`_
- unzip it as the desired place
- add in `$PATH` the pywave folder
- create an alias of your choice to simplify the call

.. code-block:: bash

   $> wget https://github.com/LudwigCRON/pywave/archive/v0.0.2.tar.gz
   $> tar -xzvf v0.0.2.tar.gz

In your *.bash_profile* add the following line

.. code-block:: bash

   export PATH="PATH/TO/pywave-0.0.2:$PATH"

As a bonus, you can define an alias in your *.bash_aliases* file

.. code-block:: bash

   alias pywave-svg="waveform.py -f svg"
   alias pywave-png="waveform.py -f cairo-svg"
   alias pywave-eps="waveform.py -f cairo-eps"
   alias pywave-pdf="waveform.py -f cairo-pdf"
   alias pywave="waveform.py"