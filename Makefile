# =============================================================================
# @file    Makefile
# @brief   Makefile for some steps in creating new releases on GitHub
# @created 2020-08-11
# @license Please see the file named LICENSE in the project directory
# @website https://github.com/caltechlibrary/dibs
# =============================================================================

# This Makefile uses syntax that needs at least GNU Make version 3.82.
# The following test is based on the approach posted by Eldar Abusalimov to
# Stack Overflow in 2012 at https://stackoverflow.com/a/12231321/743730

ifeq ($(filter undefine,$(value .FEATURES)),)
$(error Unsupported version of Make. \
    This Makefile does not work properly with GNU Make $(MAKE_VERSION); \
    it needs GNU Make version 3.82 or later)
endif

# Before we go any further, test if certain programs are available.
# The following is based on the approach posted by Jonathan Ben-Avraham to
# Stack Overflow in 2014 at https://stackoverflow.com/a/25668869

programs_needed = awk curl gh git jq sed
TEST := $(foreach p,$(programs_needed),\
	  $(if $(shell which $(p)),_,$(error Cannot find program "$(p)")))

# Set some basic variables.  These are quick to set; we set additional
# variables using the "vars" action but only when the others are needed.

name	 := $(strip $(shell awk -F "=" '/^name/ {print $$2}' setup.cfg))
version	 := $(strip $(shell awk -F "=" '/^version/ {print $$2}' setup.cfg))
url	 := $(strip $(shell awk -F "=" '/^url/ {print $$2}' setup.cfg))
desc	 := $(strip $(shell awk -F "=" '/^description / {print $$2}' setup.cfg))
author	 := $(strip $(shell awk -F "=" '/^author / {print $$2}' setup.cfg))
email	 := $(strip $(shell awk -F "=" '/^author_email/ {print $$2}' setup.cfg))
license	 := $(strip $(shell awk -F "=" '/^license / {print $$2}' setup.cfg))
branch	 := $(shell git rev-parse --abbrev-ref HEAD)
initfile := $(name)/__init__.py


# Gather additional values we sometimes need ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
# These variables take longer to compute, and for some actions like "make help"
# they are unnecessary and annoying to wait for.

.SILENT: vars
vars:
	$(info Gathering data -- this takes a few moments ...)
	$(eval repo	 := $(strip $(shell gh repo view | head -1 | cut -f2 -d':')))
	$(eval api_url   := https://api.github.com)
	$(eval id	 := $(shell curl -s $(api_url)/repos/$(repo) | jq '.id'))
	$(eval id_url	 := https://data.caltech.edu/badge/latestdoi/$(id))
	$(eval doi_url	 := $(shell curl -sILk $(id_url) | grep Locat | cut -f2 -d' '))
	$(eval doi	 := $(subst https://doi.org/,,$(doi_url)))
	$(eval doi_tail  := $(lastword $(subst ., ,$(doi))))
	$(info Gathering data -- this takes a few moments ... Done.)

report: vars
	@echo name	= $(name)
	@echo version	= $(version)
	@echo url	= $(url)
	@echo desc	= $(desc)
	@echo author	= $(author)
	@echo email	= $(email)
	@echo license	= $(license)
	@echo branch	= $(branch)
	@echo repo	= $(repo)
	@echo id	= $(id)
	@echo id_url	= $(id_url)
	@echo doi_url	= $(doi_url)
	@echo doi	= $(doi)
	@echo doi_tail	= $(doi_tail)
	@echo initfile  = $(initfile)


# make release ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

release: | test-branch release-on-github print-instructions

test-branch:;
ifneq ($(branch),main)
	$(error Current git branch != main. Merge changes into main first!)
endif

update-init:;
	@sed -i .bak -e "s|^\(__version__ *=\).*|\1 '$(version)'|"  $(initfile)
	@sed -i .bak -e "s|^\(__description__ *=\).*|\1 '$(desc)'|" $(initfile)
	@sed -i .bak -e "s|^\(__url__ *=\).*|\1 '$(url)'|"	    $(initfile)
	@sed -i .bak -e "s|^\(__author__ *=\).*|\1 '$(author)'|"    $(initfile)
	@sed -i .bak -e "s|^\(__email__ *=\).*|\1 '$(email)'|"	    $(initfile)
	@sed -i .bak -e "s|^\(__license__ *=\).*|\1 '$(license)'|"  $(initfile)

update-meta:;
	@sed -i .bak -e "/version/ s/[0-9].[0-9][0-9]*.[0-9][0-9]*/$(version)/" codemeta.json

update-citation:;
	$(eval date  := $(shell date "+%F"))
	@sed -i .bak -e "/^date-released/ s/[0-9][0-9-]*/$(date)/" CITATION.cff
	@sed -i .bak -e "/^version/ s/[0-9].[0-9][0-9]*.[0-9][0-9]*/$(version)/" CITATION.cff

edited := codemeta.json $(initfile) CITATION.cff

commit-updates:;
	@git add $(edited)
	@git diff-index --quiet HEAD $(edited) || \
	    git commit -m"Update stored version number" $(edited)

release-on-github: | vars update-init update-meta update-citation commit-updates
	$(eval tmp_file  := $(shell mktemp /tmp/release-notes-$(name).XXXX))
	git push -v --all
	git push -v --tags
	@$(info ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓)
	@$(info ┃ Write release notes in the file that gets opened in your   ┃)
	@$(info ┃ editor. Close the editor to complete the release process.  ┃)
	@$(info ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛)
	sleep 2
	$(EDITOR) $(tmp_file)
	gh release create v$(version) -t "Release $(version)" -F $(tmp_file)

print-instructions: vars
	@$(info ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓)
	@$(info ┃ Next steps:                                                ┃)
	@$(info ┃ 1. Check https://github.com/$(repo)/releases )
	@$(info ┃ 2. Wait a few seconds to let web services do their work    ┃)
	@$(info ┃ 3. Run "make update-doi" to update the DOI in README.md    ┃)
	@$(info ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛)

update-doi:;
	@sed -i .bak -e '/doi/ s|10.22002/[0-9]\{1,\}|10.22002/$(doi_tail)|' README.md
	@sed -i .bak -e '/doi/ s|10.22002/[0-9]\{1,\}|10.22002/$(doi_tail)|' CITATION.cff
	git add README.md CITATION.cff
	git commit -m"Update DOI" README.md CITATION.cff && git push -v --all


# Cleanup and miscellaneous directives ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

clean: clean-release clean-other

clean-release:;
	-rm -rf $(name).egg-info codemeta.json.bak $(initfile).bak README.md.bak

clean-other:;
	-rm -fr $(name)/__pycache__

.PHONY: release release-on-github update-init update-meta \
	print-instructions clean
