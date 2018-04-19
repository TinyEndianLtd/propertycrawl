"""
Common utilities
"""

import json


def read_json_lines(filename):
    """
    Given a filename reads data from file assuming json lines format
    :param filename:
    :return:
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines]
