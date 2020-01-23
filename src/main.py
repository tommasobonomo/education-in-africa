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


def plot_choropleth() -> None:
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


def plot_scatter():
    ed_data = get_data(indicators_path="data/indicators/education.csv")
    ed_data = wide2long_format(ed_data).dropna()

    top_ed_indicators = ed_data["Indicator Code"].value_counts()[:10].index
    ed_data = ed_data[ed_data["Indicator Code"].isin(top_ed_indicators)]

    ed_indicator = st.selectbox(
        label="Education Indicator", options=ed_data["Indicator Code"].unique()
    )
    indicator_data = ed_data[ed_data["Indicator Code"] == ed_indicator]
    year = str(st.slider(label="Year of interest", min_value=1970, max_value=2019))
    # year = st.selectbox(
    #     label="Year of interest", options=indicator_data["Year"].unique()
    # )
    final_ed_data = indicator_data[indicator_data["Year"] == year]
    st.write(final_ed_data)


option = st.selectbox("Plot to render", ["scatter", "map"])

if option == "scatter":
    plot_scatter()
elif option == "map":
    plot_choropleth()
else:
    st.write("### Sorry! Plot not yet implemented")
