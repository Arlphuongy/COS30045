import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import load_table

def section_area():
    st.header("🌾 Land Use in Agriculture")

    agri = load_table("agri")

    st.markdown("""
    Understanding how agricultural land is used provides insight into food systems, sustainability, and biodiversity impact.  
    This section explores trends in **arable land**, **pasture**, **permanent crops**, and **organic farming**.
    """)

    # ----------------------------------------
    # Filter relevant measures
    # ----------------------------------------
    land_keywords = [
        "Arable land", "Permanent pasture", "Permanent crops",
        "Organic farming", "Total agricultural land area"
    ]
    df_land = agri[
        agri["Measure"].str.contains("|".join(land_keywords), case=False, na=False) &
        agri["Unit of measure"].str.contains("Hectares", na=False) &
        (agri["Year"] >= 2012)
    ]

    if df_land.empty:
        st.warning("No land use data available.")
        return

    # ----------------------------------------
    # Select land use type
    # ----------------------------------------
    land_types = sorted(df_land["Measure"].unique())
    selected_type = st.selectbox("🌍 Select Land Use Type", land_types)
    df_selected = df_land[df_land["Measure"] == selected_type]

    # ----------------------------------------
    # Global trend over time
    # ----------------------------------------
    st.subheader(f"📈 Global Trend: {selected_type}")
    df_global = df_selected.groupby("Year")["Value"].sum().reset_index()
    fig_global = px.line(
        df_global, x="Year", y="Value", markers=True,
        title=f"Global Area of {selected_type} (2012+)",
        labels={"Value": "Area (hectares)"}
    )
    st.plotly_chart(fig_global)

    # ----------------------------------------
    # Top countries by land area
    # ----------------------------------------
    st.subheader(f"🏆 Top Countries by {selected_type} (avg since 2012)")
    df_top = df_selected.groupby("Reference area")["Value"].mean().nlargest(10).reset_index()
    fig_top = px.bar(
        df_top, x="Reference area", y="Value",
        color="Value", color_continuous_scale="Greens",
        labels={"Value": "Avg Area (ha)"},
        title=f"Top 10 Countries with Most {selected_type}"
    )
    st.plotly_chart(fig_top)

    # ----------------------------------------
    
    # Drill-down by country
    # ----------------------------------------
    with st.expander("🔎 Explore Country-wise Land Use"):
        country_list = sorted(df_selected["Reference area"].dropna().unique())
        selected_country = st.selectbox("Select Country", country_list)
        df_country = df_selected[df_selected["Reference area"] == selected_country]

        df_country_year = df_country.groupby("Year")["Value"].mean().reset_index()

        fig_country = px.line(
            df_country_year, x="Year", y="Value", markers=True,
            title=f"{selected_country} - {selected_type} Over Time",
            labels={"Value": "Area (hectares)"}
        )
        st.plotly_chart(fig_country)

    # ----------------------------------------
    # Choropleth Map - separated section
    # ----------------------------------------
    st.subheader("🗺️ Global Distribution Map")
    st.markdown("Visualize land use by country for a selected year.")
    available_years = sorted(df_selected["Year"].unique(), reverse=True)
    year_map = st.selectbox("Select Year", available_years, key="land_map_year")

    df_map = df_selected[df_selected["Year"] == year_map]
    df_map_grouped = df_map.groupby("Reference area")["Value"].mean().reset_index()

    fig_map = px.choropleth(
        df_map_grouped, locations="Reference area", locationmode="country names",
        color="Value", hover_name="Reference area",
        color_continuous_scale="YlGn",
        labels={"Value": "Area (hectares)"},
        title=f"{selected_type} by Country in {year_map}"
    )
    st.plotly_chart(fig_map)

    # ----------------------------------------
    # Download option
    # ----------------------------------------
    st.markdown("### 📥 Download This Dataset")
    csv = df_selected.to_csv(index=False)
    st.download_button(
        label="⬇️ Download CSV",
        data=csv,
        file_name=f"{selected_type.lower().replace(' ', '_')}_area.csv",
        mime='text/csv'
    )