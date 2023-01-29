Dependencies
****************

At the origin, Undulate only need a `Python 3 <https://www.python.org/downloads/>`_.
The strategy is to always support active python releases which at this date
correspond to latest 4 versions.

By the time, the json/jsonml format is not adapted to human during a long
documentation process. Some text formats are more user-friendly. Undulate also 
digests `PyYAML <https://pypi.org/project/PyYAML/>`_ and 
`Toml <https://pypi.org/project/toml/>`_ as well.

.. note::

    **Why do I need a toml library while I am on python 3.11 ?**

    Indeed in the `PEP 680 <https://peps.python.org/pep-0680/>`_, the tomlib library is part of the standard
    library to read and parse toml files. The limiting factor of the
    tomlib is the writing of toml file that is not supported. As Undulate
    only use read capability, it should be a perfect fit.

    As Fedora also `deprecates <https://fedoraproject.org/wiki/Changes/DeprecatePythonToml>`_
    the python-toml package it is legitimate to do so as well.

    The tomlib is under consideration and compatibility should be ensured
    for previous python versions.

    The smooth-transition planned is the following:

    - Add support of the tomlib library
    - Add auto import selection in Undulate
    - Remove toml dependencies when the minimum stable version of python is 3.11


For the rendering, SVG is the legacy format of `Wavedrom <https://wavedrom.com/>`_.
SVG is well-known, simple, and versatile vector format for the web.
However, the integration into Word/LibreOffice Writer/Latex documentation is a
limiting factor. So without any extra module, Undulate, as Wavedrom, only export
to the SVG format.

By adding `Cairo <https://www.cairographics.org/>`_ via `CairoCFFI <https://cairocffi.readthedocs.io/en/stable/overview.html>`_ 
(the source of the Egyptian logo style), Undulate can export to:

- SVG
- EPS
- PS
- PDF
- PNG

In fact, Cairo is a drawing librairy which has some difficulties to process
fonts. It is usual to combine Cairo with another library called Pango for that
purpose. The Pango library adds the support of fonts and unicode characters.
Undulate also relies on `PangoCFFI <https://pangocffi.readthedocs.io/en/latest/overview.html#installing>`_
and `PangoCairoCFFI <https://pangocairocffi.readthedocs.io/en/latest/overview.html>`_
that does the link between Pango and Cairo.

To install the complete set of dependencies run in a terminal

.. code-block:: bash

    pip install --user pyyaml toml cairocffi pangocffi pangocairocffi

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

