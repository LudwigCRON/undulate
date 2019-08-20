TESTPATH=$(shell pwd)
WAVEFORM=../waveform.py

.PHONY: new legacy internal eps cairo-svg register

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

cairo-svg:
	$(WAVEFORM) -i ${TESTPATH}/$< -f cairo-svg -o ${TESTPATH}/output/$(subst .yaml,-yaml.eps,$<)

register:
	$(WAVEFORM) -r -i "${TESTPATH}/reg-opivi.jsonml" -f svg -o "${TESTPATH}/legacy/reg-opivi-jsonml.svg"
	$(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f svg -o "${TESTPATH}/legacy/reg-vl-jsonml.svg"
	$(WAVEFORM) -r -i "${TESTPATH}/reg-opivi.jsonml" -f eps -o "${TESTPATH}/legacy/reg-opivi-jsonml.eps"
	$(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f eps -o "${TESTPATH}/legacy/reg-vl-jsonml.eps"
	$(WAVEFORM) -r -i "${TESTPATH}/reg-opivi.jsonml" -f cairo-svg -o "${TESTPATH}/legacy/reg-opivi-jsonml-cairo.svg"
	$(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f cairo-svg -o "${TESTPATH}/legacy/reg-vl-jsonml-cairo.svg"