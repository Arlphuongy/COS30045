import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from utils.db import load_table

def section_environment():
    st.header("🌱 Environmental Impact: Nutrient Surpluses")

    # Load data
    agri = load_table("agri")
    area = load_table("area")

    st.markdown("""
    Excess **Nitrogen (N)** and **Phosphorus (P)** from agriculture can lead to water pollution, soil degradation, and greenhouse gas emissions.  
    This section evaluates nutrient surpluses by country since 2012 to assess environmental sustainability.
    """)

    # ------------------------
    # Nutrient Selection
    # ------------------------
    nutrient_options = agri['Nutrients'].dropna().unique()
    nutrient = st.selectbox("🔬 Select Nutrient", nutrient_options)
    agri_filtered = agri[(agri['Nutrients'] == nutrient) & (agri['Year'] >= 2012)]

    # ------------------------
    # Global Trend
    # ------------------------
    st.subheader(f"📈 {nutrient} Surplus Over Time (Global Average)")
    st.markdown(f"Average {nutrient} surplus across all countries since 2012.")
    df_yearly = agri_filtered.groupby('Year')['Value'].mean().reset_index()
    fig_trend = px.line(df_yearly, x='Year', y='Value', markers=True,
                        labels={"Value": f"{nutrient} Surplus (kg/ha)"})
    st.plotly_chart(fig_trend)

    # ------------------------
    # Country Drill-down
    # ------------------------
    with st.expander("🔎 Country-level Trend"):
        country_list = agri_filtered["Reference area"].dropna().unique()
        selected_country = st.selectbox("🌐 Select a Country", sorted(country_list))
        df_country = agri_filtered[agri_filtered["Reference area"] == selected_country]
        df_country_yearly = df_country.groupby("Year")["Value"].mean().reset_index()

        fig_country = px.line(
            df_country_yearly, x="Year", y="Value", markers=True,
            title=f"{nutrient} Surplus Over Time: {selected_country}",
            labels={"Value": f"{nutrient} Surplus (kg/ha)"}
        )
        st.plotly_chart(fig_country)

    # ------------------------
    # Heatmap by Country-Year
    # ------------------------
    st.subheader(f"🌡️ {nutrient} Surplus by Country and Year")
    st.markdown("Heatmap showing intensity of nutrient surplus across countries over time.")
    df_heatmap = agri_filtered.pivot_table(index="Reference area", columns="Year", values="Value")
    st.dataframe(df_heatmap.style.background_gradient(cmap="YlGnBu", axis=1))

    # ------------------------
    # Top Countries (Raw)
    # ------------------------
    st.subheader(f"🏆 Top 10 {nutrient} Surplus Countries (Raw Average)")
    st.markdown("Shows countries with highest average nutrient surplus since 2012 (not normalized).")
    df_top = agri_filtered.groupby('Reference area')['Value'].mean().nlargest(10).reset_index()
    fig_top = px.bar(df_top, x='Reference area', y='Value', color='Value',
                     labels={'Value': f'{nutrient} Surplus (kg/ha)'},
                     color_continuous_scale='viridis')
    st.plotly_chart(fig_top)

    # ------------------------
    # Histogram (Distribution)
    # ------------------------
    with st.expander("📊 Distribution of Surplus Values"):
        st.markdown("Distribution of raw surplus values (check for skew or outliers).")
        fig_hist = px.histogram(agri_filtered, x='Value', nbins=50,
                                labels={'Value': f'{nutrient} Surplus (kg/ha)'})
        st.plotly_chart(fig_hist)

    # ------------------------
    # Choropleth
    # ------------------------
    st.subheader("🗺️ Choropleth Map: Nutrient Surplus by Country")
    selected_year = st.selectbox("📅 Select Year", sorted(agri_filtered['Year'].unique(), reverse=True))
    df_map = agri_filtered[agri_filtered['Year'] == selected_year].groupby('Reference area')['Value'].mean().reset_index()
    fig_map = px.choropleth(df_map, locations="Reference area", locationmode="country names",
                            color="Value", hover_name="Reference area",
                            color_continuous_scale="YlOrRd",
                            labels={'Value': f'{nutrient} Surplus (kg/ha)'})
    st.plotly_chart(fig_map)

    # ------------------------
    # N vs P Comparison
    # ------------------------
    st.subheader("🔬 Nitrogen vs Phosphorus Comparison")
    st.markdown("Explore nutrient imbalance by comparing average N vs P surplus per country.")
    df_compare = agri[agri['Nutrients'].isin(['Nitrogen', 'Phosphorus']) & (agri['Year'] >= 2012)]
    df_pivot = df_compare.groupby(['Reference area', 'Nutrients'])['Value'].mean().unstack().dropna()

    fig_scatter = px.scatter(df_pivot, x='Nitrogen', y='Phosphorus', hover_name=df_pivot.index,
                             color_discrete_sequence=['green'],
                             labels={'Nitrogen': 'Avg Nitrogen Surplus', 'Phosphorus': 'Avg Phosphorus Surplus'},
                             title="Country-level Comparison: N vs P")
    st.plotly_chart(fig_scatter)
    st.markdown("""
    - 🟢 **Top-right quadrant**: High N and P → environmental risk.  
    - ⚠️ **Off-diagonal**: Imbalance in fertilizer application.
    """)

    # ------------------------
    # Normalize by Arable Land
    # ------------------------
    st.subheader("📐 Normalized Nutrient Surplus per Hectare")
    st.markdown("""
    Surplus values divided by arable land area (from land-use dataset) to allow meaningful cross-country comparisons.
    """)

    area_filtered = area[area['Measure'].str.lower().str.contains("arable", na=False)]
    df_norm = pd.merge(agri_filtered, area_filtered,
                       on=["Reference area", "Year"], suffixes=("_surplus", "_area"))
    df_norm['Surplus per hectare'] = df_norm['Value_surplus'] / df_norm['Value_area']

    # --- Top countries by normalized surplus
    st.markdown("#### 🏆 Top 10 Countries by Normalized Surplus")
    df_norm_top = df_norm.groupby("Reference area")["Surplus per hectare"].mean().nlargest(10).reset_index()
    fig_norm = px.bar(df_norm_top, x="Reference area", y="Surplus per hectare",
                      color="Surplus per hectare", color_continuous_scale="viridis",
                      labels={"Surplus per hectare": f"Normalized {nutrient} Surplus (kg/ha)"},
                      title=f"Top 10 Countries by Normalized {nutrient} Surplus")
    st.plotly_chart(fig_norm)

    # --- Outliers
    st.markdown("#### 📌 Outlier Countries (Top 5%)")
    df_country_avg = df_norm.groupby("Reference area")["Surplus per hectare"].mean().reset_index()
    threshold = np.percentile(df_country_avg["Surplus per hectare"].dropna(), 95)
    outlier_avg = df_country_avg[df_country_avg["Surplus per hectare"] >= threshold].sort_values(
        "Surplus per hectare", ascending=False)
    st.dataframe(outlier_avg.reset_index(drop=True))
    st.caption("Countries with exceptionally high normalized surplus per hectare.")

    # --- Download CSV
    st.markdown("#### 📥 Download Normalized Dataset")
    csv = df_norm.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Normalized Surplus Data as CSV",
        data=csv,
        file_name=f"normalized_{nutrient.lower()}_surplus.csv",
        mime='text/csv'
    )