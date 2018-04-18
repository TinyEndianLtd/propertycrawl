import sys
import math
import os

from .utils.common import read_json_lines
from .utils.flat import get_districts, add_districts


def avg_price_per_square_meter(data):
    return sum([datum['price'] / datum['area'] for datum in data]) / len(data)

def avg_roi(for_rent_data, for_sale_data):
    return avg_price_per_square_meter(for_rent_data) * 10 / avg_price_per_square_meter(for_sale_data)


if __name__ == '__main__':
    rent_in, sales_in = sys.argv[1:]
    for_rent = read_json_lines(rent_in)
    for_sale = read_json_lines(sales_in)
    all_property = for_rent + for_sale
    all_districts = get_districts(all_property) 
    add_districts(all_property, all_districts)

    results = [(u"City Average", avg_roi(for_rent, for_sale) * 100)]
    for district in all_districts:
        for_rent_in_district = [datum for datum in for_rent if datum['district'] == district]
        for_sale_in_district = [datum for datum in for_sale if datum['district'] == district]
        if len(for_rent_in_district) != 0 and len(for_sale_in_district) != 0:
            results.append((district, avg_roi(for_rent_in_district, for_sale_in_district) * 100))
        else:
            results.append((district, ""))

    sys.stdout.buffer.write(u"# Dzielnica, ROI (%){0}".format(os.linesep).encode('utf-8'))
    for r in sorted(results, key=lambda p: p[1], reverse=True):
        sys.stdout.buffer.write(u"{0}, {1}{2}".format(r[0], r[1], os.linesep).encode('utf-8'))
