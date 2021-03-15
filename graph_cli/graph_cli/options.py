import argparse
import logging
from sys import stdin, exit
import pandas as pd
import os

# flags that can have multiple values
specific_attrs = [
    'xcol', 'ycol', 'legend', 'color', 'style', 'marker', 'width',
    'offset', 'markersize', 'time_format_input', 'resample'
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
            if type(val) is list:
                # when passing '--' the type becomes a list
                # TODO: investigate why this happens
                val = '--'
            setattr(args, opt, val.split(','))

    # load df
    if args.file == '-': args.file = stdin
    elif not os.path.isfile(args.file):
        logging.error('%s: file not found' % args.file)
        exit(1)
    df = pd.read_csv(args.file)

    # get column names from integers
    args.xcol = [get_column_name(df, x) for x in args.xcol]
    if args.ycol is None:
        # ycol default is every column besides xcols
        ycols = [col for col in df.columns if col not in args.xcol]
    else:
        ycols = [get_column_name(df, y) for y in args.ycol]
    args.ycol = [ycol for ycol in ycols if ycol is not None]

    if sum([args.bar, args.barh, args.hist, args.hist_perc]) > 1:
        logging.error('--bar, --barh, --hist, and --hist-perc are mutually exclusive')
        exit(1)

    # make arguments all the same length
    # by filling in with default values
    fill_args(args)

    # fill in defaults for global arguments, mark as user-specified,
    # and convert types
    fill_global_args(args, df)

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

    args.legend             =  fill_list(args.legend, args.ycol)
    args.color              =  fill_list(args.color, [None], length=num_graphs)
    args.style              =  fill_list(args.style, length=num_graphs)
    args.fill               =  fill_list([args.fill], length=num_graphs)
    args.marker             =  fill_list(args.marker, length=num_graphs)
    args.width              =  fill_list(args.width, length=num_graphs, map_fn=float)
    args.offset             =  fill_list(args.offset, length=num_graphs, map_fn=float)
    args.markersize         =  fill_list(args.markersize, length=num_graphs, map_fn=int)
    args.output             =  [args.output] * num_graphs
    args.time_format_input  =  fill_list(args.time_format_input, length=num_graphs)
    args.resample           =  fill_list(args.resample, length=num_graphs)
    args.sort               =  fill_list([args.sort], length=num_graphs)
    args.bar                =  fill_list([args.bar], length=num_graphs)
    args.barh               =  fill_list([args.barh], length=num_graphs)
    args.hist               =  fill_list([args.hist], length=num_graphs)
    args.hist_perc          =  fill_list([args.hist_perc], length=num_graphs)
    args.bins               =  fill_list([args.bins], length=num_graphs, map_fn=lambda y: None if y is None else int(y))
    args.bin_size           =  fill_list([args.bin_size], length=num_graphs, map_fn=lambda y: None if y is None else float(y))

def fill_global_args(args, df):
    # xlabel
    if args.xlabel is None:
        if any(args.hist + args.hist_perc):
            args.xlabel = (', '.join(args.ycol), False)
        else:
            args.xlabel = (', '.join(set(args.xcol)), False)
    else:
        args.xlabel = (args.xlabel, True)

    # xscale: default is None
    args.xscale = (args.xscale, args.xscale is not None)

    # xrange
    if args.xrange:
        vals = args.xrange.split(':')
        args.xrange = list(map(float, vals))
        args.xrange = (args.xrange, True)
    else:
        args.xrange = (args.xrange, False)

    # ylabel
    if args.ylabel is None:
        if any(args.hist):
            args.ylabel = ('Count', False)
        elif any(args.hist_perc):
            args.ylabel = ('Percent', False)
        else:
            args.ylabel = (', '.join(args.ycol), False)
    else:
        args.ylabel = (args.ylabel, True)

    # yscale: default is None
    args.yscale = (args.yscale, args.yscale is not None)

    # yrange
    if args.yrange:
        vals = args.yrange.split(':')
        args.yrange = list(map(float, vals))
        args.yrange = (args.yrange, True)
    else:
        args.yrange = (args.yrange, False)

    # figsize
    args.figsize = (tuple(map(lambda y: float(y)/100, args.figsize.split('x'))), True)

    # title
    if not args.title:
        if any(args.hist + args.hist_perc):
            args.title = '%s Histogram' % args.xlabel[0]
        else:
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

    # no-grid
    args.no_grid = (args.no_grid, args.no_grid)

    # grid
    if type(args.grid) is list:
        # args.grid is a list when you pass '--'
        # TODO: investigate why this happens
        args.grid = '--'
    args.grid = (args.grid, True)

    # grid-color
    args.grid_color = (args.grid_color, True)

    # grid-alpha
    args.grid_alpha = (args.grid_alpha, True)

    # grid-width
    args.grid_width = (args.grid_width, True)

    # text
    for i in range(len(args.text)):
        pos, msg = args.text[i].split('=', 1)
        pos = (pos.split(':') + [None])[:2]
        args.text[i] = (pos[0], pos[1], msg)
    args.text = (args.text, True)

    # annotate
    for i in range(len(args.annotate)):
        pos, msg = args.annotate[i].split('=', 1)
        pos = pos.split(':')
        if len(pos) == 1:
            # xpos
            xpos, ypos, xtext, ytext = pos + [None]*3
        elif len(pos) == 2:
            # xpos, ycol
            pos[1] = get_column_name(df, pos[1])
            xpos, ypos, xtext, ytext = pos + [None]*2
        else:
            # xtext, ytext, xpos, ypos
            xtext, ytext, xpos, ypos = pos
        args.annotate[i] = ((xpos, ypos), (xtext, ytext), msg)
    args.annotate = (args.annotate, True)

    # exponent range
    args.exponent_range = (tuple(map(float, args.exponent_range.split(':'))), True)

    # output time format
    args.time_format_output = (args.time_format_output, args.time_format_output is not None)

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
    parser = argparse.ArgumentParser(description='Graph CSV data')

    # required arguments
    parser.add_argument('file', metavar='CSV', type=str,
            help='the CSV file to graph')

    # graph specific values
    parser.add_argument('--xcol', '-x', metavar='COL', type=str,
            help='the column number or name to use for the x-axis (default: 1)',
            default='1')
    parser.add_argument('--ycol', '-y', metavar='COL', type=str,
            help='the column number or name to use for the y-axis (default: all other columns)',
            default=None)
    parser.add_argument('--legend', '-l', metavar='LEGEND', type=str,
            help='the label name for the legend (default: match ycol)')
    parser.add_argument('--color', '-c', metavar='COLOR', type=str,
            help='color of the graph (default: auto)')
    parser.add_argument('--style', metavar='STYLE', type=str,
            help='style of the lines')
    parser.add_argument('--fill', action='store_true',
            help='fill in beneath the lines')
    parser.add_argument('--marker', '-m', metavar='MARKER', type=str, default='o',
            help='marker style of the data points')
    parser.add_argument('--width', '-w', type=str,
            help='Line or bar width size')
    parser.add_argument('--offset', type=str, default='0',
            help='Bar chart base offset')
    parser.add_argument('--markersize', type=str, default='6',
            help='Marker (point) size')
    parser.add_argument('--output', '-o', metavar='FILE', type=str,
            help='save the graph to FILE')
    parser.add_argument('--time-format-input', '-f', metavar='FORMAT',
            help='time format of timeseries CSV column (using standard datetime values)')
    parser.add_argument('--time-format-output', '-F', metavar='FORMAT',
            help='display time format (using standard datetime values)')
    parser.add_argument('--resample', '-r', metavar='FREQ',
            help='resample values by FREQ and take the mean')
    parser.add_argument('--sort', '-s', action='store_true',
            help='sort xcol values')
    parser.add_argument('--bar', action='store_true',
            help='create a bar graph')
    parser.add_argument('--barh', action='store_true',
            help='create a barh graph (horizontal bars)')
    parser.add_argument('--hist', action='store_true',
            help='create a histogram from the y columns')
    parser.add_argument('--hist-perc', action='store_true',
            help='create a histogram from the y columns weighted to sum to 100%%')
    parser.add_argument('--bins', type=str,
            help='number of bins to use in the histogram (default: auto)')
    parser.add_argument('--bin-size', type=str,
            help='size of each bin to use in the histogram (default: auto)')

    # global values
    parser.add_argument('--xlabel', '-X', metavar='LABEL', type=str,
            help='the x-axis label (default: match xcol)')
    parser.add_argument('--xscale', metavar='SCALE', type=float,
            help='the x-axis scaling (default: auto)')
    parser.add_argument('--xrange', metavar='RANGE', type=str,
            help='the x-axis window (min:max) (default: auto)')
    parser.add_argument('--ylabel', '-Y', metavar='LABEL', type=str,
            help='the y-axis label (default: match ycol)')
    parser.add_argument('--yscale', metavar='SCALE', type=float,
            help='the y-axis scaling (default: auto)')
    parser.add_argument('--yrange', metavar='RANGE', type=str,
            help='the y-axis window (min:max) (default: auto)')
    parser.add_argument('--figsize', metavar='SIZE', type=str,
            help='size of the graph (XxY) (default: 800x500)', default='800x500')
    parser.add_argument('--title', '-T', metavar='TITLE', type=str,
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
    parser.add_argument('--no-grid', action='store_true',
            help='disable grid')
    parser.add_argument('--grid', type=str, default='-.',
            help='grid linestyle')
    parser.add_argument('--grid-color', type=str, default='gray',
            help='grid color')
    parser.add_argument('--grid-alpha', type=float, default=0.5,
            help='grid alpha')
    parser.add_argument('--grid-width', type=float, default=0.5,
            help='grid width')
    parser.add_argument('--text', '-t', type=str, action='append', default=[],
            help='add text to the graph (xpos=text | xpos:ypos=text)')
    parser.add_argument('--annotate', '-a', type=str, action='append', default=[],
            help='add annotation (text and arrow) to the graph '+
            '(xpos=text | xpos:ycol=text | xtext:ytext:xpos:ypos=text)')
    parser.add_argument('--exponent-range', metavar='RANGE', type=str,
            help='the window of 10^n to 10^m  where exponents will not be displayed (n:m) (default: -3:9)',
            default='-3:9')
    parser.add_argument('--chain', '-C', action='store_true',
            help='use this option to combine graphs into a single image')
    return validate_args(parser.parse_args())
