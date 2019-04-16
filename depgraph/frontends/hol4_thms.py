import logging
import re
from argparse import ArgumentParser
from typing import List, Set, Dict, Tuple

from .frontend import FrontEnd, make_frontend_action
from ..config import Config
from ..dependency_graph import DependencyGraph
from ..utils import get_all_files_ending_with, OrderedSet, DefaultOrderedDict

logger = logging.getLogger(__name__)


def _read_thm_names_in_file(theory_sig_file: str) -> Set[Tuple[str, str]]:
    thm_name_regex = re.compile('val +([^ ]+) *: *thm')
    thm_names = OrderedSet()
    with open(theory_sig_file, 'r') as f:
        for line in f.readlines():
            result = thm_name_regex.search(line)
            if result:
                thm_name = result.group(1)
                thm_names.add((theory_sig_file, thm_name))
    return thm_names


def _read_thm_names_in(theory_sig_files: List[str]) -> Set[Tuple[str, str]]:
    thm_names = OrderedSet()
    for sig_file in theory_sig_files:
        names_in_file = _read_thm_names_in_file(sig_file)
        thm_names |= names_in_file
    return thm_names


def _get_thm_locations(script_sml_file: str, thm_names: Set[str]) \
        -> Dict[str, str]:
    pass


def _read_dependencies_in_file(script_sml_file: str, thm_names: Set[str]) \
        -> Dict[Tuple[str, str], Set[str]]:
    dependencies = DefaultOrderedDict(lambda: OrderedSet())

    # We are scanning through a xxxScript.sml file and adding all known
    # theorem name as a dependency.
    curr_thm = None

    thm_block_regex = re.compile('val +([^ ]+) *=')

    with open(script_sml_file, 'r') as f:
        for line in f.readlines():
            thm_block_result = thm_block_regex.search(line)
            if thm_block_result:  # New theorem
                curr_thm = thm_block_result.group(1)
                if curr_thm == '_':
                    curr_thm = None
                # else:
                #     logger.debug('New curr_thm: %s', curr_thm)
            # no `else` because of one-liners

            delimiters = [
                ' ', ',', ';', '\\', '[', ']', '(', ')', '+', '-', '*',
                '/', '<', '>', '!', '?', '`', ':',
                '.',
            ]
            regex_pattern = '|'.join(map(re.escape, delimiters))

            if curr_thm is not None:
                for word in re.split(regex_pattern, line):
                    if word in thm_names and word != curr_thm:
                        # logger.info('New dep: %s -> %s', curr_thm, word)
                        dependencies[(script_sml_file, curr_thm)].add(word)

    return dependencies


def _read_dependencies(script_sml_files: List[str], thm_names: Set[str]) \
        -> Dict[str, Set[str]]:
    dependencies = DefaultOrderedDict(lambda: OrderedSet())
    for script_sml_file in script_sml_files:
        deps_in_file = _read_dependencies_in_file(script_sml_file, thm_names)
        for thm_name, deps in deps_in_file.items():
            dependencies[thm_name] |= deps
    return dependencies


class Hol4ThmsFrontEnd(FrontEnd):
    def __init__(self, config: Config):
        super().__init__('HOL4 theorem hierarchy')
        self.config = config
        self.path = config['hol4-thms-src-root']

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        def store_callback(_parser, namespace, values, _option_string):
            setattr(namespace, 'hol4-thms', True)
            setattr(namespace, 'hol4-thms-src-root', values[0])
            setattr(namespace, 'hol4-thms-thms-in', values[1])

        parser.add_argument(
            '--hol4-thms',
            dest='hol4-thms',
            required=False,
            default=False,
            action=make_frontend_action(Hol4ThmsFrontEnd,
                                        callback=store_callback,
                                        nargs=2))

    def get_dependency_graph(self) -> DependencyGraph:
        logger.info("Generating dependency graph in: %s", self.path)

        # Get the list of all xxxTheory.sig and xxxScript.sml files
        theory_sig_files = list(filter(
            lambda f: '.hollogs' not in f,
            get_all_files_ending_with(self.path, ['Theory.sig'])))
        script_sml_files = list(filter(
            lambda f: '.hollogs' not in f,
            get_all_files_ending_with(self.path, ['Script.sml'])))

        # Extract all theorem names from xxxTheory.sig files
        thms = _read_thm_names_in(theory_sig_files)
        thm_names = set(thm_name for (file, thm_name) in thms)

        # Get the theorem locations
        # thm_locations = _get_thm_locations(script_sml_files, thm_names)

        # Read dependencies from xxxScript.sml files
        thm_dependencies = _read_dependencies(script_sml_files, thm_names)

        # Generate the dependency graph
        graph = DependencyGraph()
        skipped_thms = dict()
        for theory_sig_file, thm_name in thms:
            long_name = '::'.join([theory_sig_file[:-10], thm_name])
            node_attrs = {'long_name': long_name,
                          'pretty_name': thm_name}

            if self.config['hol4-thms-thms-in'] not in theory_sig_file:
                skipped_thms[thm_name] = node_attrs
            else:
                graph.add_node(thm_name, **node_attrs)

        for (script_sml_file, thm_name), dep_names in thm_dependencies.items():
            # long_name = '::'.join([script_sml_file[:-10], thm_name])
            for dep_name in dep_names:
                if thm_name in graph.nodes:
                    graph.add_edge(thm_name, dep_name)
                    if dep_name in skipped_thms:
                        node_attrs = skipped_thms[dep_name]
                        graph.add_node(dep_name, **node_attrs)
                        del node_attrs

        logger.info("Done.")
        return graph
