.PHONY:
.PHONY: all clean distclean package release stage

basename := DGTCentaurMods
version  := $(shell git describe --abbrev=0 --tags | tr --delete [A-Z])
package  := $(basename)_A.alpha-ON$(version)
tmp      := $(shell mktemp -d)
stage    := $(tmp)/$(package)
deb      := releases/$(package).deb

package: all stage distclean release
	sudo $(RM) -R $(tmp)

all clean:
	$(MAKE) -C $(basename) $@
	$(RM) -R $(dir $(deb))

stage:
	mkdir $(stage)
	cp -R $(foreach d,DEBIAN etc opt,$(basename)/$d) $(stage)
	cp $(basename)/GNUmakefile $(stage)
	sed -e 's/\$$Version\$$/$(version)/' \
		$(basename)/DEBIAN/control > $(stage)/DEBIAN/control
	sed -e 's/TAG_RELEASE.*/TAG_RELEASE = "ON$(version)"/' \
		$(basename)/opt/DGTCentaurMods/consts/consts.py > \
		$(stage)/opt/DGTCentaurMods/consts/consts.py

distclean:
	$(MAKE) -C $(stage) distclean
	$(RM) $(stage)/GNUmakefile
	$(RM) $(deb)

release:
	sudo chown -R root:root $(stage)/etc
	mkdir -p $(dir $(deb))
	dpkg-deb -Zxz --build $(stage) $(deb)
