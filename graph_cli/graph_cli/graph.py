from sys import stdin
import sys
# set default encoding to utf8 instead of ascii for python2
if sys.version_info[0] == 2:
    reload(sys)
    sys.setdefaultencoding('utf8')

import numpy as np
import pickle
from math import sin, cos, pi

import pandas as pd
import numpy as np
import logging

graph_global_fns = ['update_globals', 'dump', 'remove_global_flags']

class Graph:
    # static variables
    xlabel = None
    xscale = None
    xrange = None
    ylabel = None
    yscale = None
    yrange = None
    title = None
    figsize = None
    fontsize = None
    tick_fontsize = None
    label_fontsize = None
    xtick_fontsize = None
    ytick_fontsize = None
    xlabel_fontsize = None
    ylabel_fontsize = None
    no_grid = None
    grid = None
    grid_color = None
    grid_alpha = None
    grid_width = None
    text = None
    annotate = None
    xtick_angle = None
    ytick_angle = None
    xtick_align = None
    ytick_align = None
    exponent_range = None
    time_format_output = None
    def __init__(self):
        self.xcol = None
        self.ycol = None
        self.legend = None
        self.color = None
        self.style = None
        self.fill = None
        self.marker = None
        self.width = None
        self.offset = None
        self.markersize = None
        self.output = None
        self.time_format_input = None
        self.resample = None
        self.sort = None
        self.bar = None
        self.barh = None
        self.hist = None
        self.hist_perc = None
        self.bins = None
        self.bin_size = None
        self.timeseries = None
    def __str__(self):
        return str(self.__data__())
    def __repr__(self):
        return self.__str__()
    def __data__(self):
        data = {'globals': {}, 'attributes': {}}
        for attr in [y for y in dir(Graph)
                if not (y.startswith('__') and y.endswith('__'))]:
            if attr in graph_global_fns: continue
            data['globals'][attr] = getattr(Graph, attr)
        for attr in [y for y in dir(self)
                if not (y.startswith('__') and y.endswith('__'))]:
            if attr in graph_global_fns: continue
            if attr in data['globals']: continue
            data['attributes'][attr] = getattr(self, attr)
        data['attributes']['xcol'] = str(data['attributes']['xcol']).split('\n')[-1]
        data['attributes']['ycol'] = str(data['attributes']['ycol']).split('\n')[-1]
        return data
    @staticmethod
    def update_globals(args):
        # first load previous pickled globals
        # loop through all attributes that don't start and end with '__'
        for attr in [y for y in dir(Graph)
                if not (y.startswith('__') and y.endswith('__'))]:
            if attr in graph_global_fns: continue
            if attr not in dir(args): continue
            val = getattr(args, attr)
            cur = getattr(Graph, attr)
            # if the attribute has already been set and index 1
            # (flag for user-set) is False, then update
            if cur is None:
                setattr(Graph, attr, val)
            if type(cur) is tuple and not cur[1]:
                setattr(Graph, attr, val)
            if type(cur) is tuple and cur[1] and type(val) is tuple and val[1]:
                # if list, append
                if type(val[0]) is list:
                    val = (cur[0] + val[0], val[1])
                setattr(Graph, attr, val)
    @staticmethod
    def dump(graphs):
        return (graphs, graphs[0].__data__()['globals'])
    @staticmethod
    def remove_global_flags():
        for attr in [y for y in dir(Graph)
                if not (y.startswith('__') and y.endswith('__'))]:
            if attr in graph_global_fns: continue
            val = getattr(Graph, attr)
            if type(val) is tuple:
                setattr(Graph, attr, val[0])

def process_graph_def(g):
    g.timeseries = False
    try:
        # automatically convert to datetime
        # if time_format is specified or the column type is object
        if g.time_format_input is not None:
            g.xcol = pd.to_datetime(g.xcol, format=g.time_format_input)
            g.timeseries = True
        elif g.xcol.dtype == np.dtype('O'):
            g.xcol = pd.to_datetime(g.xcol)
            g.timeseries = True
    except: pass

    # sort
    if g.sort:
        df = pd.DataFrame({g.xcol.name: g.xcol, g.ycol.name: g.ycol})
        df.sort_values(g.xcol.name, inplace=True)
        xcol, ycol = df[g.xcol.name], df[g.ycol.name]
    # resample
    if g.resample:
        df = pd.DataFrame({g.xcol.name: g.xcol, g.ycol.name: g.ycol})
        try:
            if g.timeseries:
                df.set_index(g.xcol, inplace=True)
                # TODO: figure out what to do with NA
                df = df.resample(g.resample).mean().dropna()
                df.reset_index(inplace=True)
            else:
                x_min, x_max = df[g.xcol.name].min(), df[g.xcol.name].max()
                g.resample = float(g.resample)
                bins = np.linspace(x_min + g.resample/2,
                        x_max - g.resample/2,
                        float(x_max - x_min + g.resample)/g.resample)
                df = df.groupby(np.digitize(df[g.xcol.name], bins)).mean().dropna()
        except Exception as e:
            logging.error('Error: Could not resample. "%s"' % str(e))
            exit(1)
        g.xcol, g.ycol = df[g.xcol.name], df[g.ycol.name]

def get_graph_def(xcol, ycol, legend, color, style, fill, marker, width,
        offset, markersize, output, time_format_input, resample, sort, bar, barh,
        hist, hist_perc, bins, bin_size):
    # get dict of args (must match Graph attribute names)
    from copy import copy
    kvs = copy(locals())
    # build graph
    g = Graph()
    for attr, val in kvs.items():
        setattr(g, attr, val)
    # apply functions in preparation of graphing
    process_graph_def(g)
    return g

def get_graph_defs(args):
    graphs, globals = read_chain(args)
    class AttrDict(dict):
        def __init__(self, *args, **kwargs):
            super(AttrDict, self).__init__(*args, **kwargs)
            self.__dict__ = self
    Graph.update_globals(AttrDict(globals))

    # zip together options.specific_attrs with default values
    # and generate graphs definitions
    for g in zip(args.xcol, args.ycol, args.legend, args.color, args.style,
            args.fill, args.marker, args.width, args.offset, args.markersize,
            args.output, args.time_format_input, args.resample, args.sort,
            args.bar, args.barh, args.hist, args.hist_perc, args.bins,
            args.bin_size):
        graphs += [get_graph_def(*g)]

    return graphs

def read_chain(args):
    chain = ([], {})
    # read stdin for chained data and unpickle into chain array
    # check if stdin is not a terminal
    if stdin is not None and not stdin.isatty() and args.file != stdin:
        data = stdin.buffer.read()
        if len(data) > 0:
            chain = pickle.loads(data)

    # check our data is what we expect it to be
    # TODO: error handling
    assert(isinstance(chain, tuple))
    assert(len(chain) == 2)
    assert(isinstance(chain[0], list))
    assert(isinstance(chain[1], dict))
    for link in chain[0]:
        assert(isinstance(link, Graph))

    return chain

def create_graph(graphs):
    import matplotlib
    if graphs[-1].output:
        # disables screen requirement for plotting
        # must be called before importing matplotlib.pyplot
        matplotlib.use('Agg')
    else:
        # sets backend to qt4
        # required for python2
        matplotlib.rcParams['backend'] = 'Qt5Agg'
    import matplotlib.pyplot as plt
    from matplotlib.ticker import PercentFormatter, ScalarFormatter
    from matplotlib.dates import DateFormatter

    # set global fontsize if any
    if Graph.fontsize[1]:
        plt.rcParams.update({'font.size': Graph.fontsize[0]})
        # TODO: override individual font settings
        if Graph.label_fontsize[1] is False:
            Graph.xlabel_fontsize = (None, False)
            Graph.ylabel_fontsize = (None, False)
        if Graph.tick_fontsize[1] is False:
            Graph.xtick_fontsize = (None, False)
            Graph.ytick_fontsize = (None, False)

    # make Graph.global = (val, flag) just val
    Graph.remove_global_flags()

    # create figure
    fig, ax = plt.subplots(figsize=(Graph.figsize))

    # iterate over graphs array
    for graph in graphs:
        if graph.bar:
            x = np.arange(len(graph.xcol))
            ax.bar(x + graph.offset, graph.ycol, align='center',
                label=graph.legend, color=graph.color, width=graph.width)
            plt.xticks(x, graph.xcol)
        elif graph.barh:
            x = np.arange(len(graph.xcol))
            ax.barh(x + graph.offset, graph.ycol, align='center',
                label=graph.legend, color=graph.color, height=graph.width)
            plt.yticks(x, graph.xcol)
        elif graph.hist or graph.hist_perc:
            bins = graph.bins
            if bins is None and graph.bin_size is None:
                # default: one bin for each
                bins = int((graph.ycol.max() - graph.ycol.min()))
            elif graph.bin_size:
                _min, _max, _bin = graph.ycol.min(), graph.ycol.max(), graph.bin_size
                bins = np.arange(_min - (_min % _bin),
                        _max + (_bin - (_max % _bin)), _bin)
            weights = np.ones_like(graph.ycol)
            if graph.hist_perc:
                weights = weights * 100.0 / len(graph.ycol)
                ax.yaxis.set_major_formatter(PercentFormatter(xmax=100, decimals=1))
            ax.hist(graph.ycol, bins=bins, weights=weights)
        else:
            l = ax.plot(graph.xcol, graph.ycol, label=graph.legend,
                marker=graph.marker, color=graph.color, linestyle=graph.style,
                linewidth=graph.width, markersize=graph.markersize)[0]
            if not graph.timeseries:
                yformat = ScalarFormatter(useOffset=False, useMathText=True)
                xformat = ScalarFormatter(useOffset=False, useMathText=True)
                yformat.set_powerlimits(Graph.exponent_range)
                xformat.set_powerlimits(Graph.exponent_range)
                ax.yaxis.set_major_formatter(yformat)
                ax.xaxis.set_major_formatter(xformat)
            elif graph.timeseries and Graph.time_format_output is not None:
                xformat = DateFormatter(Graph.time_format_output)
                ax.xaxis.set_major_formatter(xformat)
            if graph.fill:
                ax.fill_between(graph.xcol, graph.ycol, alpha=0.1,
                color=l.get_color())
        if graph.output:
            apply_globals(plt, ax, graphs)
            plt.savefig(graph.output)
        elif graph == graphs[-1]:
            apply_globals(plt, ax, graphs)
            plt.show()

def apply_globals(plt, ax, graphs):
    if Graph.tick_fontsize is not None:
        Graph.xtick_fontsize = Graph.tick_fontsize
        Graph.ytick_fontsize = Graph.tick_fontsize
    if Graph.label_fontsize is not None:
        Graph.xlabel_fontsize = Graph.label_fontsize
        Graph.ylabel_fontsize = Graph.label_fontsize
    plt.xlabel(Graph.xlabel, fontsize=Graph.xlabel_fontsize)
    plt.ylabel(Graph.ylabel, fontsize=Graph.ylabel_fontsize)
    plt.title(Graph.title)
    plt.setp(ax.get_xticklabels(), fontsize=Graph.xtick_fontsize,
        rotation=Graph.xtick_angle, horizontalalignment=Graph.xtick_align)
    plt.setp(ax.get_yticklabels(), fontsize=Graph.ytick_fontsize,
        rotation=Graph.ytick_angle, verticalalignment=Graph.ytick_align)

    if Graph.xscale is not None:
        plt.xticks(np.arange(round(ax.get_xlim()[0] / Graph.xscale) *
            Graph.xscale, ax.get_xlim()[1], Graph.xscale))
    if Graph.yscale is not None:
        plt.yticks(np.arange(round(ax.get_ylim()[0] / Graph.yscale) *
            Graph.yscale, ax.get_ylim()[1], Graph.yscale))
    if Graph.xrange is not None:
        plt.xlim(*Graph.xrange)
    if Graph.yrange is not None:
        plt.ylim(*Graph.yrange)

    xcols = [g.xcol.name for g in graphs]
    ycols = [g.ycol.name for g in graphs]
    dfs = [pd.DataFrame({g.xcol.name: g.xcol, g.ycol.name: g.ycol}) for g in graphs]
    df = dfs[0]
    # TODO: this might cause issues with separate csv files with similar column names
    for frame in dfs[1:]:
        df = pd.merge(df, frame)

    # text
    for i in range(len(Graph.text)):
        xpos, ypos, msg = Graph.text[i]
        xpos = float(xpos)
        if ypos is None:
            # xpos
            # add ypos as the mean of all lines at that xpos
            ypos = get_ypos(df, xpos, zip(xcols, ycols))
        Graph.text[i] = (xpos, float(ypos), msg)

    # annotate
    for i in range(len(Graph.annotate)):
        pos, textpos, msg = Graph.annotate[i]
        pos = (float(pos[0]), pos[1])
        if pos[1] is None:
            # xpos
            # choose a ycol (cycle through all ycols)
            pos = (pos[0], ycols[i % len(ycols)])
        if None in textpos:
            # xpos, ycol
            ycol = pos[1]
            # match xcol with ycol
            xcol = xcols[ycols.index(ycol)]
            # use slope when deciding where to put text
            slope = get_slope(df, xcol, ycol, xpos=pos[0])
            # replace ycol with ypos
            ypos = (get_ypos(df, pos[0], [(xcol, ycol)]) +
                get_ofs(df, xcols, [ycol], mag=0.02,
                        figsize=Graph.figsize)[1])
            pos = (pos[0], float(ypos))
            rad = pi/3
            if slope > 0: rad *= 2
            # choose xtext, ytext
            textpos = get_ofs(df, xcols, ycols, pos, mag=1.6,
                               rad=rad, figsize=Graph.figsize)
        pos = tuple(map(float, pos))
        textpos = tuple(map(float, textpos))
        Graph.annotate[i] = (pos, textpos, msg)

    for xpos, ypos, text in Graph.text:
        ax.text(xpos, ypos, text)
    # TODO: make these configurable
    for pos, textpos, text in Graph.annotate:
        ax.annotate(text, xy=pos, xytext=textpos, arrowprops={
            'facecolor': 'black', 'shrink': 0.05,
            'width': 2, 'headwidth': 8, 'headlength': 5
        })

    if not Graph.no_grid:
        plt.grid(True, alpha=Graph.grid_alpha, linestyle=Graph.grid,
            color=Graph.grid_color, linewidth=Graph.grid_width)
    plt.legend()

def get_ypos(df, xpos, xycols):
    pos = []
    for xcol, ycol in xycols:
        df2 = df.copy()
        # minimize distance to xpos
        df2[xcol] = (df2[xcol] - xpos).pow(2)
        # get mean of all y positions
        pos += [df2.iloc[df2[xcol].idxmin()][ycol]]
    return 1.0 * sum(pos) / len(pos)

def get_slope(df, xcol, ycol, xpos=0):
    df = df.copy()
    df['dx'] = df[xcol].diff()
    df['dy'] = df[ycol].diff()
    df[xcol] = (df[xcol] - xpos).pow(2)
    loc = df[xcol].idxmin()
    # get mean of all y positions
    return df.iloc[loc]['dy'] / df.iloc[loc]['dx']

def get_ofs(df, xcols, ycols, pos=(0, 0), mag=0.1, rad=pi/3, figsize=(16, 10)):
    # x / y scale is based off max and min values
    xrange = max(df[xcols].max()) - min(df[xcols].min())
    yrange = max(df[ycols].max()) - min(df[ycols].min())

    xscale = mag * xrange / figsize[0]
    yscale = mag * yrange / figsize[1]

    ofs = [xscale * cos(rad),
           yscale * sin(rad)]
    if pos is not None:
        ofs[0] += pos[0]
        ofs[1] += pos[1]
    return tuple(ofs)
