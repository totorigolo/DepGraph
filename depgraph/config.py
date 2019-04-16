import argparse
from collections import OrderedDict


def make_pipeline_action(pipeline_stage: str, action_class,
                         callback=None, nargs=0, **kwargs):
    class PipelineAction(argparse.Action):
        def __init__(self, **kw):
            super().__init__(nargs=nargs, **kw, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            if pipeline_stage not in namespace:
                setattr(namespace, pipeline_stage, [])
            previous = getattr(namespace, pipeline_stage)
            previous.append((self.dest, action_class, values))
            setattr(namespace, pipeline_stage, previous)
            if callback:
                callback(parser, namespace, values, option_string)

    return PipelineAction


class Config(OrderedDict):
    @staticmethod
    def new_parser():
        parser = argparse.ArgumentParser()
        return parser

    def __init__(self, arg_parser: argparse.ArgumentParser, **kwargs):
        namespace = arg_parser.parse_args()
        sorted_dict = OrderedDict(sorted(vars(namespace).items()))
        super().__init__(sorted_dict, **kwargs)

    def __str__(self):
        return '\n'.join('- %s: %s' % (name, value)
                         for name, value in self.items() if value is not None)
