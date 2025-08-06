import streamlit as st
import pandas as pd
from utils.db import load_table


def section_summary():
    st.subheader("📊 Sustainability Summary Table")

    # Load data
    agri = load_table("agri")
    energy = load_table("energy")

    # Select countries and years
    countries = sorted(agri["Reference area"].dropna().unique())
    selected_countries = st.multiselect("🌍 Select Countries", countries, default=["France", "Germany", "Mexico"])

    years = sorted(agri["Year"].dropna().unique())
    selected_years = st.multiselect("📅 Select Years", years, default=[max(years)])

    if not selected_countries or not selected_years:
        st.warning("Please select at least one country and one year.")
        return

    # Filter data
    agri_filtered = agri[agri["Reference area"].isin(selected_countries) & agri["Year"].isin(selected_years)]
    energy_filtered = energy[energy["Reference area"].isin(selected_countries) & energy["Year"].isin(selected_years)]

    # Build summary table
    summary_data = []
    for country in selected_countries:
        for year in selected_years:
            agri_c = agri_filtered[(agri_filtered["Reference area"] == country) & (agri_filtered["Year"] == year)]
            energy_c = energy_filtered[(energy_filtered["Reference area"] == country) & (energy_filtered["Year"] == year)]

            summary_data.append({
                "Country": country,
                "Year": year,
                "Nitrogen Surplus (kg/ha)": agri_c[agri_c["Nutrients"] == "Nitrogen"]["Value"].mean(),
                "Phosphorus Surplus (kg/ha)": agri_c[agri_c["Nutrients"] == "Phosphorus"]["Value"].mean(),
                "GHG Emissions (tonnes)": agri_c[agri_c["Measure"] == "Total greenhouse gas emissions"]["Value"].sum(),
                "Energy Use (TOE)": energy_c[energy_c["Measure"] == "Direct on-farm energy consumption"]["Value"].sum(),
                "Water Use (m³)": agri_c[agri_c["Measure"] == "Agriculture freshwater abstraction"]["Value"].sum(),
                "Arable Land (ha)": agri_c[agri_c["Measure"] == "Arable land"]["Value"].sum(),
            })

    df_summary = pd.DataFrame(summary_data)
    df_summary = df_summary.sort_values(by=["Year", "Country"]).reset_index(drop=True)

    # Format for display
    st.dataframe(
        df_summary.style.format({
            "Nitrogen Surplus (kg/ha)": "{:,.2f}",
            "Phosphorus Surplus (kg/ha)": "{:,.2f}",
            "GHG Emissions (tonnes)": "{:,.0f}",
            "Energy Use (TOE)": "{:,.0f}",
            "Water Use (m³)": "{:,.0f}",
            "Arable Land (ha)": "{:,.0f}"
        }),
        use_container_width=True
    )

    # Download button
    st.markdown("---")
    st.download_button(
        label="⬇️ Download Summary as CSV",
        data=df_summary.to_csv(index=False),
        file_name="sustainability_summary.csv",
        mime="text/csv"
    )