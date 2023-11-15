#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Nov 10 14:54:47 2023

@author: hannahmetaireau
"""

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from flask import Flask, render_template
from bokeh.models import LinearAxis
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.resources import INLINE
from bokeh.models import ColumnDataSource, DatetimeTickFormatter
from bokeh.transform import factor_cmap
import bokeh.palettes as bp
from sqlalchemy import create_engine, text as sql_text
from cartopy import crs as ccrs
from shapely.geometry import LineString
import folium


app = Flask(__name__)

@app.route('/map_arctox')
def bokeh():

    
    # Importation des données  
    data = pd.read_excel('Kap Hoegh GLS 20102011_sun3_saison.xlsx')

    # Sélection d'un individu
    data = data[data['ID'] == 148] 

    # Dataframe en Geodataframe
    data = gpd.GeoDataFrame(
        data, geometry=gpd.points_from_xy(data.Long, data.Lat_compensate), crs="EPSG:4326"
    )

    # Sélection de colonnes
    data = data[['ID', 'Period', 'date', 'time', 'geometry']]

    # Tri des données par date et heure
    data.sort_values(by=['date', 'time'], inplace=True)
    
    # Créer une ligne à partir des points triés
    line = LineString(data['geometry'].tolist())
    
    # Créer un GeoDataFrame pour la ligne
    line_gdf = gpd.GeoDataFrame({'geometry': [line]}, crs="EPSG:4326")
    
    # Trouver les limites 
    minx, miny, maxx, maxy = data.geometry.total_bounds
    
    # Calculer une marge pour dézoomer
    margin_x = (maxx - minx) * 0.2  # ajustez la marge selon vos besoins
    margin_y = (maxy - miny) * 0.2
    
    # Créer une carte Folium
    m = folium.Map(location=[(miny + maxy) / 2, (minx + maxx) / 2], zoom_start=12)
    
    # Ajouter les points à la carte sans marqueurs
    for _, row in data.iterrows():
        folium.CircleMarker(location=[row['geometry'].y, row['geometry'].x], radius=1, color='blue').add_to(m)

    # Ajouter la ligne à la carte
    line_coords = [(point[1], point[0]) for point in line_gdf['geometry'].iloc[0].coords]
    folium.PolyLine(line_coords, color='red', weight=1).add_to(m)
    
    # Définir les limites 
    m.fit_bounds([(miny - margin_y, minx - margin_x), (maxy + margin_y, maxx + margin_x)])

    # grab the static resources
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
     
    # render template
    
    map_html = m._repr_html_()
    return render_template('map_arctox.html', map=map_html)


if __name__ == '__main__':
    app.run(debug=True, port=5050)



