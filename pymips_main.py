import argparse
from pathlib import Path

from compiler.compiler import Compiler


def compile_file(file: Path, debug=False):
    file_o = Path(f'{file}.mips')
    with file.open('r') as fd_r, file_o.open('w') as fd_w:
        a = fd_r.read()

        compiler = Compiler(debug=debug)
        compiler.compile(a)

        output = ""
        if debug:
            output = a.strip() + '\n'

            output += "Begin Python**************************\n"
            output += a.strip(a) + '\n'
            output += "End Python*****************************\n"

            output += "MIPS***********************************\n"
            for i, (line, desc) in enumerate(compiler.final_program):
               output += f'{line:35} {i:2}: {desc}\n'

            output += "MIPS***********************************\n"
        for i, (line, desc) in enumerate(compiler.final_program):
            output += f'{line}\n'
        print(output)
        fd_w.write(output)


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
