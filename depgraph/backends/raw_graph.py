import logging
from argparse import ArgumentParser
from typing import Iterable

from .backend import BackEnd, make_backend_action
from ..config import Config
from ..dependency_graph import DependencyGraph

logger = logging.getLogger(__name__)


class RawGraphBackEnd(BackEnd):
    def __init__(self, config: Config):
        super().__init__('Raw graph')
        self.config = config

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--as-raw-graph',
            dest='as-raw-graph',
            required=False,
            default=False,
            action=make_backend_action(RawGraphBackEnd)
        )

    def convert(self, dep_graph: DependencyGraph) -> Iterable[str]:
        yield len(dep_graph.nodes())
        for node_id, node_attrs in dep_graph.nodes.items():
            yield node_id
            yield str(node_attrs)
            yield len(dep_graph.adj[node_id])
            for dep in dep_graph.adj[node_id]:
                yield dep
