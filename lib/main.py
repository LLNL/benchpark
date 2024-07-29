# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import argparse
import os
import pathlib
import shlex
import shutil
import subprocess
import sys
import yaml

import benchpark.system_cmd
from benchpark.runtime import RuntimeResources

DEBUG = False

__version__ = "0.1.0"


def debug_print(message):
    if DEBUG:
        print("(debug) " + str(message))


def main():
    if sys.version_info[:2] < (3, 8):
        raise Exception("Benchpark requires at least python 3.8+.")

    parser = argparse.ArgumentParser(description="Benchpark")
    parser.add_argument(
        "-V", "--version", action="store_true", help="show version number and exit"
    )

    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

    actions = {}
    benchpark_list(subparsers, actions)
    benchpark_setup(subparsers, actions)
    benchpark_tags(subparsers, actions)
    init_commands(subparsers, actions)

    args = parser.parse_args()
    no_args = True if len(sys.argv) == 1 else False

    if no_args:
        parser.print_help()
        return 1

    if args.version:
        print(get_version())
        return 0

    if args.subcommand in actions:
        actions[args.subcommand](args)
    else:
        print(
            "Invalid subcommand ({args.subcommand}) - must choose one of: "
            + " ".join(actions.keys())
        )


def get_version():
    benchpark_version = __version__
    return benchpark_version


def source_location():
    script_location = os.path.dirname(os.path.abspath(__file__))
    return pathlib.Path(script_location).parent


def benchpark_list(subparsers, actions_dict):
    list_parser = subparsers.add_parser(
        "list", help="List available experiments, systems, and modifiers"
    )
    list_parser.add_argument("sublist", nargs="?")
    actions_dict["list"] = benchpark_list_handler


def benchpark_benchmarks():
    source_dir = source_location()
    benchmarks = []
    experiments_dir = source_dir / "experiments"
    for x in os.listdir(experiments_dir):
        benchmarks.append(f"{x}")
    return benchmarks


def benchpark_experiments():
    source_dir = source_location()
    experiments = []
    experiments_dir = source_dir / "experiments"
    for x in os.listdir(experiments_dir):
        for y in os.listdir(experiments_dir / x):
            experiments.append(f"{x}/{y}")
    return experiments


def benchpark_systems():
    source_dir = source_location()
    systems = []
    for x in os.listdir(source_dir / "configs"):
        if not (
            os.path.isfile(os.path.join(source_dir / "configs", x)) or x == "common"
        ):
            systems.append(x)
    return systems


def benchpark_modifiers():
    source_dir = source_location()
    modifiers = []
    for x in os.listdir(source_dir / "modifiers"):
        modifiers.append(x)
    return modifiers


def benchpark_get_tags():
    f = source_location() / "tags.yaml"
    tags = []

    with open(f, "r") as stream:
        try:
            data = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    for k0, v0 in data.items():
        if k0 == "benchpark-tags":
            for k, v in v0.items():
                if isinstance(v, list):
                    for i in v:
                        tags.append(i)
        else:
            print("ERROR file does not contain benchpark-tags")

    return tags


def benchpark_list_handler(args):
    sublist = args.sublist
    benchmarks = benchpark_benchmarks()
    experiments = benchpark_experiments()
    systems = benchpark_systems()
    modifiers = benchpark_modifiers()

    if sublist is None:
        print("Experiments:")
        for experiment in experiments:
            print(f"\t{experiment}")
        print("Systems:")
        for system in systems:
            print(f"\t{system}")
    elif sublist == "benchmarks":
        print("Benchmarks:")
        for benchmark in benchmarks:
            print(f"\t{benchmark}")
    elif sublist == "experiments":
        print("Experiments:")
        for experiment in experiments:
            print(f"\t{experiment}")
    elif sublist == "systems":
        print("Systems:")
        for system in systems:
            print(f"\t{system}")
    elif sublist == "modifiers":
        print("Modifiers:")
        for modifier in modifiers:
            print(f"\t{modifier}")
    else:
        raise ValueError(
            f'Invalid benchpark list "{sublist}" - must choose [experiments], [systems], [modifiers] or leave empty'
        )


def benchpark_check_benchmark(arg_str):
    benchmarks = benchpark_benchmarks()
    found = arg_str in benchmarks
    if not found:
        out_str = f'Invalid benchmark "{arg_str}" - must choose one of: '
        for benchmark in benchmarks:
            out_str += f"\n\t{benchmark}"
        raise ValueError(out_str)
    return found


def benchpark_check_experiment(arg_str):
    experiments = benchpark_experiments()
    found = arg_str in experiments
    if not found:
        out_str = f'Invalid experiment (benchmark/ProgrammingModel) "{arg_str}" - must choose one of: '
        for experiment in experiments:
            out_str += f"\n\t{experiment}"
        raise ValueError(out_str)
    return found


def benchpark_check_system(arg_str):
    systems = benchpark_systems()
    found = arg_str in systems
    if not found:
        out_str = f'Invalid system "{arg_str}" - must choose one of: '
        for system in systems:
            out_str += f"\n\t{system}"
        raise ValueError(out_str)
    return found


def benchpark_check_tag(arg_str):
    tags = benchpark_get_tags()
    found = arg_str in tags
    if not found:
        out_str = f'Invalid tag "{arg_str}" - must choose one of: '
        for tag in tags:
            out_str += f"\n\t{tag}"
        raise ValueError(out_str)
    return found


def benchpark_check_modifier(arg_str):
    modifiers = benchpark_modifiers()
    found = arg_str in modifiers
    if not found:
        out_str = f'Invalid modifier "{arg_str}" - must choose one of: '
        for modifier in modifiers:
            out_str += f"\n\t{modifier}"
        raise ValueError(out_str)
    return found


def benchpark_setup(subparsers, actions_dict):
    create_parser = subparsers.add_parser(
        "setup", help="Set up an experiment and prepare it to build/run"
    )

    create_parser.add_argument(
        "experiment",
        type=str,
        help="The experiment (benchmark/ProgrammingModel) to run",
    )
    create_parser.add_argument(
        "system", type=str, help="The system on which to run the experiment"
    )
    create_parser.add_argument(
        "experiments_root",
        type=str,
        help="Where to install packages and store results for the experiments. Benchpark expects to manage this directory, and it should be empty/nonexistent the first time you run benchpark setup experiments.",
    )
    create_parser.add_argument(
        "--modifier",
        type=str,
        default="none",
        help="The modifier to apply to the experiment (default none)",
    )

    actions_dict["setup"] = benchpark_setup_handler


def init_commands(subparsers, actions_dict):
    """This function is for initializing commands that are defined outside
    of this script. It is intended that all command setup will eventually
    be refactored in this way (e.g. `benchpark_setup` will be defined in
    another file.
    """
    system_parser = subparsers.add_parser("system", help="Initialize a system config")
    benchpark.system_cmd.setup_parser(system_parser)
    actions_dict["system"] = benchpark.system_cmd.command


def run_command(command_str, env=None):
    proc = subprocess.Popen(
        shlex.split(command_str),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(
            f"Failed command: {command_str}\nOutput: {stdout}\nError: {stderr}"
        )

    return (stdout, stderr)


def benchpark_tags(subparsers, actions_dict):
    create_parser = subparsers.add_parser("tags", help="Tags in Benchpark experiments")
    create_parser.add_argument(
        "experiments_root",
        type=str,
        help="The experiments_root you specified during Benchpark setup.",
    )
    create_parser.add_argument(
        "-a",
        "--application",
        action="store",
        help="The application for which to find Benchpark tags",
    )
    create_parser.add_argument(
        "-t",
        "--tag",
        action="store",
        help="The tag for which to search in Benchpark experiments",
    )
    actions_dict["tags"] = benchpark_tags_handler


# Note: it would be nice to vendor spack.llnl.util.link_tree, but that
# involves pulling in most of llnl/util/ and spack/util/
def symlink_tree(src, dst, include_fn=None):
    """Like ``cp -R`` but instead of files, create symlinks"""
    src = os.path.abspath(src)
    dst = os.path.abspath(dst)
    # By default, we include all filenames
    include_fn = include_fn or (lambda f: True)
    for x in [src, dst]:
        if not os.path.isdir(x):
            raise ValueError(f"Not a directory: {x}")
    for src_subdir, directories, files in os.walk(src):
        relative_src_dir = pathlib.Path(os.path.relpath(src_subdir, src))
        dst_dir = pathlib.Path(dst) / relative_src_dir
        dst_dir.mkdir(parents=True, exist_ok=True)
        for x in files:
            if not include_fn(x):
                continue
            dst_symlink = dst_dir / x
            src_file = os.path.join(src_subdir, x)
            os.symlink(src_file, dst_symlink)


def benchpark_setup_handler(args):
    """
    experiments_root/
        spack/
        ramble/
        <experiment>/
            <system>/
                workspace/
                    configs/
                        (everything from source/configs/<system>)
                        (everything from source/experiments/<experiment>)
    """

    experiment = args.experiment
    system = args.system
    experiments_root = pathlib.Path(os.path.abspath(args.experiments_root))
    modifier = args.modifier
    source_dir = source_location()
    debug_print(f"source_dir = {source_dir}")
    debug_print(f"specified experiment (benchmark/ProgrammingModel) = {experiment}")
    benchpark_check_experiment(experiment)
    debug_print(f"specified system = {system}")
    benchpark_check_system(system)
    debug_print(f"specified modifier = {modifier}")
    benchpark_check_modifier(modifier)

    workspace_dir = experiments_root / str(experiment) / str(system)

    if workspace_dir.exists():
        if workspace_dir.is_dir():
            print(f"Clearing existing workspace {workspace_dir}")
            shutil.rmtree(workspace_dir)
        else:
            print(
                f"Benchpark expects to manage {workspace_dir} as a directory, but it is not"
            )
            sys.exit(1)

    workspace_dir.mkdir(parents=True)

    ramble_workspace_dir = workspace_dir / "workspace"
    ramble_configs_dir = ramble_workspace_dir / "configs"
    ramble_logs_dir = ramble_workspace_dir / "logs"
    ramble_spack_experiment_configs_dir = (
        ramble_configs_dir / "auxiliary_software_files"
    )

    print(f"Setting up configs for Ramble workspace {ramble_configs_dir}")

    configs_src_dir = source_dir / "configs" / str(system)
    experiment_src_dir = source_dir / "experiments" / experiment
    modifier_config_dir = source_dir / "modifiers" / modifier / "configs"
    ramble_configs_dir.mkdir(parents=True)
    ramble_logs_dir.mkdir(parents=True)
    ramble_spack_experiment_configs_dir.mkdir(parents=True)

    def include_fn(fname):
        # Only include .yaml and .tpl files
        # Always exclude files that start with "."
        if fname.startswith("."):
            return False
        if fname.endswith(".yaml"):
            return True
        return False

    symlink_tree(configs_src_dir, ramble_configs_dir, include_fn)
    symlink_tree(experiment_src_dir, ramble_configs_dir, include_fn)
    symlink_tree(modifier_config_dir, ramble_configs_dir, include_fn)
    symlink_tree(
        source_dir / "configs" / "common",
        ramble_spack_experiment_configs_dir,
        include_fn,
    )

    template_name = "execute_experiment.tpl"
    experiment_template_options = [
        configs_src_dir / template_name,
        experiment_src_dir / template_name,
        source_dir / "common-resources" / template_name,
    ]
    for choice_template in experiment_template_options:
        if os.path.exists(choice_template):
            break
    os.symlink(
        choice_template,
        ramble_configs_dir / "execute_experiment.tpl",
    )

    initializer_script = experiments_root / "setup.sh"

    per_workspace_setup = RuntimeResources(experiments_root)

    spack, first_time_spack = per_workspace_setup.spack_first_time_setup()
    ramble, first_time_ramble = per_workspace_setup.ramble_first_time_setup()

    if first_time_spack:
        spack("repo", "add", "--scope=site", f"{source_dir}/repo")

    if first_time_ramble:
        ramble(f"repo add --scope=site {source_dir}/repo")
        ramble('config --scope=site add "config:disable_progress_bar:true"')
        ramble(f"repo add -t modifiers --scope=site {source_dir}/modifiers")
        ramble("config --scope=site add \"config:spack:global:args:'-d'\"")

    if not initializer_script.exists():
        with open(initializer_script, "w") as f:
            f.write(
                f"""\
if [ -n "${{_BENCHPARK_INITIALIZED:-}}" ]; then
    return 0
fi

. {per_workspace_setup.spack_location}/share/spack/setup-env.sh
. {per_workspace_setup.ramble_location}/share/ramble/setup-env.sh

export SPACK_DISABLE_LOCAL_CONFIG=1

export _BENCHPARK_INITIALIZED=true
"""
            )

    instructions = f"""\
To complete the benchpark setup, do the following:

    . {initializer_script}

Further steps are needed to build the experiments (ramble -P -D {ramble_workspace_dir} workspace setup) and run them (ramble -P -D {ramble_workspace_dir} on)
"""
    print(instructions)


def helper_experiments_tags(ramble_exe, benchmarks):
    # find all tags in Ramble applications (both in Ramble built-in and in Benchpark/repo)
    (tags_stdout, tags_stderr) = run_command(f"{ramble_exe} attributes --tags --all")
    ramble_applications_tags = {}
    lines = tags_stdout.splitlines()

    for line in lines:
        key_value = line.split(":")
        ramble_applications_tags[key_value[0]] = key_value[1].strip().split(",")

    benchpark_experiments_tags = {}
    for benchmark in benchmarks:
        benchpark_experiments_tags[benchmark] = ramble_applications_tags[benchmark]
    return benchpark_experiments_tags


def benchpark_tags_handler(args):
    """
    Filter ramble tags by benchpark benchmarks
    """
    experiments_root = pathlib.Path(os.path.abspath(args.experiments_root))
    ramble_location = experiments_root / "ramble"
    ramble_exe = ramble_location / "bin" / "ramble"
    benchmarks = benchpark_benchmarks()

    if args.tag:
        if benchpark_check_tag(args.tag):
            # find all applications in Ramble that have a given tag (both in Ramble built-in and in Benchpark/repo)
            (tag_stdout, tag_stderr) = run_command(f"{ramble_exe} list -t {args.tag}")
            lines = tag_stdout.splitlines()

            for line in lines:
                if line in benchmarks:
                    print(line)

    elif args.application:
        if benchpark_check_benchmark(args.application):
            benchpark_experiments_tags = helper_experiments_tags(ramble_exe, benchmarks)
            print(benchpark_experiments_tags[args.application])
    else:
        benchpark_experiments_tags = helper_experiments_tags(ramble_exe, benchmarks)
        print("All tags that exist in Benchpark experiments:")
        for k, v in benchpark_experiments_tags.items():
            print(k)


if __name__ == "__main__":
    main()
