Installation
************

With recent pip versions, pip is able to install a python module from github
directly. The installation process is thus utterly simplified:

.. code-block:: bash

    $> pip install git+https://github.com/LudwigCRON/undulate.git

In fact, you can even specify a version or a branch name in the following manner

.. code-block:: bash

    $> pip install git+https://github.com/LudwigCRON/undulate.git@v0.0.6

or

.. code-block:: bash

    $> pip install git+https://github.com/LudwigCRON/undulate.git@architecture_update


.. warning::

    Unfortunately on some operating system, the versions of pip and python are 
    frozen by the administrator and cannot support this direct installation process.

    The installation procedure is as follow:

    1. download a stable release from `github <https://github.com/LudwigCRON/undulate/releases/latest>`_

        .. code-block:: bash

            $> wget https://github.com/LudwigCRON/undulate/archive/v0.0.5.tar.gz
        
    2. unzip it at the desired place

        .. code-block:: bash

            $> tar -xzvf v0.0.5.tar.gz

    3. install via pip

        .. code-block:: bash

            $> cd ./v0.0.5/ 
            $> pip install --user .

.. tip::

    As a bonus, you can define an alias in your *.bash_aliases* file

        .. code-block:: bash

            alias undulate-svg="undulate -f svg"
            alias undulate-csvg="undulate -f cairo-svg"
            alias undulate-cpng="undulate -f cairo-png -d 300"
            alias undulate-ceps="undulate -f cairo-eps"
            alias undulate-cpdf="undulate -f cairo-pdf"
