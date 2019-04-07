import logging
from argparse import ArgumentParser
from typing import Iterable

from .backend import BackEnd, make_backend_action
from ..config import Config
from ..dependency_graph import DependencyGraph
from ..utils import random_hex_color, OrderedSet

logger = logging.getLogger(__name__)


class DotBackEnd(BackEnd):
    def __init__(self, config: Config):
        super().__init__('GraphViz Dot')
        self.config = config

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--as-dot',
            dest='as-dot',
            required=False,
            default=False,
            action=make_backend_action(DotBackEnd)
        )
        parser.add_argument(
            '--dot-horizontal',
            dest='dot-horizontal',
            required=False,
            default=False,
            action="store_true",
        )

    def convert(self, dep_graph: DependencyGraph) -> Iterable[str]:
        yield 'digraph G {'

        yield 'graph [compound=true];'
        yield 'node [shape=box];'

        if self.config['dot-horizontal']:
            yield 'rankdir=LR'

        yield ''
        yield '# Nodes'
        yield ''

        node_id_mapping = dict()
        for i, (node_id, node_attrs) in enumerate(dep_graph.nodes.items()):
            dot_id = 'n{}'.format(i)
            node_id_mapping[node_id] = dot_id
            try:
                pretty_name = node_attrs['pretty_name']
            except KeyError:
                pretty_name = node_id
                logger.warn('No "pretty_name" for node "%s".', node_id)
            yield '{}[label="{}"]'.format(dot_id, pretty_name)

        yield ''
        yield '# Edges'
        yield ''

        for node_id in dep_graph.nodes:
            from_id = node_id_mapping[node_id]
            edge_color = random_hex_color()
            yield '%s -> {' % from_id
            for dependency_id in dep_graph.adj[node_id]:
                to_id = node_id_mapping[dependency_id]
                yield '  %s' % to_id

            yield '}[color="%s"]' % edge_color

        yield ''
        yield '# Clusters'
        yield ''

        for i, cluster in enumerate(dep_graph.clusters):
            yield 'subgraph cluster_%d {' % i
            yield '  label="%s"' % cluster.name

            cluster_color = random_hex_color()
            yield '  color="%s";' % cluster_color
            yield ''

            for node_id in cluster.nodes:
                yield '  "%s"' % node_id_mapping[node_id]

            yield '}'

        yield '}'
