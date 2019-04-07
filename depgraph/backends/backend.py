import abc
from argparse import ArgumentParser
from typing import Iterable

from ..config import make_pipeline_action
from ..dependency_graph import DependencyGraph


class BackEnd(metaclass=abc.ABCMeta):
    def __init__(self, name):
        self.backend_name = name

    @staticmethod
    @abc.abstractmethod
    def install_arg_parser(parser: ArgumentParser):
        raise NotImplementedError()

    @abc.abstractmethod
    def convert(self, dep_graph: DependencyGraph) -> Iterable[str]:
        raise NotImplementedError()


def make_backend_action(action_class, **kwargs):
    return make_pipeline_action('backend', action_class, **kwargs)
