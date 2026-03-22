all:
	$(MAKE) -f Makefile.main all
	$(MAKE) -f Makefile.main00001 all

mainBuild:
	$(MAKE) -f Makefile.main all

main00001Build:
	$(MAKE) -f Makefile.main00001 all


mainRun:
	$(MAKE) -f Makefile.main run

main00001Run:
	$(MAKE) -f Makefile.main00001 run

clean:
	$(MAKE) -f Makefile.main clean
	$(MAKE) -f Makefile.main00001 clean

fclean:
	$(MAKE) -f Makefile.main fclean
	$(MAKE) -f Makefile.main00001 fclean

re: fclean all

.PHONY: all mainBuild mainRun main00001Build main00001Run clean fclean re
