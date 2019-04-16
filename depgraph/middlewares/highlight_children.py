import logging
from argparse import ArgumentParser

import networkx as nx

from .middleware import Middleware, make_middleware_action
from ..config import Config
from ..dependency_graph import DependencyGraph

logger = logging.getLogger(__name__)


class HighlightChildren(Middleware):
    def __init__(self, config: Config, args):
        super().__init__('Highlight child nodes')
        self.config = config
        self.color = args[0]

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--highlight-children',
            required=False,
            action=make_middleware_action(HighlightChildren,
                                          nargs=1,
                                          metavar='COLOR'),
        )

    def transform(self, dep_graph: DependencyGraph) -> DependencyGraph:
        logger.info("Highlighting child nodes in %s...", self.color)

        node_ids = []
        for node_id in dep_graph.nodes:
            if len(nx.descendants(dep_graph, node_id)) == 0:
                node_ids.append(node_id)

        attrs = {node_id: {'color': self.color} for node_id in node_ids}
        nx.set_node_attributes(dep_graph, attrs)

        logger.info("Done.")
        return dep_graph
