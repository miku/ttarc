SHELL := /bin/bash
TARGETS := ttarc
PKGNAME := ttarc

COMMIT := $(shell git rev-parse --short HEAD)
BUILDTIME := $(shell date -u '+%Y-%m-%dT%H:%M:%SZ')

GOLDFLAGS += -X main.Commit=$(COMMIT)
GOLDFLAGS += -X main.Buildtime=$(BUILDTIME)
GOFLAGS = -ldflags "$(GOLDFLAGS)"

.PHONY: all
all: $(TARGETS)

%: cmd/%/main.go
	go build -o $@ -ldflags "$(GOLDFLAGS)" $<

.PHONY: clean
clean:
	rm -f $(TARGETS)
	rm -f $(PKGNAME)_*.deb
	rm -f $(PKGNAME)*.rpm

.PHONY: deb
deb: all
	mkdir -p packaging/deb/$(PKGNAME)/usr/local/bin
	cp $(TARGETS) packaging/deb/$(PKGNAME)/usr/local/bin
	cd packaging/deb && fakeroot dpkg-deb --build $(PKGNAME) .
	mv packaging/deb/$(PKGNAME)_*.deb .

.PHONY: rpm
rpm: all
	mkdir -p $(HOME)/rpmbuild/{BUILD,SOURCES,SPECS,RPMS}
	cp ./packaging/rpm/$(PKGNAME).spec $(HOME)/rpmbuild/SPECS
	cp $(TARGETS) $(HOME)/rpmbuild/BUILD
	./packaging/rpm/buildrpm.sh $(PKGNAME)
	cp $(HOME)/rpmbuild/RPMS/x86_64/$(PKGNAME)*.rpm .

