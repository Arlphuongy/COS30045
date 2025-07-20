import streamlit as st
import pandas as pd
from utils.db import load_table

def section_intro():
    st.title("🌍 OECD Agricultural Sustainability Dashboard")
    st.markdown("""Created by Anh Khoa Nguyen - Arlene Phuong Brown - Thien Thao Vy Tran""")
    # --- Project Overview ---
    st.markdown("""
    ### 🧭 Project Overview

    Agriculture remains central to economic development and food security across the globe. However, it also places immense pressure on natural resources — land, water, and energy — and requires balanced economic support for producers.

    This dashboard provides a multi-faceted exploration of agricultural sustainability indicators across **OECD countries**, focusing on:

    - 🌾 **Farming practices and land use**
    - 💧 **Water consumption and irrigation**
    - ⚡ **Energy usage in agriculture**
    - 💰 **Producer protection and environmental impacts**

    Data spans from **2012 onwards**, sourced and cleaned from the [OECD Data Explorer](https://data-explorer.oecd.org/).
    """)

    # --- Load datasets ---
    agri = load_table("agri")
    area = load_table("area")
    water = load_table("water")
    energy = load_table("energy")

    # --- Section: Agri ---
    st.markdown("### 🌍 Agricultural Production & Environmental Impact")
    st.markdown("""
    This dataset covers **nutrient balances** (nitrogen and phosphorus surpluses), and **economic indicators** like producer protection.  
    It helps analyze the environmental cost and economic support behind agricultural activities.
    """)
    with st.expander("🔍 Preview dataset"):
        st.dataframe(agri)

    # --- Section: Area ---
    st.markdown("### 🗺️ Agricultural Land Use")
    st.markdown("""
    Provides yearly data on **land area** used for different agricultural purposes like:
    - Arable land
    - Pasture land
    - Transgenic crop area  
    Useful for evaluating spatial land-use patterns.
    """)
    with st.expander("🔍 Preview dataset"):
        st.dataframe(area)

    # --- Section: Water ---
    st.markdown("### 💧 Water Resource Use in Agriculture")
    st.markdown("""
    This dataset includes information on:
    - Total freshwater withdrawal for agricultural purposes
    - Area equipped for irrigation  
    It supports evaluation of agricultural water dependency and efficiency.
    """)
    with st.expander("🔍 Preview dataset"):
        st.dataframe(water)

    # --- Section: Energy ---
    st.markdown("### ⚡ Energy Consumption in Agriculture")
    st.markdown("""
    Presents energy usage trends in agriculture, both total and on-farm.  
    Critical for understanding emissions and sustainability of farming practices.
    """)
    with st.expander("🔍 Preview dataset"):
        st.dataframe(energy)

    st.success("📌 Use the sidebar to explore in-depth visualizations for each topic.")