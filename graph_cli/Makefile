PROJECT = graph_cli
PYTHON  = python3

.DEFAULT: build

.PHONY: build
build: setup.py $(PROJECT)
	$(PYTHON) setup.py sdist bdist_wheel

dist: build

.PHONY: test
test: $(PROJECT)
	$(PYTHON) -m unittest discover tests

.PHONY: install
install: build
	sudo $(PYTHON) setup.py install --record .install-files

.PHONY: uninstall
uninstall: setup.py .install-files
	cat .install-files | xargs sudo rm -rf
	rm -f .install-files

.PHONY: push
push: dist
	twine upload dist/*

.PHONY: push-test
push-test: dist
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

.PHONY: clean
clean:
	rm -rf build dist *.egg-info $(PROJECT)/*.pyc
