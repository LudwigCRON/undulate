SUBDIRS := $(wildcard *)
WAVEFORM := undulate

.PHONY: all $(SUBDIRS)

all: $(SUBDIRS)
	@echo "[images updated]"

debug:
	@echo $(SUBDIRS)

$(SUBDIRS):
	find $@ -name "*.*ml" -print0 | xargs -0 -I@ bash -c "echo '@' && ${WAVEFORM} -i './@' -f cairo-svg -o $@/\$$(basename '@').svg" 
