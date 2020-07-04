1. Dependencies
===============
At the origin, `Undulate` only need a python3.5+. By the time, the json/jsonml format as been a
tedious part in the documentation process.

In consequence, `Undulate` also now relies on `PyYAML <https://pypi.org/project/PyYAML/>`_ and
`Toml <https://pypi.org/project/toml/>`_.

For the rendering, SVG is the legacy format from `Wavedrom <https://wavedrom.com/>`_.
SVG is well-known and simple versatile format for the web.
However, the integration into Word/Libreoffice Writer/Latex documents is the bottleneck.

So without any extra module, one can only export to the SVG format.

By adding `Pycairo <https://pypi.org/project/pycairo/>`_, `Undulate` can export to:

- SVG
- EPS
- PS
- PDF
- PNG

For tests the following modules are needed:

- `coverage <https://pypi.org/project/coverage/>`_
- `numpy <https://pypi.org/project/numpy/>`_
- `scipy <https://pypi.org/project/scipy/>`_
- `scikit-image <https://pypi.org/project/scikit-image/>`_

The last three are used to compare images between format and check the similarity between them.
