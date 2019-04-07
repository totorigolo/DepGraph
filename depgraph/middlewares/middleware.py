import abc
from argparse import ArgumentParser

from ..config import make_pipeline_action
from ..dependency_graph import DependencyGraph


class Middleware(metaclass=abc.ABCMeta):
    def __init__(self, name):
        self.middleware_name = name

    @staticmethod
    @abc.abstractmethod
    def install_arg_parser(parser: ArgumentParser):
        raise NotImplementedError()

    @abc.abstractmethod
    def transform(self, dep_graph: DependencyGraph) -> DependencyGraph:
        raise NotImplementedError()


def make_middleware_action(action_class, **kwargs):
    return make_pipeline_action('middlewares', action_class, **kwargs)
