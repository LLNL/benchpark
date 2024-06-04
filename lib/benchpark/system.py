

def system_create(args):
    pass

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
