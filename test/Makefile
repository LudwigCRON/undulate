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

internal:
	./test.py

eps: wavetest.yaml
	../waveform.py -i ${TESTPATH}/$< -f eps -o ${TESTPATH}/output/$(subst .yaml,-yaml.eps,$<)
	gs -sDEVICE=jpeg -dJPEGQ=100 -dNOPAUSE -dBATCH -dSAFER -r300 -sOutputFile=${TESTPATH}/output/$(subst .yaml,-yaml.jpg,$<) ${TESTPATH}/output/$(subst .yaml,-yaml.eps,$<)