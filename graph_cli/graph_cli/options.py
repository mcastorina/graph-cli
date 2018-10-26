import argparse
import logging
from sys import stdin, exit
import pandas as pd
import os

# flags that can have multiple values
specific_attrs = [
    'xcol', 'ycol', 'legend', 'color', 'style', 'marker', 'width',
    'offset', 'markersize', 'time_format', 'resample'
]

def get_column_name(df, col):
    # find column named col
    # if it doesn't exist, see if col is a number
    if col in df.columns:
        return col
    try: return df.columns[int(col)-1]
    except ValueError: pass
    logging.info('Column "%s" not found, ignoring' % col)
    return None

def validate_args(args):
    # convert comma separated args into lists (matches graph.get_graph_def)
    for opt in specific_attrs:
        val = getattr(args, opt)
        if val is not None:
            setattr(args, opt, val.split(','))

    # load df
    if args.file == '-': args.file = stdin
    if not os.path.isfile(args.file):
        logging.error('%s: file not found' % args.file)
        exit(1)
    df = pd.read_csv(args.file)

    # get column names from integers
    ycols = [get_column_name(df, y) for y in args.ycol]
    args.ycol = [ycol for ycol in ycols if ycol is not None]
    args.xcol = [get_column_name(df, x) for x in args.xcol]

    if args.bar and args.barh:
        logging.warning('Both --bar and --barh given. Using --bar')
        args.barh = False

    # make arguments all the same length
    # by filling in with default values
    fill_args(args)

    # fill in defaults for global arguments, mark as user-specified,
    # and convert types
    fill_global_args(args)

    # save actual data in xcol and ycol
    args.ycol = [df[ycol].copy() for ycol in args.ycol]
    args.xcol = [df[xcol].copy() for xcol in args.xcol]

    return args

def fill_args(args):
    # TODO: is this reasonable?
    num_graphs = len(args.ycol)

    if args.width is None:
        if args.bar or args.barh:
            args.width = [0.8]
        else:
            args.width = [2]

    # make x and y arrays the same length
    # usually the x value will be shorter than y
    # so repeat the last x value
    args.xcol = fill_list(args.xcol, [args.xcol[-1]], num_graphs)

    args.legend      =  fill_list(args.legend, args.ycol)
    args.color       =  fill_list(args.color, [None], length=num_graphs)
    args.style       =  fill_list(args.style, length=num_graphs)
    args.marker      =  fill_list(args.marker, length=num_graphs)
    args.width       =  fill_list(args.width, length=num_graphs, map_fn=float)
    args.offset      =  fill_list(args.offset, length=num_graphs, map_fn=float)
    args.markersize  =  fill_list(args.markersize, length=num_graphs, map_fn=int)
    args.output      =  [args.output] * num_graphs
    args.time_format =  fill_list(args.time_format, [None], num_graphs)
    args.resample    =  fill_list(args.resample, [None], num_graphs)
    args.sort        =  fill_list([args.sort], length=num_graphs)
    args.bar         =  fill_list([args.bar], length=num_graphs)
    args.barh        =  fill_list([args.barh], length=num_graphs)

def fill_global_args(args):
    # xlabel
    if args.xlabel is None:
        args.xlabel = (', '.join(set(args.xcol)), False)
    else:
        args.xlabel = (args.xlabel, True)

    # xscale: default is None
    args.xscale = (args.xscale, args.xscale is not None)

    # xrange
    if args.xrange:
        vals = args.xrange.split('-')
        args.xrange = list(map(lambda y: float(y.replace('_', '-')), vals))
        args.xrange = (args.xrange, True)
    else:
        args.xrange = (args.xrange, False)

    # ylabel
    if args.ylabel is None:
        args.ylabel = (', '.join(args.ycol), False)
    else:
        args.ylabel = (args.ylabel, True)

    # yscale: default is None
    args.yscale = (args.yscale, args.yscale is not None)

    # yrange
    if args.yrange:
        vals = args.yrange.split('-')
        args.yrange = list(map(lambda y: float(y.replace('_', '-')), vals))
        args.yrange = (args.yrange, True)
    else:
        args.yrange = (args.yrange, False)

    # figsize
    args.figsize = (tuple(map(int, args.figsize.split('x'))), True)

    # title
    if not args.title:
        args.title = '%s vs %s' % (args.ylabel[0], args.xlabel[0])
        args.title = (args.title, False)
    else:
        args.title = (args.title, True)

    # fontsize: default is already set
    args.fontsize = (args.fontsize, True)

    # tick-fontsize
    args.tick_fontsize = (args.tick_fontsize, args.tick_fontsize is not None)

    # label-fontsize
    args.label_fontsize = (args.label_fontsize, args.label_fontsize is not None)

    # xtick-fontsize
    args.xtick_fontsize = (args.xtick_fontsize, True)

    # xtick-angle
    if args.xtick_angle is None:
        args.xtick_angle = (0, False)
    else:
        args.xtick_angle = (args.xtick_angle % 360, True)

    # xtick-align
    if args.xtick_align is None:
        args.xtick_align = 'center'
        if args.xtick_angle[0] > 15:
            args.xtick_align = 'right'
        elif args.xtick_angle[0] > 285:
            args.xtick_align = 'left'
        args.xtick_align = (args.xtick_align, False)
    else:
        args.xtick_align = (args.xtick_align, True)

    # xlabel-fontsize
    args.xlabel_fontsize = (args.xlabel_fontsize, True)

    # ytick-fontsize
    args.ytick_fontsize = (args.ytick_fontsize, True)

    # ytick-angle
    if args.ytick_angle is None:
        args.ytick_angle = (0, False)
    else:
        args.ytick_angle = (args.ytick_angle, True)

    # ytick-align
    if args.ytick_align is None:
        args.ytick_align = ('center', False)
    else:
        args.ytick_align = (args.ytick_align, True)

    # ylabel-fontsize
    args.ylabel_fontsize = (args.ylabel_fontsize, True)

# replace None in array with value from default_vals
def fill_list(lst, default_vals=None, length=None, map_fn=None):
    if not lst:
        lst = []
    if default_vals is None:
        val = lst[0] if len(lst) >= 1 else None
        default_vals = [val]
    if not length:
        length = len(default_vals)
    lst += [None] * (length - len(lst))
    for i in range(len(lst)):
        if lst[i] == None:
            lst[i] = default_vals[i % len(default_vals)]
    if map_fn:
        lst = list(map(map_fn, lst))
    return lst

def parse_args():
    parser = argparse.ArgumentParser(
            description='Graph CSV data')

    # required arguments
    parser.add_argument('file', metavar='CSV', type=str,
            help='the CSV file to graph')

    # graph specific values
    parser.add_argument('--xcol', '-x', metavar='COL', type=str,
            help='the column number or name to use for the x-axis (default: 1)',
            default='1')
    parser.add_argument('--ycol', '-y', metavar='COL', type=str,
            help='the column number or name to use for the y-axis (default: 2)',
            default='2')
    parser.add_argument('--legend', '-l', metavar='LEGEND', type=str,
            help='the label name for the legend (default: match ycol)')
    parser.add_argument('--color', '-c', metavar='COLOR', type=str,
            help='color of the graph (default: auto)')
    parser.add_argument('--style', metavar='STYLE', type=str,
            help='style of the lines (Note: replace "-" with "_" to avoid argparse bug)')
    parser.add_argument('--marker', '-m', metavar='MARKER', type=str, default='o',
            help='marker style of the data points (Note: replace "-" with "_" to avoid argparse bug)')
    parser.add_argument('--width', '-w', type=str,
            help='Line or bar width size')
    parser.add_argument('--offset', type=str, default='0',
            help='Bar chart base offset')
    parser.add_argument('--markersize', type=str, default='6',
            help='Marker (point) size')
    parser.add_argument('--output', '-o', metavar='FILE', type=str,
            help='save the graph to FILE')
    parser.add_argument('--time-format', '-f', metavar='FORMAT',
            help='time format of timeseries column (using standard datetime values)')
    parser.add_argument('--resample', '-r', metavar='FREQ',
            help='resample values by FREQ and take the mean')
    parser.add_argument('--sort', '-s', action='store_true',
            help='sort xcol values')
    parser.add_argument('--bar', action='store_true',
            help='create a bar graph')
    parser.add_argument('--barh', action='store_true',
            help='create a barh graph (horizontal bars)')

    # global values
    parser.add_argument('--xlabel', '-X', metavar='LABEL', type=str,
            help='the x-axis label (default: match xcol)')
    parser.add_argument('--xscale', metavar='SCALE', type=float,
            help='the x-axis scaling (default: auto)')
    parser.add_argument('--xrange', metavar='RANGE', type=str,
            help='the x-axis window (Note: replace "-" with "_" for negative values to avoid argparse bug) (default: auto)')
    parser.add_argument('--ylabel', '-Y', metavar='LABEL', type=str,
            help='the y-axis label (default: match ycol)')
    parser.add_argument('--yscale', metavar='SCALE', type=float,
            help='the y-axis scaling (default: auto)')
    parser.add_argument('--yrange', metavar='RANGE', type=str,
            help='the y-axis window (Note: replace "-" with "_" for negative values to avoid argparse bug) (default: auto)')
    parser.add_argument('--figsize', metavar='SIZE', type=str,
            help='size of the graph (default: 16x10)', default='16x10')
    parser.add_argument('--title', '-t', metavar='TITLE', type=str,
            help='title of the graph (default: ylabel vs. xlabel)')
    parser.add_argument('--fontsize', type=int, default=18,
            help='font size')
    parser.add_argument('--tick-fontsize', type=int,
            help='tick font size')
    parser.add_argument('--label-fontsize', type=int,
            help='label font size')
    parser.add_argument('--xtick-fontsize', type=int, default=10,
            help='xtick font size')
    parser.add_argument('--xtick-angle', type=float,
            help='xtick label angle (degrees)')
    parser.add_argument('--xtick-align', type=str,
            help='xtick label text alignment')
    parser.add_argument('--xlabel-fontsize', type=int, default=10,
            help='xlabel font size')
    parser.add_argument('--ytick-fontsize', type=int, default=10,
            help='ytick font size')
    parser.add_argument('--ytick-angle', type=float,
            help='ytick label angle (degrees)')
    parser.add_argument('--ytick-align', type=str,
            help='ytick label text alignment')
    parser.add_argument('--ylabel-fontsize', type=int, default=10,
            help='ylabel font size')
    parser.add_argument('--chain', '-C', action='store_true',
            help='use this option to combine graphs into a single image')
    return validate_args(parser.parse_args())
