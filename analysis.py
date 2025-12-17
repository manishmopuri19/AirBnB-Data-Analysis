import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
#------------>data loading

data=pd.read_csv(r'D:\python\AirBnb\source.csv')

#------------>exploring
print(data.shape)
print(data.columns)
print(data.isnull().sum())
print(data.describe())

#------------>handling missing values

#here we fill missing name's of the hotels or stays will a "no name provided" because it don't change the rent and room type information but may cause the trouble while making or building of a model
data['name']=data['name'].fillna('no name provided')
print(data.isnull().sum())


print(data['last_review'])
#converted the last_review to proper datatime format to avoid the choas --->(year/month/date)
data['last_review']=pd.to_datetime(data['last_review'])
data['last_review']=data['last_review'].fillna(pd.NaT)
print(data['last_review'])

#filling the missing host name with word unkown host to avoid and maintain consistency over the data set
data['host_name']=data['host_name'].fillna('unkown host')
data['host_name']=data['host_name'].str.replace('(Email hidden by Airbnb)','unkown host',regex=False)
print(data.isnull().sum())

#filling missing reviews per month with zero because the if the data is missing probably there are no reviews at all there some another reason but we consider this because it maintain integreity
data['reviews_per_month']=data['reviews_per_month'].fillna(0)
print(data.isnull().sum())




#------------>fun with pandas

#who is the Boss?
host_count=(data.groupby('host_name')['id'].count().reset_index(name='no.of hotels'))
host_count=host_count.sort_values('no.of hotels',ascending=False)
host_count=host_count.reset_index(drop=True)
print(host_count)

#Top ten Leaders
host_count['ranking']=host_count['no.of hotels'].rank(method='first',ascending=False).astype(int)
host_count=host_count.reset_index(drop=True)
print(host_count.head(10))



#grouping by NeighboorHood_group
print()
print("Grouping by individual neighbourhood_groups")
Area_count=(data.groupby('neighbourhood_group')['id'].count().reset_index(name='no.of hotels in an area'))
Area_count=Area_count.sort_values('no.of hotels in an area',ascending=False)
Area_count=Area_count.reset_index(drop=True)
print(Area_count)


#grouping based on neighbourhood
print()
print("Grouping by individual neighbourhood")
neigh_grouping=(data.groupby('neighbourhood')['id'].count().reset_index(name='no.of listed hotel in a neighbourhood'))
neigh_grouping=neigh_grouping.sort_values('no.of listed hotel in a neighbourhood',ascending=False)
neigh_grouping=neigh_grouping.reset_index(drop=True)
print(neigh_grouping)


#grouping along with there princings
print()
print("Grouping with the price comparions")
price_in_neighbourhood_group=(data.groupby('neighbourhood_group').agg(average_price=('price','mean'),count=('id','count')).reset_index())

price_in_neighbourhood_group=price_in_neighbourhood_group.sort_values('average_price',ascending=False)
print(price_in_neighbourhood_group)


#grouping the data based on room type and prices
print()
print("Grouping the data based on room type and pricesgrouping the data based on room type and prices")
price_based_on_room_type=(data.groupby('room_type').agg(average_prices_for_room=('price','mean')).reset_index())
price_based_on_room_type=price_based_on_room_type.sort_values('average_prices_for_room',ascending=False)
print(price_based_on_room_type)


#Complete grouping
print()
print("grouping based on each neibhourhood and there roomtypes available and there count and averages prices")
room_price_stats=(data.groupby(['neighbourhood_group','room_type']).agg(average_priceing=('price','mean'),available_stays=('id','count')).reset_index())
room_price_stats=room_price_stats.sort_values(['average_priceing','available_stays']).reset_index(drop=True)
print(room_price_stats)


print()
print()
#pivot
pivot_1=data.pivot_table(index=['neighbourhood_group','room_type'],
                      values=['price','id'],
                      aggfunc={'price':'mean','id':'count'})
pivot_1.columns=['count','average_prices_in_listing']
pivot_1=pivot_1.round(2)

print(pivot_1)

#who is charging more in an average 
print()
print("top 10 villans in this game")
villans=data.groupby('host_name')['price'].mean().sort_values(ascending=False).reset_index(name='average_prices_charged').head(10)
print()


#----------->Play with plots
#average prices by neighbourhood_group
avg_price=data.groupby('neighbourhood_group')['price'].mean().reset_index()

plt.figure(figsize=(8,5))
sns.barplot(data=avg_price,x='neighbourhood_group',y='price')
plt.title("Average prices by  Neighbourhood Group")
plt.xticks(rotation=45)
plt.show()



# center the map around NYC
m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

# prepare heatmap data: list of [lat, lon]
heat_data = data[['latitude', 'longitude']].dropna().values.tolist()

HeatMap(heat_data).add_to(m)

m.save("airbnb_density_heatmap.html")
m
weighted_data = data[['latitude', 'longitude', 'price']]
weighted_data = weighted_data.dropna()

HeatMap(
    weighted_data.values.tolist(),
    radius=12,
    max_zoom=13
).add_to(m)

for hood in data['neighbourhood_group'].unique():
    sub = data[data['neighbourhood_group'] == hood]

    m = folium.Map(location=[40.7128, -74.0060], zoom_start=12)
    HeatMap(sub[['latitude','longitude']].dropna().values.tolist()).add_to(m)

    m.save(f"heatmap_{hood}.html")
m = folium.Map(location=[40.7128, -74.0060], zoom_start=11)

color_map = {
    "Entire home/apt": "red",
    "Private room": "blue",
    "Shared room": "green"
}

for _, row in data.iterrows():
    folium.CircleMarker(
        location=[row['latitude'], row['longitude']],
        radius=3,
        color=color_map.get(row['room_type'], "gray"),
        fill=True,
        fill_opacity=0.6
    ).add_to(m)

m.save("roomtype_map.html")
m
neigh = "https://data.cityofnewyork.us/resource/geos-c5n4.geojson"

folium.GeoJson(neigh, name="neighbourhoods").add_to(m)
m.save("my_map.html")