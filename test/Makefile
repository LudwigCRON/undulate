TESTPATH=$(shell pwd)
WAVEFORM=../pywave/waveform.py

.PHONY: new legacy internal cairo-svg register legacy_1.jsonml legacy_2.jsonml legacy_3.jsonml wavetest.json wavetest.yaml internal-svg internal-cairo-svg coverage

all: new legacy internal cairo-svg register legacy_1.jsonml legacy_2.jsonml legacy_3.jsonml wavetest.json wavetest.yaml adcec coverage

%.jsonml:
	@echo $@
	python3 $(WAVEFORM) -i "${TESTPATH}/$@" -f svg -o "${TESTPATH}/legacy/$(subst .jsonml,-jsonml.svg,$@)"

%.json:
	@echo $@
	python3 $(WAVEFORM) -i "${TESTPATH}/$@" -f svg -o "${TESTPATH}/legacy/$(subst .json,-json.svg,$@)"

%.yaml:
	@echo $@
	python3 $(WAVEFORM) -i "${TESTPATH}/$@" -f svg -o "${TESTPATH}/output/$(subst .yaml,-yaml.svg,$@)"

%.toml:
	@echo $@
	python3 $(WAVEFORM) -i "${TESTPATH}/$@" -f svg -o "${TESTPATH}/output/$(subst .toml,-toml.svg,$@)"

legacy: legacy_1.jsonml legacy_2.jsonml legacy_3.jsonml
	@echo "Legacy Done"

new: wavetest.json wavetest.yaml
	@echo "New Done"

internal-svg:
	./test.py -f svg

internal-cairo-svg:
	./test.py -f cairo-svg

internal: internal-svg internal-cairo-svg

cairo-eps: wavetest.yaml
	python3 $(WAVEFORM) -i ${TESTPATH}/$< -f cairo-eps -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.eps,$<)

cairo-ps: wavetest.yaml
	python3 $(WAVEFORM) -i ${TESTPATH}/$< -f cairo-ps -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.ps,$<)

cairo-png: wavetest.yaml
	python3 $(WAVEFORM) -i ${TESTPATH}/$< -f cairo-png -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.png,$<)

cairo-pdf: wavetest.yaml
	python3 $(WAVEFORM) -i ${TESTPATH}/$< -f cairo-pdf -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.pdf,$<)

cairo-svg: wavetest.yaml
	python3 $(WAVEFORM) -i ${TESTPATH}/$< -f cairo-svg -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.svg,$<)

register:
	python3 $(WAVEFORM) -r -i "${TESTPATH}/reg-opivi.jsonml" -f svg -o "${TESTPATH}/legacy/reg-opivi-jsonml.svg"
	python3 $(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f svg -o "${TESTPATH}/legacy/reg-vl-jsonml.svg"
	python3 $(WAVEFORM) -r -i "${TESTPATH}/reg-opivi.jsonml" -f cairo-svg -o "${TESTPATH}/legacy/reg-opivi-jsonml-cairo.svg"
	python3 $(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f cairo-svg -o "${TESTPATH}/legacy/reg-vl-jsonml-cairo.svg"

annotation:
	python3 $(WAVEFORM) -i "${TESTPATH}/annotation.yaml" -f cairo-svg -o "${TESTPATH}/output/annotation-cairo.svg"
	python3 $(WAVEFORM) -i "${TESTPATH}/annotation.yaml" -f svg -o "${TESTPATH}/output/annotation.svg"

overlay:
	python3 $(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f cairo-svg -o "${TESTPATH}/output/overlay-cairo.svg"
	python3 $(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f svg -o "${TESTPATH}/output/overlay.svg"

adcec:
	python3 $(WAVEFORM) -i "${TESTPATH}/adcec.jsonml" -f svg -o "${TESTPATH}/output/adcec.svg"

coverage:
	coverage run -a $(WAVEFORM) -i ${TESTPATH}/wavetest.yaml -f svg -o ${TESTPATH}/output/$(subst .yaml,-yaml.svg,wavetest.yaml)
	coverage run -a $(WAVEFORM) -i ${TESTPATH}/wavetest.yaml -f cairo-svg -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.svg,wavetest.yaml)
	coverage run -a $(WAVEFORM) -i ${TESTPATH}/wavetest.json -f cairo-eps -o ${TESTPATH}/output/$(subst .json,-json-cairo.eps,wavetest.json)
	coverage run -a $(WAVEFORM) -i ${TESTPATH}/wavetest.json -f cairo-png -o ${TESTPATH}/output/$(subst .json,-json-cairo.png,wavetest.json)
	coverage run -a $(WAVEFORM) -i ${TESTPATH}/wavetest.yaml -f cairo-pdf -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.pdf,wavetest.yaml)
	coverage run -a ./test.py -f svg
	coverage run -a ./test.py -f cairo-svg
	coverage run -a $(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f svg -o "${TESTPATH}/legacy/reg-vl-jsonml.svg"
	coverage run -a $(WAVEFORM) -r -i "${TESTPATH}/reg-opivi.jsonml" -f cairo-ps -o "${TESTPATH}/legacy/reg-opivi-jsonml-cairo.ps"
	coverage run -a $(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f cairo-png -o "${TESTPATH}/legacy/reg-vl-jsonml-cairo.png"
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/annotation.yaml" -f cairo-svg -o "${TESTPATH}/output/annotation-cairo.svg"
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/annotation.yaml" -f svg -o "${TESTPATH}/output/annotation.svg"
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f cairo-svg -o "${TESTPATH}/output/overlay-cairo.svg"
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f svg -o "${TESTPATH}/output/overlay.svg"
	coverage run -a $(WAVEFORM) -f doc; test $$? -eq 2
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/wrong_ext.c" -f json; test $$? -eq 2
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/missing_grp.jsonml" -f json; test $$? -eq 1
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f json; test $$? -eq 0
	coverage run -a $(WAVEFORM); test $$? -eq 2
	coverage run -a $(WAVEFORM) -i; test $$? -eq 2
	coverage run -a $(WAVEFORM) -h
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/adcec.jsonml" -f svg -o "${TESTPATH}/output/adcec.svg"
	coverage report
	coverage html
