import logging
from argparse import ArgumentParser

import networkx as nx

from .middleware import Middleware, make_middleware_action
from ..config import Config
from ..dependency_graph import DependencyGraph

logger = logging.getLogger(__name__)


class HighlightDependentsOf(Middleware):
    def __init__(self, config: Config, args):
        self.config = config
        self.root = args[0]
        self.color = args[1]
        super().__init__('Highlight dependents of "%s" in %s'
                         % (self.root, self.color))

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--highlight-dependents-of',
            required=False,
            action=make_middleware_action(HighlightDependentsOf,
                                          nargs=2,
                                          metavar=('NODE', 'COLOR')),
        )

    def transform(self, dep_graph: DependencyGraph) -> DependencyGraph:
        logger.info('Highlighting dependents of "%s" in %s...',
                    self.root, self.color)

        if self.root not in dep_graph:
            logger.error('No node "%s" in the graph.', self.root)
            exit(1)

        attr = {'color': self.color}
        nx.set_node_attributes(dep_graph, {self.root: attr})
        for dependent in nx.ancestors(dep_graph, self.root):
            nx.set_node_attributes(dep_graph, {dependent: attr})

        logger.info("Done.")
        return dep_graph
