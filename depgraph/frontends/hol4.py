import logging
import re
from argparse import ArgumentParser
from collections import OrderedDict
from typing import List, Set, Iterable

from .frontend import FrontEnd, make_frontend_action
from ..config import Config
from ..dependency_graph import DependencyGraph
from ..utils import OrderedSet, DefaultOrderedDict
from ..utils import get_all_files_ending_with

logger = logging.getLogger(__name__)


def _remove_extension(path: str) -> str:
    path = path.replace('.sml', '')
    path = path.replace('.sig', '')
    path = path.replace('.ui', '')
    path = path.replace('.uo', '')
    return path


def _read_holmake_dep_file(path: str) -> List[str]:
    with open(path, 'r') as f:
        content = f.readlines()
        content = map(str.strip, content)
        content = map(_remove_extension, content)
        return list(content)


def _prettify_long_name(long_name: str) -> str:
    pretty = long_name

    hol_index = pretty.find('$(HOLDIR)/sigobj/')
    if hol_index >= 0:
        pretty = 'HOL4/' + pretty[hol_index + len('$(HOLDIR)/sigobj/'):]

    hol_ba_index = pretty.find('/HolBA/')
    if hol_ba_index >= 0:
        pretty = pretty[hol_ba_index + 1:]

    return pretty


def _prettify_path(long_path: str) -> str:
    short = long_path
    short = _remove_extension(short)
    short = _prettify_long_name(short)
    return short


def _get_filename(file_path):
    filename = _remove_extension(file_path).split('/')[-1]
    return filename


def _get_non_uniques_file_names(paths: Iterable[str]) -> Set[str]:
    seen = set()
    non_uniques = OrderedSet()
    for file_path in paths:
        filename = _get_filename(file_path)
        if filename in seen:
            non_uniques.add(filename)
        seen.add(filename)
    return non_uniques


def _generate_short_filename_mapping(long_module_paths: Set[str]):
    non_unique_file_names = _get_non_uniques_file_names(long_module_paths)
    non_uniques_todo = DefaultOrderedDict(list)

    mapping = OrderedDict()
    for module_path in long_module_paths:
        pretty = _prettify_path(module_path)
        if pretty.startswith('HOL4/'):
            mapping[module_path] = pretty
        else:
            filename = _get_filename(pretty)
            if filename not in non_unique_file_names:
                mapping[module_path] = filename
            else:
                non_uniques_todo[filename].append((module_path, pretty))

    non_unique_mappings_for_logs = OrderedDict()
    for filename, dup_list in non_uniques_todo.items():
        for idx in range(-2, -20, -1):
            long_set = set()
            for module_path, pretty in dup_list:
                short = '/'.join(pretty.split('/')[idx:])
                long_set.add(short)
                mapping[module_path] = short
                non_unique_mappings_for_logs[module_path] = short
            if len(long_set) == len(dup_list):
                break

    if len(non_unique_mappings_for_logs) > 0:
        logger.info(
            'There are some non-unique module names:\n%s',
            '\n'.join(map(lambda x: ' - %s -> %s' % x,
                          non_unique_mappings_for_logs.items())))

    return mapping


class Hol4FrontEnd(FrontEnd):
    def __init__(self, config: Config, args):
        super().__init__('HOL4 from .uo files')
        self.config = config
        self.path = args[0]

    @staticmethod
    def install_arg_parser(parser: ArgumentParser):
        def store_callback(_parser, namespace, values, _option_string):
            setattr(namespace, 'hol4', True)
            setattr(namespace, 'hol4-src-root', values[0])

        parser.add_argument(
            '--hol4',
            dest='hol4',
            required=False,
            default=False,
            action=make_frontend_action(Hol4FrontEnd,
                                        callback=store_callback,
                                        nargs=1,
                                        metavar='SRC-ROOT')
        )

    def get_dependency_graph(self) -> DependencyGraph:
        logger.info("Generating dependency graph in: %s", self.path)

        # Get all Holmake dependency files
        holmake_dep_exts = ['.uo']
        holmake_dep_files = get_all_files_ending_with(
            self.path, holmake_dep_exts, self.config['filter-files-regex'])

        # Read all the files, resulting in [(path, [dep_path])]
        files_and_deps = []
        for file_path in holmake_dep_files:
            deps = _read_holmake_dep_file(
                file_path)
            files_and_deps.append((file_path, deps))

        # Merge all the Holmake dep files (.uo, .ui)
        deps_of_modules_dict = DefaultOrderedDict(OrderedSet)
        for file_path, dependencies in files_and_deps:
            for dependency in dependencies:
                module_path = _remove_extension(file_path)
                deps_of_modules_dict[module_path].add(dependency)
        for module_path in deps_of_modules_dict:
            if module_path in deps_of_modules_dict[module_path]:
                deps_of_modules_dict[module_path].remove(module_path)

        # Gather all modules paths
        all_module_paths = OrderedSet()
        for module_path, dependencies in deps_of_modules_dict.items():
            all_module_paths.add(module_path)
            for dependency in dependencies:
                all_module_paths.add(dependency)

        # Generate a short name mapping
        short_name_mapping = _generate_short_filename_mapping(all_module_paths)

        # Compile those two regex to filter dependencies
        exclude_dependencies_regex = None
        if self.config['exclude-dependencies-regex'] is not None:
            exclude_dependencies_regex = re.compile(
                self.config['exclude-dependencies-regex'])
        keep_dependencies_regex = None
        if self.config['keep-dependencies-regex'] is not None:
            keep_dependencies_regex = re.compile(
                self.config['keep-dependencies-regex'])
        edr = exclude_dependencies_regex
        kdr = keep_dependencies_regex
        filtered_dependencies = set()

        # Generate the dependency graph
        graph = DependencyGraph()
        for module_path in all_module_paths:  # Nodes
            short_name = short_name_mapping[module_path]
            graph.add_node(
                short_name,
                long_name=module_path,
                pretty_name=short_name,
            )
        for module_path, dependencies in deps_of_modules_dict.items():  # Edges
            short_name = short_name_mapping[module_path]
            for dependency in dependencies:
                short_dep_name = short_name_mapping[dependency]

                d = short_dep_name  # that's the dependency's module_path
                keep_dep = True
                if edr and kdr:
                    keep_dep = not edr.search(d) or kdr.search(d)
                elif edr:
                    keep_dep = not edr.search(d)
                elif kdr:
                    keep_dep = kdr.search(d)

                if keep_dep:
                    graph.add_edge(short_name, short_dep_name)
                else:
                    filtered_dependencies.add(short_dep_name)

        # Remove all nodes that have been filtered as dependencies and
        # that don't have any edge
        for filtered_dependency in filtered_dependencies:
            if len(graph.adj[filtered_dependency]) == 0:
                graph.remove_node(filtered_dependency)

        logger.info("Done.")
        return graph
