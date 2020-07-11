1.1 Dependencies
****************

At the origin, Undulate only need a python3.5+. By the time, the json/jsonml format is not
adapted to human during a long documentation process. Some text formats are more 
user-friendly. Undulate also digests `PyYAML <https://pypi.org/project/PyYAML/>`_ and
`Toml <https://pypi.org/project/toml/>`_ texts.

For the rendering, SVG is the legacy format of `Wavedrom <https://wavedrom.com/>`_.
SVG is well-known, simple, and versatile format for the web.
However, the integration into Word/Libreoffice Writer/Latex documents is the limiting factor.

So without any extra module, Undulate, as wavedrom, only export to the SVG format. By adding
`Pycairo <https://pypi.org/project/pycairo/>`_ (the source of the egyptian logo style),
Undulate can export to:

- SVG
- EPS
- PS
- PDF
- PNG

To install pycairo, check `pycairo needs for you operating system <https://pycairo.readthedocs.io/en/latest/getting_started.html>`_ 
and then run in a terminal

.. code-block:: bash

    pip install pycairo


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
    
    This was used to compare the results between wavedrom and Undulate.

