import logging
from argparse import ArgumentParser

import networkx as nx

from .middleware import Middleware, make_middleware_action
from ..config import Config
from ..dependency_graph import DependencyGraph

logger = logging.getLogger(__name__)


class KeepOnlyDescendantsOf(Middleware):
    def __init__(self, config: Config, args):
        self.config = config
        self.root = args[0]
        super().__init__('Keep only descendants of "%s"' % self.root)

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--keep-only-descendants-of',
            required=False,
            action=make_middleware_action(KeepOnlyDescendantsOf,
                                          nargs=1, metavar='NODE'),
        )

    def transform(self, dep_graph: DependencyGraph) -> DependencyGraph:
        logger.info("Keeping only descendants of %s...", self.root)

        if self.root not in dep_graph:
            logger.error('No node "%s" in the graph.', self.root)
            exit(1)

        descendants = nx.descendants(dep_graph, self.root)
        dep_graph.remove_nodes_from(
            n for n in list(dep_graph.nodes) if n not in descendants)

        logger.info("Done.")
        return dep_graph