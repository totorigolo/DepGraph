import logging
from argparse import ArgumentParser
from typing import Iterable

from .backend import BackEnd, make_backend_action
from ..config import Config
from ..dependency_graph import DependencyGraph

logger = logging.getLogger(__name__)


class NoBackEnd(BackEnd):
    def __init__(self, config: Config, _args):
        super().__init__('No backend')
        self.config = config

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--no-backend',
            required=False,
            action=make_backend_action(NoBackEnd)
        )

    def convert(self, dep_graph: DependencyGraph) -> Iterable[str]:
        return ''
