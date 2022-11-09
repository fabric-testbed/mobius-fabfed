import logging
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from typing import List

from fabfed.model.state import ProviderState
from fabfed.util.constants import Constants


def create_parser(usage='%(prog)s [options]',
                  description='',
                  formatter_class=None):
    formatter_class = formatter_class or RawDescriptionHelpFormatter
    return ArgumentParser(usage=usage, description=description, formatter_class=formatter_class)


def build_parser(*, manage_workflow, manage_sessions):
    description = (
        'Fabfed'
        '\n'
        '\n'
        'Examples:'
        '\n'
        "      fabfed workflow --var-file vars.yml --session test-chi -validate"
        '\n'
        "      fabfed workflow --config-dir . --session test-chi -validate"
        '\n'
    )

    parser = create_parser(description=description)
    subparsers = parser.add_subparsers()
    workflow_parser = subparsers.add_parser('workflow', help='Manage fabfed workflows')
    workflow_parser.add_argument('-c', '--config-dir', type=str, default='.',
                                 help='config directory with .fab files. Defaults to current directory.',
                                 required=False)
    workflow_parser.add_argument('-v', '--var-file', type=str, default='',
                                 help="Yaml file with key-value pairs to override the variables' default values",
                                 required=False)
    workflow_parser.add_argument('-s', '--session', type=str, default='',
                                 help='friendly session name to help track a workflow', required=True)
    workflow_parser.add_argument('-validate', action='store_true', default=False,
                                 help='assembles and validates all .fab files  in the config directory')
    workflow_parser.add_argument('-apply', action='store_true', default=False, help='create resources')
    workflow_parser.add_argument('-plan', action='store_true', default=False, help='shows plan')
    workflow_parser.add_argument('-show', action='store_true', default=False, help='display resources')
    workflow_parser.add_argument('-summary', action='store_true', default=False, help='display resources')
    workflow_parser.add_argument('-json', action='store_true', default=False,
                                 help='use json output. relevant when used with -show or -plan')
    workflow_parser.add_argument('-destroy', action='store_true', default=False, help='delete resources')
    workflow_parser.set_defaults(dispatch_func=manage_workflow)

    sessions_parser = subparsers.add_parser('sessions', help='Manage fabfed sessions ')
    sessions_parser.add_argument('-show', action='store_true', default=False, help='display sessions')
    sessions_parser.add_argument('-json', action='store_true', default=False, help='use json format')
    sessions_parser.set_defaults(dispatch_func=manage_sessions)
    return parser


def init_looger(log_level=logging.INFO):
    from logging.handlers import RotatingFileHandler

    log_config = {'log-file': './fabfed.log',
                  'log-level': 'INFO',
                  'log-retain': 5,
                  'log-size': 5000000,
                  'logger': 'fabfed'}

    logger = logging.getLogger(str(log_config.get(Constants.PROPERTY_CONF_LOGGER, __name__)))

    log_level = log_config.get(Constants.PROPERTY_CONF_LOG_LEVEL, log_level)
    logger.setLevel(log_level)

    file_handler = RotatingFileHandler(log_config.get(Constants.PROPERTY_CONF_LOG_FILE),
                                       backupCount=int(log_config.get(Constants.PROPERTY_CONF_LOG_RETAIN)),
                                       maxBytes=int(log_config.get(Constants.PROPERTY_CONF_LOG_SIZE)))
    # noinspection PyArgumentList
    logging.basicConfig(level=log_level,
                        format="%(asctime)s [%(filename)s:%(lineno)d] [%(levelname)s] %(message)s",
                        handlers=[logging.StreamHandler(), file_handler], force=True)
    return logger


def load_as_ns_from_yaml(*, dir_path=None, content=None):
    import yaml
    import json
    from types import SimpleNamespace

    objs = []

    if dir_path:
        from pathlib import Path
        import os

        dir_path = Path(dir_path).expanduser().absolute()

        if not os.path.isdir(dir_path):
            raise Exception(f'Expected a directory {dir_path}')

        configs = [conf for conf in os.listdir(dir_path) if conf.endswith(Constants.FAB_EXTENSION)]

        if not configs:
            raise Exception(f'No {Constants.FAB_EXTENSION} config files found in  {dir_path}')

        for config in configs:
            file_name = os.path.join(dir_path, config)

            with open(file_name, 'r') as stream:
                obj = yaml.load(stream, Loader=yaml.FullLoader)
                obj = json.loads(json.dumps(obj), object_hook=lambda dct: SimpleNamespace(**dct))
                objs.append(obj)
    else:
        obj = yaml.safe_load(content)
        obj = json.loads(json.dumps(obj), object_hook=lambda dct: SimpleNamespace(**dct))
        objs.append(obj)

    return objs


def load_yaml_from_file(file_name):
    import yaml
    from pathlib import Path

    path = Path(file_name).expanduser().absolute()

    with open(str(path), 'r') as stream:
        return yaml.load(stream, Loader=yaml.FullLoader)


def load_vars(var_file):
    import yaml
    import os

    if not os.path.isfile(var_file):
        raise Exception(f'The supplied var-file {var_file} is invalid')

    with open(var_file, 'r') as stream:
        return yaml.load(stream, Loader=yaml.FullLoader)


def get_base_dir():
    from pathlib import Path
    import os

    base_dir = os.path.join(str(Path.home()), '.fabfed', 'sessions')
    os.makedirs(base_dir, exist_ok=True)
    return base_dir


def dump_sessions(to_json: bool):
    import os
    import sys

    base_dir = get_base_dir()
    sessions = [s[:-4] for s in os.listdir(base_dir) if s.endswith('.yml')]

    if to_json:
        import json

        sys.stdout.write(json.dumps(sessions, default=lambda o: o.__dict__, indent=3))
    else:
        import yaml

        sys.stdout.write(yaml.dump(sessions))

    return sessions


def dump_states(states, to_json: bool):
    import sys
    from fabfed.model.state import get_dumper

    if to_json:
        import json

        sys.stdout.write(json.dumps(states, default=lambda o: o.__dict__, indent=3))
    else:
        import yaml

        sys.stdout.write(yaml.dump(states, Dumper=get_dumper()))


def load_states(friendly_name) -> List[ProviderState]:
    import yaml
    import os
    from fabfed.model.state import get_loader

    file_path = os.path.join(get_base_dir(), friendly_name + '.yml')

    if os.path.exists(file_path):
        with open(file_path, 'r') as stream:
            try:
                return yaml.load(stream, Loader=get_loader())
            except Exception as e:
                from fabfed.exceptions import StateException

                raise StateException(f'Exception while loading state at {file_path}:{e}')

    return []


def save_states(states: List[ProviderState], friendly_name):
    import yaml
    import os
    from fabfed.model.state import get_dumper

    file_path = os.path.join(get_base_dir(), friendly_name + '.yml')

    with open(file_path, "w") as stream:
        try:
            stream.write(yaml.dump(states, Dumper=get_dumper()))
        except Exception as e:
            from fabfed.exceptions import StateException

            raise StateException(f'Exception while saving state at {file_path}:{e}')