
import streamlit as st
import plotly.express as px
from utils.db import load_table
import pandas as pd

def section_water():
    st.header("Water Use in Agriculture 💧")

    # Load data
    water = load_table("water")

    st.markdown("""
    Excess **water use** in agriculture can lead to depletion of freshwater resources and affect ecosystem health.  
    This section evaluates freshwater abstraction by country since 2012 to assess sustainability.
    """)

    # ------------------------------------------------
    # Only allow volume-based Measures
    # ------------------------------------------------
    allowed_measures = [
        "Agriculture freshwater abstraction",
        "Total freshwater abstraction"
    ]
    water_filtered_measure = water[water['Measure'].isin(allowed_measures)]

    use_type = st.selectbox(
        "💧 Select Water Use Measure",
        allowed_measures
    )

    # Filter timeframe
    water_filtered = water_filtered_measure[
        (water_filtered_measure['Measure'] == use_type) &
        (water_filtered_measure['Year'] >= 2012) &
        (water_filtered_measure['Year'] <= 2021)
    ]

    # Normalize units
    multiplier_map = {
        'Millions': 1_000_000,
        'Thousands': 1_000,
        'Units': 1,
        'Billions': 1_000_000_000
    }
    water_filtered['Value_normalized'] = (
        water_filtered['Value'] *
        water_filtered['Unit multiplier'].map(multiplier_map).fillna(1)
    )

    # -----------------------------------------------------------
    # 1. Global Trend
    # -----------------------------------------------------------
    st.subheader(f"🌍 Global Average {use_type} (2012–2021)")
    global_trend = (
        water_filtered.groupby('Year')['Value_normalized']
        .mean()
        .reset_index()
    )
    fig_global = px.line(
        global_trend, x='Year', y='Value_normalized',
        markers=True,
        labels={'Value_normalized': 'Average Water Use'},
        title=f"Global Average {use_type} Over Time"
    )
    st.plotly_chart(fig_global, use_container_width=True)

    # -----------------------------------------------------------
    # 2. Country-Level Trend
    # -----------------------------------------------------------
    st.subheader("📈 Country-Level Trend")
    country_list = sorted(water_filtered['Reference area'].unique())
    selected_country = st.selectbox("Select Country", country_list)
    country_df = (
        water_filtered[water_filtered['Reference area'] == selected_country]
        .groupby('Year')['Value_normalized']
        .mean()
        .reset_index()
    )
    fig_country = px.line(
        country_df, x='Year', y='Value_normalized', markers=True,
        title=f"{use_type} in {selected_country} (2012–2021)",
        labels={'Value_normalized': 'Water Use'}
    )
    st.plotly_chart(fig_country, use_container_width=True)

    # -----------------------------------------------------------
    # 3. Top-10 Bar Chart
    # -----------------------------------------------------------
    st.subheader(f"🏆 Top 10 Countries with Highest {use_type} (2012–2021)")
    top10 = (
        water_filtered.groupby('Reference area')['Value_normalized']
        .sum()
        .nlargest(10)
        .reset_index()
    )
    fig_bar = px.bar(
        top10,
        x='Reference area', y='Value_normalized',
        color='Value_normalized', color_continuous_scale='Blues',
        labels={'Value_normalized': 'Total Water Use (normalized)',
                'Reference area': 'Country'}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # -----------------------------------------------------------
    # 4. Treemap – Share of Global Water Use
    # -----------------------------------------------------------
 
    st.subheader("🌳 Treemap: Global Share of Water Use (Top 20 Countries)")

    total_by_country = (
        water_filtered.groupby('Reference area')['Value_normalized']
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )

    top20_tree = total_by_country.head(20)

    fig_treemap = px.treemap(
    top20_tree,
    path=['Reference area'],
    values='Value_normalized',
    color='Value_normalized',
    color_continuous_scale='Blues',
    title=f"Top 20 Contributors to Global {use_type} (2012–2021)"
    )
    fig_treemap.update_traces(

        textinfo='label+percent entry',  # Show only percentage on the box
        marker=dict(line=dict(width=1, color='white')),
        hovertemplate='<b>%{label}</b><br>Value: %{value:,.0f}<br>Percent: %{percentEntry:.2%}<extra></extra>'
    )
    fig_treemap.update_layout(
        margin=dict(t=30, l=0, r=0, b=0),
        paper_bgcolor='white',
        plot_bgcolor='white',
        coloraxis_colorbar=dict(
            tickformat=',.0f'
        )
    )
    st.plotly_chart(fig_treemap, use_container_width=True)


    # -----------------------------------------------------------
    # 📊 Stacked Bar Chart – Surface vs Groundwater vs Not Applicable
    # -----------------------------------------------------------
    st.subheader("📊 Surface vs Groundwater Abstraction by Country & Year")

    sg_all = water[
        (water['Measure'] == 'Total freshwater abstraction') &
        (water['Water type'].isin(['Surface water', 'Ground water', 'Not applicable']))
    ].copy()

    sg_all['Value_norm'] = sg_all['Value'] * sg_all['Unit multiplier'].map(multiplier_map).fillna(1)

    # Year selector
    year_select = st.selectbox(
        "Select Year (Stacked Bar)", sorted(sg_all['Year'].unique(), reverse=True), key="sg_year"
    )

    sg_year = sg_all[sg_all['Year'] == year_select]

    # Country selector
    all_countries = sorted(sg_year['Reference area'].unique())
    selected = st.multiselect(
        "Select Countries to Compare",
        all_countries,
        default=all_countries[:5]
    )

    if selected:
        sg_plot = sg_year[sg_year['Reference area'].isin(selected)]

        fig_stack = px.bar(
            sg_plot,
            x='Reference area',
            y='Value_norm',
            color='Water type',
            barmode='stack',
            title=f"Surface vs Groundwater Abstraction ({year_select})",
            labels={
                'Reference area':'Country',
                'Value_norm':'Water Abstraction (normalized)',
                'Water type':'Source'
            }
        )
        st.plotly_chart(fig_stack, use_container_width=True)
    else:
        st.info("Please select at least one country.")


    # -----------------------------------------------------------
    # 📥 Download Normalized Water Dataset
    # -----------------------------------------------------------
    st.markdown("#### 📥 Download Normalized Water Abstraction Dataset")
    csv_water = water_filtered.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Normalized Water Data as CSV",
        data=csv_water,
        file_name=f"normalized_{use_type.lower().replace(' ', '_')}_2012_2021.csv",
        mime='text/csv'
    )

