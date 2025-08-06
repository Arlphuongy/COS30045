import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import load_table


def section_water():
    st.header("💧 Water Use in Agriculture")

    agri = load_table("agri")

    st.markdown("""
    Water is a vital input for agricultural production, but excessive use can deplete freshwater resources.  
    This section analyzes **freshwater abstraction**, **irrigation trends**, and **source breakdowns** by country.
    """)

    # ----------------------------------------
    # Filter water-related measures
    # ----------------------------------------
    water_measures = [
        "Agriculture freshwater abstraction",
        "Total freshwater abstraction",
        "Irrigable area",
        "Irrigation area"
    ]

    df_water = agri[
        agri["Measure"].isin(water_measures) &
        agri["Unit of measure"].str.contains("Cubic metres|Hectares", na=False) &
        (agri["Year"] >= 2012)
    ]

    if df_water.empty:
        st.warning("No water-related data found.")
        return

    # ----------------------------------------
    # Water measure selection
    # ----------------------------------------
    selected_measure = st.selectbox("🚰 Select Water Measure", sorted(df_water["Measure"].unique()))
    df_selected = df_water[df_water["Measure"] == selected_measure]

    # ----------------------------------------
    # Global trend over time
    # ----------------------------------------
    st.subheader(f"📈 Global Trend: {selected_measure}")
    df_global = df_selected.groupby("Year")["Value"].sum().reset_index()

    fig_trend = px.line(
        df_global, x="Year", y="Value", markers=True,
        labels={"Value": "Total (cubic metres or hectares)"},
        title=f"{selected_measure} Over Time (Global Total)"
    )
    st.plotly_chart(fig_trend)

    # ----------------------------------------
    # Top countries by average
    # ----------------------------------------
    st.subheader(f"🏆 Top 10 Countries by {selected_measure} (Avg since 2012)")
    df_top = df_selected.groupby("Reference area")["Value"].mean().nlargest(10).reset_index()

    fig_top = px.bar(
        df_top, x="Reference area", y="Value", color="Value",
        color_continuous_scale="Blues",
        labels={"Value": "Avg Usage", "Reference area": "Country"},
        title=f"Top 10 Countries for {selected_measure}"
    )
    st.plotly_chart(fig_top)

    # ----------------------------------------
    # Choropleth Map
    # ----------------------------------------
    st.subheader("🌍 Water Use Choropleth Map")
    year_map = st.selectbox("Select Year for Map", sorted(df_selected["Year"].unique(), reverse=True), key="map_year")
    df_map = df_selected[df_selected["Year"] == year_map]
    df_map_grouped = df_map.groupby("Reference area")["Value"].sum().reset_index()

    fig_map = px.choropleth(
        df_map_grouped, locations="Reference area", locationmode="country names",
        color="Value", hover_name="Reference area",
        color_continuous_scale="YlGnBu",
        title=f"{selected_measure} by Country ({year_map})",
        labels={"Value": "Value"}
    )
    st.plotly_chart(fig_map)

    # ----------------------------------------
    # Drill-down by country with stats
    # ----------------------------------------
    with st.expander("🔎 Explore Country Trend"):
        country_list = sorted(df_selected["Reference area"].dropna().unique())
        selected_country = st.selectbox("🌏 Select a Country", country_list)
        df_country = df_selected[df_selected["Reference area"] == selected_country]

        df_country_trend = df_country.groupby("Year")["Value"].sum().reset_index()
        fig_country = px.line(
            df_country_trend, x="Year", y="Value", markers=True,
            title=f"{selected_country} – {selected_measure} Over Time",
            labels={"Value": "Usage"}
        )
        st.plotly_chart(fig_country)

        if not df_country_trend.empty:
            max_val = df_country_trend["Value"].max()
            min_val = df_country_trend["Value"].min()
            delta = df_country_trend["Value"].iloc[-1] - df_country_trend["Value"].iloc[0]
            percent_change = (delta / df_country_trend["Value"].iloc[0]) * 100 if df_country_trend["Value"].iloc[0] > 0 else 0

            col1, col2, col3 = st.columns(3)
            col1.metric("📈 Peak Use", f"{max_val:,.0f}")
            col2.metric("📉 Min Use", f"{min_val:,.0f}")
            col3.metric("🔄 Change", f"{delta:,.0f}", f"{percent_change:+.1f}%")

    # ----------------------------------------
    # Optional: Water type comparison
    # ----------------------------------------
    if "Water type" in df_selected.columns and df_selected["Water type"].nunique() > 1:
        st.subheader("💧 Breakdown by Water Type")
        df_water_type = df_selected.groupby(["Year", "Water type"])["Value"].sum().reset_index()

        fig_water_type = px.area(
            df_water_type, x="Year", y="Value", color="Water type",
            labels={"Value": "Total (cubic metres)", "Water type": "Type"},
            title=f"{selected_measure} by Water Type"
        )
        st.plotly_chart(fig_water_type)

    # ----------------------------------------
    # Treemap of top 20 contributors
    # ----------------------------------------
    st.subheader("🌳 Treemap: Top 20 Countries by Total Usage")
    top20 = df_selected.groupby("Reference area")["Value"].sum().nlargest(20).reset_index()

    fig_treemap = px.treemap(
        top20, path=['Reference area'], values='Value', color='Value',
        color_continuous_scale='Blues',
        title=f"Top 20 Contributors to {selected_measure}"
    )
    st.plotly_chart(fig_treemap)

    # ----------------------------------------
    # Download
    # ----------------------------------------
    st.markdown("### 📅 Download This Dataset")
    csv = df_selected.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"{selected_measure.lower().replace(' ', '_')}_water_data.csv",
        mime='text/csv'
    )

    # ----------------------------------------
    # Insight Summary
    # ----------------------------------------
    st.markdown("---")
    st.markdown("""
    ### 🧠 Insights
    - Countries with large irrigable areas often show high abstraction levels → monitor water sustainability.
    - 💧 Surface vs. groundwater usage patterns can signal long-term water stress.
    - 🌍 Choropleth maps highlight regional disparities in freshwater use.
    - 🌳 Treemaps show the dominance of top contributors and where intervention is most needed.
    """)
