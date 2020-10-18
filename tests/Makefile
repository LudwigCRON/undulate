TESTPATH=.
WAVEFORM=undulate

.PHONY: coverage

all: coverage

%.jsonml:
	@echo $@
	$(WAVEFORM) -i "${TESTPATH}/$@" -f svg -o "${TESTPATH}/legacy/$(subst .jsonml,-jsonml.svg,$@)"

%.json:
	@echo $@
	$(WAVEFORM) -i "${TESTPATH}/$@" -f svg -o "${TESTPATH}/legacy/$(subst .json,-json.svg,$@)"

%.yaml:
	@echo $@
	$(WAVEFORM) -i "${TESTPATH}/$@" -f svg -o "${TESTPATH}/output/$(subst .yaml,-yaml.svg,$@)"

%.toml:
	@echo $@
	$(WAVEFORM) -i "${TESTPATH}/$@" -f svg -o "${TESTPATH}/output/$(subst .toml,-toml.svg,$@)"

coverage:
	coverage erase
	python -m unittest test_all -v
	coverage run -a ${TESTPATH}/test_css.py -v
	coverage report
	coverage html
