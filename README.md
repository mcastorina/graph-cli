# graph-cli

A CLI utility to create graphs from CSV files.

`graph-cli` is designed to be highly configurable for easy and detailed
graph generation. It has many flags to acquire this detail and uses
reasonable defaults to avoid bothering the user. It also leverages
chaining, so you can create complex graphs from multiple CSV files.

## Examples

```
python main.py samples/sine.csv -o sine.png
```

![sine](screenshots/sine.png)

```
python main.py samples/sine.csv --chain  \
| python main.py samples/cosine.csv --title 'sine and cosine' \
  --ylabel '' --xscale 250 -o sine-cosine.png
```

![sine-cosine](screenshots/sine-cosine.png)

## Installation

Currently the only way to use this application is to clone it and install
the requirements. It will soon be available on PyPI.
