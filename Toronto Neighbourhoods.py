import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin



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
                           
                    if columns[0].text not in df.values:
                        
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
print(df.shape)
