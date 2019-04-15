import collections
import logging
from argparse import ArgumentParser

from .middleware import Middleware, make_middleware_action
from ..config import Config
from ..dependency_graph import DependencyGraph
from ..utils import OrderedSet

logger = logging.getLogger(__name__)


class CondenseInterClustersEdges(Middleware):
    def __init__(self, config: Config):
        self.config = config
        super().__init__('Condense inter-clusters edges')

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--condense-inter-clusters-edges',
            dest='condense-inter-clusters-edges',
            required=False,
            default=False,
            action=make_middleware_action(CondenseInterClustersEdges),
        )

    def transform(self, dep_graph: DependencyGraph) -> DependencyGraph:
        cluster_of = collections.defaultdict(None)
        for cluster in dep_graph.clusters:
            for node in cluster.nodes:
                cluster_of[node] = cluster

        removed_between = OrderedSet()
        for (from_node, to_node) in list(dep_graph.edges):
            from_cluster = cluster_of[from_node]
            to_cluster = cluster_of[to_node]
            if not from_cluster or not to_cluster:  # One of them not in a cluster
                # TODO: We should simplify here as well
                continue
            elif from_cluster == to_cluster:  # In same cluster
                continue
            else:
                removed_between.add((from_cluster, to_cluster))
                dep_graph.remove_edge(from_node, to_node)

        for (from_cluster, to_cluster) in removed_between:
            dep_graph.add_edge(
                'cluster_%s' % from_cluster.name,
                'cluster_%s' % to_cluster.name)

        return dep_graph
