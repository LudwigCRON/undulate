SUBDIRS := $(wildcard *)
WAVEFORM := undulate

.PHONY: all $(SUBDIRS)

all: clean_imgs $(SUBDIRS)
	@echo "[images updated]"

debug:
	@echo $(SUBDIRS)

$(SUBDIRS):
	find $@ -name "*.*ml" -print0 | xargs -0 -I@ bash -c "echo '@' && ${WAVEFORM} -s ./no_padding.css -i './@' -f svg -o $@/\$$(basename '@').svg"
	find $@ -name "*.json" -print0 | xargs -0 -I@ bash -c "echo '@' && ${WAVEFORM} -s ./no_padding.css -i './@' -f svg -o $@/\$$(basename '@').svg" 
	find $@ -name "*reg*.*ml" -print0 | xargs -0 -I@ bash -c "echo '@' && ${WAVEFORM} -r -i './@' -f svg -o $@/\$$(basename '@').svg"
	find $@ -name "*reg*.json" -print0 | xargs -0 -I@ bash -c "echo '@' && ${WAVEFORM} -r -i './@' -f svg -o $@/\$$(basename '@').svg" 
	find $@ -name "*.svg" -print0 | xargs -0 -I@ bash -c "echo \"Copy '@' to ./docs/_images/\" && cp '@' ../../docs/_images/"

clean_imgs:
	rm -rf ../../docs/_images/
	mkdir -p ../../docs/_images/
