import streamlit as st
import pandas as pd
import pydeck as pdk
import country_converter as coco
import altair as alt

cc = coco.CountryConverter()
df = pd.read_csv('https://query.data.world/s/atfqu76bmkmwiranfkzfiqqdnvpzle',encoding = "ISO-8859-1")
countries = alt.topo_feature("https://query.data.world/s/ziovq5tz5zcqvizgghygjucscii32t", "countries")


@st.cache
def country_codes(cc, df, countries):
    unique = pd.DataFrame(df["Country"].unique())
    unique = unique.rename(columns={0:"Country"})

    unique['iso_a3'] = unique["Country"].apply(lambda x: coco.convert(names=x, to="ISO3"))

    df = pd.merge(df, unique, how="left", left_on="Country", right_on="Country")
    return df

df = country_codes(cc, df, countries)



st.title("My App")
year = st.select_slider(
    label="Year",
    options= list(df["Year"].unique()),
    value = 2019
)

df = df[df["Year"]==year]

pivot = df.pivot(index=["Country", "iso_a3"], columns="Sex", values="Estimated incidence rate of new HIV infection per 1 000 uninfected population ")
pivot = pivot.reset_index()
pivot["Diff"] = pivot["Female"] - pivot["Male"]


st.write(pivot)

chart = alt.Chart(countries).mark_geoshape().encode(
    color="Diff:Q",
).transform_lookup(
    lookup="iso_a3",
    from_ = alt.LookupData(pivot, 'iso_a3', ["Diff"])
)
st.write(chart)




