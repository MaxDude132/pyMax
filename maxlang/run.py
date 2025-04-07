from argparse import ArgumentParser
from maxlang.main import Max


if __name__ == "__main__":
    arg_parser = ArgumentParser()
    arg_parser.add_argument("script", nargs="?")
    arg_parser.add_argument("--source", "-s")
    arg_parser.add_argument("--decompose", "-d", action="store_true")
    args = arg_parser.parse_args()

    if args.script:
        Max(args.decompose).run_file(args.script)
    elif args.source:
        Max(args.decompose).run_source(args.source)
    else:
        Max(args.decompose).run_prompt()
