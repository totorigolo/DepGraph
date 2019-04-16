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
            dest='transitive-reduction',
            required=False,
            default=False,
            action=make_middleware_action(TransitiveReduction),
        )

    def transform(self, dep_graph: DependencyGraph) -> DependencyGraph:
        logger.info("Computing transitive reduction...")

        reduced = nx.algorithms.transitive_reduction(dep_graph)

        logger.info("Done.")
        return reduced
