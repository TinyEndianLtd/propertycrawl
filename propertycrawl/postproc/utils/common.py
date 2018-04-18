import json
import math


def read_json_lines(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()
    return [json.loads(line) for line in lines]
