import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    required = f.read().splitlines()

setuptools.setup(
    name="eden-python",
    version="0.2.0",
    author="Mayukh Deb, Gene Kogan",
    author_email="mayukhmainak2000@gmail.com, kogan.gene@gmail.com",
    description="Convert your python function into a hosted endpoint with minimal changes to your existing code",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abraham-ai/eden",
    packages=setuptools.find_packages(),
    install_requires=required,
    python_requires=">=3.6",
    include_package_data=True,
    keywords=["hosting", "machine learning", "neural networks", "generative art"],
    classifiers=[
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
    ],
)
