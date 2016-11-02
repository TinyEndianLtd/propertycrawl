from os.path import relpath, dirname
import sys
from math import sin, cos, atan2, sqrt, pow, log, radians, degrees, pi


from bokeh.plotting import figure, save, output_file
from bokeh.models.ranges import Range1d
from mapbox import Static
import numpy as np
from scipy.spatial import Voronoi

from ..postproc.utils.common import read_json_lines
from ..postproc.utils.flat import get_districts, add_districts

ER = 6373e3
EC = 2 * pi * ER
MAP_WIDTH = 600
MAP_HEIGHT = 400

def bounds(data):
    lats = [datum['lat'] for datum in data]
    lons = [datum['lon'] for datum in data]
    return (max(lats), min(lons)), (min(lats), max(lons))

def dist(p1, p2):
    dlon = p2[1] - p1[1]
    dlat = p2[0] - p1[0]
    a = pow(sin(dlat/2), 2) + cos(p1[0]) * cos(p2[0]) * pow(sin(dlon/2), 2)
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    d = ER * c
    return d

def map_coords(nw_edge, se_edge, image_width, aspect_ratio):
    avg_lat = (nw_edge[0]+se_edge[0]) / 2
    avg_lon = (nw_edge[1]+se_edge[1]) / 2
    xdist = dist((avg_lat, nw_edge[1]), (avg_lat, se_edge[1]))
    ydist = dist((nw_edge[0], avg_lon), (se_edge[0], avg_lon))
    image_height = image_width / aspect_ratio
    given_ratio = xdist/ydist

    if given_ratio > aspect_ratio:
        s = xdist / image_width  # s is distance represented by one pixel
        zoom = -log((s / EC) / cos(avg_lat), 2) - 8
        resulting_ydist = image_height * s
        nw_lat = avg_lat + (nw_edge[0] - avg_lat) * (resulting_ydist / ydist)
        se_lat = avg_lat - (avg_lat - se_edge[0]) * (resulting_ydist / ydist)
        new_map_coords = ((nw_lat, nw_edge[1]), (se_lat, se_edge[1]))
    else:
        s = ydist / image_height # s is distance represented by one pixel
        zoom = -log((s / EC) / cos(avg_lat), 2) - 8
        resulting_xdist = image_width * s
        nw_lon = avg_lon - (avg_lon - nw_edge[1]) * (resulting_xdist / xdist)
        se_lon = avg_lon + (se_edge[1] - avg_lon) * (resulting_xdist / xdist)
        new_map_coords = ((nw_edge[0], nw_lon), (se_edge[0], se_lon))

    return (avg_lat, avg_lon), zoom, new_map_coords

def output_plot(plot_out, rentals, sales, voronoi, background_url, map_corners):
    rental_lats = [d['lat'] for d in rentals]
    rental_lons = [d['lon'] for d in rentals]
    sales_lats = [d['lat'] for d in sales]
    sales_lons = [d['lon'] for d in sales]
    nw_lat = degrees(map_corners[0][0])
    nw_lon = degrees(map_corners[0][1])
    se_lat = degrees(map_corners[1][0])
    se_lon = degrees(map_corners[1][1])

    p = figure(
        x_range=Range1d(nw_lon, se_lon, bounds='auto'),
        y_range=Range1d(se_lat, nw_lat, bounds='auto'),
        tools='pan,wheel_zoom,reset,save'
    )
    p.plot_width = MAP_WIDTH
    p.plot_height = MAP_HEIGHT
    p.sizing_mode = 'scale_width'
    p.xaxis.visible = False
    p.yaxis.visible = False
    p.xgrid.visible = False
    p.ygrid.visible = False
    p.outline_line_color = None
    
    p.image_url(url=[relpath(background_url, dirname(plot_out))], x=nw_lon, y=nw_lat, w=se_lon-nw_lon, h=nw_lat-se_lat)

    center = voronoi.points.mean(axis=0)
    for r in voronoi.ridge_vertices:
        if r[0] >= 0 and r[1] >= 1:
            p1 = voronoi.vertices[r[0]]
            p2 = voronoi.vertices[r[1]]
            p.line([p1[1], p2[1]],[p1[0], p2[0]])
    for pointidx, simplex in zip(voronoi.ridge_points, voronoi.ridge_vertices):
            simplex = np.asarray(simplex)
            if np.any(simplex < 0):
                i = simplex[simplex >= 0][0]
                t = voronoi.points[pointidx[1]] - voronoi.points[pointidx[0]] 
                t = t / np.linalg.norm(t)
                n = np.array([-t[1], t[0]])
                midpoint = voronoi.points[pointidx].mean(axis=0)
                far_point = voronoi.vertices[i] + np.sign(np.dot(midpoint - center, n)) * n * 100
                p.line([voronoi.vertices[i,1], far_point[1]], [voronoi.vertices[i,0], far_point[0]])
            
    p.circle(sales_lons, sales_lats, size=3, fill_color="orange", line_color=None)
    p.circle(rental_lons, rental_lats, size=3, fill_color="blue", line_color=None)
    district_circles_lats = [x[0] for x in voronoi.points]
    district_circles_lons = [x[1] for x in voronoi.points]
    p.circle(district_circles_lons, district_circles_lats, size=10, fill_color="fuchsia", line_color=None)

    output_file(plot_out)
    save(p)

if __name__ == '__main__':        
    rent_data_in, sales_data_in, background_data_out, plot_data_out = sys.argv[1:]
    rentals = read_json_lines(rent_data_in)
    sales = read_json_lines(sales_data_in)
    for r in rentals:
        r['tag'] = 'rental'
    for s in sales:
        s['tag'] = 'sale'
    data = rentals + sales   
    median_coords = (
        sorted([d['lat'] for d in data])[int(len(data)/2)],
        sorted([d['lon'] for d in data])[int(len(data)/2)]
    )
    data_with_distances = [(d, sqrt(pow(d['lat']-median_coords[0], 2) + pow(d['lon']-median_coords[1], 2))) for d in data]
    data_without_outliers = sorted(data_with_distances, key=lambda c: c[1])[:int(0.9*(len(data_with_distances)))]
    lats = [radians(d[0]['lat']) for d in data_without_outliers]
    lons = [radians(d[0]['lon']) for d in data_without_outliers]
    center, zoom, map_corners =  map_coords((max(lats), min(lons)), (min(lats), max(lons)), 600, 4./3)
    data_with_districts = [d[0] for d in data_without_outliers]
    popular_districts = set(get_districts(data_with_districts))
    add_districts(data_with_districts, popular_districts)
    data_by_district = {}
    for d in data_with_districts:
        district = d['district']
        if district not in popular_districts:
            continue
        if district not in data_by_district:
            data_by_district[district] = [d]
        else:
            data_by_district[district].append(d)
    centers_of_districts = {district: (sum([d['lat'] for d in samples])/len(samples), sum([d['lon'] for d in samples])/len(samples)) for district, samples in data_by_district.items()}
    voronoi = Voronoi(np.array(centers_of_districts.values()))

    static = Static()
    response = static.image('mapbox.light',lon=degrees(center[1]), lat=degrees(center[0]), z=zoom, width=MAP_WIDTH, height=MAP_HEIGHT)
    with open(background_data_out, 'wb') as fp:
        fp.write(response.content)    

    sales_without_outliers = filter(lambda d: d['tag'] == 'sale', [x[0] for x in data_without_outliers])
    rentals_without_outliers = filter(lambda d: d['tag'] == 'rental', [x[0] for x in data_without_outliers])
    output_plot(plot_data_out, rentals_without_outliers, sales_without_outliers, voronoi, background_data_out, map_corners)

