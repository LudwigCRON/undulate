SUBDIRS := $(wildcard *)
WAVEFORM := pywave

.PHONY: all $(SUBDIRS)

all: $(SUBDIRS)
	@echo "[images updated]"

$(SUBDIRS):
	find $@ -name "*.*ml" -print0 | xargs -0 -I@ bash -c "${WAVEFORM} -i './@' -f cairo-svg -o $@/\$$(basename '@').svg" 
