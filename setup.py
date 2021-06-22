import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="eden",
    version="0.0.0",
    author="", 
    author_email="", 
    description= "",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abraham-ai/eden",
    packages=setuptools.find_packages(),
    install_requires= required,
    python_requires='>=3.6',   
    include_package_data=True,
    keywords=[
        "machine learning",
        "neural networks",
        ],
    classifiers=[
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ] 
)