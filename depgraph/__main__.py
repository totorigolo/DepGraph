#!/usr/bin/env python3
import logging
import random
import sys
from argparse import ArgumentParser

from .backends import BACK_ENDS, RawGraphBackEnd
from .config import Config
from .frontends import FRONT_ENDS
from .middlewares import MIDDLEWARES

logger = logging.getLogger(__name__)


def configure_parser(parser: ArgumentParser):
    # Optional arguments
    parser.add_argument(
        '--random-seed',
        dest='random-seed',
        required=False,
        default=6737,
        help='Seed for the PRNG (the program is deterministic)'
    )
    parser.add_argument(
        '--log',
        dest='log-level',
        required=False,
        default='info',
        help='Logging level',
        choices=['debug', 'info', 'warning', 'error', 'critical']
    )
    parser.add_argument(
        '-o',
        '--output',
        dest='output-file',
        required=False,
        default=None,
        help="Location of the generated dot file (default: stdout)",
    )

    # TODO: See where to put this when more front-ends will be implemented
    parser.add_argument(
        '--filter-files',
        dest='filter-files-regex',
        required=False,
        default=None,
        help='Regex to filter leaf files'
    )
    parser.add_argument(
        '--exclude-dependencies',
        dest='exclude-dependencies-regex',
        required=False,
        default=None,
        help='Regex to exclude some dependencies'
    )
    parser.add_argument(
        '--keep-dependencies',
        dest='keep-dependencies-regex',
        required=False,
        default=None,
        help='Regex to keep some dependencies'
    )


def configure_logger(log_level: str):
    numeric_log_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_log_level, int):
        raise ValueError('Invalid log level: %s' % log_level)

    mpl_logger = logging.getLogger('matplotlib')
    mpl_logger.setLevel(logging.WARNING)

    try:
        import coloredlogs
        coloredlogs.install(level=numeric_log_level)
    except ImportError:
        logger.warn('You should install dependencies using pipenv.')
        logging.basicConfig(level=numeric_log_level)


def main():
    # Early logger configuration
    log_arg = next((x for x in enumerate(sys.argv) if '--log' in x[1]), None)
    if log_arg:
        if '=' in log_arg[1]:  # "--log=level"
            log_level = log_arg[1].split('=')[1]
        else:  # "--log level"
            log_level = sys.argv[log_arg[0] + 1]
        configure_logger(log_level)

    # Command line arguments parsing
    parser = Config.new_parser()
    configure_parser(parser)
    for frontend in FRONT_ENDS:
        frontend.install_arg_parser(parser)
    for middleware in MIDDLEWARES:
        middleware.install_arg_parser(parser)
    for backend in BACK_ENDS:
        backend.install_arg_parser(parser)
    config = Config(parser)
    logger.debug('Configuration:\n%s', config)

    random.seed(config['random-seed'])

    # Correctly configure the logging now that we have the config
    configure_logger(config['log-level'])

    # Build the pipeline
    frontend = None
    middlewares = []
    backend = None
    try:  # frontend
        if len(config['frontend']) > 1:
            parser.error(
                'You cannot specify more that one frontend (%s)' %
                ', '.join("'%s'" % x[0] for x in config['frontend']))
        else:
            frontend_conf = config['frontend'][0]
            frontend = frontend_conf[1](config, frontend_conf[2])
            logger.info('Using front-end: %s', frontend.frontend_name)
    except KeyError:
        parser.error('You must specify one frontend.')
    try:  # middlewares
        middlewares = list(x[1](config, x[2]) for x in config['middlewares'])
        logger.info('Using middlewares: %s' %
                    ', '.join(mw.middleware_name for mw in middlewares))
    except KeyError:
        logger.info('No middleware.')
    try:  # backend
        if len(config['backend']) > 1:
            print(config['backend'])
            parser.error(
                'You cannot specify more that one backend (%s)' %
                ', '.join('"%s"' % x[0] for x in config['backend']))
        else:
            backend_conf = config['backend'][0]
            backend = backend_conf[1](config, backend_conf[2])
            logger.info('Using back-end: %s', backend.backend_name)
    except KeyError:
        logger.info('No backend specified. Defaulting to raw graph output.')
        backend = RawGraphBackEnd(config)

    assert frontend is not None
    assert isinstance(middlewares, list)
    assert backend is not None

    # Get a dependency graph from the frontend
    dep_graph = frontend.get_dependency_graph()

    # Transform it using middlewares
    for middleware in middlewares:
        dep_graph = middleware.transform(dep_graph)

    # Get the output from the backend
    output = backend.convert(dep_graph)

    # Write the output to stdout or to a file
    if config['output-file']:
        with open(config['output'], 'w') as dot_file:
            dot_file.writelines(output)
    else:
        try:
            for line in output:
                print(line, file=sys.stdout)
        except BrokenPipeError:
            exit(0)


if __name__ == '__main__':
    main()
