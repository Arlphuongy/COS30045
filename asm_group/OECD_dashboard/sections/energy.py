import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from utils.db import load_table

def section_energy():
    st.header("⚡ Energy Use in Agriculture")

    energy = load_table("energy")

    st.markdown("""
    Energy consumption in agriculture reflects production intensity, mechanization levels, and sustainability of food systems.  
    This section explores **Direct On-Farm Energy Use** and **Total Final Energy Consumption**, with global and national insights.
    """)

    # Filter and select relevant measures
    energy_measures = [
        "Direct on-farm energy consumption",
        "Total final energy consumption"
    ]
    df_energy = energy[
        energy["Measure"].isin(energy_measures) &
        (energy["Year"] >= 2000)
    ]

    if df_energy.empty:
        st.warning("No energy-related data found.")
        return

    # Select energy measure
    selected_measure = st.selectbox("🔋 Select Energy Measure", sorted(df_energy["Measure"].unique()))
    df_selected = df_energy[df_energy["Measure"] == selected_measure]

    # Global trend
    st.subheader(f"📈 Global Trend: {selected_measure}")
    df_global = df_selected.groupby("Year")["Value"].sum().reset_index()
    fig_global = px.line(
        df_global, x="Year", y="Value", markers=True,
        title=f"{selected_measure} Over Time (Global Total)",
        labels={"Value": "Energy (tonnes oil equivalent)"}
    )
    st.plotly_chart(fig_global, use_container_width=True)

    # Top countries (average)
    st.subheader(f"🏆 Top 10 Countries by {selected_measure} (Avg since 2000)")
    df_top = df_selected.groupby("Reference area")["Value"].mean().nlargest(10).reset_index()
    fig_top = px.bar(
        df_top, x="Reference area", y="Value", color="Value",
        color_continuous_scale="Oranges",
        title=f"Top 10 Countries – {selected_measure}",
        labels={"Value": "Avg Energy Use", "Reference area": "Country"}
    )
    st.plotly_chart(fig_top, use_container_width=True)

    # Growth patterns
    st.subheader("📊 Energy Growth Patterns")
    growth_data = []
    countries = df_selected['Reference area'].unique()

    for country in countries:
        country_data = df_selected[df_selected['Reference area'] == country].sort_values('Year')
        if len(country_data) >= 10:
            first_year = country_data.iloc[0]
            last_year = country_data.iloc[-1]
            years_span = last_year['Year'] - first_year['Year']

            if years_span > 0 and first_year['Value'] > 0:
                annual_growth = ((last_year['Value'] / first_year['Value']) ** (1/years_span) - 1) * 100
                total_growth = ((last_year['Value'] - first_year['Value']) / first_year['Value']) * 100

                growth_data.append({
                    'Country': country,
                    'Annual Growth Rate (%)': annual_growth,
                    'Total Growth (%)': total_growth,
                    'Start Year': first_year['Year'],
                    'End Year': last_year['Year'],
                    'Latest Consumption': last_year['Value']
                })

    df_growth = pd.DataFrame(growth_data)

    if not df_growth.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 🚀 Fastest Growing Countries (Annual %)")
            top_growth = df_growth.nlargest(10, 'Annual Growth Rate (%)').reset_index(drop=True)
            fig_growth = px.bar(top_growth, x='Annual Growth Rate (%)', y='Country',
                               orientation='h', color='Annual Growth Rate (%)',
                               color_continuous_scale='Reds')
            fig_growth.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_growth, use_container_width=True)

        with col2:
            st.markdown("#### 📉 Declining Energy Use (Annual %)")
            declining = df_growth[df_growth['Annual Growth Rate (%)'] < 0].nsmallest(10, 'Annual Growth Rate (%)').reset_index(drop=True)
            if not declining.empty:
                fig_decline = px.bar(declining, x='Annual Growth Rate (%)', y='Country',
                                   orientation='h', color='Annual Growth Rate (%)',
                                   color_continuous_scale='Blues_r')
                fig_decline.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_decline, use_container_width=True)
            else:
                st.info("No countries show declining energy consumption in this dataset.")

    # Country drill-down
    with st.expander("🔎 Country Trend Viewer"):
        country_list = sorted(df_selected["Reference area"].dropna().unique())
        selected_country = st.selectbox("🌍 Select Country", country_list)
        df_country = df_selected[df_selected["Reference area"] == selected_country]

        if not df_country.empty:
            df_year = df_country.groupby("Year")["Value"].sum().reset_index()
            fig_country = px.line(
                df_year, x="Year", y="Value", markers=True,
                title=f"{selected_country} – {selected_measure} Over Time",
                labels={"Value": "Energy (tonnes oil equivalent)"}
            )
            st.plotly_chart(fig_country)

    # Energy Efficiency Analysis (Ratio)
    if set(energy_measures).issubset(set(df_energy["Measure"].unique())):
        st.subheader("📊 Agricultural Energy Intensity (%)")

        df_farm = df_energy[df_energy["Measure"] == "Direct on-farm energy consumption"]
        df_total = df_energy[df_energy["Measure"] == "Total final energy consumption"]

        latest_year = min(df_farm["Year"].max(), df_total["Year"].max())

        farm_latest = df_farm[df_farm["Year"] == latest_year]
        total_latest = df_total[df_total["Year"] == latest_year]

        df_merge = pd.merge(
            farm_latest[["Reference area", "Value"]],
            total_latest[["Reference area", "Value"]],
            on="Reference area", suffixes=("_farm", "_total")
        )
        df_merge = df_merge[df_merge["Value_total"] > 0]
        df_merge["Intensity (%)"] = (df_merge["Value_farm"] / df_merge["Value_total"]) * 100

        top_intensive = df_merge.nlargest(10, "Intensity (%)")
        least_intensive = df_merge.nsmallest(10, "Intensity (%)")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🚜 Highest Agricultural Share")
            fig_high = px.bar(
                top_intensive, x="Intensity (%)", y="Reference area", orientation="h",
                color="Intensity (%)", color_continuous_scale="Reds",
                labels={"Reference area": "Country"},
                title="Top 10 Agricultural Energy-Intensive Countries"
            )
            st.plotly_chart(fig_high)

        with col2:
            st.markdown("#### 💡 Lowest Agricultural Share")
            fig_low = px.bar(
                least_intensive, x="Intensity (%)", y="Reference area", orientation="h",
                color="Intensity (%)", color_continuous_scale="Blues",
                labels={"Reference area": "Country"},
                title="Top 10 Energy-Efficient Countries"
            )
            st.plotly_chart(fig_low)

    # Choropleth map
    st.subheader("🗺️ Global Distribution Map")
    year_map = st.selectbox("Select Year", sorted(df_selected["Year"].unique(), reverse=True), key="energy_map")
    df_map = df_selected[df_selected["Year"] == year_map].groupby("Reference area")["Value"].sum().reset_index()

    fig_map = px.choropleth(
        df_map, locations="Reference area", locationmode="country names",
        color="Value", color_continuous_scale="YlOrRd",
        hover_name="Reference area",
        title=f"{selected_measure} by Country ({year_map})",
        labels={"Value": "Energy Use"}
    )
    st.plotly_chart(fig_map)

    # Download
    st.markdown("### 📥 Download This Dataset")
    csv_data = df_selected.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name=f"{selected_measure.lower().replace(' ', '_')}_energy.csv",
        mime='text/csv'
    )

    # Insight
    st.markdown("---")
    st.markdown("""
    ### 🧠 Insights
    - Direct on-farm energy use is rising in most regions, reflecting mechanization and fossil fuel dependency.
    - Countries with high agricultural intensity may face efficiency or emission trade-offs.
    - Integrating energy data with emissions could uncover cleaner production opportunities.
    """)
