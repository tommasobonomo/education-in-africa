import streamlit as st
import altair as alt
import pandas as pd


@st.cache
def get_data(data_path: str = 'data/african_data.csv', indicators_path: str = '') -> pd.DataFrame:
    """Returns dataframe optionally filtered on Indicator Code if indicators_path is given"""
    data = pd.read_csv(data_path)
    if not indicators_path:
        return data
    else:
        indicators = pd.read_csv(indicators_path)
        return data[data['Indicator Code'].isin(indicators['Indicator Code'])].reset_index(drop=True)


@st.cache
def wide2long_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts wide df to long format.
    I.e. single years are trasposed as a column and their value as another.
    Like un-pivoting a table on years.
    """
    identifying_vars = ['Country Code', 'Country Name',
                        'Indicator Code', 'Indicator Name']
    years = [str(x) for x in range(1960, 2020)]
    return df.melt(id_vars=identifying_vars, value_vars=years, var_name='Year')


data = get_data(indicators_path='data/indicators/education.csv')

government_expenditure = wide2long_format(data[data['Indicator Code'] ==
                                               'SE.XPD.TOTL.GD.ZS']).dropna().reset_index(drop=True)

government_expenditure_2010 = government_expenditure[government_expenditure['Year'] == '2010']

st.markdown('# Education in Africa')

source = alt.topo_feature(
    'https://raw.githubusercontent.com/deldersveld/topojson/master/continents/africa.json', "continent_Africa_subunits")

chart = alt.Chart(source).mark_geoshape(fill='white', stroke='black')
chart = chart.encode(color='value:Q')
chart = chart.transform_lookup(
    lookup='geounit',
    from_=alt.LookupData(government_expenditure_2010,
                         key='Country Name', fields=['value'])
)

st.altair_chart(chart)
