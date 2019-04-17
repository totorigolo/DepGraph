import logging
import re
from argparse import ArgumentParser

from depgraph.utils import OrderedSet
from .middleware import Middleware, make_middleware_action
from ..config import Config
from ..dependency_graph import DependencyGraph, Cluster

logger = logging.getLogger(__name__)


class ClusterRegex(Middleware):
    def __init__(self, config: Config, regex_list):
        self.config = config
        self.regex_list = regex_list
        super().__init__('Regex cluster [%s]' % ', '.join(
            '"%s"' % r for r in self.regex_list))

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--cluster-regex',
            required=False,
            action=make_middleware_action(ClusterRegex,
                                          nargs='+', metavar='REGEX'),
        )

    def transform(self, dep_graph: DependencyGraph) \
            -> DependencyGraph:
        logger.info('Clustering nodes with [%s]' % ', '.join(
            '"%s"' % r for r in self.regex_list))

        cluster_name = '-'.join('/%s/' % r for r in self.regex_list)
        logger.debug("Cluster name: %s", cluster_name)

        cluster_ids = OrderedSet()
        for regex_str in self.regex_list:
            logger.debug("Adding nodes with /%s/...", regex_str)

            compiled = re.compile(regex_str)
            for node_id in dep_graph.nodes:
                if compiled.search(node_id):
                    cluster_ids.add(node_id)

        if len(cluster_ids) > 0:
            logger.info('Cluster contains %d nodes.', len(cluster_ids))

            subgraph = dep_graph.__class__()
            subgraph.add_nodes_from(cluster_ids)
            subgraph.add_edges_from(
                (u, v) for (u, v) in dep_graph.edges()
                if u in subgraph if v in subgraph)

            cluster = Cluster(cluster_name, subgraph)
            dep_graph.clusters.add(cluster)
        else:
            logger.info('Empty cluster: %s', cluster_name)

        logger.info("Done")
        return dep_graph
