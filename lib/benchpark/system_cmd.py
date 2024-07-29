# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os

#import benchpark.systems as systems
#import benchpark.repo as repo
import benchpark.system


def system_create(args):
    init_kwargs = dict()
    if args.set:
        for kv in args.set:
            k, v = kv.split("=")
            k = k.replace("-", "_")
            init_kwargs[k] = v

    if args.system_type:
        system = benchpark.system.system_class(args.system_type)(**init_kwargs)
        #system = repo.systems.get(args.system_type)(**init_kwargs)
        #system = systems.system_from_type(args.system_type, **init_kwargs)
    elif args.use_existing:
        pass
    else:
        raise ValueError("Must specify one of: --type, --from")

    if args.basedir:
        base = args.basedir
        sysdir = system.system_id()
        destdir = os.path.join(base, sysdir)
    elif args.dest:
        destdir = args.dest
    else:
        raise ValueError("Must specify one of: --dest, --basedir")

    if os.path.exists(destdir):
        raise ValueError(f"System description dir already exists: {destdir}")
    os.mkdir(destdir)

    system.generate_description(destdir)


def system_list(args):
    raise NotImplementedError("'benchpark system list' is not available")


def setup_parser(root_parser):
    system_subparser = root_parser.add_subparsers(dest="system_subcommand")

    create_parser = system_subparser.add_parser("create")
    create_parser.add_argument(
        "--from", dest="use_existing", type=str, help="Copy an existing system config"
    )
    create_parser.add_argument(
        "--type",
        dest="system_type",
        type=str,
        help="Use a template class to generate a system config",
    )
    create_parser.add_argument("--dest", help="Place all system files here directly")
    create_parser.add_argument(
        "--basedir", help="Generate a system dir under this, and place all files there"
    )

    create_parser.add_argument(
        "--set", action="append", help="Set system-specific attributes"
    )

    system_subparser.add_parser("list")


def command(args):
    actions = {
        "create": system_create,
        "list": system_list,
    }
    if args.system_subcommand in actions:
        actions[args.system_subcommand](args)
    else:
        raise ValueError(f"Unknown subcommand for 'system': {args.system_subcommand}")
