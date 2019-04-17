import logging
from argparse import ArgumentParser

import networkx as nx

from .middleware import Middleware, make_middleware_action
from ..config import Config
from ..dependency_graph import DependencyGraph

logger = logging.getLogger(__name__)


class KeepOnlyDependentsOf(Middleware):
    def __init__(self, config: Config, args):
        self.config = config
        self.root = args[0]
        super().__init__('Keep only dependents of "%s"' % self.root)

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--keep-only-dependents-of',
            required=False,
            action=make_middleware_action(KeepOnlyDependentsOf,
                                          nargs=1, metavar='NODE'),
        )

    def transform(self, dep_graph: DependencyGraph) -> DependencyGraph:
        logger.info("Keeping only dependents of %s...", self.root)

        if self.root not in dep_graph:
            logger.error('No node "%s" in the graph.', self.root)
            exit(1)

        dependents = nx.ancestors(dep_graph, self.root)
        dep_graph.remove_nodes_from(
            n for n in list(dep_graph.nodes) if n not in dependents)

        logger.info("Done.")
        return dep_graph
