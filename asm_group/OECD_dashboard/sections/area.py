import streamlit as st
import plotly.express as px
from utils.db import load_table
import pandas as pd


def section_area():
    st.header("Land Use in Agriculture 🌾")
    st.markdown("This section highlights global agricultural land patterns, focusing on different land-use types and their distribution across countries.")

    # Load data
    area = load_table("area")

    # Normalize units
    multiplier_map = {'Millions': 1_000_000, 'Thousands': 1_000, 'Units': 1, 'Billions': 1_000_000_000}
    area['Value_norm'] = area['Value'] * area['Unit multiplier'].map(multiplier_map).fillna(1)  # normalized to hectares

    # Exclude combined/total measures
    area = area[~area['Measure'].str.contains('total', case=False)]
    total_like = ['Arable land and permanent crops', 'Agricultural area']
    land_types_of_interest = sorted([m for m in area['Measure'].unique().tolist() if m not in total_like])

    # -----------------------------------------------------------
    # 🥧 Pie Chart: Global Agricultural Land Breakdown
    # -----------------------------------------------------------
    st.subheader("🌍 Global Breakdown of Agricultural Land Types")
    st.markdown("This pie chart shows the proportion of each land-use type (in hectares) contributing to global agricultural area.")
    global_land = (
        area[area['Measure'].isin(land_types_of_interest)]
        .groupby('Measure')['Value_norm']
        .sum()
        .reset_index()
        .sort_values('Value_norm', ascending=False)
    )
    fig_land_pie = px.pie(
        global_land,
        names='Measure',
        values='Value_norm',
        color_discrete_sequence=px.colors.qualitative.Vivid,
        title='Global Agricultural Land Composition',
        hole=0.5,
    )
    fig_land_pie.update_layout(height=600, width=600)
    st.plotly_chart(fig_land_pie, use_container_width=True)

    # -----------------------------------------------------------
    # 🥧 Country-level Pie Chart (collapsible)
    # -----------------------------------------------------------
    with st.expander("Country-level Land Composition Pie Chart"):
        selected_country = st.selectbox("Select country", sorted(area['Reference area'].unique().tolist()))
        sub_country = area[area['Reference area'] == selected_country]
        country_land = sub_country.groupby('Measure')['Value_norm'].sum().reset_index().sort_values('Value_norm', ascending=False)
        fig_country_pie = px.pie(
            country_land, names='Measure', values='Value_norm', 
            color_discrete_sequence=px.colors.qualitative.Vivid,
            hole=0.5,
            title=f"Land Composition in {selected_country}")
        fig_country_pie.update_layout(height=600, width=600)
        st.plotly_chart(fig_country_pie, use_container_width=True)

    # -----------------------------------------------------------
    # 🌐 Choropleth Map: Distribution by Country & Land Type
    # -----------------------------------------------------------
    st.subheader("🌐 Land Type Distribution Across Countries")
    st.markdown("This choropleth map displays how the selected land-use type is distributed by country, based on total land area in hectares.")

    selected_type = st.selectbox("Select land type", land_types_of_interest)

    subset = area[area['Measure'] == selected_type]
    country_agg = subset.groupby(['CountryCode', 'Reference area'])['Value_norm'].sum().reset_index()

    fig_choro = px.choropleth(
        country_agg,
        locations="CountryCode",
        color="Value_norm",
        labels={'Value_norm':'Area (hectares)'},
        hover_name="Reference area",
        color_continuous_scale="Viridis",
        title=f"{selected_type} by country (Value_norm in hectares)"
    )
    fig_choro.update_layout(height=600, width=900)
    st.plotly_chart(fig_choro, use_container_width=True)

    # -----------------------------------------------------------
    # 📈 Time-Series Trend: Land Type Over Time (Multi-line comparison)
    # -----------------------------------------------------------
    st.subheader("📈 Trend Over Time by Land Type")
    st.markdown("This line chart compares trends in different land-use types from 2000 to 2020.")

    selected_ts_types = st.multiselect(
        "Select land types for trend", land_types_of_interest, default=land_types_of_interest[:2], key="ts"
    )
    ts_data = area[(area['Measure'].isin(selected_ts_types)) & (area['Year'].between(2000, 2020))].groupby(['Year','Measure'])['Value_norm'].sum().reset_index()

    fig_ts = px.line(ts_data, x='Year', y='Value_norm', color='Measure', markers=True,
                     color_discrete_sequence=px.colors.qualitative.Vivid,
                     title="Global Trend Over Time by Land Type")
    st.plotly_chart(fig_ts, use_container_width=True)
