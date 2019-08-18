TESTPATH=$(shell pwd)

%.jsonml:
	@echo $@
	../waveform.py -i "${TESTPATH}/$@" -f svg -o "${TESTPATH}/legacy/$(subst .jsonml,-jsonml.svg,$@)"

%.json:
	@echo $@
	../waveform.py -i "${TESTPATH}/$@" -f svg -o "${TESTPATH}/legacy/$(subst .json,-json.svg,$@)"

%.yaml:
	@echo $@
	../waveform.py -i "${TESTPATH}/$@" -f svg -o "${TESTPATH}/output/$(subst .yaml,-yaml.svg,$@)"

%.toml:
	@echo $@
	../waveform.py -i "${TESTPATH}/$@" -f svg -o "${TESTPATH}/output/$(subst .toml,-toml.svg,$@)"

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
	../waveform.py -i ${TESTPATH}/$< -f eps -o ${TESTPATH}/output/$(subst .yaml,-yaml.eps,$<)
	gs -sDEVICE=jpeg -dJPEGQ=100 -dNOPAUSE -dBATCH -dSAFER -r300 -sOutputFile=${TESTPATH}/output/$(subst .yaml,-yaml.jpg,$<) ${TESTPATH}/output/$(subst .yaml,-yaml.eps,$<)

cairo-svg:
	../waveform.py -i ${TESTPATH}/$< -f cairo-svg -o ${TESTPATH}/output/$(subst .yaml,-yaml.eps,$<)

register:
	../waveform.py -r -i "${TESTPATH}/reg-opivi.jsonml" -f svg -o "${TESTPATH}/legacy/reg-opivi-jsonml.svg"
	../waveform.py -r -i "${TESTPATH}/reg-vl.jsonml" -f svg -o "${TESTPATH}/legacy/reg-vl-jsonml.svg"
	../waveform.py -r -i "${TESTPATH}/reg-opivi.jsonml" -f eps -o "${TESTPATH}/legacy/reg-opivi-jsonml.eps"
	../waveform.py -r -i "${TESTPATH}/reg-vl.jsonml" -f eps -o "${TESTPATH}/legacy/reg-vl-jsonml.eps"
	../waveform.py -r -i "${TESTPATH}/reg-opivi.jsonml" -f cairo-svg -o "${TESTPATH}/legacy/reg-opivi-jsonml-cairo.svg"
	../waveform.py -r -i "${TESTPATH}/reg-vl.jsonml" -f cairo-svg -o "${TESTPATH}/legacy/reg-vl-jsonml-cairo.svg"