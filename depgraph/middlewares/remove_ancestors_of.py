import logging
from argparse import ArgumentParser

import networkx as nx

from .middleware import Middleware, make_middleware_action
from ..config import Config
from ..dependency_graph import DependencyGraph

logger = logging.getLogger(__name__)


class RemoveAncestorsOf(Middleware):
    def __init__(self, config: Config, args):
        self.config = config
        self.root = args[0]
        super().__init__('Remove ancestors of "%s"' % self.root)

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--remove-ancestors-of',
            required=False,
            action=make_middleware_action(RemoveAncestorsOf,
                                          nargs=1, metavar='NODE'),
        )

    def transform(self, dep_graph: DependencyGraph) -> DependencyGraph:
        logger.info("Removing ancestors of %s...", self.root)

        if self.root not in dep_graph:
            logger.error('No node "%s" in the graph.', self.root)
            exit(1)

        ancestors = nx.ancestors(dep_graph, self.root)
        dep_graph.remove_nodes_from(ancestors)

        logger.info("Done.")
        return dep_graph
