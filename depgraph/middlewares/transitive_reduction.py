import logging
from argparse import ArgumentParser

import networkx as nx

from .middleware import Middleware, make_middleware_action
from ..config import Config
from ..dependency_graph import DependencyGraph

logger = logging.getLogger(__name__)


class TransitiveReduction(Middleware):
    def __init__(self, config: Config, _args):
        super().__init__('Transitive reduction')
        self.config = config

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--transitive-reduction',
            required=False,
            action=make_middleware_action(TransitiveReduction),
        )

    def transform(self, dep_graph: DependencyGraph) -> DependencyGraph:
        logger.info("Computing transitive reduction...")

        if not nx.is_directed_acyclic_graph(dep_graph):
            logger.critical(
                "Directed Acyclic Graph required for transitive_reduction.")

            cycle = nx.find_cycle(dep_graph)
            logger.critical('Cycle found: %s', cycle)

            exit(1)

        reduced = nx.algorithms.transitive_reduction(dep_graph)

        if not isinstance(reduced, DependencyGraph):
            logger.critical('You should apply the patch fixing '
                            'networkx.transitive_reduction.')
        else:
            reduced.clusters = dep_graph.clusters

        logger.info("Done.")
        return reduced
