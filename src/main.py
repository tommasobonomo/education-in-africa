import streamlit as st
import altair as alt
import pandas as pd
import geopandas as gpd


@st.cache
def get_data(
    data_path: str = "data/african_data.csv", indicators_path: str = ""
) -> pd.DataFrame:
    """Returns dataframe optionally filtered on Indicator Code if indicators_path is given"""
    data = pd.read_csv(data_path)
    if not indicators_path:
        return data
    else:
        indicators = pd.read_csv(indicators_path)
        return data[
            data["Indicator Code"].isin(indicators["Indicator Code"])
        ].reset_index(drop=True)


@st.cache
def wide2long_format(df: pd.DataFrame) -> pd.DataFrame:
    """
    Converts wide df to long format.
    I.e. single years are trasposed as a column and their value as another.
    Like un-pivoting a table on years.
    """
    identifying_vars = [
        "Country Code",
        "Country Name",
        "Indicator Code",
        "Indicator Name",
    ]
    years = [str(x) for x in range(1960, 2020)]
    return df.melt(id_vars=identifying_vars, value_vars=years, var_name="Year")


data = get_data(indicators_path="data/indicators/education.csv")

# Only indicators for education with more than 40 data points in 2010:
# ['SE.COM.DURS','SE.PRM.DURS','SE.PRM.AGES','SE.PRE.DURS','SE.SEC.DURS','SE.SEC.AGES']
primary_duration = (
    wide2long_format(data[data["Indicator Code"] == "SE.PRM.DURS"])
    .dropna()
    .reset_index(drop=True)
)

primary_duration_2010 = primary_duration[primary_duration["Year"] == "2010"]

st.markdown("# Education in Africa")

world = gpd.read_file(gpd.datasets.get_path("naturalearth_lowres"))
africa = world[world.continent == "Africa"]
africa_geometry = africa[["iso_a3", "geometry"]]


source = pd.merge(
    primary_duration_2010,
    africa_geometry,
    left_on="Country Code",
    right_on="iso_a3",
    how="left",
)
geo_source = gpd.GeoDataFrame(source, geometry="geometry")
chart = alt.Chart(geo_source).mark_geoshape().encode(color="value:O")
st.altair_chart(chart)
