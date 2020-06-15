PROJECT = graph_cli
PYTHON  = python3

.DEFAULT: build

.PHONY: build test
build: setup.py $(PROJECT)
	$(PYTHON) setup.py sdist bdist_wheel
test: $(PROJECT)
	$(PYTHON) -m unittest discover tests

.PHONY: install uninstall
install: build
	sudo $(PYTHON) setup.py install --record .install-files
uninstall: setup.py .install-files
	cat .install-files | xargs sudo rm -rf
	rm -f .install-files

.PHONY: push push-test
push: dist
	twine upload dist/*
push-test: dist
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

.PHONY: clean
clean:
	rm -rf build dist *.egg-info $(PROJECT)/*.pyc
