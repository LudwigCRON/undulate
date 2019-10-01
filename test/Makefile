TESTPATH=$(shell pwd)
WAVEFORM=../waveform.py

.PHONY: new legacy internal eps cairo-svg register legacy_1.jsonml legacy_2.jsonml legacy_3.jsonml wavetest.json wavetest.yaml internal-eps internal-svg internal-cairo-svg

all: new legacy internal eps cairo-svg register legacy_1.jsonml legacy_2.jsonml legacy_3.jsonml wavetest.json wavetest.yaml adcec coverage

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

internal-eps:
	./test.py -f eps

internal-svg:
	./test.py -f svg

internal-cairo-svg:
	./test.py -f cairo-svg

internal: internal-eps internal-svg internal-cairo-svg

eps: wavetest.yaml
	$(WAVEFORM) -i ${TESTPATH}/$< -f eps -o ${TESTPATH}/output/$(subst .yaml,-yaml.eps,$<)
	gs -sDEVICE=jpeg -dJPEGQ=100 -dNOPAUSE -dBATCH -dSAFER -r300 -sOutputFile=${TESTPATH}/output/$(subst .yaml,-yaml.jpg,$<) ${TESTPATH}/output/$(subst .yaml,-yaml.eps,$<)

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
	$(WAVEFORM) -r -i "${TESTPATH}/reg-opivi.jsonml" -f eps -o "${TESTPATH}/legacy/reg-opivi-jsonml.eps"
	$(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f eps -o "${TESTPATH}/legacy/reg-vl-jsonml.eps"
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
	coverage run $(WAVEFORM) -i ${TESTPATH}/wavetest.yaml -f eps -o ${TESTPATH}/output/$(subst .yaml,-yaml.eps,wavetest.yaml)
	coverage run -a $(WAVEFORM) -i ${TESTPATH}/wavetest.yaml -f svg -o ${TESTPATH}/output/$(subst .yaml,-yaml.svg,wavetest.yaml)
	coverage run -a $(WAVEFORM) -i ${TESTPATH}/wavetest.yaml -f cairo-svg -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.svg,wavetest.yaml)
	coverage run -a $(WAVEFORM) -i ${TESTPATH}/wavetest.json -f cairo-eps -o ${TESTPATH}/output/$(subst .json,-json-cairo.eps,wavetest.json)
	coverage run -a $(WAVEFORM) -i ${TESTPATH}/wavetest.json -f cairo-png -o ${TESTPATH}/output/$(subst .json,-json-cairo.png,wavetest.json)
	coverage run -a $(WAVEFORM) -i ${TESTPATH}/wavetest.yaml -f cairo-pdf -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.pdf,wavetest.yaml)
	coverage run -a ./test.py -f eps
	coverage run -a ./test.py -f svg
	coverage run -a ./test.py -f cairo-svg
	coverage run -a $(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f svg -o "${TESTPATH}/legacy/reg-vl-jsonml.svg"
	coverage run -a $(WAVEFORM) -r -i "${TESTPATH}/reg-opivi.jsonml" -f cairo-ps -o "${TESTPATH}/legacy/reg-opivi-jsonml-cairo.ps"
	coverage run -a $(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f cairo-png -o "${TESTPATH}/legacy/reg-vl-jsonml-cairo.png"
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/annotation.yaml" -f cairo-svg -o "${TESTPATH}/output/annotation-cairo.svg"
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/annotation.yaml" -f svg -o "${TESTPATH}/output/annotation.svg"
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f cairo-svg -o "${TESTPATH}/output/overlay-cairo.svg"
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f svg -o "${TESTPATH}/output/overlay.svg"
	coverage run -a $(WAVEFORM) -f doc; test $$? -eq 1
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/wrong_ext.c" -f json; test $$? -eq 1
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/missing_grp.jsonml" -f json; test $$? -eq 1
	coverage run -a $(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f json; test $$? -eq 0
	coverage run -a $(WAVEFORM); test $$? -eq 1
	coverage report --include="*pywave/*"
	coverage html