PREFIX=/usr

all:
	@: do nothing

install:
	mkdir -p "$(DESTDIR)$(PREFIX)/bin"
	install -m 755 sysrss.py "$(DESTDIR)$(PREFIX)/bin/sysrss"

clean:
	@echo nothing to clean

.PHONY: clean
