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
    """
    Dumps json lines lines to outbuffer without modifying.
    :param lines:
    :param outbuffer:
    :return:
    """
    for line in lines:
        outbuffer.write(u"{0}{1}".format(line, os.linesep).encode('utf-8'))


def dump_env(lines, outbuffer=sys.stdout.buffer):
    """
    Extracts key from json lines lines and dumps ot outbuffer.
    :param lines:
    :param outbuffer:
    :return:
    """
    for line in lines:
        k = json.loads(line)
        outbuffer.write(u"{0}{1}".format(k['key'], os.linesep).encode('utf-8'))


if __name__ == '__main__':
    ARGUMENTS = docopt(__doc__)
    LINES_SEQ = (line.strip() for line in sys.stdin if line.strip())
    if ARGUMENTS['--jl']:
        dump_jl(LINES_SEQ)
    if ARGUMENTS['--env']:
        dump_env(LINES_SEQ)
