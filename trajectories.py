import geopandas as gpd
import pandas as pd
import numpy as np
from shapely.geometry import Point, LineString
import folium
import joblib

def path_to_points(data_points, filename='./mapping/mapper_points.jb'):
    
    P = []
    mapper_points_dict = joblib.load(filename)

    for k in range(len(data_point)):
        for key, value in zip(mapper_points_dict.keys(), mapper_points_dict.values()):
            if data_point[k] == key:
                P.append(value)
    traj = gpd.GeoDataFrame(columns=['ID', 'LON', 'LAT'])
    traj.loc[:,'ID'] = data_point[:]

    for k in range(len(P)):
        traj.loc[k,'LON'] = P[:][k][0]
        traj.loc[k,'LAT'] = P[:][k][1]

    traj = gpd.GeoDataFrame(traj, geometry=[Point(x, y) for x, y in zip(traj.LON, traj.LAT)])

    return traj

def gen_traj(data_point):
    
    traj = path_to_points(data_point)
    
    geom0 = traj.loc[0]['geometry']
    geom1 = traj.loc[1]['geometry']

    # Create LineString from coordinates
    start, end = [(geom0.x, geom0.y), (geom1.x, geom1.y)]
    line = LineString([start, end])
    print(f"Geometry type: {str(type(line))}")
    line

    def make_lines(gdf, df_out, i, geometry = 'geometry'):

        geom0 = gdf.loc[i][geometry]
        geom1 = gdf.loc[i + 1][geometry]

        start, end = [(geom0.x, geom0.y), (geom1.x, geom1.y)]
        line = LineString([start, end])

        # Create a DataFrame to hold record
        data = {'id': i,
                'geometry': [line]}
        df_line = pd.DataFrame(data, columns = ['id', 'geometry'])

        # Add record DataFrame of compiled records
        df_out = pd.concat([df_out, df_line])
        return df_out

    def add_markers(mapobj, gdf):

        coords = []
        for i, row in gdf.iterrows():
            coords.append([row.geometry.y, row.geometry.x])
        for coord in coords:
            folium.CircleMarker(location = coord,
                                radius = 2.5, 
                                fill = True,
                                fill_color = '#F50057',
                                fill_opacity = 0.75,
                                color = 'whitesmoke',
                                weight = 0.5).add_to(mapobj)
        return mapobj

    # initialize an output DataFrame
    df = pd.DataFrame(columns = ['id', 'geometry'])

    # Loop through each row of the input point GeoDataFrame
    x = 0
    while x < len(traj) - 1:
        df = make_lines(traj, df, x)
        x = x + 1

    crs = {'init': 'epsg:4326'}
    gdf_line = gpd.GeoDataFrame(df, crs=crs)

    return folium.GeoJson(gdf_line)