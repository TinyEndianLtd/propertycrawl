"""
The purpose of this module is to provide daily aggregated report about
a single city
"""

import sys
import os
import json

from ..common.utils import read_json_lines
from .utils.flat import get_districts, add_districts


def avg_price_per_square_meter(data):
    """
    Given data calculates average price per square meter for all data points
    :param data:
    :return:
    """
    return sum([datum['price'] / datum['area'] for datum in data]) / len(data)


def avg_roi(for_rent_data, for_sale_data):
    """
    Given data calculates average expected roi for all data poin
    :param for_rent_data:
    :param for_sale_data:
    :return:
    """
    return avg_price_per_square_meter(
        for_rent_data) * 10 / avg_price_per_square_meter(for_sale_data)


if __name__ == '__main__':
    RENT_IN, SALES_IN = sys.argv[1:]  # pylint: disable=unbalanced-tuple-unpacking
    FOR_RENT = read_json_lines(RENT_IN)
    FOR_SALE = read_json_lines(SALES_IN)
    ALL_PROPERTY = FOR_RENT + FOR_SALE
    ALL_DISTRICTS = get_districts(ALL_PROPERTY)
    add_districts(ALL_PROPERTY, ALL_DISTRICTS)

    RESULTS = []
    for district in ALL_DISTRICTS:
        for_rent_in_district = [
            datum for datum in FOR_RENT if datum['district'] == district
        ]
        for_sale_in_district = [
            datum for datum in FOR_SALE if datum['district'] == district
        ]
        if for_rent_in_district and for_sale_in_district:
            RESULTS.append(
                (district,
                 avg_roi(for_rent_in_district, for_sale_in_district) * 100))
        else:
            RESULTS.append((district, ""))

    CLEAN_RESULTS = [r for r in RESULTS if r[1]]
    for r in sorted(CLEAN_RESULTS, key=lambda p: p[1], reverse=True):
        datum = {'district': r[0], 'roi': r[1]}
        sys.stdout.buffer.write(u"{0}{1}".format(
            json.dumps(datum), os.linesep).encode('utf-8'))
