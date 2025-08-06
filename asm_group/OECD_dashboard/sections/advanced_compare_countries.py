import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import load_table

def compare_countries_report():
    st.subheader("🌍 Multi-Country Sustainability Comparison")

    # Load data
    agri = load_table("agri")
    area = load_table("area")
    energy = load_table("energy")
    water = load_table("water")

    # Select countries and year(s)
    countries = sorted(agri["Reference area"].dropna().unique())
    selected_countries = st.multiselect("🌐 Select Countries", countries, default=["France", "Germany"])

    years = sorted(agri["Year"].dropna().unique())
    selected_years = st.multiselect("📅 Select Year(s)", years, default=[max(years)])

    if not selected_countries or not selected_years:
        st.warning("Please select at least one country and one year.")
        return

    # Filter data
    agri_filtered = agri[agri["Reference area"].isin(selected_countries) & agri["Year"].isin(selected_years)]
    energy_filtered = energy[energy["Reference area"].isin(selected_countries) & energy["Year"].isin(selected_years)]

    # KPI Section
    st.markdown("### 📊 Key Indicators by Country")
    kpi_data = []
    for country in selected_countries:
        for year in selected_years:
            agri_c = agri_filtered[(agri_filtered["Reference area"] == country) & (agri_filtered["Year"] == year)]
            energy_c = energy_filtered[(energy_filtered["Reference area"] == country) & (energy_filtered["Year"] == year)]
            
            kpi_data.append({
                "Country": country,
                "Year": year,
                "Nitrogen Surplus": agri_c[agri_c["Nutrients"] == "Nitrogen"]["Value"].mean(),
                "Phosphorus Surplus": agri_c[agri_c["Nutrients"] == "Phosphorus"]["Value"].mean(),
                "GHG Emissions": agri_c[agri_c["Measure"] == "Total greenhouse gas emissions"]["Value"].sum(),
                "Energy Use": energy_c[energy_c["Measure"] == "Direct on-farm energy consumption"]["Value"].sum(),
                "Water Use": agri_c[agri_c["Measure"] == "Agriculture freshwater abstraction"]["Value"].sum(),
                "Arable Land": agri_c[agri_c["Measure"] == "Arable land"]["Value"].sum()
            })

    df_kpi = pd.DataFrame(kpi_data)

    # 👉 Sort by Year first, then Country
    df_kpi = df_kpi.sort_values(by=["Year", "Country"]).reset_index(drop=True)

    # Format and display
    st.dataframe(df_kpi.style.format({
        "Nitrogen Surplus": "{:,.2f}",
        "Phosphorus Surplus": "{:,.2f}",
        "GHG Emissions": "{:,.0f}",
        "Energy Use": "{:,.0f}",
        "Water Use": "{:,.0f}",
        "Arable Land": "{:,.0f}"
    }), use_container_width=True)

    # 👇 Add download button here
    csv = df_kpi.to_csv(index=False)
    st.download_button(
        label="⬇️ Download KPI Data as CSV",
        data=csv,
        file_name="multi_country_kpi.csv",
        mime="text/csv"
    )


    # ---------------------------------------------------
    # 2. Trend Comparison Section
    # ---------------------------------------------------
    st.markdown("---")
    st.subheader("📈 Compare Trends Over Time")

    trend_type = st.selectbox("Select Indicator to Compare", [
        "Nitrogen Surplus", "Phosphorus Surplus", "GHG Emissions", "Energy Use", "Water Use", "Arable Land"
    ])

    # Map each trend to its source column and value filter
    metric_map = {
        "Nitrogen Surplus": ("Nutrients", "Nitrogen"),
        "Phosphorus Surplus": ("Nutrients", "Phosphorus"),
        "GHG Emissions": ("Measure", "Total greenhouse gas emissions"),
        "Energy Use": ("Measure", "Direct on-farm energy consumption"),
        "Water Use": ("Measure", "Agriculture freshwater abstraction"),
        "Arable Land": ("Measure", "Arable land")
    }

    source_col, value_filter = metric_map[trend_type]

    # Filter and aggregate data
    if source_col == "Nutrients":
        df_trend = agri_filtered[agri_filtered[source_col] == value_filter]
        df_plot = df_trend.groupby(["Year", "Reference area"])["Value"].mean().reset_index()
        unit = df_trend["Unit of measure"].dropna().unique()
    elif trend_type in ["Water Use", "Arable Land"]:
        df_trend = agri_filtered[agri_filtered[source_col] == value_filter]
        df_plot = df_trend.groupby(["Year", "Reference area"])["Value"].sum().reset_index()
        unit = df_trend["Unit of measure"].dropna().unique()
    else:
        df_trend = energy_filtered[energy_filtered[source_col] == value_filter]
        df_plot = df_trend.groupby(["Year", "Reference area"])["Value"].sum().reset_index()
        unit = df_trend["Unit of measure"].dropna().unique()

    # Title + caption
    unit_label = unit[0] if len(unit) > 0 else "units"
    st.caption(f"Indicator source: **{source_col} = {value_filter}**  •  Unit: **{unit_label}**")

    # Plot
    fig = px.line(df_plot, x="Year", y="Value", color="Reference area",
                title=f"{trend_type} Comparison Over Time", markers=True)

    fig.update_layout(xaxis=dict(dtick=1))
    st.plotly_chart(fig, use_container_width=True)

    
