import time
import numpy as np
import streamlit as st
import altair as alt
import pandas as pd
import json
import geopandas as gpd
import matplotlib.pyplot as plt
import pydeck as pdk


from vega_datasets import data
mydf = pd.read_csv('../data/african_data.csv')

mydf.columns = mydf.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

indicator = str(st.sidebar.selectbox("Economic indicator", ["EG.ELC.ACCS.RU.ZS", "SP.POP.DPND", "MS.MIL.MPRT.KD"]))
ix = mydf.indicator_code.str.contains(indicator)
mydf = mydf[ix]
#st.write(mydf.head())

mydf = mydf.filter(items=["country_name", "country_code", "wb-2_code", "1960","1961","1962","1963","1964","1965","1966","1967","1968","1969","1970","1971","1972","1973","1974","1975","1976","1977","1978","1979","1980","1981","1982","1983","1984","1985","1986","1987","1988","1989","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019"])
#st.write(mydf.head())

col_one_list = mydf['wb-2_code'].tolist()
#st.write(mydf.shape)
#st.write(len(col_one_list))

lats = []
longs = []

with open ("country_to_latlong.json", "r") as myfile:
    data = json.load(myfile)
    for item in col_one_list:
        lats.append(data[str(item).lower()][0])
        longs.append(data[str(item).lower()][1])

mydf['lat'] = list([float(i) for i in lats])
mydf['lon'] = list([float(i) for i in longs])


# filter data one indicator one tear
# for this country - value plot

mydf = mydf.melt(id_vars=["country_name", "country_code", "wb-2_code", "lat", "lon"],
        var_name="Year",
        value_name="Value")



#st.write(mydf.head())

year_to_filter = st.slider('Year', 1960, 2019, 2004)  # min: 0h, max: 23h, default: 17h
filtered_data = mydf[mydf.Year.str.contains(str(year_to_filter))]

#st.write(filtered_data.head())
#st.map(filtered_data)


fp = "../data/Africa.shp"
map_df = gpd.read_file(fp)
# st.write(map_df["CODE"])
variable = "Value"

merged = map_df.set_index("CODE").join(filtered_data.set_index('country_code'))
# st.write(merged.keys())

vmin = merged['Value'].min()
vmax = merged['Value'].max()

fig, ax = plt.subplots(1, figsize=(10, 6))
merged.plot(column=variable, cmap="Blues", linewidth=0.8, ax=ax, edgecolor="0.8")
ax.axis("off")
sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=vmin, vmax=vmax))
sm._A = []
cbar = fig.colorbar(sm)


st.pyplot()


#st.write(filtered_data.head())
bars = alt.Chart(filtered_data).mark_bar().encode(
    x="Value:Q",
    y='country_name:O'

)

text = bars.mark_text(
    align='left',
    baseline='middle',
    dx=3  # Nudges text to right so it doesn't appear on top of the bar
).encode(
    text='wheat:Q'
)

(bars + text).properties(height=900)

geodata = filtered_data.filter(items=["lat","lon"])

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=0,
        longitude=20,
        zoom=2,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=geodata,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200000,
        ),
    ],
))

st.subheader(f'Some value in year {year_to_filter}')
st.write(bars)

st.title('Uber pickups in NYC')

DATE_COLUMN = 'date/time'
DATA_URL = ('https://s3-us-west-2.amazonaws.com/'
         'streamlit-demo-data/uber-raw-data-sep14.csv.gz')

@st.cache
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows=nrows)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis='columns', inplace=True)
    data[DATE_COLUMN] = pd.to_datetime(data[DATE_COLUMN])
    return data

# Create a text element and let the reader know the data is loading.
data_load_state = st.text('Loading data...')
# Load 10,000 rows of data into the dataframe.
data = load_data(10000)
# Notify the reader that the data was successfully loaded.
data_load_state.text('Loading data...done!')

if st.checkbox('Show raw data'):
    st.subheader('Raw data')
    st.write(data)

st.subheader('Number of pickups by hour')
hist_values = np.histogram(
    data[DATE_COLUMN].dt.hour, bins=24, range=(0,24))[0]
st.bar_chart(hist_values)

hour_to_filter = st.slider('hour', 0, 23, 17)  # min: 0h, max: 23h, default: 17h
filtered_data = data[data[DATE_COLUMN].dt.hour == hour_to_filter]
st.subheader(f'Map of all pickups at {hour_to_filter}:00')
st.map(filtered_data)

# df = pd.DataFrame(
#     np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
#     columns=['lat', 'lon'])
# st.map(df)

















