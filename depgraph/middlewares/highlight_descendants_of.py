import logging
from argparse import ArgumentParser

import networkx as nx

from .middleware import Middleware, make_middleware_action
from ..config import Config
from ..dependency_graph import DependencyGraph

logger = logging.getLogger(__name__)


class HighlightDescendantsOf(Middleware):
    def __init__(self, config: Config, args):
        self.config = config
        self.root = args[0]
        self.color = args[1]
        super().__init__('Highlight descendants of "%s" in %s'
                         % (self.root, self.color))

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--highlight-descendants',
            required=False,
            action=make_middleware_action(HighlightDescendantsOf,
                                          nargs=2,
                                          metavar=('NODE', 'COLOR')),
        )

    def transform(self, dep_graph: DependencyGraph) -> DependencyGraph:
        logger.info("Highlighting descendants of %s in %s...",
                    self.root, self.color)

        if self.root not in dep_graph:
            logger.error('No node "%s" in the graph.', self.root)
            exit(1)

        attr = {'color': self.color}
        nx.set_node_attributes(dep_graph, {self.root: attr})
        for descendant in nx.descendants(dep_graph, self.root):
            nx.set_node_attributes(dep_graph, {descendant: attr})

        logger.info("Done.")
        return dep_graph
