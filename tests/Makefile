TESTPATH=.
WAVEFORM=undulate

.PHONY: new legacy internal cairo-svg register legacy_1.jsonml legacy_2.jsonml legacy_3.jsonml wavetest.json wavetest.yaml internal-svg internal-cairo-svg coverage

all: new legacy internal cairo-svg register legacy_1.jsonml legacy_2.jsonml legacy_3.jsonml wavetest.json wavetest.yaml adcec coverage

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

legacy: legacy_1.jsonml legacy_2.jsonml legacy_3.jsonml
	@echo "Legacy Done"

new: wavetest.json wavetest.yaml
	@echo "New Done"

internal-svg:
	python ./test.py -f svg

internal-cairo-svg:
	python ./test.py -f cairo-svg

internal: internal-svg internal-cairo-svg

cairo-eps: wavetest.yaml
	$(WAVEFORM) -i ${TESTPATH}/$< -f cairo-eps -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.eps,$<)

cairo-ps: wavetest.yaml
	$(WAVEFORM) -i ${TESTPATH}/$< -f cairo-ps -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.ps,$<)

cairo-png: wavetest.yaml
	$(WAVEFORM) -i ${TESTPATH}/$< -f cairo-png -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.png,$<)

cairo-pdf: wavetest.yaml
	$(WAVEFORM) -i ${TESTPATH}/$< -f cairo-pdf -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.pdf,$<)

cairo-svg: wavetest.yaml
	$(WAVEFORM) -i ${TESTPATH}/$< -f cairo-svg -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.svg,$<)

register:
	$(WAVEFORM) -r -i "${TESTPATH}/reg-opivi.jsonml" -f svg -o "${TESTPATH}/legacy/reg-opivi-jsonml.svg"
	$(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f svg -o "${TESTPATH}/legacy/reg-vl-jsonml.svg"
	$(WAVEFORM) -r -i "${TESTPATH}/reg-opivi.jsonml" -f cairo-svg -o "${TESTPATH}/legacy/reg-opivi-jsonml-cairo.svg"
	$(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f cairo-svg -o "${TESTPATH}/legacy/reg-vl-jsonml-cairo.svg"

annotation:
	$(WAVEFORM) -i "${TESTPATH}/annotation.yaml" -f cairo-svg -o "${TESTPATH}/output/annotation-cairo.svg"
	$(WAVEFORM) -i "${TESTPATH}/annotation.yaml" -f svg -o "${TESTPATH}/output/annotation.svg"

overlay:
	$(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f cairo-svg -o "${TESTPATH}/output/overlay-cairo.svg"
	$(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f svg -o "${TESTPATH}/output/overlay.svg"

adcec:
	$(WAVEFORM) -i "${TESTPATH}/adcec.jsonml" -f svg -o "${TESTPATH}/output/adcec.svg"

coverage:
	coverage erase
	coverage run -a -m $(WAVEFORM).__init__ -i ${TESTPATH}/wavetest.yaml -f svg -o ${TESTPATH}/output/$(subst .yaml,-yaml.svg,wavetest.yaml)
	coverage run -a -m $(WAVEFORM).__init__ -i ${TESTPATH}/wavetest.yaml -f cairo-svg -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.svg,wavetest.yaml)
	coverage run -a -m $(WAVEFORM).__init__ -i ${TESTPATH}/wavetest.json -f cairo-eps -o ${TESTPATH}/output/$(subst .json,-json-cairo.eps,wavetest.json)
	coverage run -a -m $(WAVEFORM).__init__ -i ${TESTPATH}/wavetest.json -f cairo-png -o ${TESTPATH}/output/$(subst .json,-json-cairo.png,wavetest.json)
	coverage run -a -m $(WAVEFORM).__init__ -i ${TESTPATH}/wavetest.yaml -f cairo-pdf -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.pdf,wavetest.yaml)
	coverage run -a ./test.py -f svg
	coverage run -a ./test.py -f cairo-svg
	coverage run -a -m $(WAVEFORM).__init__ -r -i "${TESTPATH}/reg-vl.jsonml" -f svg -o "${TESTPATH}/legacy/reg-vl-jsonml.svg"
	coverage run -a -m $(WAVEFORM).__init__ -r -i "${TESTPATH}/reg-opivi.jsonml" -f cairo-ps -o "${TESTPATH}/legacy/reg-opivi-jsonml-cairo.ps"
	coverage run -a -m $(WAVEFORM).__init__ -r -i "${TESTPATH}/reg-vl.jsonml" -f cairo-png -o "${TESTPATH}/legacy/reg-vl-jsonml-cairo.png"
	coverage run -a -m $(WAVEFORM).__init__ -i "${TESTPATH}/annotation.yaml" -f cairo-svg -o "${TESTPATH}/output/annotation-cairo.svg"
	coverage run -a -m $(WAVEFORM).__init__ -i "${TESTPATH}/annotation.yaml" -f svg -o "${TESTPATH}/output/annotation.svg"
	coverage run -a -m $(WAVEFORM).__init__ -i "${TESTPATH}/overlay.toml" -f cairo-svg -o "${TESTPATH}/output/overlay-cairo.svg"
	coverage run -a -m $(WAVEFORM).__init__ -i "${TESTPATH}/overlay.toml" -f svg -o "${TESTPATH}/output/overlay.svg"
	coverage run -a -m $(WAVEFORM).__init__ -f doc; test $$? -eq 1
	coverage run -a -m $(WAVEFORM).__init__ -f svg -i "${TESTPATH}/inexisting_symbol.toml" -o "${TESTPATH}/inexisting_symbol.svg"; test $$? -eq 3
	coverage run -a -m $(WAVEFORM).__init__ -f doc -i "${TESTPATH}/overlay.toml"; test $$? -eq 1
	coverage run -a -m $(WAVEFORM).__init__ -i "${TESTPATH}/wrong_ext.c" -f json; test $$? -eq 1
	coverage run -a -m $(WAVEFORM).__init__ -i "${TESTPATH}/missing_grp.jsonml" -f json; test $$? -eq 1
	coverage run -a -m $(WAVEFORM).__init__ -i "${TESTPATH}/overlay.toml" -f json; test $$? -eq 0
	coverage run -a -m $(WAVEFORM).__init__; test $$? -eq 1
	coverage run -a -m $(WAVEFORM).__init__ -i; test $$? -eq 2
	coverage run -a -m $(WAVEFORM).__init__ -h
	coverage run -a -m $(WAVEFORM).__init__ -i "${TESTPATH}/adcec.jsonml" -f svg -o "${TESTPATH}/output/adcec.svg"
	coverage run -a -m $(WAVEFORM).__init__ -i "${TESTPATH}/local_config_nodes.yaml" -f svg -o "${TESTPATH}/output/local_config_nodes.svg"
	coverage run -a -m $(WAVEFORM).__init__ -i "${TESTPATH}/reg_control.jsonml" -f svg -r -o "${TESTPATH}/output/local_config_nodes.svg"
	coverage run -a -m $(WAVEFORM).__init__ -i "${TESTPATH}/reg_err5.jsonml" -f svg -r -o "${TESTPATH}/output/local_config_nodes.svg"; test $$? -eq 5
	coverage run -a -m $(WAVEFORM).__init__ -i "${TESTPATH}/reg_err6.jsonml" -f svg -r -o "${TESTPATH}/output/local_config_nodes.svg"; test $$? -eq 6
	coverage report
	coverage html
