build: setup.py graph_cli
	python setup.py sdist bdist_wheel

push: dist
	twine upload dist/*

push-test: dist
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

clean:
	rm -rf build dist *.egg-info graph_cli/*.pyc

.PHONY: build push push-test clean
