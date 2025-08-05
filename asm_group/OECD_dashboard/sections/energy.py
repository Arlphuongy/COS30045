import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from utils.db import load_table

def section_energy():
    st.header("⚡ Energy Use: Global Consumption & Agricultural Patterns")

    # Load data
    energy = load_table("energy")  # Assuming your energy data is loaded this way
    
    st.markdown("""
    Energy consumption patterns reveal economic development, industrialization trends, and agricultural efficiency.  
    This section analyzes **Total Final Energy Consumption** and **Direct On-Farm Energy Consumption** across countries from 1985-2021.
    """)

    # Data preprocessing
    energy_filtered = energy[energy['Year'] >= 1985].copy()
    
    # ------------------------
    # Energy Measure Selection
    # ------------------------
    measure_options = energy_filtered['Measure'].dropna().unique()
    selected_measure = st.selectbox("🔬 Select Energy Measure", measure_options)
    energy_subset = energy_filtered[energy_filtered['Measure'] == selected_measure]

    # ------------------------
    # Global Energy Trends
    # ------------------------
    st.subheader(f"📈 Global {selected_measure} Trends")
    st.markdown(f"Worldwide trends in {selected_measure.lower()} from 1985-2021.")
    
    # Global yearly average
    df_global = energy_subset.groupby('Year')['Value'].sum().reset_index()
    df_global['Value_Billions'] = df_global['Value'] / 1000000  # Convert to millions of tonnes oil equivalent
    
    fig_global = px.line(df_global, x='Year', y='Value_Billions', markers=True,
                        title=f"Global {selected_measure} Over Time",
                        labels={"Value_Billions": "Energy Consumption (Million Tonnes Oil Equivalent)"})
    fig_global.update_layout(height=500)
    st.plotly_chart(fig_global, use_container_width=True)

    # ------------------------
    # Top Energy Consumers
    # ------------------------
    st.subheader("🏆 Top Energy Consuming Countries")
    
    # Year selector for top consumers
    available_years = sorted(energy_subset['Year'].unique(), reverse=True)
    selected_year = st.selectbox("📅 Select Year for Ranking", available_years)
    
    # Top 15 countries for selected year
    df_top = energy_subset[energy_subset['Year'] == selected_year].nlargest(15, 'Value').reset_index(drop=True)
    df_top['Value_Millions'] = df_top['Value'] / 1000  # Convert to millions
    
    fig_top = px.bar(df_top, x='Value_Millions', y='Reference area', 
                     orientation='h', color='Value_Millions',
                     title=f"Top 15 Countries - {selected_measure} ({selected_year})",
                     labels={'Value_Millions': 'Energy Consumption (Million Tonnes Oil Equivalent)',
                            'Reference area': 'Country'},
                     color_continuous_scale='viridis')
    fig_top.update_layout(height=600, yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_top, use_container_width=True)

    # ------------------------
    # Country Growth Analysis
    # ------------------------
    st.subheader("📊 Energy Growth Patterns")
    
    # Calculate growth rates for countries with sufficient data
    growth_data = []
    countries = energy_subset['Reference area'].unique()
    
    for country in countries:
        country_data = energy_subset[energy_subset['Reference area'] == country].sort_values('Year')
        if len(country_data) >= 10:  # At least 10 years of data
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
        # Growth rate visualization
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

    # ------------------------
    # Country-Specific Analysis
    # ------------------------
    with st.expander("🔎 Individual Country Deep Dive"):
        country_list = sorted(energy_subset["Reference area"].dropna().unique())
        selected_country = st.selectbox("🌐 Select a Country for Detailed Analysis", country_list)
        
        df_country = energy_subset[energy_subset["Reference area"] == selected_country].sort_values('Year')
        
        if not df_country.empty:
            # Country timeline
            fig_country = px.line(df_country, x="Year", y="Value", markers=True,
                                 title=f"{selected_measure}: {selected_country} (1985-2021)",
                                 labels={"Value": "Energy Consumption (Thousand Tonnes Oil Equivalent)"})
            fig_country.update_layout(height=400)
            st.plotly_chart(fig_country, use_container_width=True)
            
            # Country statistics
            if len(df_country) >= 2:
                first_val = df_country.iloc[0]['Value']
                last_val = df_country.iloc[-1]['Value']
                peak_val = df_country['Value'].max()
                peak_year = df_country[df_country['Value'] == peak_val]['Year'].iloc[0]
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Current Level", f"{last_val:,.0f}")
                with col2:
                    change = last_val - first_val
                    st.metric("Total Change", f"{change:,.0f}", f"{((change/first_val)*100):+.1f}%")
                with col3:
                    st.metric("Peak Consumption", f"{peak_val:,.0f}")
                with col4:
                    st.metric("Peak Year", f"{peak_year}")

    # ------------------------
    # Agricultural Energy Efficiency (if applicable)
    # ------------------------
    if "Direct on-farm energy consumption" in energy_filtered['Measure'].values and "Total final energy consumption" in energy_filtered['Measure'].values:
        st.subheader("🌾 Agricultural Energy Efficiency Analysis")
        st.markdown("Comparing agricultural energy use as a percentage of total energy consumption.")
        
        # Get both measures for comparison
        farm_energy = energy_filtered[energy_filtered['Measure'] == "Direct on-farm energy consumption"]
        total_energy = energy_filtered[energy_filtered['Measure'] == "Total final energy consumption"]
        
        # Calculate efficiency for latest available year
        latest_year = max(farm_energy['Year'].max(), total_energy['Year'].max())
        
        farm_latest = farm_energy[farm_energy['Year'] == latest_year]
        total_latest = total_energy[total_energy['Year'] == latest_year]
        
        # Merge and calculate percentages
        efficiency_df = pd.merge(farm_latest[['Reference area', 'Value']], 
                               total_latest[['Reference area', 'Value']], 
                               on='Reference area', suffixes=('_farm', '_total'))
        efficiency_df['Efficiency_Ratio'] = (efficiency_df['Value_farm'] / efficiency_df['Value_total']) * 100
        efficiency_df = efficiency_df[efficiency_df['Value_total'] > 1000].sort_values('Efficiency_Ratio')  # Filter small countries
        
        if not efficiency_df.empty:
            # Most and least efficient
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🎯 Most Efficient (Lowest Agricultural %)")
                most_efficient = efficiency_df.head(10)
                fig_eff = px.bar(most_efficient, x='Efficiency_Ratio', y='Reference area',
                               orientation='h', color='Efficiency_Ratio',
                               color_continuous_scale='Greens',
                               labels={'Efficiency_Ratio': 'Agricultural Energy as % of Total'})
                fig_eff.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_eff, use_container_width=True)
            
            with col2:
                st.markdown("#### 🚜 Highest Agricultural Intensity")
                least_efficient = efficiency_df.tail(10)
                fig_intensive = px.bar(least_efficient, x='Efficiency_Ratio', y='Reference area',
                                     orientation='h', color='Efficiency_Ratio',
                                     color_continuous_scale='Oranges',
                                     labels={'Efficiency_Ratio': 'Agricultural Energy as % of Total'})
                fig_intensive.update_layout(height=400, yaxis={'categoryorder':'total ascending'})
                st.plotly_chart(fig_intensive, use_container_width=True)

    # ------------------------
    # Interactive World Map
    # ------------------------
    st.subheader("🗺️ Global Energy Consumption Map")
    map_year = st.selectbox("📅 Select Year for Map", available_years, key="map_year")
    
    df_map = energy_subset[energy_subset['Year'] == map_year].copy()
    df_map['Value_Log'] = np.log10(df_map['Value'] + 1)  # Log scale for better visualization
    
    fig_map = px.choropleth(df_map, 
                           locations="Reference area", 
                           locationmode="country names",
                           color="Value_Log", 
                           hover_name="Reference area",
                           hover_data={'Value': ':,.0f', 'Value_Log': False},
                           color_continuous_scale="Viridis",
                           labels={'Value_Log': 'Log10(Energy Consumption)', 'Value': 'Energy Consumption'})
    fig_map.update_layout(height=500)
    st.plotly_chart(fig_map, use_container_width=True)

    # ------------------------
    # Statistical Summary
    # ------------------------
    with st.expander("📊 Statistical Summary"):
        st.markdown("### Dataset Statistics")
        
        # Basic stats
        latest_data = energy_subset[energy_subset['Year'] == energy_subset['Year'].max()]
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Countries Tracked", len(energy_subset['Reference area'].unique()))
        with col2:
            st.metric("Years Covered", f"{energy_subset['Year'].min()}-{energy_subset['Year'].max()}")
        with col3:
            st.metric("Total Data Points", len(energy_subset))
        
        # Distribution analysis
        st.markdown("#### Value Distribution")
        fig_hist = px.histogram(latest_data, x='Value', nbins=30,
                               labels={'Value': f'{selected_measure} (Thousand Tonnes Oil Equivalent)'},
                               title=f"Distribution of {selected_measure} Values ({latest_data['Year'].iloc[0]})")
        st.plotly_chart(fig_hist, use_container_width=True)

    # ------------------------
    # Download Options
    # ------------------------
    st.markdown("#### 📥 Download Data")
    csv_data = energy_subset.to_csv(index=False)
    st.download_button(
        label="⬇️ Download Energy Data as CSV",
        data=csv_data,
        file_name=f"energy_consumption_{selected_measure.lower().replace(' ', '_')}.csv",
        mime='text/csv'
    )