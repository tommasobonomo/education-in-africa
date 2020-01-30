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
    indicator = "SE.PRM.DURS"
    data = (
        wide2long_format(data[data["Indicator Code"] == indicator])
        .dropna()
        .reset_index(drop=True)
    )

    year_to_filter = st.slider('Year', 1960, 2019, 2004)  # min: 0h, max: 23h, default: 17h
    filtered_data = data[data.Year.str.contains(str(year_to_filter))]

    african_countries = alt.topo_feature(
        'https://raw.githubusercontent.com/deldersveld/topojson/master/continents/africa.json',
        'continent_Africa_subunits')
    africa_chart = alt.Chart(african_countries).mark_geoshape().encode(
        color='value:Q',
        tooltip=[alt.Tooltip('properties.geounit:O', title='Country name'),
                 alt.Tooltip('value:Q', title=indicator)],
    ).transform_lookup(
        lookup='properties.geounit',
        default='0',
        from_=alt.LookupData(filtered_data, 'Country Name', ['value'])
    ).properties(
        width=800,
        height=500
    )

    st.write(africa_chart)


def plot_scatter():
    ed_data = get_data(indicators_path="data/indicators/education.csv")
    ed_data = wide2long_format(ed_data).dropna()
    top_ed_indicators = ed_data["Indicator Name"].value_counts()[:10].index
    ed_data = ed_data[ed_data["Indicator Name"].isin(top_ed_indicators)]
    ed_indicator = st.selectbox(
        label="Education Indicator", options=ed_data["Indicator Name"].unique()
    )
    ed_indicator_data = ed_data[ed_data["Indicator Name"] == ed_indicator]

    women_data = get_data(indicators_path="data/indicators/women.csv")
    women_data = wide2long_format(women_data).dropna()
    top_women_indicators = women_data["Indicator Name"].value_counts()[
        :10].index
    women_data = women_data[women_data["Indicator Name"].isin(
        top_women_indicators)]
    women_indicator = st.selectbox(
        label="Women's rights Indicator", options=women_data["Indicator Name"].unique()
    )
    women_indicator_data = women_data[women_data["Indicator Name"]
                                      == women_indicator]

    year = str(st.slider(label="Year of interest",
                         min_value=1970, max_value=2019))
    # year = st.selectbox(
    #     label="Year of interest", options=ed_indicator_data["Year"].unique()
    # )
    final_ed_data = ed_indicator_data[ed_indicator_data["Year"] == year]
    final_women_data = women_indicator_data[women_indicator_data["Year"] == year]
    columns = ["Country Code", "Country Name", "value"]
    plot_data = pd.merge(
        final_women_data[columns],
        final_ed_data[columns],
        on=["Country Code", "Country Name"],
        suffixes=("_women", "_education"),
    )

    if not plot_data.empty:
        women_is_ordinal = set(final_women_data["value"].unique().tolist()) == {
            0.0,
            1.0,
        }
        type_women = "ordinal" if women_is_ordinal else "quantitative"
        chart = (
            alt.Chart(plot_data)
            .mark_point()
            .encode(
                x=alt.X("value_women", title=women_indicator, type=type_women),
                y=alt.Y("value_education", title=ed_indicator),
                tooltip="Country Name",
            )
            .properties(height=400, width=600)
        )
        st.altair_chart(chart)
    else:
        st.markdown("### No data for that year!")


st.markdown("# Education in Africa")
option = st.selectbox("Plot to render", ["scatter", "map"])

if option == "scatter":
    plot_scatter()
elif option == "map":
    plot_choropleth()
else:
    st.write("### Sorry! Plot not yet implemented")
