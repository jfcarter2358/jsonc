.PHONY: bump-major bump-minor bump-patch test pypi-build pypi-test pypi-upload

bump-major:
	bumpversion major jsonc/VERSION

bump-minor:
	bumpversion minor jsonc/VERSION

bump-patch:
	bumpversion patch jsonc/VERSION

pypi-build:
	python setup.py sdist bdist_wheel
	twine check dist/*

pypi-test:
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

pypi-upload:
	twine upload dist/*

test:
	python test.py