# -*- coding: utf-8 -*-
"""
Created on Sun Oct 16 22:51:43 2022

@author: solel
"""

import pandas as pd 
import matplotlib.pyplot as plt

import networkx as nx
import osmnx as ox
import geopandas as gp

"""
import cv2
import os
import glob
"""

gtfs = {}

fname = "gtfsv34/shapes.txt"

archivo = "Detalle_Registros_GPS_20170922.zip"
df = pd.read_csv(f"{archivo}", compression="zip", sep=";", encoding="latin-1")
    
lat = df.groupby("Patente")["Latitud"].apply(list).to_dict()
lon = df.groupby("Patente")["Longitud"].apply(list).to_dict()
# tiempo = df.groupby("Patente")["Tiempogps"].apply(list).to_dict()
# ruta = df.groupby("Patente")["Ruta"].apply(list).to_dict()
# vel = df.groupby("Patente")["Velocidad"].apply(list).to_dict()
# ign = df.groupby("Patente")["Ignición"].apply(list).to_dict()

G = ox.graph_from_bbox(
    north = -33.3829, 
    south = -33.4194, 
    east = -70.4877, 
    west = -70.5360, 
    network_type = "drive", 
    clean_periphery = True)

for e in G.edges: #esto itera los edges

    ni, nj, k = e
    edgeinfo = G.edges[ni, nj, k]

utm = "EPSG:32719"

gdf_nodes, gdf_edges = ox.graph_to_gdfs(G)

gdf_edges = gdf_edges.to_crs(utm)
gdf_nodes = gdf_nodes.to_crs(utm)


from shapely.geometry import Point


deltat = 30

i = 0
for u in lat.keys():
    val_lat = lat[u]  #y
    val_lon = lon[u]  #x
    #val_tiempo = tiempo[u]
     
    dif_dist = []
    
    for w in range(len(val_lat)):
        if w == len(val_lat)-1:
            a = ((val_lat[0] - val_lat[w])**2 + (val_lon[0] - val_lon[w])**2)**0.5
            dif_dist.append(a)
            continue
        
        a = ((val_lat[w+1] - val_lat[w])**2 + (val_lon[w+1] - val_lon[w])**2)**0.5
        dif_dist.append(a)
        
    vel = []
    for i in range(len(dif_dist)):
        if i == 0:
            v = 0
            continue
        v = dif_dist[i]/((i)*30)
        vel.append(v)
    
    target = gp.GeoSeries([Point(val_lon[i], val_lat[i])], 
                          index = range(1), 
                          crs="EPSG:4326", )
    
    target = target.to_crs(utm)
    
    distancias = gdf_edges.distance(target[0]) #encontrar las distancias a un punto
    
    min_dist = distancias.min()      #entrega el minimo
    indice_min = distancias.idxmin() #entrega el indice del minimo
    
    u, v, k = indice_min
    nombre_calle = G.edges[u, v, k]["name"] #se accede al grafo para buscar la calle
    
    
    plt.figure()
    ax = plt.subplot(111)
    
    gdf_nodes.plot(ax = ax)
    target.plot(ax = ax, color = "#FF0000")
     
    plt.show()
    #print(val_lon)
    
    i+=1
    if i > 10:
        break
   
plt.show()
#print(distancias)



"""
CREACIÓN DEL VIDEO

foldername = "imagenes"
video_name = "video.avi"
path = os.path.join(os.path.dirname(os.path.abspath(__file__)), foldername)

def saveAVI():
    img_array = []
    
    for filename in glob.glob(f"{path}/*.png"):
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)
    
    out = cv2.VideoWriter("video.avi", cv2.VideoWriter_fourcc(*"DIVX"), 15, size)
    
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()
        
saveAVI() 

"""