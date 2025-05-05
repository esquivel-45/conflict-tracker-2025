import streamlit as st
import pandas as pd
from streamlit_folium import folium_static
import folium

# ----- CONFIGURATION -----
st.set_page_config(page_title="Global Conflict Tracker", layout="wide")

# ----- HEADER -----
st.title("📰 Global Conflict Risk Dashboard")
st.markdown("Monitor global instability using real-time news and geospatial insights.")

# ----- LOAD DATA -----
@st.cache_data

def load_data():
    df = pd.read_csv("combined_conflict_news_tagged.csv")
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce")
    return df.dropna(subset=["headline", "published_at"])

df = load_data()

# ----- SIDEBAR -----
st.sidebar.header("🔎 Filter Options")
st.sidebar.markdown("Use the date range slider to filter headlines.")

min_date = df["published_at"].min().date()
max_date = df["published_at"].max().date()

start_date, end_date = st.sidebar.slider(
    "Select date range",
    min_value=min_date,
    max_value=max_date,
    value=(min_date, max_date)
)

filtered_df = df[(df["published_at"].dt.date >= start_date) & (df["published_at"].dt.date <= end_date)]

# ----- METRICS -----
st.subheader("📊 Summary Statistics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Articles", len(filtered_df))
col2.metric("Positive", (filtered_df["sentiment_label"] == "positive").sum())
col3.metric("Negative", (filtered_df["sentiment_label"] == "negative").sum())

# ----- EXPANDER FOR RAW DATA -----
with st.expander("🔍 Show Raw Headlines Table"):
    st.dataframe(filtered_df[["headline", "source", "sentiment_label", "published_at"]])

# ----- CHOROPLETH MAP -----
st.subheader("🗺️ Conflict Intensity by Country (Choropleth)")
choropleth_map = "choropleth_map.html"
with open(choropleth_map, "r", encoding="utf-8") as f:
    st.components.v1.html(f.read(), height=600)

# ----- REFRESH BUTTON -----
if st.button("🔄 Refresh Data"):
    df = load_data()
    st.success("Data refreshed!")

#sentiment choice
sentiment_choice = st.sidebar.selectbox(
    "🧠 Sentiment Filter",
    options=["All", "positive", "neutral", "negative"]
)

if sentiment_choice != "All":
    filtered_df = filtered_df[filtered_df["sentiment_label"] == sentiment_choice]
####Top countries chart
st.subheader("🌍 Top 10 Countries by Headline Volume")
top_countries = (
    filtered_df["country_poly"]
    .value_counts()
    .head(10)
    .sort_values(ascending=True)
)

st.bar_chart(top_countries)


###Headlines searching
search_term = st.text_input("🔍 Search headlines")

if search_term:
    filtered_df = filtered_df[filtered_df["headline"].str.contains(search_term, case=False, na=False)]
    st.write(f"Found {len(filtered_df)} matching articles.")

###timeline of articles
import altair as alt

timeline = (
    filtered_df.groupby(filtered_df["published_at"].dt.date)
    .size()
    .reset_index(name="count")
)

chart = alt.Chart(timeline).mark_line().encode(
    x="published_at:T",
    y="count:Q"
).properties(title="📈 Article Volume Over Time")

st.altair_chart(chart, use_container_width=True)
