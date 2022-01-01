SUBDIRS := $(wildcard *)
WAVEFORM := undulate

.PHONY: all $(SUBDIRS)

all: clean_imgs $(SUBDIRS)
	@echo "[images updated]"

debug:
	@echo $(SUBDIRS)

$(SUBDIRS):
	find $@ -name "*.*ml" -print0 | xargs -0 -I@ bash -c "echo '@' && ${WAVEFORM} -i './@' -f cairo-svg -o $@/\$$(basename '@').svg" 
	find $@ -name "*.svg" -print0 | xargs -0 -I@ bash -c "echo \"Copy '@' to ./docs/_images/\" && cp '@' ../../docs/_images/"

clean_imgs:
	rm -rf ../../docs/_images/
	mkdir -p ../../docs/_images/
