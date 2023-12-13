.PHONY:
.PHONY: all clean distclean

all clean:
	$(MAKE) -C web/client $@

distclean:
	$(MAKE) -C web/client $@
	$(RM) config/centaur.ini
	$(RM) db/centaur.db
	$(RM) -R engines/books
	$(RM) -R engines/maia_weights
	$(RM) -R engines/personalities
	py3clean .
	chmod ugo=rwx engines
