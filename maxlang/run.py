from argparse import ArgumentParser
from maxlang.main import Max


if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument("script", nargs='?')
    arg_parser.add_argument("--source", "-s")
    args = arg_parser.parse_args()

    if args.script:
        Max().run_file(args.script)
    elif args.source:
        Max().run_source(args.source)
    else:
        Max().run_prompt()
