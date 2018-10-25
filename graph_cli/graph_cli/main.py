from . import options
import pickle
from sys import stdout

from .graph import Graph, get_graph_defs, create_graph

def main():
    args = options.parse_args()

    graphs = get_graph_defs(args)
    Graph.update_globals(args)

    if args.chain:
        data = Graph.dump(graphs)
        stdout.buffer.write(pickle.dumps(data))
    else:
        create_graph(graphs)

if __name__ == '__main__':
    main()
