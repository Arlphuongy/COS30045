import streamlit as st
import pandas as pd
import plotly.express as px
from utils.db import load_table

def single_country_report():
    st.subheader("📌 Single Country Sustainability Report")

    # Load all data
    agri = load_table("agri")
    area = load_table("area")
    energy = load_table("energy")
    water = load_table("water")

    # Select country and year(s)
    countries = sorted(agri["Reference area"].dropna().unique())
    selected_country = st.selectbox("🌍 Select Country", countries)

    years = sorted(agri["Year"].dropna().unique())
    selected_years = st.multiselect("📅 Select Year(s)", years, default=[max(years)])

    if not selected_years:
        st.warning("Please select at least one year.")
        return

    # Filter base data by country and year
    agri_country = agri[(agri["Reference area"] == selected_country) & (agri["Year"].isin(selected_years))]
    area_country = area[(area["Reference area"] == selected_country) & (area["Year"].isin(selected_years))]
    energy_country = energy[(energy["Reference area"] == selected_country) & (energy["Year"].isin(selected_years))]
    water_country = water[(water["Reference area"] == selected_country) & (water["Year"].isin(selected_years))]

    # CSS for card styling and hover effects
    st.markdown("""
    <style>
    .kpi-card {
        border: 1px solid #ddd;
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        background-color: #fff;
        min-height: 150px;
        margin: 10px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .kpi-card:hover {
        box-shadow: 0 6px 20px rgba(0,0,0,0.1);
        transform: translateY(-3px);
    }
    .kpi-title {
        font-size: 1.1rem;
        color: #888;
    }
    .kpi-value {
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    .kpi-delta {
        font-size: 1rem;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------
    # 1. KPI Cards Summary (latest year only)
    # ---------------------------------------------------
    latest_year = max(selected_years)
    previous_year = latest_year - 1 if latest_year - 1 in selected_years else None

    def render_card(title, current, previous, unit="", icon=""):
        delta_html = ""
        if previous is not None and pd.notnull(previous) and previous != 0:
            change = ((current - previous) / previous) * 100
            arrow = "↑" if change > 0 else "↓"
            color = "green" if change > 0 else "red"
            delta_html = f"<div class='kpi-delta' style='color:{color};'>{arrow} {abs(change):.2f}%</div>"

        display_value = f"{current:,.2f}" if pd.notnull(current) else "0.00"
        st.markdown(f'''
            <div class="kpi-card">
                <div class="kpi-title">{icon} {title}</div>
                <div class="kpi-value">{display_value} {unit}</div>
                {delta_html}
            </div>
        ''', unsafe_allow_html=True)

    st.markdown(f"### 📊 Key Indicators – {selected_country} in {latest_year}")
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            n_now = agri_country[(agri_country["Nutrients"] == "Nitrogen") & (agri_country["Year"] == latest_year)]["Value"].mean()
            n_prev = agri_country[(agri_country["Nutrients"] == "Nitrogen") & (agri_country["Year"] == previous_year)]["Value"].mean() if previous_year else None
            render_card("Nitrogen Surplus", n_now, n_prev, "kg/ha", "🧪")
        with col2:
            p_now = agri_country[(agri_country["Nutrients"] == "Phosphorus") & (agri_country["Year"] == latest_year)]["Value"].mean()
            p_prev = agri_country[(agri_country["Nutrients"] == "Phosphorus") & (agri_country["Year"] == previous_year)]["Value"].mean() if previous_year else None
            render_card("Phosphorus Surplus", p_now, p_prev, "kg/ha", "🧪")
        with col3:
            ghg_now = agri_country[(agri_country["Measure"] == "Total greenhouse gas emissions") & (agri_country["Year"] == latest_year)]["Value"].sum()
            ghg_prev = agri_country[(agri_country["Measure"] == "Total greenhouse gas emissions") & (agri_country["Year"] == previous_year)]["Value"].sum() if previous_year else None
            render_card("GHG Emissions", ghg_now, ghg_prev, "tonnes", "🌫️")

        col4, col5, col6 = st.columns(3)
        with col4:
            en_now = energy_country[(energy_country["Measure"] == "Direct on-farm energy consumption") & (energy_country["Year"] == latest_year)]["Value"].sum()
            en_prev = energy_country[(energy_country["Measure"] == "Direct on-farm energy consumption") & (energy_country["Year"] == previous_year)]["Value"].sum() if previous_year else None
            render_card("Energy Use", en_now, en_prev, "TOE", "⚡")
        with col5:
            water_now = agri_country[(agri_country["Measure"] == "Agriculture freshwater abstraction") & (agri_country["Year"] == latest_year)]["Value"].sum()
            water_prev = agri_country[(agri_country["Measure"] == "Agriculture freshwater abstraction") & (agri_country["Year"] == previous_year)]["Value"].sum() if previous_year else None
            render_card("Water Use", water_now, water_prev, "m³", "💧")
        with col6:
            arable_now = agri_country[(agri_country["Measure"] == "Arable land") & (agri_country["Year"] == latest_year)]["Value"].sum()
            arable_prev = agri_country[(agri_country["Measure"] == "Arable land") & (agri_country["Year"] == previous_year)]["Value"].sum() if previous_year else None
            render_card("Arable Land", arable_now, arable_prev, "ha", "🌾")

    # ---------------------------------------------------
    # 2. Environment Section
    # ---------------------------------------------------
    st.markdown("---")
    st.subheader("🧪 Nutrient Surplus Analysis")
    st.caption("Shows annual nutrient surplus (kg/ha) for selected nutrient type.")
    nutrient_options = agri_country["Nutrients"].dropna().unique()
    if nutrient_options.size > 0:
        selected_nutrient = st.selectbox("Select Nutrient", sorted(nutrient_options), key="nutrient_select")
        df_nutrient = agri_country[agri_country["Nutrients"] == selected_nutrient].groupby("Year")["Value"].mean().reset_index()
        fig_nutrient = px.line(df_nutrient, x="Year", y="Value", title=f"{selected_nutrient} Surplus Over Time",
                               labels={"Value": "kg/ha"}, markers=True)
        fig_nutrient.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(fig_nutrient, use_container_width=True)
    else:
        st.info("No nutrient data available.")

    # ---------------------------------------------------
    # 3. Emissions Section
    # ---------------------------------------------------
    st.markdown("---")
    st.subheader("🌫️ GHG Emissions Analysis")
    st.caption("Tracks greenhouse gas emissions from agriculture.")
    gas_options = agri_country["Measure"].dropna().unique()
    gas_choices = [g for g in gas_options if "emission" in g.lower()]
    if gas_choices:
        selected_gas = st.selectbox("Select Gas Type", sorted(gas_choices), key="gas_select")
        df_gas = agri_country[agri_country["Measure"] == selected_gas].groupby("Year")["Value"].sum().reset_index()
        fig_gas = px.line(df_gas, x="Year", y="Value", title=f"{selected_gas} Over Time",
                          labels={"Value": "Emissions (tonnes)"}, markers=True)
        fig_gas.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(fig_gas, use_container_width=True)
    else:
        st.info("No GHG emission data available.")

    # ---------------------------------------------------
    # 4. Energy Section
    # ---------------------------------------------------
    st.markdown("---")
    st.subheader("⚡ Energy Use Analysis")
    st.caption("Shows energy consumption over time in tonnes of oil equivalent.")
    energy_measures = energy_country["Measure"].dropna().unique()
    if energy_measures.size > 0:
        selected_energy = st.selectbox("Select Energy Measure", sorted(energy_measures), key="energy_select")
        df_energy = energy_country[energy_country["Measure"] == selected_energy].groupby("Year")["Value"].sum().reset_index()
        fig_energy = px.line(df_energy, x="Year", y="Value", title=f"{selected_energy} Over Time",
                             labels={"Value": "TOE"}, markers=True)
        fig_energy.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(fig_energy, use_container_width=True)
    else:
        st.info("No energy data available.")

    # ---------------------------------------------------
    # 5. Water Section
    # ---------------------------------------------------
    st.markdown("---")
    st.subheader("💧 Water Use Analysis")
    st.caption("Analyzes abstraction and irrigation metrics.")
    water_measures = agri_country["Measure"].dropna().unique()
    water_options = [m for m in water_measures if "water" in m.lower() or "irrigation" in m.lower()]
    if water_options:
        selected_water = st.selectbox("Select Water Measure", sorted(water_options), key="water_select")
        df_water = agri_country[agri_country["Measure"] == selected_water].groupby("Year")["Value"].sum().reset_index()
        fig_water = px.line(df_water, x="Year", y="Value", title=f"{selected_water} Over Time",
                            labels={"Value": "m³ / ha"}, markers=True)
        fig_water.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(fig_water, use_container_width=True)
    else:
        st.info("No water-related data available.")

    # ---------------------------------------------------
    # 6. Land Use Section
    # ---------------------------------------------------
    st.markdown("---")
    st.subheader("🌾 Land Use Analysis")
    st.caption("Tracks agricultural land use types over time.")
    land_options = agri_country[agri_country["Unit of measure"].str.contains("Hectares", na=False)]["Measure"].dropna().unique()
    if land_options.size > 0:
        selected_land = st.selectbox("Select Land Use Type", sorted(land_options), key="land_select")
        df_land = agri_country[agri_country["Measure"] == selected_land].groupby("Year")["Value"].sum().reset_index()
        fig_land = px.line(df_land, x="Year", y="Value", title=f"{selected_land} Over Time",
                           labels={"Value": "Hectares"}, markers=True)
        fig_land.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(fig_land, use_container_width=True)
    else:
        st.info("No land use data available.")

    # ---------------------------------------------------
    # Download Button
    # ---------------------------------------------------
    st.markdown("---")
    st.download_button(
        label="⬇️ Download This Country's Data as CSV",
        data=agri_country.to_csv(index=False),
        file_name=f"{selected_country}_report.csv",
        mime="text/csv"
    )
