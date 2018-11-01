# Examples
An extended list of examples to demonstrate features and usage.

```
graph samples/sine.csv --marker '' --fill
```

![example-01](screenshots/example-01.png)

```
graph samples/sine.csv --marker '' --xrange 0:500
```

![example-02](screenshots/example-02.png)

```
graph samples/sine-cosine.csv --marker '' --style='-.,-' --ylabel 'y' --legend 'sin,cos'
```

![example-03](screenshots/example-03.png)

```
graph samples/bar.csv --bar
```

![example-04](screenshots/example-04.png)

```
graph samples/bar.csv --bar --width 0.4 --offset='-0.2,0.2' --ylabel 'Price ($)'
```

![example-05](screenshots/example-05.png)

```
graph samples/avocado.csv -y 2 --resample 2W
```

![example-06](screenshots/example-06.png)
