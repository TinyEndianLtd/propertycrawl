"""
Usage:
  dump_cities.py [--jl | --env]

Options:
  --jl      Dump json lines.
  --env     Dump keys.
"""

import sys
import os
import json
from docopt import docopt


def dump_jl(lines, outbuffer=sys.stdout.buffer):
    for line in lines:
        outbuffer.write(u"{0}{1}".format(line, os.linesep).encode('utf-8'))


def dump_env(lines, outbuffer=sys.stdout.buffer):
    for line in lines:
        k = json.loads(line)
        outbuffer.write(u"{0}{1}".format(k['key'], os.linesep).encode('utf-8'))


if __name__ == '__main__':
    arguments = docopt(__doc__)
    lines = [line.strip() for line in sys.stdin if len(line.strip()) > 0]
    if arguments['--jl']:
        dump_jl(lines)
    if arguments['--env']:
        dump_env(lines)
