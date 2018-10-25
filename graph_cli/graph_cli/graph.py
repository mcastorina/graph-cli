#!/usr/bin/python3

from sys import stdin
import numpy as np
import pickle

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
    xtick_angle = None
    ytick_angle = None
    xtick_align = None
    ytick_align = None
    def __init__(self):
        self.xcol = None
        self.ycol = None
        self.legend = None
        self.color = None
        self.style = None
        self.marker = None
        self.width = None
        self.offset = None
        self.markersize = None
        self.output = None
        self.time_format = None
        self.resample = None
        self.sort = None
        self.bar = None
        self.barh = None
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

def get_graph_def(xcol, ycol, legend, color, style, marker, width,
        offset, markersize, output, time_format, resample, sort, bar, barh):
    # get dict of args (must match Graph attribute names)
    timeseries = False
    try:
        # automatically convert to datetime
        if time_format is not None:
            xcol = pd.to_datetime(xcol, format=time_format)
            timeseries = True
        elif xcol.dtype == np.dtype('O'):
            xcol = pd.to_datetime(xcol)
            timeseries = True
    except: pass

    if sort:
        df = pd.DataFrame({xcol.name: xcol, ycol.name: ycol})
        df.sort_values(xcol.name, inplace=True)
        xcol, ycol = df[xcol.name], df[ycol.name]
    if resample:
        df = pd.DataFrame({xcol.name: xcol, ycol.name: ycol})
        try:
            if timeseries:
                df.set_index(xcol, inplace=True)
                # TODO: figure out what to do with NA
                df = df.resample(resample).mean().dropna()
                df.reset_index(inplace=True)
            else:
                x_min, x_max = df[xcol.name].min(), df[xcol.name].max()
                resample = float(resample)
                bins = np.linspace(x_min + resample/2, x_max - resample/2, float(x_max - x_min + resample)/resample)
                df = df.groupby(np.digitize(df[xcol.name], bins)).mean().dropna()
                del x_min, x_max, bins
        except Exception as e:
            logging.error('Error: Could not resample. "%s"' % str(e))
            exit(1)
        xcol, ycol = df[xcol.name], df[ycol.name]
        del df
    del timeseries

    kvs = locals()
    g = Graph()
    for attr, val in kvs.items():
        setattr(g, attr, val)
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
            args.marker, args.width, args.offset, args.markersize, args.output,
            args.time_format, args.resample, args.sort, args.bar, args.barh):
        graphs += [get_graph_def(*g)]

    return graphs

def read_chain(args):
    chain = ([], {})
    # read stdin for chained data and unpickle into chain array
    # check if stdin is not a terminal
    if not stdin.isatty() and args.file != '-':
        chain = pickle.loads(stdin.buffer.read())

    # check our data is what we expect it to be
    # TODO: error handling
    assert(type(chain) is tuple)
    assert(len(chain) == 2)
    assert(type(chain[0]) is list)
    assert(type(chain[1]) is dict)
    for link in chain[0]:
        assert(type(link) is Graph)

    return chain

def create_graph(graphs):
    # make Graph.global = (val, flag) just val
    Graph.remove_global_flags()

    if graphs[-1].output:
        # disables screen requirement for plotting
        # must be called before importing matplotlib.pyplot
        import matplotlib
        matplotlib.use('Agg')
    import matplotlib.pyplot as plt

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
        else:
            ax.plot(graph.xcol, graph.ycol, label=graph.legend,
                marker=graph.marker, color=graph.color, linestyle=graph.style,
                linewidth=graph.width, markersize=graph.markersize)
        if graph.output:
            apply_globals(plt, ax)
            plt.savefig(graph.output)
        elif graph == graphs[-1]:
            apply_globals(plt, ax)
            plt.show()

def apply_globals(plt, ax):
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

    # TODO: make these configurable
    plt.grid(True, alpha=0.5, linestyle='-.')
    plt.legend()
