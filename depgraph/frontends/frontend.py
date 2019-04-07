import abc
from argparse import ArgumentParser

from ..config import make_pipeline_action
from ..dependency_graph import DependencyGraph


class FrontEnd(metaclass=abc.ABCMeta):
    def __init__(self, name):
        self.frontend_name = name

    @staticmethod
    @abc.abstractmethod
    def install_arg_parser(parser: ArgumentParser):
        raise NotImplementedError()

    @abc.abstractmethod
    def get_dependency_graph(self) -> DependencyGraph:
        raise NotImplementedError()


def make_frontend_action(action_class, **kwargs):
    return make_pipeline_action('frontend', action_class, **kwargs)
