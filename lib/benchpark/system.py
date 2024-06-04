import hashlib
import os

import benchpark.systems as systems


def _hash_id(content_list):
    sha256_hash = hashlib.sha256()
    for x in content_list:
        sha256_hash.update(x.encode("utf-8"))
    return sha256_hash.hexdigest()


def system_create(args):
    init_kwargs = dict()
    if args.set:
        for kv in args.set:
            k, v = kv.split("=")
            k = k.replace("-", "_")
            init_kwargs[k] = v

    if args.system_type:
        system = systems.system_from_type(args.system_type, **init_kwargs)
    elif args.use_existing:
        pass
    else:
        raise ValueError("Must specify one of: --type, --from")

    variables_yaml = system.generate_system_description()

    if args.basedir:
        base = args.basedir
        sysdir = _hash_id([variables_yaml])
        destdir = os.path.join(base, sysdir)
    elif args.dest:
        destdir = args.dest
    else:
        raise ValueError("Must specify one of: --dest, --basedir")

    if os.path.exists(destdir):
        raise ValueError(f"System description dir already exists: {destdir}")
    os.mkdir(destdir)

    gen_files = {
        "variables.yaml": variables_yaml
    }
    for fname, content in gen_files.items():
        path = os.path.join(destdir, fname)
        with open(path, "w") as f:
            f.write(content)

def system_list(args):
    raise NotImplementedError("'benchpark system list' is not available")


def setup_parser(root_parser):
    system_subparser = root_parser.add_subparsers(dest="system_subcommand")

    create_parser = system_subparser.add_parser("create")
    create_parser.add_argument(
        "--from", dest="use_existing", type=str, help="Copy an existing system config"
    )
    create_parser.add_argument(
        "--type", dest="system_type", type=str,
        help="Use a template class to generate a system config"
    )
    create_parser.add_argument("--dest", help="Place all system files here directly")
    create_parser.add_argument(
        "--basedir", help="Generate a system dir under this, and place all files there"
    )

    create_parser.add_argument(
        "--set", action="append", help="Set system-specific attributes"
    )

    list_subparser = system_subparser.add_parser("list")


def command(args):
    actions = {
        "create": system_create,
        "list": system_list,
    }
    if args.system_subcommand in actions:
        actions[args.system_subcommand](args)
    else:
        raise ValueError(f"Unknown subcommand for 'system': {args.system_subcommand}")
