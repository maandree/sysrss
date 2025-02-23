.POSIX:

CONFIGFILE = config.mk
include $(CONFIGFILE)


all:
	@:

install:
	mkdir -p -- "$(DESTDIR)$(PREFIX)/bin"
	mkdir -p -- "$(DESTDIR)$(MANPREFIX)/man1"
	cp -- sysrss "$(DESTDIR)$(PREFIX)/bin/"
	cp -- sysrss.1 "$(DESTDIR)$(MANPREFIX)/man1/"


uninstall:
	-rm -f -- "$(DESTDIR)$(PREFIX)/bin/sysrss"
	-rm -f -- "$(DESTDIR)$(MANPREFIX)/man1/sysrss.1"

clean:
	-rm -rf -- __pycache__

.PHONY: all uninstall install clean
