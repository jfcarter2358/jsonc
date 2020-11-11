import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open("jsonc/VERSION", "r") as f:
    version = f.read()

setuptools.setup(
    name="jsoncparser",
    version=version,
    author="John Carter",
    author_email="jfcarter2358@gmail.com",
    license="MIT",
    description="A Python package to enable reading/writing of json files with comments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jfcarter2358/jsonc",
    packages=setuptools.find_packages(),
    python_requires=">=3.7"
)
