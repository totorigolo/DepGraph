import logging
import re
from argparse import ArgumentParser
from typing import List, Set, Dict, NewType

from .frontend import FrontEnd, make_frontend_action
from ..config import Config
from ..dependency_graph import DependencyGraph
from ..utils import get_all_files_ending_with, OrderedSet, DefaultOrderedDict

logger = logging.getLogger(__name__)

ThmId = NewType('ThmId', str)

comment_regex = re.compile("\\(\\*.*?\\*\\)", re.DOTALL)
thm_name_regex = re.compile('val +([^ ]+) *: *thm')
new_name_regex = re.compile(
    'val\\s+([^ ]+)\\s*=\\s*(?:store_thm|prove|Define)',
    re.MULTILINE)


def _remove_comments(lines: List[str]) -> List[str]:
    text = '\n'.join(lines)
    stripped = re.sub(comment_regex, "", text)
    yield from stripped.split('\n')


class Thm:
    def __init__(self, thm_id: ThmId, file_path, full_name):
        self.thm_id = thm_id
        self.file_path = file_path
        self.full_name = full_name

    def __hash__(self):
        return hash(self.thm_id)

    def __eq__(self, other):
        return (isinstance(other, Thm)
                and self.thm_id == other.thm_id)


def _id_of_thm_name(thm_name: str) -> ThmId:
    thm_id = thm_name
    thm_id = thm_id.replace('_def', '')
    thm_id = thm_id.replace('_DEF', '')
    return ThmId(thm_id)


def _read_thm_names_in_sig_file(theory_sig_file: str) -> Set[Thm]:
    thm_names = OrderedSet()
    with open(theory_sig_file, 'r') as f:
        for line in _remove_comments(f.readlines()):
            result = thm_name_regex.search(line)
            if result:
                thm_name = result.group(1)
                thm_names.add(Thm(
                    thm_id=_id_of_thm_name(thm_name),
                    file_path=theory_sig_file,
                    full_name=thm_name,
                ))
    return thm_names


def _read_thm_names_in_sig_files(theory_sig_files: List[str]) -> Set[Thm]:
    thm_names = OrderedSet()
    for sig_file in theory_sig_files:
        names_in_file = _read_thm_names_in_sig_file(sig_file)
        thm_names |= names_in_file
    return thm_names


def _read_thm_names_in_sml_file(script_sml_file: str) -> Set[Thm]:
    thm_names = OrderedSet()
    with open(script_sml_file, 'r') as f:
        for line in _remove_comments(f.readlines()):
            regex_result = new_name_regex.search(line)
            if regex_result:
                thm_name = regex_result.group(1)
                thm_names.add(Thm(
                    thm_id=_id_of_thm_name(thm_name),
                    file_path=script_sml_file,
                    full_name=thm_name,
                ))
    return thm_names


def _read_thm_names_in_sml_files(script_sml_files: List[str]) -> Set[Thm]:
    thms = OrderedSet()
    for sml_file in script_sml_files:
        thms_in_file = _read_thm_names_in_sml_file(sml_file)
        thms |= thms_in_file

    forbidden_names = {'thm', 'lemma'}
    for i in range(20):
        forbidden_names.add('thm%d' % i)
        forbidden_names.add('thm_%d' % i)
        forbidden_names.add('lemma%d' % i)
        forbidden_names.add('lemma_%d' % i)

    to_remove = []
    for thm in thms:
        if thm.thm_id in forbidden_names:
            to_remove.append(thm)
    for thm in to_remove:
        thms.remove(thm)

    return thms


def _read_dependencies_in_file(script_sml_file: str, thm_ids: Set[ThmId]) \
        -> Dict[ThmId, Set[ThmId]]:
    dependencies = DefaultOrderedDict(lambda: OrderedSet())

    # We are scanning through a xxxScript.sml file and adding all known
    # theorem name as a dependency.
    curr_thm = None

    with open(script_sml_file, 'r') as f:
        for line in _remove_comments(f.readlines()):
            regex_result = new_name_regex.search(line)
            if regex_result:  # New theorem
                curr_thm_candidate = _id_of_thm_name(regex_result.group(1))
                if curr_thm_candidate in thm_ids:
                    if curr_thm == '_':
                        curr_thm = None
                    else:
                        curr_thm = curr_thm_candidate
            # no `else`, because of one-liners

            delimiters = [
                ' ', ',', ';', '\\', '[', ']', '(', ')', '+', '-', '*',
                '/', '<', '>', '!', '?', '`', ':',
                '.',
            ]
            regex_pattern = '|'.join(map(re.escape, delimiters))

            if curr_thm is not None:
                for word in re.split(regex_pattern, line):
                    possible_thm_id = _id_of_thm_name(word)
                    if (possible_thm_id in thm_ids
                            and possible_thm_id != curr_thm):
                        dependencies[curr_thm].add(possible_thm_id)

    return dependencies


def _read_dependencies(script_sml_files: List[str], thm_ids: Set[ThmId]) \
        -> Dict[ThmId, Set[ThmId]]:
    dependencies = DefaultOrderedDict(lambda: OrderedSet())

    for script_sml_file in script_sml_files:
        deps_in_file = _read_dependencies_in_file(script_sml_file, thm_ids)
        for thm_name, deps in deps_in_file.items():
            dependencies[thm_name] |= deps

    # Remove self-loops
    for thm_id, thm_deps in dependencies.items():
        thm_deps.discard(thm_id)

    return dependencies


class Hol4ThmsFrontEnd(FrontEnd):
    def __init__(self, config: Config, args):
        self.config = config
        self.path = args[0]
        self.thm_path = args[1]
        super().__init__('HOL4 theorem hierarchy in %s of %s'
                         % (self.path, self.thm_path))

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
        logger.info("Generating theorem hierarchy graph in %s of %s...",
                    self.path, self.thm_path)

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
        thm_ids = set(thm.thm_id for thm in thms)

        # Get the theorem locations
        # thm_locations = _get_thm_locations(script_sml_files, thm_names)

        # Read dependencies from xxxScript.sml files
        thm_dependencies = _read_dependencies(script_sml_files, thm_ids)

        # Generate the dependency graph
        graph = DependencyGraph()
        skipped_thms = dict()
        for thm in thms:
            long_name = '::'.join([thm.file_path[:-10], thm.full_name])
            node_attrs = {
                'long_name': long_name,
                'pretty_name': thm.thm_id,
            }

            if self.thm_path not in thm.file_path:
                skipped_thms[thm.thm_id] = node_attrs
            else:
                graph.add_node(thm.thm_id, **node_attrs)

        for thm_id, dep_names in thm_dependencies.items():
            if thm_id not in thm_ids:
                logger.warn('Skipping dependencies of: %s', thm_id)
            for dep_name in dep_names:
                if dep_name not in thm_ids:
                    logger.warn('Skipping dependency: %s -> %s',
                                thm_id, dep_name)
                graph.add_edge(thm_id, dep_name)
                if dep_name in skipped_thms:
                    node_attrs = skipped_thms[dep_name]
                    graph.add_node(dep_name, **node_attrs)
                    del node_attrs
                if thm_id in skipped_thms:
                    node_attrs = skipped_thms[thm_id]
                    graph.add_node(thm_id, **node_attrs)
                    del node_attrs

        logger.info("Done.")
        return graph
