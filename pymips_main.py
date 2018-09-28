import sys
MIN_PYTHON = (3, 6)
if sys.version_info < MIN_PYTHON:
    print("Require python" +
          str(MIN_PYTHON[0]) + "." + str(MIN_PYTHON[1]) +
          " got " + str(sys.version_info.major) + "." + str(sys.version_info.minor))
    sys.exit(1)

import argparse

from pathlib import Path
from compiler.compiler import compile_file

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-i', '--input', dest='input',
                        help='folder or file for scripts')
    parser.add_argument('--debug', dest='debug', default=False,
                        help='Output additional debug information for the code', action='store_true')
    args = parser.parse_args()
    a = Path(args.input)

    if Path.is_dir(a):
        for child in a.iterdir():
            if child.suffix == '.py':
                compile_file(child, args.debug)
    elif a.suffix == '.py':
        compile_file(a, args.debug)
