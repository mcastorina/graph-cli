#!/usr/bin/python2

import pandas as pd
import argparse
from sys import argv, exit, stdout, stderr, stdin
import pickle
import numpy as np

# disables screen requirement for plotting
# must be called before importing matplotlib.pyplot
import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
from matplotlib.dates import SecondLocator, AutoDateFormatter

# graph_defs is an array of dictionaries defining each line on the graph
# {
#   x: 'column name in df',
#   xlabel: 'string',
#   xscale: float,
#   y: 'column name in df',
#   ylabel: 'string',
#   yscale: float,
#   legend: 'string',
#   title: 'string',
#   color: 'string'
#   style: 'string'
#   marker: 'string'
#   xrange: [int, int]
#   yrange: [int, int]
#   timeseries: boolean
# }
def generate_graph(df, graph_defs, figax=None, filename=None):
    if figax is None: fig, ax = plt.subplots(figsize=(16, 10))
    else: fig, ax = figax
    title = ''
    xlabel = ''
    xscale = yscale = None
    x_range = y_range = None
    timeseries = False
    no_legend = False
    try:
        for graph_def in graph_defs:
            x_name = graph_def['x']
            y_name = graph_def['y']
            ylabel = graph_def['ylabel'] if 'ylabel' in graph_def else ''
            style = ''
            marker = 'o'
            if 'xlabel' in graph_def:       xlabel = graph_def['xlabel']
            if 'title' in graph_def:        title = graph_def['title']
            if 'xscale' in graph_def:       xscale = graph_def['xscale']
            if 'yscale' in graph_def:       yscale = graph_def['yscale']
            if 'style' in graph_def:        style = graph_def['style']
            if 'marker' in graph_def:       marker = graph_def['marker']
            if 'xrange' in graph_def:       x_range = graph_def['xrange']
            if 'yrange' in graph_def:       y_range = graph_def['yrange']
            if 'timeseries' in graph_def:   timeseries = graph_def['timeseries']
            if 'no_legend' in graph_def:    no_legend = graph_def['no_legend']
            data = df[[x_name,y_name]].dropna()
            l = ax.plot(data[x_name], data[y_name], label=graph_def['legend'], marker=marker, color=graph_def['color'], linestyle=style)[0]

    except Exception as e:
        stderr.write("Error: %s\n" % str(e))
        return None
    if xlabel == '':
        xlabel = x_name
    if title == '':
        title = '%s vs %s' % (y_name, xlabel)

    if xscale is not None:
        if timeseries:
            loc = SecondLocator(interval=int(xscale))
            ax.xaxis.set_major_locator(loc)
            ax.xaxis.set_major_formatter(AutoDateFormatter(loc))
        else:
            plt.xticks(np.arange(round(ax.get_xlim()[0] / xscale) * xscale, ax.get_xlim()[1], xscale))
    if yscale is not None:
        plt.yticks(np.arange(round(ax.get_ylim()[0] / yscale) * yscale, ax.get_ylim()[1], yscale))

    if x_range is not None: plt.xlim(x_range[0], x_range[1])
    if y_range is not None: plt.ylim(y_range[0], y_range[1])

    plt.xlabel(xlabel)
    # TODO: only add legend for some graphs
    if not no_legend:
        plt.legend()
    plt.grid(True, alpha=0.5, linestyle='-.')
    plt.ylabel(ylabel)
    plt.title(title)
    fig.autofmt_xdate()

    if filename is not None:
        plt.savefig(filename)
    return fig, ax

def parse_args():
    parser = argparse.ArgumentParser(
            description='Graph CSV data')
    parser.add_argument('file', metavar='CSV', type=str,
            help='the CSV file to graph')
    parser.add_argument('--xcol', '-x', metavar='COL', type=str,
            help='the column number or name to use for the x-axis (default: 1)', default='1')
    parser.add_argument('--xlabel', '-X', metavar='LABEL', type=str,
            help='the x-axis label (default: match xcol)')
    parser.add_argument('--xscale', metavar='SCALE', type=float,
            help='the x-axis scaling (default: auto)')
    parser.add_argument('--xrange', metavar='RANGE', type=str,
            help='the x-axis window (Note: replace "-" with "_" for negative values to avoid argparse bug) (default: auto)')
    parser.add_argument('--ycol', '-y', metavar='COL', type=str,
            help='the column number or name to use for the y-axis (default: 2)', default='2')
    parser.add_argument('--ylabel', '-Y', metavar='LABEL', type=str,
            help='the y-axis label (default: match ycol)')
    parser.add_argument('--yscale', metavar='SCALE', type=float,
            help='the y-axis scaling (default: auto)')
    parser.add_argument('--yrange', metavar='RANGE', type=str,
            help='the y-axis window (Note: replace "-" with "_" for negative values to avoid argparse bug) (default: auto)')
    parser.add_argument('--legend', '-l', metavar='LEGEND', type=str,
            help='the label name for the legend (default: match ycol)')
    parser.add_argument('--no-legend', action='store_true',
            help='do not draw the legend')
    parser.add_argument('--title', '-t', metavar='TITLE', type=str,
            help='title of the graph (default: ylabel vs. xlabel)')
    parser.add_argument('--color', '-c', metavar='COLOR', type=str,
            help='color of the graph (default: auto)', default=None)
    parser.add_argument('--style', '-s', metavar='STYLE', type=str,
            help='style of the lines (Note: replace "-" with "_" to avoid argparse bug)', default=None)
    parser.add_argument('--marker', '-m', metavar='MARKER', type=str,
            help='marker style of the data points (Note: replace "-" with "_" to avoid argparse bug)', default=None)
    parser.add_argument('--output', '-o', metavar='FILE', type=str,
            help='save the graph to FILE')
    parser.add_argument('--timeseries', '-T', action='store_true',
            help='Convert the x column to time before graphing')
    parser.add_argument('--time-format', '-f', metavar='FORMAT', default=None,
            help='Time format of timeseries column (using standard datetime values)')
    parser.add_argument('--resample', '-r', metavar='FREQ',
            help='Resample values by FREQ and take the mean')
    parser.add_argument('--sum', action='store_true',
            help='Sum instead of mean when resampling')
    parser.add_argument('--fontsize', type=int, default=18,
            help='Font size')
    parser.add_argument('--linewidth', type=int, default=2,
            help='Line width size')
    parser.add_argument('--markersize', type=int, default=6,
            help='Marker (point) size')
    parser.add_argument('--chain', '-C', action='store_true',
            help='Use this option to chain graph commands. e.g. `python graph.py ... -C | python graph.py ... -o file.png`')
    return parser.parse_args()

def get_column_name(df, col):
    # find column named col
    # if it doesn't exist, see if col is a number
    if col in df.columns:
        return col
    try: return df.columns[int(col)-1]
    except ValueError: pass
    stderr.write('Column "%s" not found, ignoring.\n' % col)
    return None

def sum_groupby(df, ycols):
    if any([df[ycol].dtype[0].kind == 'O' for ycol in ycols]):
        return df.nunique()
    return df.sum()

if __name__ == '__main__':
    args = parse_args()

    # update font
    matplotlib.rcParams.update({'font.size': args.fontsize})
    matplotlib.rcParams.update({'lines.linewidth': args.linewidth})
    matplotlib.rcParams.update({'lines.markersize': args.markersize})

    # read stdin for chained data and unpickle into figax
    count = 0
    figax = None
    # check if stdin is not a terminal
    if not stdin.isatty() and args.file != '-':
        count, figax = pickle.loads(stdin.read())

    # load df
    if args.file == '-': args.file = stdin
    df = pd.read_csv(args.file)

    # get all args that are comma separated
    # xcol, ycol, legend, color, style
    ycols = [get_column_name(df, y) for y in args.ycol.split(',')]
    ycols = [ycol for ycol in ycols if ycol is not None]
    xcols = [get_column_name(df, x) for x in args.xcol.split(',')]
    # make xcols match ycols
    xcols = (xcols * len(ycols))[:len(ycols)]

    if args.legend is not None: legends = args.legend.split(',')
    else: legends = ycols
    if args.color is not None: colors = args.color.split(',')
    else: colors = ['C%d' % x for x in range(len(ycols))]
    if args.style is not None: styles = args.style.replace('_', '-').split(',')
    else: styles = [None]*len(ycols)
    if args.marker is not None: markers = args.marker.replace('_', '-').split(',')
    else: markers = ['o']*len(ycols)

    # set defaults
    if args.ylabel is None: args.ylabel = ', '.join(ycols)
    if args.xlabel is None: args.xlabel = ', '.join(set(xcols))
    if args.title is None: args.title = '%s vs. %s' % (args.ylabel, args.xlabel)
    if args.xrange is not None:
        args.xrange = list(map(lambda y: float(y.replace('_', '-')), args.xrange.split('-')))[:2]
        if len(args.xrange) != 2 or args.xrange[0] > args.xrange[1]:
            stderr.write('--xrange needs to be in the form "LOW-HIGH"\n')
            exit(1)
    if args.yrange is not None:
        args.yrange = list(map(lambda y: float(y.replace('_', '-')), args.yrange.split('-')))[:2]
        if len(args.yrange) != 2 or args.yrange[0] > args.yrange[1]:
            stderr.write('--yrange needs to be in the form "LOW-HIGH"\n')
            exit(1)

    # delete not needed columns
    for col in df.columns:
        if col not in set(xcols + ycols):
            del df[col]

    for xcol in set(xcols):
        # set x as index
        df.set_index(xcol, inplace=True)

        # change x column to time
        if args.timeseries:
            df.index = pd.to_datetime(df.index, format=args.time_format)
            if args.resample != None:
                try:
                    df = df.resample(args.resample)
                    if args.sum: df = sum_groupby(df, ycols)
                    else:        df = df.mean()
                except Exception as e:
                    stderr.write('Error: Could not resample. "%s"\n' % str(e))
                    exit(1)
            # unset x as index
            df.reset_index(inplace=True)
            if args.xscale is None:
                args.xscale = 30
        elif args.resample != None:
            args.resample = float(args.resample)
            # unset x as index
            df.reset_index(inplace=True)

            x_min = df[xcol].min()
            x_max = df[xcol].max()
            bins = np.linspace(x_min + args.resample/2, x_max - args.resample/2, float(x_max - x_min + args.resample)/args.resample)
            df = df.groupby(np.digitize(df[xcol], bins))
            if args.sum: df = sum_groupby(df, ycols)
            else:        df = df.mean()
        else:
            # unset x as index
            df.reset_index(inplace=True)

        df.sort_values(xcol, inplace=True)

    # generate graph_defs
    graph_defs = []
    for xcol, ycol, legend, color, style, marker in zip(xcols, ycols, legends, colors, styles, markers):
        if xcol is None or ycol is None: continue
        xlabel, ylabel = args.xlabel, args.ylabel

        if xlabel is None: xlabel = xcol
        if ylabel is None: ylabel = ycol
        if legend is None: legend = ycol

        # generate graph
        graph_defs += [{
            'x': xcol, 'y': ycol,
            'xlabel': xlabel, 'ylabel': ylabel,
            'xscale': args.xscale, 'yscale': args.yscale,
            'legend': legend,
            'title': args.title, 'color': color, 'style': style, 'marker': marker,
            'xrange': args.xrange, 'yrange': args.yrange,
            'timeseries': args.timeseries,
            'no_legend': args.no_legend
        }]
    figax = generate_graph(df, graph_defs, figax, args.output)

    # pickle and print figax if chain
    if args.chain:
        stdout.write(pickle.dumps((count+1, figax)))
