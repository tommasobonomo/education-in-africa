import altair as alt
import pandas as pd
import streamlit as st


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
        "Geo Name",
    ]
    years = [str(x) for x in range(1960, 2020)]
    return df.melt(id_vars=identifying_vars, value_vars=years, var_name="Year")


def plot_choropleth() -> None:
    category = st.sidebar.selectbox(
        "Data to visualize", ["Education", "Economy", "Women's rights"]
    )
    st.markdown("# " + category + " in Africa")
    if category == "Education":
        data = get_data(indicators_path="data/indicators/education.csv")
        handpicked_indicators = pd.read_csv("data/indicators/education_handpicked.csv")
    elif category == "Women's rights":
        data = get_data(indicators_path="data/indicators/women.csv")
        handpicked_indicators = pd.read_csv("data/indicators/wr_handpicked.csv")
    else:
        # category == "Economy":
        data = get_data(indicators_path="data/indicators/economics.csv")
        handpicked_indicators = pd.read_csv("data/indicators/eco_handpicked.csv")

    metadata = pd.read_csv("data/indicators/indicator_metadata.csv")

    # Only indicators for education with more than 40 data points in 2010:
    # ['SE.COM.DURS','SE.PRM.DURS','SE.PRM.AGES','SE.PRE.DURS','SE.SEC.DURS','SE.SEC.AGES']
    top_indicators = handpicked_indicators["Indicator Name"]
    data = data[data["Indicator Name"].isin(top_indicators)]
    if category == "Education":
        defaulttindex=16
    elif category == "Women's rights":
        defaulttindex=0
    elif category == "Economy":
        defaulttindex=9
    else:
        defaulttindex=0

    ed_indicator = st.selectbox(
        label=category + " Indicator", options=data["Indicator Name"].unique(), index=defaulttindex
    )

    indicator_metadata = metadata[metadata["Indicator Name"] == ed_indicator]
    info = st.checkbox("info", value=True)
    if info:
        # st.write(ed_indicator)
        # st.markdown("***Short definition: *** *" + indicator_metadata['Short definition'].values[0] + "*")
        st.markdown(
            f"***Definition: *** *{indicator_metadata['Long definition'].values[0]}*"
        )

    olddata = data[data["Indicator Name"] == ed_indicator]
    data = (
        wide2long_format(data[data["Indicator Name"] == ed_indicator])
        .dropna()
        .reset_index(drop=True)
    )

    year_to_filter = st.slider("Year", 1960, 2019, 2010)
    filtered_data = data[data.Year.str.contains(str(year_to_filter))]

    if filtered_data.empty:
        st.markdown("### No data available for that year!")
        return

    color_scheme = st.sidebar.selectbox(
        "Color scheme",
        ["yellowgreenblue", "greens", "yellowgreen", "redpurple", "goldgreen"],
        index=1,
    )

    african_countries = alt.topo_feature(
        "https://raw.githubusercontent.com/deldersveld/topojson/master/continents/africa.json",
        "continent_Africa_subunits",
    )

    map_selection = alt.selection_multi(fields=["properties.geounit"], empty='none')

    bar_chart = (
        alt.Chart(african_countries)
        .mark_bar()
        .encode(
            x=alt.X("Country Code:O", sort="-y"),
            y=alt.Y("value:Q", title=ed_indicator),
            color=alt.condition(
                map_selection, 
                alt.value("red"), 
                alt.Color("value:Q", scale=alt.Scale(scheme=color_scheme), legend=None)),
            tooltip=[
                alt.Tooltip("Country Code:O"),
                alt.Tooltip("properties.geounit:O", title="Country Name"),
                alt.Tooltip("value:Q", title=ed_indicator),
            ],
        )
        .transform_lookup(
            lookup="properties.geounit",
            from_=alt.LookupData(
                filtered_data, key="Geo Name", fields=["value", "Country Code"]
            ),
        )
        .transform_filter(alt.datum["Country Code"] != None)
        .add_selection(map_selection)
    )

    color = alt.condition(
        map_selection,
        alt.value("red"),
        alt.Color(
            "value:Q",
            scale=alt.Scale(scheme=color_scheme),
            legend=alt.Legend(title="Indicator value"),
        )
    )

    african_outline = (
        alt.Chart(african_countries)
        .mark_geoshape(stroke="white", strokeWidth=2)
        .encode(
            color=alt.condition(map_selection, alt.value("red"), alt.value("lightgrey")),
            tooltip=[
                alt.Tooltip("properties.geounit:O", title="Country name"),
                alt.Tooltip("value:Q", title="Indicator value"),
            ],
        )
        .transform_lookup(
            lookup="properties.geounit",
            from_=alt.LookupData(filtered_data, "Geo Name", ["value"]),
        )
        .properties(width=600, height=500)
    )

    africa_chart = (
        alt.Chart(african_countries)
        .mark_geoshape(stroke="white", strokeWidth=2)
        .encode(
            color=color,
            tooltip=[
                alt.Tooltip("properties.geounit:O", title="Country name"),
                alt.Tooltip("value:Q", title="Indicator value"),
            ],
        )
        .transform_lookup(
            lookup="properties.geounit",
            from_=alt.LookupData(filtered_data, "Geo Name", ["value"]),
        )
        .properties(width=600, height=500)
        .add_selection(map_selection)
    )

    africa = african_outline + africa_chart

    columns = [
        str(year)
        for year in range(1960,2020)
    ]

    pan_selection = alt.selection_interval(bind="scales", encodings=["x"])
    trends = (
        alt.Chart(african_countries)
        .transform_lookup(
            lookup="properties.geounit",
            from_=alt.LookupData(olddata, "Geo Name", columns),
        )
        .transform_fold(columns, as_=["Year", "value"])
        .mark_line(point=True)
        .encode(
            x=alt.X("year(Year):T", title="Year", scale=alt.Scale(domain=(1960,2019))),
            y=alt.Y("value:Q", title="Indicator value"), # impute=alt.ImputeParams(method="mean", keyvals=columns)),
            color=alt.Color(
                "properties.geounit:N", legend=alt.Legend(title="Selected Country")
            ),
            tooltip=[
                alt.Tooltip("properties.geounit:O", title="Country name"),
                alt.Tooltip("year(Year):T", title="Year"),
                alt.Tooltip("value:Q", title="Indicator value"),
            ],
        )
        .properties(width=600, height=500)
        .transform_filter(map_selection)
        .add_selection(pan_selection)
    )
    st.write(bar_chart & africa & trends)


def plot_scatter():
    st.markdown("# Education in Africa")
    ed_data = get_data(indicators_path="data/indicators/education.csv")
    metadata = pd.read_csv("data/indicators/indicator_metadata.csv")
    education_handpicked = pd.read_csv("data/indicators/education_handpicked.csv")
    wr_handpicked = pd.read_csv("data/indicators/wr_handpicked.csv")
    eco_handpicked = pd.read_csv("data/indicators/eco_handpicked.csv")
    ed_data = wide2long_format(ed_data).dropna()
    top_ed_indicators = education_handpicked["Indicator Name"]
    ed_data = ed_data[ed_data["Indicator Name"].isin(top_ed_indicators)]
    ed_indicator = st.selectbox(
        label="Education Indicator", options=ed_data["Indicator Name"].unique(), index=1
    )
    ed_indicator_data = ed_data[ed_data["Indicator Name"] == ed_indicator]
    ed_metadata = metadata[metadata["Indicator Name"] == ed_indicator]
    info_edu = st.checkbox("info", value=False, key="edu")
    if info_edu:
        st.markdown(f"***Definition: *** *{ed_metadata['Long definition'].values[0]}*")


    eco_data = get_data(indicators_path="data/indicators/economics.csv")
    eco_data = wide2long_format(eco_data).dropna()
    top_eco_indicators = eco_handpicked["Indicator Name"]
    eco_data = eco_data[eco_data["Indicator Name"].isin(top_eco_indicators)]
    eco_indicator = st.selectbox(
        label="Economic Indicator", options=eco_data["Indicator Name"].unique(), index=20
    )
    eco_indicator_data = eco_data[eco_data["Indicator Name"] == eco_indicator]
    eco_metadata = metadata[metadata["Indicator Name"] == eco_indicator]
    info_eco = st.checkbox("info", value=False, key="eco")
    if info_eco:
        st.markdown(f"***Definition: *** *{eco_metadata['Long definition'].values[0]}*")

    women_data = get_data(indicators_path="data/indicators/women.csv")
    women_data = wide2long_format(women_data).dropna()
    top_women_indicators = wr_handpicked["Indicator Name"]
    women_data = women_data[women_data["Indicator Name"].isin(top_women_indicators)]
    women_indicator = st.selectbox(
        label="Women's rights Indicator", options=women_data["Indicator Name"].unique()
    )
    women_indicator_data = women_data[women_data["Indicator Name"] == women_indicator]
    women_metadata = metadata[metadata["Indicator Name"] == women_indicator]
    info_women = st.checkbox("info", value=False, key="women")
    if info_women:
        st.markdown(
            f"***Definition: *** *{women_metadata['Long definition'].values[0]}*"
        )


    year = str(st.slider("Year of interest", 1970, 2019, 2010))
    # year = st.selectbox(
    #     label="Year of interest", options=ed_indicator_data["Year"].unique()
    # )
    final_ed_data = ed_indicator_data[ed_indicator_data["Year"] == year]
    final_women_data = women_indicator_data[women_indicator_data["Year"] == year]
    final_eco_data = eco_indicator_data[eco_indicator_data["Year"] == year]

    columns = ["Country Code", "Country Name", "value"]
    plot_data = pd.merge(
        final_women_data[columns],
        final_ed_data[columns],
        on=["Country Code", "Country Name"],
        suffixes=("_women", "_education"),
    )

    columns = ["Country Code", "Country Name", "value"]

    plot_data = pd.merge(
        plot_data, final_eco_data[columns], on=["Country Code", "Country Name"],
    )
    plot_data.rename(columns={"value": "value_eco"}, inplace=True)

    if not plot_data.empty:
        women_is_ordinal = set(final_women_data["value"].unique().tolist()) == {
            0.0,
            1.0,
        }
        type_women = "ordinal" if women_is_ordinal else "quantitative"

        brush = alt.selection_interval()  # selection of type "interval"
        color = alt.condition(brush, alt.value("teal"), alt.value("lightgray"))
        chart_base = (
            alt.Chart(plot_data).mark_point(size=80)
                .properties(height=500, width=680)
        )
        chart = chart_base.encode(
            x=alt.X("value_women", title=women_indicator, type=type_women),
            y=alt.Y("value_education", title=ed_indicator),
            tooltip="Country Name",
            color=color,
        )
        chart2 = chart_base.encode(
            x=alt.X("value_eco", title=eco_indicator, type=type_women),
            y=alt.Y("value_education", title=ed_indicator),
            tooltip="Country Name",
            color=color,
        )

        polynomial_fit = (
            chart.transform_regression(
                "value_women", "value_education", method="poly", order=1
            )
            .mark_line()
            .encode(color=alt.value("darkorange"))
        )
        polynomial_fit2 = (
            chart2.transform_regression(
                "value_eco", "value_education", method="poly", order=1
            )
            .mark_line()
            .encode(color=alt.value("darkorange"))
        )

        b = st.checkbox(label="Show correlation line", value=True, key=None)
        if b:
            st.altair_chart(
                alt.vconcat(chart.add_selection(brush) + polynomial_fit)
                | alt.vconcat(chart2.add_selection(brush) + polynomial_fit2),
                use_container_width=True
            )
        else:
            st.altair_chart(
                alt.vconcat(chart.add_selection(brush))
                | alt.vconcat(chart2.add_selection(brush)),
                use_container_width=True
            )
    else:
        st.markdown("### No data for that year!")


option = st.sidebar.selectbox("Plot to render", ["Analysis of an Indicator", "Interaction of Indicators"])

if option == "Interaction of Indicators":
    plot_scatter()
elif option == "Analysis of an Indicator":
    plot_choropleth()
else:
    st.write("### Sorry! Plot not yet implemented")
