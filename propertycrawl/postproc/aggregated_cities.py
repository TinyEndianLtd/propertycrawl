"""
The purpose of this file is to perform a merge of list of json lines
into a set of json lines based on uniqueness of `key` property.
When duplicate is found `update` is called on dicts to perform merge.
Merging of dates in `available_dates` is done by set addition

Usage:
  aggregated_cities.py <job_start_date>
"""
import sys
import os
import json
from docopt import docopt

if __name__ == '__main__':
    ARGUMENTS = docopt(__doc__)
    JOB_START_DATE = ARGUMENTS['<job_start_date>']
    RESULT = dict()

    for line in sys.stdin:
        new_datum = json.loads(line)
        old_datum = RESULT.get(new_datum['key'], dict())
        old_datum.update(new_datum)
        dates_list = old_datum.get('available_dates', [])
        dates_set = set(dates_list)
        dates_set.add(JOB_START_DATE)
        old_datum['available_dates'] = list(dates_set)
        RESULT[new_datum['key']] = old_datum

    for v in RESULT.values():
        raw = json.dumps(v)
        sys.stdout.buffer.write('{0}{1}'.format(raw,
                                                os.linesep).encode('utf-8'))
