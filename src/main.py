import time
import numpy as np
import streamlit as st
import altair as alt
import pandas as pd

from vega_datasets import data

source = data.wheat()

st.header("Data exploration")
# st.subheader("by Mark")

chart = alt.Chart(source).mark_bar().encode(
    x='year:O',
    y="wheat:Q",
    # The highlight will be set on the result of a conditional statement
    color=alt.condition(
        alt.datum.year == 1810,  # If the year is 1810 this test returns True,
        alt.value('orange'),     # which sets the bar orange.
        alt.value('steelblue')   # And if it's not true it sets the bar steelblue.
    )
).properties(width=600)

df = pd.DataFrame(
     np.random.randn(200, 3),
     columns=['a', 'b', 'c'])

c = alt.Chart(df).mark_circle().encode(x='a', y='b', size='c', color='c')

st.write(chart)
st.write(c)

mydf = pd.read_csv('../data/aggregate_data.csv')
st.write(mydf.head())