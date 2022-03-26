import random
import numpy as np
import pandas as pd

from shapely.geometry import Polygon, Point

def random_points_in_polygon(number, polygon):
    """
    This function is used for generating the location of all units of a building

    Args :
        number          : number of units
        polygon         : building polygon object

    Returns :
        Coordinates of the units generated
    """
    points = []
    min_x, min_y, max_x, max_y = polygon.bounds
    i = 0
    while i < number:
        point = Point(random.uniform(min_x, max_x), random.uniform(min_y, max_y))
        if polygon.contains(point):
            points.append(point)
            i += 1
    return points

def cal_coordinates(df):
    """
    Generates shapely polygon from geopandas dataframe

    Args :
        df           :  geopandas dataframe object

    Returns :
        Shapely polygon
    """
    temp = []
    for i in range(len(df['geometry'])):
        temp.append(list(df['geometry'][i].exterior.coords))



    coordinates = []
    for i in range(len(temp)):
        build_cord = []
        for j in range(len(temp[i])):
            #x = (temp[i][j][0] * 100) % 100
            #y = (temp[i][j][1] * 100) % 100
            #xy = [round((x - ref[0]) * 100, 3), round((y - ref[1]) * 100, 3)]
            x = temp[i][j][0]
            y = temp[i][j][1]
            xy = [x,y]
            build_cord.append(xy)
        coordinates.append(build_cord)

    polygons = []
    for pointList in coordinates:
        poly = Polygon([(p[0], p[1]) for p in pointList])
        polygons.append(poly)

    return coordinates,polygons
