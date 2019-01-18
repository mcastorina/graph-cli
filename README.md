# graph-cli

A CLI utility to create graphs from CSV files.

`graph-cli` is designed to be highly configurable for easy and detailed
graph generation. It has many flags to acquire this detail and uses
reasonable defaults to avoid bothering the user. It also leverages
chaining, so you can create complex graphs from multiple CSV files.

A full list of options can be found in [OPTIONS.md](OPTIONS.md).

## Installation

```
pip install graph-cli
```

## Examples
A few quick examples. For an extended list that further demonstrates
features and usage, please view [EXAMPLES.md](EXAMPLES.md).

```
graph samples/sine.csv -o sine.png
```

![sine](screenshots/sine.png)

```
graph samples/normal.csv --hist -o hist.png
```

![hist](screenshots/hist.png)

```
graph samples/sine.csv --marker '' --chain | \
graph samples/cosine.csv --title 'sine and cosine' \
  --ylabel '' --xscale 250 --marker '' -o sine-cosine.png
```

```
graph samples/sine-cosine.csv --title 'sine and cosine' \
  --ylabel '' --xscale 250 --marker '' -o sine-cosine.png
```

![sine-cosine](screenshots/sine-cosine.png)

```
graph samples/sine.csv --resample 125 -o sine-resample.png
```

![sine-resample](screenshots/sine-resample.png)

```
graph samples/avocado.csv -x 'Date' -y 'AveragePrice' --resample 1W -o avocado-resample.png
```

![avocado-resample](screenshots/avocado-resample.png)

## Donate

I develop this software in my spare time. If you find it useful, consider
buying me a coffee! Thank you!

[![ko-fi](https://www.ko-fi.com/img/donate_sm.png)](https://ko-fi.com/O5O0LAWC)
