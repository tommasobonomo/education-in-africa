import time
import numpy as np
import streamlit as st
import altair as alt
import pandas as pd

from vega_datasets import data
mydf = pd.read_csv('../data/aggregate_data.csv')

mydf.columns = mydf.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
ix = mydf.indicator_code.str.contains("EG.ELC.ACCS.RU.ZS")
mydf = mydf[ix]
#st.write(mydf.head())

mydf = mydf.filter(items=["country_name", "1960","1961","1962","1963","1964","1965","1966","1967","1968","1969","1970","1971","1972","1973","1974","1975","1976","1977","1978","1979","1980","1981","1982","1983","1984","1985","1986","1987","1988","1989","1990","1991","1992","1993","1994","1995","1996","1997","1998","1999","2000","2001","2002","2003","2004","2005","2006","2007","2008","2009","2010","2011","2012","2013","2014","2015","2016","2017","2018","2019"])
#st.write(mydf.head())

# filter data one indicator one tear
# for this country - value plot

mydf = mydf.melt(id_vars=["country_name"],
        var_name="Year",
        value_name="Value")

year_to_filter = st.slider('Year', 1960, 2019, 2004)  # min: 0h, max: 23h, default: 17h
filtered_data = mydf[mydf.Year.str.contains(str(year_to_filter))]

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


















