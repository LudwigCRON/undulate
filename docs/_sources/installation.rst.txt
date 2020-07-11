1.2 Installation
****************

To install Undulate, the global procedure is the following:

1. download a stable release from `github <https://github.com/LudwigCRON/undulate/releases/latest>`_

    .. code-block:: bash

        $> wget https://github.com/LudwigCRON/undulate/archive/v0.0.4.tar.gz

2. unzip it at the desired place

    .. code-block:: bash

        $> tar -xzvf v0.0.4.tar.gz

3. install via pip

    .. code-block:: bash

        $> python3 -m pip install -r requirements.txt
        $> python3 -m pip install .

As a bonus, you can define an alias in your *.bash_aliases* file

    .. code-block:: bash

        alias undulate-svg="undulate -f svg"
        alias undulate-csvg="undulate -f cairo-svg"
        alias undulate-cpng="undulate -f cairo-png -d 300"
        alias undulate-ceps="undulate -f cairo-eps"
        alias undulate-cpdf="undulate -f cairo-pdf"

For now, the simplest way to install Undulate is using pip

    .. code-block:: bash

        $ pip install git+https://github.com/LudwigCRON/undulate.git

.. note::

    The project has been renamed to Undulate for the sake of unicity on pypi.
    It is planned to publish the package to make the installation simpler with
    a simple

    .. code-block:: bash

        $ pip install undulate