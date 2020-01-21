import streamlit as st
import altair as alt
import pandas as pd
from vega_datasets import data

st.markdown('# Education in Africa')

source = alt.topo_feature(
    'https://raw.githubusercontent.com/deldersveld/topojson/master/continents/africa.json', "continent_Africa_subunits")

chart = alt.Chart(source).mark_geoshape(fill='white', stroke='black')

st.altair_chart(chart)
