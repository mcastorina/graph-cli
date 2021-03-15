import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="graph_cli",
    version="0.1.9",
    author="miccah",
    author_email="m.castorina93@gmail.com",
    description="A CLI utility to create graphs from CSV files.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mcastorina/graph-cli",
    packages=setuptools.find_packages(),
    install_requires=[
        "numpy",
        "pandas",
        "matplotlib",
    ],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    entry_points={
        'console_scripts': [
            'graph=graph_cli:main.main',
        ],
    },
)
