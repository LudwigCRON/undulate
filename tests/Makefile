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

legacy:
	$(WAVEFORM) -i "${TESTPATH}/legacy_1.jsonml" -f svg -o "${TESTPATH}/legacy/legacy_1.jsonml.svg"
	$(WAVEFORM) -i "${TESTPATH}/legacy_2.jsonml" -f svg -o "${TESTPATH}/legacy/legacy_2.jsonml.svg"
	$(WAVEFORM) -i "${TESTPATH}/legacy_3.jsonml" -f svg -o "${TESTPATH}/legacy/legacy_3.jsonml.svg"
	$(WAVEFORM) -i "${TESTPATH}/legacy_1.jsonml" -f cairo-svg -o "${TESTPATH}/legacy/legacy_1.jsonml.cairo.svg"
	$(WAVEFORM) -i "${TESTPATH}/legacy_2.jsonml" -f cairo-svg -o "${TESTPATH}/legacy/legacy_2.jsonml.cairo.svg"
	$(WAVEFORM) -i "${TESTPATH}/legacy_3.jsonml" -f cairo-svg -o "${TESTPATH}/legacy/legacy_3.jsonml.cairo.svg"
	@echo "Legacy Done"

new: wavetest.json wavetest.yaml
	@echo "New Done"

internal-svg:
	python ./test_wavedrom.py -f svg

internal-cairo-svg:
	python ./test_wavedrom.py -f cairo-svg

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
	python3 ./covrun.py $(WAVEFORM) -i ${TESTPATH}/wavetest.yaml -f svg -o ${TESTPATH}/output/$(subst .yaml,-yaml.svg,wavetest.yaml)
	python3 ./covrun.py $(WAVEFORM) -i ${TESTPATH}/wavetest.yaml -f cairo-svg -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.svg,wavetest.yaml)
	python3 ./covrun.py $(WAVEFORM) -i ${TESTPATH}/wavetest.json -f cairo-eps -o ${TESTPATH}/output/$(subst .json,-json-cairo.eps,wavetest.json)
	python3 ./covrun.py $(WAVEFORM) -i ${TESTPATH}/wavetest.json -f cairo-png -o ${TESTPATH}/output/$(subst .json,-json-cairo.png,wavetest.json)
	python3 ./covrun.py $(WAVEFORM) -i ${TESTPATH}/wavetest.yaml -f cairo-pdf -o ${TESTPATH}/output/$(subst .yaml,-yaml-cairo.pdf,wavetest.yaml)
	coverage run -a ./test_wavedrom.py -f svg
	coverage run -a ./test_wavedrom.py -f cairo-svg
	coverage run -a ./test_css.py
	python3 ./covrun.py $(WAVEFORM) -i ${TESTPATH}/wavetest_alt.json -f cairo-png -s ${TESTPATH}/ut_css/overload.css -o ${TESTPATH}/output/$(subst .json,-json-cairo.png,wavetest_alt.json)
	python3 ./covrun.py $(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f svg -o "${TESTPATH}/legacy/reg-vl-jsonml.svg"
	python3 ./covrun.py $(WAVEFORM) -r -i "${TESTPATH}/reg-opivi.jsonml" -f cairo-ps -o "${TESTPATH}/legacy/reg-opivi-jsonml-cairo.ps"
	python3 ./covrun.py $(WAVEFORM) -r -i "${TESTPATH}/reg-vl.jsonml" -f cairo-png -o "${TESTPATH}/legacy/reg-vl-jsonml-cairo.png"
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/annotation.yaml" -f cairo-svg -o "${TESTPATH}/output/annotation-cairo.svg"
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/annotation.yaml" -f svg -o "${TESTPATH}/output/annotation.svg"
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f cairo-svg -o "${TESTPATH}/output/overlay-cairo.svg"
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f svg -o "${TESTPATH}/output/overlay.svg"
ifeq (${ISPWSH}, 1)
	python3 ./covrun.py $(WAVEFORM) -f doc & python ./test.py $$LASTEXITCODE -eq 1
	python3 ./covrun.py $(WAVEFORM) -f svg -i "${TESTPATH}/inexisting_symbol.toml" -o "${TESTPATH}/inexisting_symbol.svg" & python ./test.py $$LASTEXITCODE -eq 3
	python3 ./covrun.py $(WAVEFORM) -f doc -i "${TESTPATH}/overlay.toml" & python ./test.py $$LASTEXITCODE -eq 1
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/wrong_ext.c" -f json & python ./test.py $$LASTEXITCODE -eq 1
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/missing_grp.jsonml" -f json &  python ./test.py $$LASTEXITCODE -eq 1
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f json & python ./test.py $$LASTEXITCODE -eq 0
	python3 ./covrun.py $(WAVEFORM) & python ./test.py $$LASTEXITCODE -eq 1
	python3 ./covrun.py $(WAVEFORM) -i & python ./test.py $$LASTEXITCODE -eq 2
else
	python3 ./covrun.py $(WAVEFORM) -f doc; test $$? -eq 1
	python3 ./covrun.py $(WAVEFORM) -f svg -i "${TESTPATH}/inexisting_symbol.toml" -o "${TESTPATH}/inexisting_symbol.svg"; test $$? -eq 3
	python3 ./covrun.py $(WAVEFORM) -f doc -i "${TESTPATH}/overlay.toml"; test $$? -eq 1
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/wrong_ext.c" -f json; test $$? -eq 1
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/missing_grp.jsonml" -f json; test $$? -eq 1
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/overlay.toml" -f json; test $$? -eq 0
	python3 ./covrun.py $(WAVEFORM); test $$? -eq 1
	python3 ./covrun.py $(WAVEFORM) -i; test $$? -eq 2
endif
	python3 ./covrun.py $(WAVEFORM) -h
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/adcec.jsonml" -f svg -o "${TESTPATH}/output/adcec.svg"
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/local_config_nodes.yaml" -f svg -o "${TESTPATH}/output/local_config_nodes.svg"
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/reg_control.jsonml" -f svg -r -o "${TESTPATH}/output/local_config_nodes.svg"
ifeq (${ISPWSH}, 1)
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/reg_err5.jsonml" -f svg -r -o "${TESTPATH}/output/local_config_nodes.svg" & python ./test.py $$LASTEXITCODE -eq 5
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/reg_err6.jsonml" -f svg -r -o "${TESTPATH}/output/local_config_nodes.svg" & python ./test.py $$LASTEXITCODE -eq 6
else
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/reg_err5.jsonml" -f svg -r -o "${TESTPATH}/output/local_config_nodes.svg"; test $$? -eq 5
	python3 ./covrun.py $(WAVEFORM) -i "${TESTPATH}/reg_err6.jsonml" -f svg -r -o "${TESTPATH}/output/local_config_nodes.svg"; test $$? -eq 6
endif
	coverage report
	coverage html
