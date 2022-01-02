Dependencies
****************

At the origin, Undulate only need a `Python 3 <https://www.python.org/downloads/>`_.
The strategy is to always support active python releases which at this date
correspond to latest 4 versions.

By the time, the json/jsonml format is not adapted to human during a long
documentation process. Some text formats are more user-friendly. Undulate also 
digests `PyYAML <https://pypi.org/project/PyYAML/>`_ and 
`Toml <https://pypi.org/project/toml/>`_ as well.

For the rendering, SVG is the legacy format of `Wavedrom <https://wavedrom.com/>`_.
SVG is well-known, simple, and versatile vector format for the web.
However, the integration into Word/LibreOffice Writer/Latex documentation is a
limiting factor. So without any extra module, Undulate, as Wavedrom, only export
to the SVG format. By adding `PyCairo <https://pypi.org/project/pycairo/>`_ 
(the source of the Egyptian logo style), Undulate can export to:

- SVG
- EPS
- PS
- PDF
- PNG

To install PyCairo, check for your operating system 
`its requirements <https://pycairo.readthedocs.io/en/latest/getting_started.html>`_.

To install the complete set of dependencies run in a terminal

.. code-block:: bash

    pip install pyyaml toml pycairo

.. note::

    Undulate can run without those dependencies. You desire to use a feature
    requiring one of those module an error message will advise you which
    module need to be installed.

    .. code-block:: bash

        $> undulate -i "./unsupported.yaml"
        CRITICAL: To read yaml file PyYAML is required. Run 'pip install pyyaml'
        $> undulate -i "./unsupported.toml"
        CRITICAL: To read toml file toml is required. Run 'pip install toml'

.. tip::

    You want to contribute on the project or you forked it ?
    
    All needed modules are in the requirements.txt file at the top of the project.
    To install them run 

    .. code-block:: bash
    
        pip install -r requirements.txt

    To check the similarity between two images, tests/checks.py needs:
        - `imagemagick <https://imagemagick.org/index.php>`_
        - `numpy <https://pypi.org/project/numpy/>`_
        - `scipy <https://pypi.org/project/scipy/>`_
        - `scikit-image <https://pypi.org/project/scikit-image/>`_
    
    This was used to compare the results between Wavedrom and Undulate.

