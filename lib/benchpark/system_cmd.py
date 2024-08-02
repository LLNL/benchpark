# Copyright 2023 Lawrence Livermore National Security, LLC and other
# Benchpark Project Developers. See the top-level COPYRIGHT file for details.
#
# SPDX-License-Identifier: Apache-2.0

import os
import shutil
import sys

import benchpark.system
import benchpark.spec


def system_create(args):
    system_spec = benchpark.spec.SystemSpec(' '.join(args.spec))
    system_spec = system_spec.concretize()
    import pdb; pdb.set_trace()
    #system = benchpark.system.system_class(args.system_type)(**init_kwargs)

    if args.basedir:
        base = args.basedir
        sysdir = system.system_id()
        destdir = os.path.join(base, sysdir)
    elif args.dest:
        destdir = args.dest
    else:
        raise ValueError("Must specify one of: --dest, --basedir")

    try:
        os.mkdir(destdir)
        system.generate_description(destdir)
    except FileExistsError:
        print(f"Abort: system description dir already exists ({destdir})")
        sys.exit(1)
    except:
        # If there was a failure, remove any partially-generated resources
        shutil.rmtree(destdir)
        raise


def system_list(args):
    raise NotImplementedError("'benchpark system list' is not available")


def setup_parser(root_parser):
    system_subparser = root_parser.add_subparsers(dest="system_subcommand")

    create_parser = system_subparser.add_parser("create")
    create_parser.add_argument(
        "--from", dest="use_existing", type=str, help="Copy an existing system config"
    )
    create_parser.add_argument("--dest", help="Place all system files here directly")
    create_parser.add_argument(
        "--basedir", help="Generate a system dir under this, and place all files there"
    )

    create_parser.add_argument("spec", nargs="+", help="System spec")

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
