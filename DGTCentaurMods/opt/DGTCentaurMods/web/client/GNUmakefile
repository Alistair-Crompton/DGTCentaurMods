.PHONY:
.PHONY: all clean distclean

all:
	npm ci
	npm run build

clean: distclean
	$(RM) -R dist

distclean:
	$(RM) -R node_modules
