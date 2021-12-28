# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = ./docs-srcs
BUILDDIR      = ./docs

export SPHINX_APIDOC_OPTIONS := members,show-inheritance

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	sphinx-apidoc -f -e -o $(SOURCEDIR) undulate
	@$(SPHINXBUILD) -b $@ "$(SOURCEDIR)" "$(BUILDDIR)"

# install the required packages
# for pycairo consults https://pycairo.readthedocs.io/en/latest/getting_started.html
# this make file is done for non-regression tests
build_dependencies:
	sudo apt-get update -y
	sudo apt-get install -y build-essential libcairo2-dev pkg-config python3-dev
	pip install --upgrade pip
	pip install pycairo
	pip install pyyaml
	pip install toml
	pip install coverage
	pip install requests

# install package
install_pkg:
	pip install .
