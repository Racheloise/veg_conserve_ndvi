#!/usr/bin/env python
# coding: utf-8

# ### MODIS MOD13A2 Image Collection
# 
# **Dataset:** MODIS/006/MOD13A2 (Version 6, Collection 6.1)
# 
# **Instrument:** Moderate Resolution Imaging Spectroradiometer (MODIS) on NASA Terra and Aqua satellites
# 
# **Temporal resolution:** 16-day composite (one image every 16 days)
# 
# **Spatial resolution:** 1 km (1000 m pixel size)
# 
# **Bands:** NDVI (Normalized Difference Vegetation Index), EVI (Enhanced Vegetation Index), quality flags
# 
# **Coverage:** Global, including Northern California (1 km pixel size provides regional detail while maintaining long-term historical record)
# 
# **Data availability:** 2000 to present (latest data approximately 1-2 months behind real-time due to processing lag)
# 
# **Use case:** Suitable for 10+ year vegetation trends and climate-scale changes where 1 km resolution is adequate. Monthly compositing reduces cloud contamination and atmospheric noise compared to daily observations.

# #### Import libraries

# In[1]:


import folium
import pandas as pd
import json
import os
import geopandas as gpd


# #### Read in MODIS NDVI aggregation csv from GEE

# In[2]:


os.chdir(r"G:\My Drive\Coursera\Visualisation, web mapping and cloud GIS")
df= pd.read_csv(r".\ndvi_anomaly_2022.csv")

print(df.head())


# #### Correct csv file loaded in correctly confirmation:
# Median values of baseline, current and anomly NDVI for each of the 4 areas aggregated from MODIS collection are visible

# #### Inspect json files

# In[3]:


# Check all field match correctly
geo_hq=json.load(open("hq_points.json"))
print(geo_hq["features"][0]["properties"])

geo_con=json.load(open("conservation_areas.json"))
print(geo_con["features"][0]["properties"])

# Load with geopandas
geo_con = gpd.read_file('conservation_areas.json')
geo_hq = gpd.read_file('hq_points.json')


# #### Field matching confirmation:
# 
# **Properties match between files:**
# Both hq_points.json and conservation_areas.json contain identical property fields: area_id and area_name.
# 
# **First feature verified:**
# Both files show area_id = 1 with area_name = 'North Preserve' for the first feature, confirming alignment.
# 
# **Four areas consistent across both files:**
# HQ points and conservation area boundaries share the same four area identifiers and names, enabling spatial joins and cross-referencing.
# 

# #### Join df to conservation_area by area_id

# In[4]:


# unclipped conservation area
merged=geo_con.merge(df, on="area_id", how="left")
print(merged)


# #### Merge confirmation:
# 
# The four conservation areas have been successfully merged with df.
# area_name, baseline ndvi, current ndvi and anomaly ndvi variables are available for web mapping

# #### Create a folium map centred on study area (around 37.9°N, 122.5°W)

# In[5]:


map = folium.Map(location = [37.9254, -122.425], zoom_start=10,    tiles='OpenStreetMap')


# In[6]:


# Set up manual legend and colour schemes

# Use continuous diverging colour map
from branca.colormap import LinearColormap

# Find max absolute value to center the scale at zero
max_abs = max(abs(merged['anomaly'].min()), 
              abs(merged['anomaly'].max()))

# This is an added step otherwise you cannot distinguish the negatives clearly
# Create diverging colormap centered at zero: red (negative) → yellow (zero) → green (positive)

# Colours for anomaly
colormap_anomaly = LinearColormap(
    colors=['darkred', 'orange', 'lightyellow', 'lightgreen', 'darkgreen'],
    vmin=-max_abs,
    vmax=max_abs,
    caption='NDVI Anomaly (2022-2012)'
)

colormap_anomaly.width = 50  # Make legend wider
colormap_anomaly.height = 350  # Make legend taller

# Colours for current year NDVI
colormap_current = LinearColormap(
    colors=['brown', 'yellow', 'green'],
    vmin=merged['current_ndvi'].min(),
    vmax=merged['current_ndvi'].max(),
    caption='Current NDVI (2022)'
)
# Colours for baseline year NDVI
colormap_baseline = LinearColormap(
    colors=['brown', 'yellow', 'green'],
    vmin=merged['baseline_ndvi'].min(),
    vmax=merged['baseline_ndvi'].max(),
    caption='Baseline NDVI (2012)'
)
legend_html = f"""
<div style="
    position: fixed;
    bottom: 40px; left: 40px;
    z-index: 9999;
    background-color: white;
    padding: 12px;
    border: 1px solid grey;
    border-radius: 5px;
    font-size: 12px;
    font-family: Arial, sans-serif;
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
">
    <b>NDVI Anomaly</b><br>
    <b>(2022 vs 2012)</b><br>
    <hr style="margin: 5px 0;">
    
    <!-- Gradient bar and labels aligned -->
    <div style="display: flex; gap: 8px; align-items: center;">
        <!-- Gradient bar -->
        <div style="
            height: 200px;
            width: 30px;
            background: linear-gradient(to top, darkred, orange, lightyellow, lightgreen, darkgreen);
            border: 1px solid black;
        "></div>
        
        <!-- Scale labels aligned with gradient -->
        <div style="font-size: 11px; height: 200px; display: flex; flex-direction: column; justify-content: space-between;">
            <div>{max_abs:.4f}</div>
            <div>0.0000</div>
            <div>{-max_abs:.4f}</div>
        </div>
    </div>
</div>
"""


# ### Create main NDVI anomaly map and add layers

# In[7]:


# Load HQ points
geo_hq = gpd.read_file('hq_points.json')
# Merge HQ with df to get colors
hq_merged = geo_hq.merge(merged, on='area_id')
hq_merged = gpd.GeoDataFrame(hq_merged, geometry='geometry_x')

# Create Feature Groups
hq_layer = folium.FeatureGroup(name='Headquarters', show=True)
anomaly_layer = folium.FeatureGroup(name='Anomaly', show=True)

# Convert merged to GeoJSON with properties
geojson_with_props = {
    "type": "FeatureCollection",
    "features": []
}

for idx, row in merged.iterrows():
    feature = {
        "type": "Feature",
        "geometry": row['geometry'].__geo_interface__,
        "properties": {
            "Area": row['area_name_x'],
            "Baseline": f"{row['baseline_ndvi']:.4f}",
            "Current": f"{row['current_ndvi']:.4f}",
            "Anomaly": f"{row['anomaly']:.4f}"
        }
    }
    geojson_with_props["features"].append(feature)

# Add to map with tooltip
folium.GeoJson(
    data=geojson_with_props,
    style_function=lambda x: {
        'fillColor': colormap_anomaly(float(x['properties']['Anomaly'])),
        'color': 'black',
        'weight': 1,
        'fillOpacity': 0.7
    },
    tooltip=folium.features.GeoJsonTooltip(fields=['Area', 'Baseline', 'Current', 'Anomaly'])
).add_to(anomaly_layer)

# Add HQ markers
for idx, row in hq_merged.iterrows():
    geom = row['geometry_x']
    lat, lon = geom.y, geom.x
    
    folium.Marker(
        location=[lat, lon],
        popup=f"HQ: {row['area_name_x']}",
        icon=folium.Icon(color='black', icon='info-sign'),
        tooltip=row['area_name_x']
    ).add_to(hq_layer)

# Add to map
hq_layer.add_to(map)
anomaly_layer.add_to(map)

# Add layer control and legend
folium.LayerControl(position='topright', collapsed=False).add_to(map)
map.get_root().html.add_child(folium.Element(legend_html))

map


# #### Add cartographic elements

# In[8]:


# Map title
title_html = """
<div style="
    position: fixed;
    top: 10px; left: 50px;
    z-index: 9999;
    background-color: white;
    padding: 10px;
    border: 2px solid grey;
    border-radius: 5px;
    font-family: Arial, sans-serif;
    box-shadow: 0 0 10px rgba(0,0,0,0.2);
">
    <h3 style="margin: 0;">Northern California Conservation Areas</h3>
    <p style="margin: 5px 0; font-size: 12px;">NDVI Anomaly Analysis (2022 vs 2012)</p>
</div>
"""

# Attribution box
attribution_html = """
<div style="
    position: fixed;
    bottom: 10px; right: 10px;
    z-index: 9999;
    background-color: white;
    padding: 10px;
    border: 1px solid grey;
    border-radius: 5px;
    font-family: Arial, sans-serif;
    font-size: 9px;
    line-height: 1.4;
">
    <b>Data Sources:</b><br>
    NDVI: MODIS MOD13A2 v6 (2022 current, 2012 baseline)<br>
    Boundaries: Conservation area GeoJSON<br>
    <br>
    <b>Methods:</b><br>
    Water-masked analysis via JRC Global Surface Water<br>
    NDVI anomaly = Current NDVI - Baseline NDVI
</div>
"""

# Add to map
map.get_root().html.add_child(folium.Element(title_html))
map.get_root().html.add_child(folium.Element(attribution_html))
map.get_root().html.add_child(folium.Element(legend_html))

#folium.LayerControl(position='topright', collapsed=False).add_to(map)

map


# In[9]:


map.save('vegetation_dashboard.html')

