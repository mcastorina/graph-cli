# Options
This document details each option in `graph-cli`. There are two "types"
of options: global and line specific. Global options are things like the
title or ylabel, and line specific options are things like width and style.

### Required Options

| Option | Description |
| ------ | ----------- |
| CSV    | the CSV file containing the data to graph |

### Global Options
These options persist across chains and are generally set only once.

| Long | Short | Default | Description |
| ----------- | ------------ | ------- | ----------- |
| --xlabel | -X | match xcol | the x-axis label |
| --xscale |    | auto | the x-axis scaling |
| --xrange |    | auto | the x-axis window (Note: replace `-` with `_` for negative values to avoid argparse bug) |
| --ylabel | -Y | match ycol | the y-axis label |
| --yscale |    | auto | the y-axis scaling |
| --yrange |    | auto | the y-axis window (Note: replace `-` with `_` for negative values to avoid argparse bug) |
| --figsize | | 16x10 | figure dimensions |
| --title  | -t | ylabel vs. xlabel | title of the graph |
| --fontsize |  | 18 | font size on graph |
| --tick-fontsize | | 10 | font size of tick labels |
| --label-fontsize | | 10 | label font size |
| --xtick-fontsize | | 10 | font size of xtick labels |
| --xtick-angle | | 0 | xtick label angle in degrees |
| --xtick-align | | center | xtick label text alignment |
| --xlabel-fontsize | | 10 | xlabel font size |
| --ytick-fontsize | | 10 | font size of ytick labels |
| --ytick-angle | | 0 | ytick label angle in degrees |
| --ytick-align | | center | ytick label text alignment |
| --ylabel-fontsize | | 10 | ylabel font size |
| --chain | -C | false | use this option to combine graphs into a single image |

### Line Specific Options
These options a specific to each invocation of `graph-cli` and can be
used to customize each line. Generally speaking, each of these options
can be a comma separated list.

| Long | Short | Default | Description |
| ----------- | ------------ | ------- | ----------- |
| --xcol | -x | 1 | the column number or name to use for the x-axis |
| --ycol | -y | all other columns | the column number or name to use for the y-axis |
| --legend | -l | match ycol | the label name for the legend |
| --color | -c | auto | the color of the line |
| --style |  | auto | the style of the line (Note: replace `-` with `_` to avoid argparse bug) |
| --marker | -m | o | marker style of the data points (Note: replace `-` with `_` to avoid argparse bug) |
| --width | -w | line: 2, bar: 0.8 | line or bar width size |
| --offset | | 0 | bar chart base offset |
| --markersize | | 2 | marker (point) size |
| --output | -o | | save the graph to a file |
| --time-format | -f | auto | time format of timeseries column (this option can speed up processing of large datasets) |
| --resample | -r | | resample values and take the mean (can be used with timeseries data as well) |
| --sort | -s | false | sort by xcol values |
| --bar | | false | create a bar graph |
| --barh | | false | create a barh graph (horizontal bars) |
