import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans
import folium # map rendering library



res = requests.get("https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M").text
#print(res)
soup = BeautifulSoup(res,"lxml")



df = pd.DataFrame(columns=['Postal Code','Borough','Neighbourhood']) # I know the size



for table in soup.findAll("table", {"class": "wikitable sortable"}):
    row_marker = 0
    #iterate and apply logic to clean the data
    for row in table.find_all('tr'):
        if(len(row)==6):
            columns = row.find_all('td')
            if len(columns)>0:
                nan=0
                if columns[1].text!='Not assigned':
                    if columns[2].text=='Not assigned\n':
                        #df.loc[df['Postal Code'] == columns[0].text] = columns[1].text
                        #print(df.loc[df['Postal Code'] == columns[0].text].values)
                        #columns[2].text=columns[1].text
                        nan=1
                        


                        #print(columns[1].text)
                    
                    for ind,t in df.iterrows():
                        if t['Borough']==columns[1].text:
                            t['Neighbourhood']=t['Neighbourhood']+", "+columns[2].text
                           
                    if columns[0].text in df.values:
                        # do nothing
                        print(' ')
                    else:
                        if nan != 0:
                            #append to the empty dataframe
                            df=df.append({'Postal Code':columns[0].text,'Borough':columns[1].text,'Neighbourhood':columns[1].text},ignore_index=True)
                        else:
                            df=df.append({'Postal Code':columns[0].text,'Borough':columns[1].text,'Neighbourhood':columns[2].text},ignore_index=True)
                            nan=0

#Replace all \n
df=df.replace(to_replace='\n', value='', regex=True)

#print(df)
#df
#df.shape

df_geo=pd.read_csv("Geospatial_Coordinates.csv")
#print (df_geo)
df_new=pd.merge (df,df_geo,on="Postal Code")
#print (df_new)

df_grouped = df_new.groupby('Neighbourhood').mean().reset_index()
print(df_grouped)

# set number of clusters
kclusters = 5

df_clustering = df_grouped.drop('Neighbourhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(df_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10]

df_merged = df_new

# add clustering labels
df_merged['Cluster Labels'] = kmeans.labels_


print(df_merged.head()) # check the last columns!

latitude=43.6542599
longitude=-79.3606359

# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i+x+(i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(df_merged['Latitude'], df_merged['Longitude'], df_merged['Neighbourhood'], df_merged['Cluster Labels']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters
