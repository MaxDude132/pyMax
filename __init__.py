from argparse import ArgumentParser
from main import Lox


if __name__ == '__main__':
    arg_parser = ArgumentParser()
    arg_parser.add_argument("script", nargs='?')
    args = arg_parser.parse_args()

    Lox(args.script)
