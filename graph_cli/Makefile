all: build

build: setup.py graph_cli
	python setup.py sdist bdist_wheel

push: dist
	twine upload dist/*

clean:
	rm -rf build dist *.egg-info

.phony: build push clean
