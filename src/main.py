import time
import numpy as np
import streamlit as st
import altair as alt
import pandas as pd
import json
import geopandas as gpd
import matplotlib.pyplot as plt
from vega_datasets import data as usdata
import pydeck as pdk


full_data = pd.read_csv('../data/african_data.csv')

full_data.columns = full_data.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

indicator = str(st.sidebar.selectbox("Economic indicator", ["EG.ELC.ACCS.RU.ZS", "SP.POP.DPND", "MS.MIL.MPRT.KD"]))
mydf = full_data[full_data['indicator_code'] == indicator]
mydf = mydf.filter(items=["country_name", "country_code", "wb-2_code", "1960","1961","1962","1963","1964","1965","1966","1967","1968","1969","1970","1971","1972","1973","1974","1975","1976","1977","1978","1979","1980","1981","1982","1983","1984","1985","1986","1987","1988","1989","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019"])
col_one_list = mydf['wb-2_code'].tolist()

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

#
# fp = "../data/Africa.shp"
# map_df = gpd.read_file(fp)
# # st.write(map_df["CODE"])
# variable = "Value"
#
# merged = map_df.set_index("CODE").join(filtered_data.set_index('country_code'))
# # st.write(merged.keys())
#
# vmin = merged['Value'].min()
# vmax = merged['Value'].max()
#
# fig, ax = plt.subplots(1, figsize=(10, 6))
# merged.plot(column=variable, cmap="Blues", linewidth=0.8, ax=ax, edgecolor="0.8")
# ax.axis("off")
# sm = plt.cm.ScalarMappable(cmap='Blues', norm=plt.Normalize(vmin=vmin, vmax=vmax))
# sm._A = []
# cbar = fig.colorbar(sm)
#
#
# st.pyplot()

african_countries = alt.topo_feature('https://raw.githubusercontent.com/deldersveld/topojson/master/continents/africa.json', 'continent_Africa_subunits')
mychart2 = alt.Chart(african_countries).mark_geoshape().encode(
    color='Value:Q'
).transform_lookup(
    lookup='properties.geounit',
    default='0',
    from_=alt.LookupData(filtered_data, 'country_name', ['Value'])
).properties(
    width=800,
    height=500
)

st.write(mychart2)


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
#
# geodata = filtered_data.filter(items=["lat","lon"])
#
# st.pydeck_chart(pdk.Deck(
#     map_style='mapbox://styles/mapbox/light-v9',
#     initial_view_state=pdk.ViewState(
#         latitude=0,
#         longitude=20,
#         zoom=2,
#         pitch=0,
#     ),
#     layers=[
#         pdk.Layer(
#             'ScatterplotLayer',
#             data=geodata,
#             get_position='[lon, lat]',
#             get_color='[200, 30, 0, 160]',
#             get_radius=200000,
#         ),
#     ],
# ))

st.subheader(f'Some value in year {year_to_filter}')
st.write(bars)


corr1_indicator = str(st.sidebar.selectbox("Corr 1", ["EG.ELC.ACCS.RU.ZS", "SP.POP.DPND", "MS.MIL.MPRT.KD"]))
corr1 = full_data[full_data['indicator_code'] == corr1_indicator]
corr1 = corr1.filter(items=["country_name", "country_code", "wb-2_code", "1960","1961","1962","1963","1964","1965","1966","1967","1968","1969","1970","1971","1972","1973","1974","1975","1976","1977","1978","1979","1980","1981","1982","1983","1984","1985","1986","1987","1988","1989","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019"])

corr2_indicator = str(st.sidebar.selectbox("Corr 2", ["SP.POP.DPND", "EG.ELC.ACCS.RU.ZS", "MS.MIL.MPRT.KD"]))
corr2 = full_data[full_data['indicator_code'] == corr2_indicator]
corr2 = corr2.filter(items=["country_name", "country_code", "wb-2_code", "1960","1961","1962","1963","1964","1965","1966","1967","1968","1969","1970","1971","1972","1973","1974","1975","1976","1977","1978","1979","1980","1981","1982","1983","1984","1985","1986","1987","1988","1989","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019"])

corr1 = corr1.melt(id_vars=["country_name", "country_code", "wb-2_code"],
        var_name="Year",
        value_name="Value")

corr2 = corr2.melt(id_vars=["country_name", "country_code", "wb-2_code"],
        var_name="Year",
        value_name="Value")

year_to_filter2 = st.slider('Year for correlation', 1960, 2019, 2009)  # min: 0h, max: 23h, default: 17h
corr1_filtered_data = corr1[corr1.Year.str.contains(str(year_to_filter2))]
corr2_filtered_data = corr2[corr2.Year.str.contains(str(year_to_filter2))]

df = pd.DataFrame({
    'x':corr1_filtered_data['Value'],
    'y':corr2_filtered_data['Value'],
    'country_code':corr2_filtered_data['country_code'],
    'country_name':corr2_filtered_data['country_name'],
})

ch = alt.Chart(df).mark_circle(size=100).encode(
    x='x',
    y='y',
    # color='Origin',
    tooltip=['country_name', 'country_code']
).interactive()

st.write(ch)














