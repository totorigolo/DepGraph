import logging
import re
from argparse import ArgumentParser
from typing import List, Set, Dict, Tuple

from .frontend import FrontEnd, make_frontend_action
from ..config import Config
from ..dependency_graph import DependencyGraph
from ..utils import get_all_files_ending_with, OrderedSet, DefaultOrderedDict

logger = logging.getLogger(__name__)

thm_name_regex = re.compile('val +([^ ]+) *: *thm')
val_stmt_regex = re.compile('val +([^ ]+) *=')
prove_stmt_regex = re.compile('val\\s+([^ ]+)\\s*=\\s*prove', re.MULTILINE)
store_stmt_regex = re.compile('val\\s+([^ ]+)\\s*=\\s*store_thm', re.MULTILINE)


def _read_thm_names_in_sig_file(theory_sig_file: str) -> Set[Tuple[str, str]]:
    thm_names = OrderedSet()
    with open(theory_sig_file, 'r') as f:
        for line in f.readlines():
            result = thm_name_regex.search(line)
            if result:
                thm_name = result.group(1)
                thm_names.add((theory_sig_file, thm_name))
    return thm_names


def _read_thm_names_in_sig_files(theory_sig_files: List[str]) \
        -> Set[Tuple[str, str]]:
    thm_names = OrderedSet()
    for sig_file in theory_sig_files:
        names_in_file = _read_thm_names_in_sig_file(sig_file)
        thm_names |= names_in_file
    return thm_names


def _read_thm_names_in_sml_file(script_sml_file: str) -> Set[Tuple[str, str]]:
    thm_names = OrderedSet()
    with open(script_sml_file, 'r') as f:
        for line in f.readlines():
            prove_result = prove_stmt_regex.search(line)
            store_result = store_stmt_regex.search(line)
            if prove_result:
                thm_name = prove_result.group(1)
                thm_names.add((script_sml_file, thm_name))
            if store_result:
                thm_name = store_result.group(1)
                thm_names.add((script_sml_file, thm_name))
    return thm_names


def _read_thm_names_in_sml_files(script_sml_files: List[str]) \
        -> Set[Tuple[str, str]]:
    thm_names = OrderedSet()
    for sml_file in script_sml_files:
        names_in_file = _read_thm_names_in_sml_file(sml_file)
        thm_names |= names_in_file

    forbidden_names = {'thm', 'lemma'}
    for i in range(20):
        forbidden_names.add('thm%d' % i)
        forbidden_names.add('thm_%d' % i)
        forbidden_names.add('lemma%d' % i)
        forbidden_names.add('lemma_%d' % i)

    to_remove = []
    for file, name in thm_names:
        if name in forbidden_names:
            to_remove.append((file, name))
    for x in to_remove:
        thm_names.remove(x)

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

    with open(script_sml_file, 'r') as f:
        for line in f.readlines():
            thm_block_result = val_stmt_regex.search(line)
            if thm_block_result:  # New theorem
                curr_thm_candidate = thm_block_result.group(1)
                if curr_thm_candidate in thm_names:
                    if curr_thm == '_':
                        curr_thm = None
                    else:
                        curr_thm = curr_thm_candidate
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
    def __init__(self, config: Config, args):
        super().__init__('HOL4 theorem hierarchy')
        self.config = config
        self.path = args[0]
        self.thm_path = args[1]

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        parser.add_argument(
            '--hol4-thms',
            required=False,
            action=make_frontend_action(Hol4ThmsFrontEnd,
                                        nargs=2,
                                        metavar=('SRC-ROOT', 'THM-ROOT'))
        )

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
        sig_thms = _read_thm_names_in_sig_files(theory_sig_files)
        sml_thms = _read_thm_names_in_sml_files(script_sml_files)
        thms = sig_thms | sml_thms
        thm_names = set(thm_name for (file, thm_name) in thms)

        # Get the theorem locations
        # thm_locations = _get_thm_locations(script_sml_files, thm_names)

        # Read dependencies from xxxScript.sml files
        thm_dependencies = _read_dependencies(script_sml_files, thm_names)

        # Generate the dependency graph
        graph = DependencyGraph()
        skipped_thms = dict()
        for file_path, thm_name in thms:
            long_name = '::'.join([file_path[:-10], thm_name])
            node_attrs = {'long_name': long_name,
                          'pretty_name': thm_name}

            if self.thm_path not in file_path:
                skipped_thms[thm_name] = node_attrs
            else:
                graph.add_node(thm_name, **node_attrs)

        for (script_sml_file, thm_name), dep_names in thm_dependencies.items():
            # long_name = '::'.join([script_sml_file[:-10], thm_name])
            if thm_name not in thm_names:
                logger.warn('Skipping dependencies of: %s', thm_name)
            for dep_name in dep_names:
                if dep_name not in thm_names:
                    logger.warn('Skipping dependency: %s -> %s',
                                thm_name, dep_name)
                graph.add_edge(thm_name, dep_name)
                if dep_name in skipped_thms:
                    node_attrs = skipped_thms[dep_name]
                    graph.add_node(dep_name, **node_attrs)
                    del node_attrs
                if thm_name in skipped_thms:
                    node_attrs = skipped_thms[thm_name]
                    graph.add_node(thm_name, **node_attrs)
                    del node_attrs

        logger.info("Done.")
        return graph
