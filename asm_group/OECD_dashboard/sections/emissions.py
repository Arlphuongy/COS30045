import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from utils.db import load_table

def section_emissions():
    st.header("🌍 Emissions & Chemical Use in Agriculture")

    agri = load_table("agri")

    st.markdown("""
    Agriculture contributes significantly to **greenhouse gas (GHG) emissions**, **ammonia (NH₃)** release, and **pesticide usage**.  
    This section explores these environmental pressures using OECD data to support evidence-based sustainability assessments.
    """)

    # ------------------------
    # 1. GHG Emissions Over Time
    # ------------------------
    st.subheader("🔥 Greenhouse Gas (GHG) Emissions Over Time")
    st.markdown("""
    Tracks total GHG emissions (CO₂, CH₄, N₂O) from agriculture.  
    High emissions are linked to intensive farming, livestock, and fertilizer use.
    """)

    ghg_keywords = ['Total greenhouse gas emissions', 'Methane', 'Nitrous oxide', 'Carbone dioxide']
    df_ghg = agri[
        agri['Measure'].str.contains('|'.join(ghg_keywords), case=False, na=False) &
        (agri['Unit of measure'].str.contains("Tonnes", na=False))
    ]

    if df_ghg.empty:
        st.warning("No GHG emission data found in this dataset.")
    else:
        gases = df_ghg['Measure'].dropna().unique()
        selected_gas = st.selectbox("🌫️ Select Greenhouse Gas", sorted(gases))

        df_gas = df_ghg[df_ghg['Measure'] == selected_gas]
        df_gas_avg = df_gas.groupby("Year")["Value"].sum().reset_index()

        fig_ghg = px.line(
            df_gas_avg, x="Year", y="Value", markers=True,
            title=f"{selected_gas} from Agriculture (Total across countries)",
            labels={"Value": "Emissions (tonnes)"}
        )
        st.plotly_chart(fig_ghg)

        with st.expander("🔍 View by Country"):
            country_list_ghg = sorted(df_gas["Reference area"].dropna().unique())
            selected_country_ghg = st.selectbox("Select Country", country_list_ghg, key="ghg-country")
            df_gas_country = df_gas[df_gas["Reference area"] == selected_country_ghg]
            df_gas_country_yearly = df_gas_country.groupby("Year")["Value"].sum().reset_index()

            fig_country = px.line(df_gas_country_yearly, x="Year", y="Value", markers=True,
                                  title=f"{selected_gas} Emissions: {selected_country_ghg}",
                                  labels={"Value": "Emissions (tonnes)"})
            st.plotly_chart(fig_country)

    # ------------------------
    # 2. Country Comparison
    # ------------------------
    st.subheader("🌐 GHG Emissions by Country")
    st.markdown("Average GHG emissions from agriculture per country since 2012.")

    df_ghg_recent = df_ghg[df_ghg["Year"] >= 2012]
    df_country_ghg = (
        df_ghg_recent.groupby(["Reference area", "Measure"])["Value"]
        .mean()
        .reset_index()
    )

    selected_gas_bar = st.selectbox("📦 Select Gas for Comparison", sorted(df_country_ghg["Measure"].unique()))

    df_bar = df_country_ghg[df_country_ghg["Measure"] == selected_gas_bar].sort_values("Value", ascending=False).head(15)

    fig_bar = px.bar(
        df_bar,
        x="Reference area",
        y="Value",
        labels={"Value": f"{selected_gas_bar} Emissions (tonnes)", "Reference area": "Country"},
        color="Value",
        color_continuous_scale="Reds",
        title=f"Top 15 Countries: {selected_gas_bar} Emissions"
    )
    st.plotly_chart(fig_bar)

    # ------------------------
    # 3. Ammonia Emissions
    # ------------------------
    st.subheader("💨 Ammonia (NH₃) Emissions from Agriculture")
    st.markdown("Ammonia emissions contribute to air pollution and eutrophication. Major sources: livestock manure & fertilizer volatilization.")

    df_nh3 = agri[
        agri["Measure"].str.contains("Ammonia", case=False, na=False) &
        (agri["Unit of measure"].str.contains("Tonnes", na=False)) &
        (agri["Year"] >= 2012)
    ]

    if df_nh3.empty:
        st.warning("No Ammonia emission data found.")
    else:
        df_nh3_country = df_nh3.groupby("Reference area")["Value"].mean().nlargest(10).reset_index()
        fig_nh3 = px.bar(
            df_nh3_country,
            x="Reference area",
            y="Value",
            color="Value",
            color_continuous_scale="Plasma",
            labels={"Value": "Average NH₃ Emissions (tonnes)", "Reference area": "Country"},
            title="Top 10 NH₃ Emitting Countries (since 2012)"
        )
        st.plotly_chart(fig_nh3)

        with st.expander("🔍 View by Country"):
            country_list_nh3 = sorted(df_nh3["Reference area"].dropna().unique())
            selected_country_nh3 = st.selectbox("Select Country", country_list_nh3, key="nh3-country")
            df_nh3_country_detail = df_nh3[df_nh3["Reference area"] == selected_country_nh3]
            df_nh3_yearly = df_nh3_country_detail.groupby("Year")["Value"].sum().reset_index()
            fig_nh3_country = px.line(df_nh3_yearly, x="Year", y="Value", markers=True,
                                       labels={"Value": "NH₃ Emissions (tonnes)"},
                                       title=f"{selected_country_nh3}: NH₃ Emissions Over Time")
            st.plotly_chart(fig_nh3_country)

    # ------------------------
    # 4. Pesticide Usage
    # ------------------------
    st.subheader("🧪 Agricultural Pesticide Usage")
    st.markdown("Pesticides impact biodiversity and human health. Tracking their sales helps monitor chemical input intensity.")

    pest_keywords = ['Sales of insecticides', 'Sales of fungicides', 'Sales of herbicides', 'Total sales of agricultural pesticides']
    df_pest = agri[
        agri['Measure'].isin(pest_keywords) &
        (agri['Unit of measure'].str.contains("Tonnes", na=False)) &
        (agri["Year"] >= 2012)
    ]

    if df_pest.empty:
        st.warning("No pesticide sales data found.")
    else:
        selected_pesticide = st.selectbox("🧴 Select Pesticide Type", sorted(df_pest["Measure"].unique()))
        df_pest_type = df_pest[df_pest["Measure"] == selected_pesticide]
        df_pest_avg = df_pest_type.groupby("Reference area")["Value"].mean().nlargest(10).reset_index()

        fig_pest = px.bar(
            df_pest_avg,
            x="Reference area",
            y="Value",
            color="Value",
            color_continuous_scale="Oranges",
            labels={"Value": "Avg Sales (tonnes)", "Reference area": "Country"},
            title=f"Top 10 Countries by {selected_pesticide}"
        )
        st.plotly_chart(fig_pest)

        with st.expander("🔍 View by Country"):
            country_list_pest = sorted(df_pest_type["Reference area"].dropna().unique())
            selected_country_pest = st.selectbox("Select Country", country_list_pest, key="pest-country")
            df_pest_country = df_pest_type[df_pest_type["Reference area"] == selected_country_pest]
            df_pest_yearly = df_pest_country.groupby("Year")["Value"].sum().reset_index()
            fig_pest_country = px.line(df_pest_yearly, x="Year", y="Value", markers=True,
                                       labels={"Value": f"{selected_pesticide} (tonnes)"},
                                       title=f"{selected_country_pest}: {selected_pesticide} Usage Over Time")
            st.plotly_chart(fig_pest_country)

    # ------------------------
    # 5. Insight
    # ------------------------
    st.markdown("---")
    st.markdown("""
    ### 🧠 Insights
    - Countries with high **GHG + NH₃ emissions** likely have large livestock sectors and fertilizer-intensive practices.
    - **Pesticide sales** trends can highlight regulatory gaps or overuse.
    - Emission intensity could be further normalized by land use in **Advanced Analysis**.
    """)
