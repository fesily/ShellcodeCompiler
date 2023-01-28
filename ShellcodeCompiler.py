#! /usr/bin/env python3
import re
import sys
import subprocess
import shlex
import pathlib
from typing import List


def compiler(sourcefile, target_file):
    ret_code = subprocess.call(shlex.split(f"clang {sourcefile} -shared -fpic -o {target_file} -std=c++17 -O3"))
    if ret_code < 0:
        print("Child was terminated by signal", -ret_code, file=sys.stderr)
        sys.exit(1)
    if ret_code != 0:
        print("Child returned", ret_code, file=sys.stderr)
        sys.exit(1)


def split_lines(lines: List[bytes]):
    stats = 0
    reg = re.compile("([0-9a-f]{2,}) ")
    code = bytearray()
    for line in lines:
        if stats == 1:
            matched = reg.findall(line[6:])
            code += bytearray.fromhex("".join(matched))
            if len(matched) == 0:
                stats = 0
        if stats == 0:
            if line == 'Contents of section __TEXT,__text:':
                stats = 1
            elif line == 'Contents of section __TEXT,__cstring:':
                stats = 1
    return code


def main(sourcefile, outputfile):
    if not sourcefile.exists():
        print(f"{sourcefile} is not exists")
        return
    target_file = sourcefile.with_suffix('.so')
    compiler(sourcefile, target_file)

    pc = subprocess.run(shlex.split(f"objdump {target_file} -s"), stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                        text=True)
    if pc.returncode == 0:
        lines = pc.stdout.splitlines()
        code = split_lines(lines)
        if outputfile:
            with open(outputfile, "wb") as f:
                f.write(code)
        else:
            code = '\\' + code.hex('\\')
            sys.stdout.write(code.replace('\\', '\\x'))


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("need source_file_path \r\n help:\r\n \tshellcodecompiler source_file_path [output_file_path]")
        sys.exit(0)
    sourcefile = pathlib.Path(sys.argv[1])
    outputfile = len(sys.argv) >= 3 and pathlib.Path(sys.argv[2]) or None
    main(sourcefile, outputfile)
