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

internal: internal-eps internal-svg

eps: wavetest.yaml
	../waveform.py -i ${TESTPATH}/$< -f eps -o ${TESTPATH}/output/$(subst .yaml,-yaml.eps,$<)
	gs -sDEVICE=jpeg -dJPEGQ=100 -dNOPAUSE -dBATCH -dSAFER -r300 -sOutputFile=${TESTPATH}/output/$(subst .yaml,-yaml.jpg,$<) ${TESTPATH}/output/$(subst .yaml,-yaml.eps,$<)

register:
	../waveform.py -r -i "${TESTPATH}/reg-opivi.jsonml" -f svg -o "${TESTPATH}/legacy/reg-opivi-jsonml.svg"
	../waveform.py -r -i "${TESTPATH}/reg-vl.jsonml" -f svg -o "${TESTPATH}/legacy/reg-vl-jsonml.svg"