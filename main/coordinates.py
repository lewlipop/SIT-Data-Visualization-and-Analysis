
 ############# imported modules ###############

from geopy.geocoders import Nominatim      
import pandas as pd
import re


############### reading data  from csv file##################### 
data = pd.read_csv(r'scraped_data_food.csv') #!!!!!!!!!!! remember to change the file location if needed!!!!!!!!!!!!!!!!!!!!!!!!!!

address_list= data['Address'].values.tolist()
postal_list=[]






for i in address_list:
        postal_code_pattern = re.compile(r'\b\d{6}\b')
        postal_codes=postal_code_pattern.findall(i)
        postal_list.append(postal_codes)
    


longitude_list=[]
latitude_list=[]
for x in postal_list:
    try:
        geolocator = Nominatim(user_agent = 'coordinates')
        location_query = f"{x}, Singapore"
        location = geolocator.geocode(location_query)
        longitude=location.longitude
        latitude=location.latitude
        longitude_list.append(longitude)
        latitude_list.append(latitude)
        
    except Exception as e:
        latitude= 1.287953
        longitude= 103.851784
        longitude_list.append(longitude)
        latitude_list.append(latitude)





data['latitude']=latitude_list
data['longitude']= longitude_list

data.to_csv('modified_data.csv')
print("done")




