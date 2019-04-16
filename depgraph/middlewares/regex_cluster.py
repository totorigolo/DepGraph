import logging
import re
from argparse import ArgumentParser

from depgraph.utils import OrderedSet
from .middleware import Middleware, make_middleware_action
from ..config import Config
from ..dependency_graph import DependencyGraph, Cluster

logger = logging.getLogger(__name__)


def store_regex_action(parser, namespace, values, option_string):
    setattr(namespace, 'cluster-regex-middleware-regex-list', values)


class ClusterRegex(Middleware):
    def __init__(self, config: Config):
        self.config = config
        self.regex_list = config['cluster-regex-middleware-regex-list']
        super().__init__('Regex cluster [%s]' % ', '.join(
            '"%s"' % r for r in self.regex_list))

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--cluster-regex',
            dest='cluster-regex',
            required=False,
            default=False,
            action=make_middleware_action(ClusterRegex,
                                          callback=store_regex_action,
                                          nargs='+'),
        )

    def transform(self, dep_graph: DependencyGraph) -> DependencyGraph:
        for regex_str in self.regex_list:
            cluster_ids = OrderedSet()
            compiled = re.compile(regex_str)
            for node_id, long_name in dep_graph.nodes('long_name'):
                if compiled.search(long_name):
                    cluster_ids.add(node_id)
            if len(cluster_ids) > 0:
                subgraph = dep_graph.__class__()
                subgraph.add_nodes_from(cluster_ids)
                subgraph.add_edges_from(
                    (u, v) for (u, v) in dep_graph.edges()
                    if u in subgraph if v in subgraph)

                cluster = Cluster(regex_str, subgraph)
                dep_graph.clusters.add(cluster)

        return dep_graph