import streamlit as st
import pandas as pd
import datetime
from PIL import Image
import plotly.express as px
import plotly.graph_objects as go

# ----------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------
st.set_page_config(
    page_title="Adidas Sales Dashboard",
    layout="wide"
)

# ----------------------------------------------------
# LOAD DATA
# ----------------------------------------------------
df = pd.read_excel("Adidas_sales.xlsx")
df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

# ----------------------------------------------------
# HEADER (LOGO + TITLE) — STREAMLIT ONLY
# ----------------------------------------------------
logo = Image.open("adidas-logo.jpg")
logo.thumbnail((160, 80))  # prevent cropping

col1, col2 = st.columns([0.15, 0.85])
with col1:
    st.image(logo)

with col2:
    st.title("Adidas Interactive Sales Dashboard")
    st.caption(f"📅 Last updated: {datetime.datetime.now().strftime('%d %B %Y')}")

st.divider()

# ----------------------------------------------------
# SIDEBAR FILTERS
# ----------------------------------------------------
st.sidebar.header("🔍 Filters")

regions = st.sidebar.multiselect(
    "Select Region",
    options=df["Region"].unique(),
    default=df["Region"].unique()
)

states = st.sidebar.multiselect(
    "Select State",
    options=df["State"].unique(),
    default=df["State"].unique()
)

df = df[df["Region"].isin(regions) & df["State"].isin(states)]

# ----------------------------------------------------
# KPI METRICS
# ----------------------------------------------------
total_sales = df["TotalSales"].sum()
total_units = df["UnitsSold"].sum()
total_states = df["State"].nunique()

k1, k2, k3 = st.columns(3)
k1.metric("💰 Total Sales ($)", f"{total_sales:,.0f}")
k2.metric("📦 Units Sold", f"{total_units:,}")
k3.metric("📍 Active States", total_states)

st.divider()

# ----------------------------------------------------
# SALES OVERVIEW
# ----------------------------------------------------
st.subheader("📊 Sales Overview")

col4, col5 = st.columns(2)

with col4:
    fig = px.bar(
        df,
        x="Retailer",
        y="TotalSales",
        title="Total Sales by Retailer",
        text_auto=".2s"
    )
    st.plotly_chart(fig, use_container_width=True)

df["Month_Year"] = df["InvoiceDate"].dt.to_period("M").astype(str)
monthly_sales = df.groupby("Month_Year")["TotalSales"].sum().reset_index()

with col5:
    fig1 = px.line(
        monthly_sales,
        x="Month_Year",
        y="TotalSales",
        title="Total Sales Over Time",
        markers=True
    )
    st.plotly_chart(fig1, use_container_width=True)

# ----------------------------------------------------
# DATA DOWNLOADS
# ----------------------------------------------------
with st.expander("📥 Download Sales Data"):
    st.download_button(
        "Download Retailer Sales",
        data=df.groupby("Retailer")["TotalSales"].sum().to_csv().encode("utf-8"),
        file_name="Retailer_Sales.csv",
        mime="text/csv"
    )

    st.download_button(
        "Download Monthly Sales",
        data=monthly_sales.to_csv(index=False).encode("utf-8"),
        file_name="Monthly_Sales.csv",
        mime="text/csv"
    )

st.divider()

# ----------------------------------------------------
# STATE LEVEL ANALYSIS
# ----------------------------------------------------
st.subheader("📍 State Level Performance")

state_data = df.groupby("State")[["TotalSales", "UnitsSold"]].sum().reset_index()

fig2 = go.Figure()
fig2.add_bar(
    x=state_data["State"],
    y=state_data["TotalSales"],
    name="Total Sales"
)
fig2.add_scatter(
    x=state_data["State"],
    y=state_data["UnitsSold"],
    mode="lines+markers",
    name="Units Sold",
    yaxis="y2"
)

fig2.update_layout(
    yaxis=dict(title="Total Sales"),
    yaxis2=dict(title="Units Sold", overlaying="y", side="right"),
    title="Total Sales and Units Sold by State"
)

st.plotly_chart(fig2, use_container_width=True)

with st.expander("📄 View State-wise Data"):
    st.dataframe(state_data)

st.divider()

# ----------------------------------------------------
# REGION & CITY TREEMAP
# ----------------------------------------------------
st.subheader("🌍 Sales by Region and City")

region_city = (
    df.groupby(["Region", "City"])["TotalSales"]
    .sum()
    .reset_index()
)

fig3 = px.treemap(
    region_city,
    path=["Region", "City"],
    values="TotalSales",
    title="Total Sales Distribution"
)

st.plotly_chart(fig3, use_container_width=True)

with st.expander("📄 View Region & City Data"):
    st.dataframe(region_city)

st.divider()

# ----------------------------------------------------
# RAW DATA
# ----------------------------------------------------
with st.expander("🧾 View Raw Sales Data"):
    st.dataframe(df)
