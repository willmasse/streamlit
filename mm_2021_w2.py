import streamlit as st
import pandas as pd
import pydeck as pdk
import country_converter as coco
import altair as alt
import geojson
import time


st.title("Closing the gap in Adolescent African HIV Infections")

container = st.beta_container()

top1, top2 = container.beta_columns((1,3))

top1.image("M2M-Logo.png", use_column_width=True)
top2.write("Mothers 2 Mothers, a group of non-profit organizations across Southern Africa, works to empower and employ women living with HIV as Community Health Workers to help close the systemic gap in HIV infections across gender.")
top2.write("Here we focused on the gap in infection rates between Females and Males in the ages of 10 and 19. Use our interactive chart to see how the HIV infection rates between males and females is changing over time across the continent of Africa.")

st.markdown("""
    <style type='text/css'>
        details {
            display: none;
        }
    </style>
""", unsafe_allow_html=True)


@st.cache
def country_codes():
    cc = coco.CountryConverter()
    df = pd.read_csv('https://query.data.world/s/atfqu76bmkmwiranfkzfiqqdnvpzle',encoding = "ISO-8859-1")

    url_geojson = "https://query.data.world/s/ziovq5tz5zcqvizgghygjucscii32t"
    countries = alt.Data(url=url_geojson, format=alt.DataFormat(property="features", type="json"))

    unique = pd.DataFrame(df["Country"].unique())
    unique = unique.rename(columns={0:"Country"})

    unique['iso_a3'] = unique["Country"].apply(lambda x: coco.convert(names=x, to="ISO3"))

    df = pd.merge(df, unique, how="left", left_on="Country", right_on="Country")
    return df, countries, unique

df, countries, unique = country_codes()

options = ["with the Largest Gap","with the Smallest Gap"]
country_list = unique["Country"].to_list()
options.extend(country_list)

add_selectbox = st.selectbox("Show the country...", options)

year_slider = st.select_slider(
    label="for the Year",
    options= list(df["Year"].unique()),
    value = 2019,
    key="initial"
)

col1, col2 = st.beta_columns(2)




tdf = df[df["Year"]==year_slider]



pivot = tdf.pivot(index=["Country", "iso_a3"], columns="Sex", values="Estimated incidence rate of new HIV infection per 1 000 uninfected population ")
pivot = pivot.reset_index()
pivot["Diff"] = pivot["Female"] - pivot["Male"]

if add_selectbox == "with the Largest Gap":
    max_country = pivot[pivot["Diff"] == pivot["Diff"].max()]
    text = "largest"
    c_text = False
elif add_selectbox == "with the Smallest Gap":
    max_country = pivot[pivot["Diff"] == pivot["Diff"].min()]
    text = "smallest"
    c_text = False
else:
    max_country = pivot[pivot["Country"]==add_selectbox]
    c_text = True


if (max_country["Female"].values[0]) >(max_country["Male"].values[0]):
    compare_text = "This means females are ***" + str(round((max_country["Female"].values[0])/(max_country["Male"].values[0]),2))+ "*** times more likely to be infected than males."
else:
    compare_text = "This means females are ***" + str(round((max_country["Female"].values[0])/(max_country["Male"].values[0]),2))+ "*** times less likely to be infected than males."

if c_text:
    col1.write(
        "In the year " + str(year_slider) + ", in ***" +
        max_country["Country"].values[0] +
        "***, females had an infection rate of " +
        str(max_country["Female"].values[0]) + " per 1000 uninfected females, while males had an infection rate of " + str(max_country["Male"].values[0]) +
        " per 1000 uninfected males. " + compare_text
        )
else:
    col1.write(
        "In " + str(year_slider) + " ***" +
        max_country["Country"].values[0] +
        "*** had the " + text + " gap between rates of new HIV infections between females and males. Females had an infection rate of " +
        str(max_country["Female"].values[0]) + " per 1000 uninfected females, while males had an infection rate of " + str(max_country["Male"].values[0]) +
        " per 1000 uninfected males. " + compare_text
        )


chart = alt.Chart(countries).mark_geoshape().encode(
    color=alt.Color("Diff:Q", title="Gap", scale=alt.Scale(domain=[0,20])),
    tooltip=["Country:N","Female:Q", "Male:Q", "Diff:Q"]
).transform_lookup(
    lookup="properties.iso_a3",
    from_ = alt.LookupData(pivot, 'iso_a3', ["Diff", "Country", "Female", "Male"])
).configure_view(strokeWidth=0)



col2.altair_chart(chart, use_container_width=False)
col2.write(
    "_ The map shows the gap in infection rate. Darker countries have larger gaps in infection rate between female and males. _"
)

cdf = df[df["Country"] == max_country["Country"].values[0]]

line_chart = alt.Chart(cdf).mark_line().encode(
    x=alt.X("Year", axis=alt.Axis(format="d")),
    y=alt.Y("Estimated incidence rate of new HIV infection per 1 000 uninfected population ", title="New Infections per 1000"),
    color="Sex",
    tooltip=["Year", "Sex" ,alt.Tooltip("Estimated incidence rate of new HIV infection per 1 000 uninfected population ", title="New Infections per 1000")]
)


max_country["Year"] = year_slider

max_country["Times"] = round(max_country["Female"]/max_country["Male"],2)
max_country["Times"] = max_country["Times"].astype("str")
max_country["Times"] = max_country["Times"] + "x"


gap = alt.Chart(max_country).mark_rule().encode(
    x="Year",
    y="Female",
    y2="Male",
    tooltip=alt.Tooltip("Diff", title="Difference")
)

text = gap.mark_text(
    align="left",
    baseline="top",
    dx=4,
    dy=10
).encode(
    text="Times"
)

diff_chart = line_chart + gap + text

col1.altair_chart(diff_chart, use_container_width=True)


st.write("_ Visualization by William Masse, Data from UNICEF _")






