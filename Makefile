CWD    = $(CURDIR)
MODULE = $(notdir $(CWD))

NOW = $(shell date +%d%m%y)
REL = $(shell git rev-parse --short=4 HEAD)

PIP = $(CWD)/bin/pip3
PY  = $(CWD)/bin/python3

.PHONY: all
all: systemd
#	bin/jt -t monokai

.PHONY: systemd
systemd: bin/jupyterhub jupyterhub_config.py
	sudo systemctl enable jupyterhub.service
	sudo systemctl stop  jupyterhub.service
	sudo systemctl start jupyterhub.service
	echo http://127.0.0.1:8000/user/$(USER)/tree


.PHONY: test
test:
	$(MAKE) -C $(CWD)/nb/meteo PY=$(PY) $@


.PHONY: doxy
doxy: doxy.gen
	rm -rf $(CWD)/docs ; doxygen $< 1>/dev/null


.PHONY: install
install: os $(PIP)
	$(PIP) install       wheel
	$(PIP) install    -r requirements.txt
	$(MAKE) requirements.txt
	sudo npm install -g configurable-http-proxy
	bin/jupyter contrib nbextension install --user
	bin/jupyter labextension install @jupyterlab/toc

.PHONY: update
update: os $(PIP)
	$(PIP) install -U -r requirements.txt
	$(MAKE) requirements.txt

$(PIP) $(PY):
	python3 -m venv .
	$(CWD)/bin/pip3 install -U pip pylint autopep8 mypy

.PHONY: requirements.txt
requirements.txt: $(PIP)
	$< freeze | grep -v 0.0.0 > $@

.PHONY: os
ifeq ($(OS),Windows_NT)
os: windows
else
os: debian
endif

.PHONY: debian
debian:
	# curl -sL https://deb.nodesource.com/setup_13.x | sudo bash -
	sudo apt update
	sudo apt install -u \
		python3 python3-venv \
		python3-psycopg2 postgresql-plpython3-12 \
		postgresql-12 postgresql-12-postgis-3 pgadmin4 \
		python3-gdal gdal-bin libgdal-dev qgis \
		nodejs \
		redis \
		graphviz yarn


.PHONY: master shadow release zip

MERGE  = Makefile README.md .gitignore .vscode
MERGE += requirements.txt jupyterhub_config.py
MERGE += etc nb/EDS.ipynb

public:
	git checkout $@
	git checkout shadow -- $(MERGE)

shadow:
	git checkout $@

release:
	git tag $(NOW)-$(REL)
	git push -v && git push -v --tags
	git checkout shadow

zip:
	git archive --format zip --output $(MODULE)_src_$(NOW)_$(REL).zip HEAD
