import logging
from argparse import ArgumentParser

import networkx as nx

from .middleware import Middleware, make_middleware_action
from ..config import Config
from ..dependency_graph import DependencyGraph

logger = logging.getLogger(__name__)


class RemoveLeafs(Middleware):
    def __init__(self, config: Config, args):
        self.keep_ids = args
        if len(self.keep_ids) == 0:
            super().__init__('Remove leaf nodes')
        else:
            super().__init__('Remove leaf nodes but [%s]'
                             % ', '.join('"%s"' % x for x in self.keep_ids))
        self.config = config

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--remove-leafs',
            required=False,
            action=make_middleware_action(RemoveLeafs,
                                          nargs='*',
                                          metavar='KEEP_ID'),
        )

    def transform(self, dep_graph: DependencyGraph) -> DependencyGraph:
        if len(self.keep_ids) == 0:
            logger.info("Removing leaf nodes...")
        else:
            logger.info("Removing leaf nodes except [%s]...",
                        ', '.join('"%s"' % x for x in self.keep_ids))

        node_ids = []
        for node_id in dep_graph.nodes:
            if len(nx.descendants(dep_graph, node_id)) == 0:
                node_ids.append(node_id)

        dep_graph.remove_nodes_from(node_ids)

        logger.info("Done.")
        return dep_graph
