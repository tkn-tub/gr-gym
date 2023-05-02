'''
gnugym project, TU-Berlin 2020
Ali Alouane <ali.alouane@campus.tu-berlin.de>
'''

import os
from ruamel import yaml as yaml
from pathlib import Path
import argparse
import sys


def make_path_absolute(base_path, path):
    base_path = Path(base_path)
    path = Path(path)
    if path.is_absolute():
        return path
    else:
        return str(base_path / path)


def _construct_join(loader, node: yaml.Node):
    seq = loader.construct_sequence(node)
    return ''.join([str(i) for i in seq])


def get_dir_by_indicator(path=sys.path[0], indicator=".git"):
    """ Returns the path of the folder that contains the given indicator

    :param path: Path from where to search the directory tree upwards. (Default value = sys.path[0])
    :type path: str
    :param indicator: Name of the file that indicates the searched directory. (Default value = ".git")
    :type indicator: str
    :raises FileNotFoundError : If any path or any toplevel folder is not found with the given indicator, it raises
    FileNotFoundError.
    """

    is_root = os.path.exists(os.path.join(path, indicator))
    while not is_root:
        new_path = os.path.dirname(path)
        if new_path == path:
            raise FileNotFoundError(
                "Could not find folder containing indicator {:} in any path or any toplevel directory.".format(
                    indicator))
        path = new_path
        is_root = os.path.exists(os.path.join(path, indicator))

    return path

def load_yaml(yaml_path, **kwargs):
    """
    Returns a dict from a yaml file. Enables concatenation of strings with !join [str1, str2, ...]

    :param yaml_path: Path of the yaml file.
    :type yaml_path: str
    :param kwargs: Kwargs accepted from yaml.load function
    """

    if "Loader" not in kwargs:
        kwargs["Loader"] = yaml.SafeLoader
    yaml.add_constructor('!join', _construct_join, kwargs["Loader"])
    with open(yaml_path, 'r') as stream:
        yaml_dict = yaml.load(stream, **kwargs)

    return yaml_dict


def parse_yaml_path(yaml_path):
    parsed_path = str(yaml_path).split("::")
    p = parsed_path[0]
    sub_refs = parsed_path[1:] if len(parsed_path) > 1 else []
    return p, sub_refs


def args_from_dict(d):
    """Creates (nested) argparse.Namespace objects from (nested) dict.

        :param d: a dict
        :type d: dict
        :returns: (nested) argparse.Namespace object
        :rtype: argparse.Namepsace
        """

    args = argparse.Namespace(**d)
    for k, v in d.items():
        if isinstance(v, dict):
            setattr(args, k, args_from_dict(v))
    return args


def yaml_argparse(yaml_path, raw_args=None):
    """
    Allows default command line argument definition with a yaml file and enables to overwrite them via command line.

    This function first needs to have a template yaml file, where all needed command line arguments are defined with
    help and default values. Then according to the given command line argument, the function sets a new value of an
    existing command line argument key. These arguments are stored as Argumentparser object and can be
    accessed directly with the dot notation.

    Also, you can add a yaml file with '--file path_to_file', that contained customized configuration of
    command line arguments, and that overwrites default values. You can add multiple key-value pairs with
    `--tag key1=value1 key2=value"' that are stored as a dict in the resulting argument object.

    :param yaml_path: The path of the yaml file that defines default command line arguments.
    :param raw_args:  Allows to set command line arguments via python e.g raw_args=['--key', 'value'].
                      If raw_args is set, argparse ignores given command line arguments and uses
                      parser.parse_args(raw_args). (Default value = None)

    """
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-f", "--file",
                        help="yaml file containing experiment parameters. Stored as attribute 'file' in parsed "
                             "args.",
                        metavar="FILE",
                        required=False)

    hparam_dict = load_yaml(yaml_path)

    for key, value in hparam_dict.items():
        # kwargs unpacking
        if isinstance(value, dict):
            kwargs = dict(value)
            print(kwargs)
            value = kwargs.pop("default")
        else:
            kwargs = {}

        if isinstance(value, list):
            parser.add_argument("--" + key, default=value, **kwargs)
        elif isinstance(value, bool):
            parser.add_argument("--" + key, default=value, **kwargs)
        else:
            parser.add_argument("--" + key, type=type(value), default=value, **kwargs)

    def _get_cmd_args(args):
        cmd_args = []
        [cmd_args.append(x[2::]) for x in args if x[0:2] == "--"]
        return cmd_args

    # get command line arguments to prevent overriding them when applying parameters from another yaml file
    if raw_args:
        raw_args_cmd = _get_cmd_args(raw_args)
    elif len(sys.argv) > 1:
        raw_args_cmd = _get_cmd_args(sys.argv[1::])
    else:
        raw_args_cmd = []

    args = parser.parse_args(raw_args)
    if args.file:
        file_cfg = args.file.split("::")
        hparam_dict_yaml = load_yaml(file_cfg[0])
        if len(file_cfg) > 1:
            hparam_dict_yaml = hparam_dict_yaml[file_cfg[1]]

        # hparam analysis
        [print("Obsolete parameter '{:}' in {:}".format(key, args.file)) for key in hparam_dict_yaml.keys()
         if (key not in hparam_dict and not key == "file")]
        [print("Missing parameter {:} in {:}. Using default value.".format(key, args.file)) for key in
         hparam_dict.keys() if key not in hparam_dict_yaml]

        for key, value in hparam_dict.items():
            value = value["default"] if isinstance(value, dict) else value
            if (key in hparam_dict_yaml) and (key not in raw_args_cmd):
                if isinstance(hparam_dict_yaml[key], dict):
                    if "default" in hparam_dict_yaml[key]:
                        setattr(args, key, hparam_dict_yaml[key]["default"])
                    else:
                        setattr(args, key, hparam_dict_yaml[key])
                else:
                    setattr(args, key, hparam_dict_yaml[key])
    else:
        args.file = str(yaml_path)

    return args

