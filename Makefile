.PHONY: bump-major bump-minor bump-patch

bump-major:
	bumpversion major src/jsonc/VERSION

bump-minor:
	bumpversion minor src/jsonc/VERSION

bump-patch:
	bumpversion patch src/jsonc/VERSION

pypi-build:
	python setup.py sdist bdist_wheel
	twine check dist/*

pypi-test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

pypi-upload:
	twine upload dist/*