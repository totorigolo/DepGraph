import networkx as nx

from .utils import OrderedSet


class Cluster(nx.OrderedDiGraph):
    def __init__(self, name, subgraph=None, **attr):
        if subgraph:
            super().__init__(subgraph, **attr)
        else:
            super().__init__(**attr)
        self.name = name


class DependencyGraph(nx.OrderedDiGraph):
    def __init__(self, **attr):
        super().__init__(**attr)
        self.clusters = OrderedSet()
