import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from utils import create_time_series_chart, create_bar_chart, create_gauge_chart, format_number, get_color_from_value

def show_pollution_visualizations(df, preview_mode=False):
    """
    Display pollution data visualizations
    
    Args:
        df (pandas.DataFrame): Pollution data
        preview_mode (bool): If True, show a condensed preview
    """
    # Get the data in chronological order for time series
    chronological_df = df.sort_values('year')
    
    if preview_mode:
        # Abbreviated version for overview page
        col1, col2 = st.columns(2)
        
        with col1:
            # CO2 levels chart
            if 'co2_level' in df.columns:
                fig = create_time_series_chart(
                    chronological_df, 'year', 'co2_level',
                    'CO2 Concentration Trend',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("CO2 data not available")
        
        with col2:
            # Air quality or plastic pollution
            if 'global_air_quality_index' in df.columns:
                recent_df = chronological_df.tail(20)  # Last 20 years
                fig = create_time_series_chart(
                    recent_df, 'year', 'global_air_quality_index',
                    'Global Air Quality Index Trend',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            elif 'ocean_plastic_mil_tons' in df.columns:
                fig = create_time_series_chart(
                    chronological_df, 'year', 'ocean_plastic_mil_tons',
                    'Ocean Plastic Pollution Trend',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Air quality and plastic pollution data not available")
    
    else:
        # Full detailed view
        st.header("Greenhouse Gas Concentrations")
        
        # CO2 Levels visualization
        if 'co2_level' in df.columns:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Create CO2 trend chart
                fig = create_time_series_chart(
                    chronological_df, 'year', 'co2_level',
                    'Atmospheric CO2 Concentration',
                    height=400,
                    y_label='CO2 (parts per million)'
                )
                
                # Add reference lines for important thresholds
                fig.add_shape(
                    type="line",
                    x0=min(chronological_df['year']),
                    y0=350,
                    x1=max(chronological_df['year']),
                    y1=350,
                    line=dict(color="yellow", width=2, dash="dash"),
                )
                
                fig.add_shape(
                    type="line",
                    x0=min(chronological_df['year']),
                    y0=400,
                    x1=max(chronological_df['year']),
                    y1=400,
                    line=dict(color="orange", width=2, dash="dash"),
                )
                
                fig.add_shape(
                    type="line",
                    x0=min(chronological_df['year']),
                    y0=450,
                    x1=max(chronological_df['year']),
                    y1=450,
                    line=dict(color="red", width=2, dash="dash"),
                )
                
                # Add annotations for threshold lines
                fig.add_annotation(
                    x=min(chronological_df['year']) + 5,
                    y=350,
                    text="350 ppm - Climate Safety Level",
                    showarrow=False,
                    yshift=10,
                    font=dict(color="yellow")
                )
                
                fig.add_annotation(
                    x=min(chronological_df['year']) + 5,
                    y=400,
                    text="400 ppm - Significant Warming",
                    showarrow=False,
                    yshift=10,
                    font=dict(color="orange")
                )
                
                fig.add_annotation(
                    x=min(chronological_df['year']) + 5,
                    y=450,
                    text="450 ppm - Dangerous Warming",
                    showarrow=False,
                    yshift=10,
                    font=dict(color="red")
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("What does this mean?"):
                    st.markdown("""
                    **CO2 Concentration** measures the amount of carbon dioxide in the atmosphere in parts per million (ppm).
                    
                    - Pre-industrial levels were approximately 280 ppm
                    - 350 ppm is considered the safe upper limit for avoiding dangerous climate change
                    - We passed 400 ppm in 2016, a level not seen in millions of years
                    - Higher CO2 levels lead to increased global warming and ocean acidification
                    """)
            
            with col2:
                # Current status gauge
                latest_year = max(df['year'])
                latest_co2 = df[df['year'] == latest_year]['co2_level'].iloc[0]
                
                threshold_ranges = [
                    (280, 350, "green"),
                    (350, 400, "yellow"),
                    (400, 450, "orange"),
                    (450, 500, "red"),
                ]
                
                fig = create_gauge_chart(
                    latest_co2, 
                    f"Current CO2 Level ({latest_year})",
                    min_val=280,
                    max_val=500,
                    threshold_ranges=threshold_ranges
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # CO2 statistics
                yearly_increase = np.mean(np.diff(chronological_df['co2_level'].tail(10)))
                
                st.metric("Latest Reading", f"{latest_co2:.1f} ppm")
                st.metric("Annual Increase", f"{yearly_increase:.2f} ppm/year")
                st.metric("Pre-industrial Level", "280 ppm")
        
        else:
            st.warning("CO2 data not available")
        
        # Other greenhouse gases
        if 'methane_level' in df.columns and 'nitrous_oxide_level' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Methane trend
                fig = create_time_series_chart(
                    chronological_df, 'year', 'methane_level',
                    'Atmospheric Methane Concentration',
                    height=350,
                    y_label='CH4 (parts per billion)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Nitrous oxide trend
                fig = create_time_series_chart(
                    chronological_df, 'year', 'nitrous_oxide_level',
                    'Atmospheric Nitrous Oxide Concentration',
                    height=350,
                    y_label='N2O (parts per billion)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Methane (CH4)** and **Nitrous Oxide (N2O)** are powerful greenhouse gases.
                
                - Methane has ~28 times the warming power of CO2 over a 100-year period
                - Nitrous oxide has ~265 times the warming power of CO2 over a 100-year period
                - Major sources include agriculture, fossil fuel extraction, and waste management
                - These gases have shorter atmospheric lifetimes than CO2 but contribute significantly to warming
                """)
        
        # Air Pollution section
        st.header("Air Pollution")
        
        if 'pm25_level' in df.columns and 'ozone_level' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # PM2.5 trend
                fig = create_time_series_chart(
                    chronological_df, 'year', 'pm25_level',
                    'Global Average PM2.5 Levels',
                    height=350,
                    y_label='PM2.5 (μg/m³)'
                )
                
                # Add WHO guideline
                fig.add_shape(
                    type="line",
                    x0=min(chronological_df['year']),
                    y0=5,
                    x1=max(chronological_df['year']),
                    y1=5,
                    line=dict(color="green", width=2, dash="dash"),
                )
                
                fig.add_annotation(
                    x=max(chronological_df['year']),
                    y=5,
                    text="WHO guideline (5 μg/m³)",
                    showarrow=False,
                    yshift=10,
                    font=dict(color="green")
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Ozone trend
                fig = create_time_series_chart(
                    chronological_df, 'year', 'ozone_level',
                    'Ground-level Ozone Concentration',
                    height=350,
                    y_label='Ozone (ppb)'
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Global AQI if available
            if 'global_air_quality_index' in df.columns:
                # AQI visualization
                fig = create_time_series_chart(
                    chronological_df, 'year', 'global_air_quality_index',
                    'Global Air Quality Index Trend',
                    height=400,
                    y_label='Air Quality Index'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Add AQI explanation
                st.markdown("""
                **Air Quality Index (AQI) Values:**
                - 0-50: Good (Green) - Air quality is satisfactory
                - 51-100: Moderate (Yellow) - Acceptable air quality
                - 101-150: Unhealthy for Sensitive Groups (Orange)
                - 151-200: Unhealthy (Red) - Everyone may experience health effects
                - 201-300: Very Unhealthy (Purple) - Health alert
                - 301+: Hazardous (Maroon) - Health warning of emergency conditions
                """)
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Air Pollution** refers to harmful substances in the air we breathe.
                
                - PM2.5 refers to particulate matter smaller than 2.5 micrometers, which can penetrate deep into the lungs and bloodstream
                - Ground-level ozone forms when pollutants react with sunlight and can cause respiratory problems
                - Air pollution causes an estimated 7 million premature deaths annually worldwide
                - Sources include transportation, industry, power generation, and agricultural activities
                """)
            
            # Latest air quality statistics
            latest_year = max(df['year'])
            latest_data = df[df['year'] == latest_year]
            
            if not latest_data.empty:
                latest_pm25 = latest_data['pm25_level'].iloc[0]
                latest_ozone = latest_data['ozone_level'].iloc[0]
                
                # Display information on health impacts
                if latest_pm25 > 35:
                    st.error(f"⚠️ Current global average PM2.5 level ({latest_pm25:.1f} μg/m³) is at a level that poses significant health risks, including respiratory and cardiovascular diseases.")
                elif latest_pm25 > 12:
                    st.warning(f"⚠️ Current global average PM2.5 level ({latest_pm25:.1f} μg/m³) exceeds the WHO annual guideline and may cause health issues with prolonged exposure.")
                else:
                    st.success(f"✅ Current global average PM2.5 level ({latest_pm25:.1f} μg/m³) is within acceptable ranges, though local levels may be much higher in urban and industrial areas.")
        
        else:
            st.warning("Air pollution data not available")
        
        # Ocean & Plastic Pollution section
        st.header("Ocean & Plastic Pollution")
        
        if 'ocean_plastic_mil_tons' in df.columns:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Ocean plastic trend
                fig = create_time_series_chart(
                    chronological_df, 'year', 'ocean_plastic_mil_tons',
                    'Cumulative Ocean Plastic Pollution',
                    height=400,
                    y_label='Million Metric Tons'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("What does this mean?"):
                    st.markdown("""
                    **Ocean Plastic Pollution** measures the cumulative amount of plastic waste in the world's oceans.
                    
                    - Plastic waste can persist in the environment for hundreds of years
                    - It breaks down into microplastics that enter food chains
                    - Marine wildlife is harmed through entanglement and ingestion
                    - Major sources include improper waste disposal, fishing gear, and microbeads from consumer products
                    """)
            
            with col2:
                # Current status and projections
                if len(chronological_df) >= 5:
                    # Calculate exponential growth rate from recent years
                    recent_df = chronological_df.tail(5)
                    recent_plastics = recent_df['ocean_plastic_mil_tons'].values
                    years_diff = recent_df['year'].iloc[-1] - recent_df['year'].iloc[0]
                    
                    if recent_plastics[0] > 0 and years_diff > 0:
                        growth_rate = (recent_plastics[-1] / recent_plastics[0]) ** (1 / years_diff) - 1
                        
                        # Project to 2050
                        latest_year = max(df['year'])
                        latest_value = df[df['year'] == latest_year]['ocean_plastic_mil_tons'].iloc[0]
                        years_to_2050 = 2050 - latest_year
                        projected_2050 = latest_value * (1 + growth_rate) ** years_to_2050
                        
                        st.metric("Current Ocean Plastic", f"{latest_value:.1f} million tons")
                        st.metric("Projected by 2050", f"{projected_2050:.1f} million tons")
                        
                        # Display warning
                        st.warning(f"⚠️ At current rates, there could be more plastic than fish in the oceans by weight by 2050.")
                    
                    # Microplastic trend if available
                    if 'microplastic_concentration' in df.columns:
                        latest_microplastic = df[df['year'] == latest_year]['microplastic_concentration'].iloc[0]
                        st.metric("Microplastic Concentration", f"{latest_microplastic:.1f} particles/m³")
            
            # Microplastic visualization
            if 'microplastic_concentration' in df.columns:
                fig = create_time_series_chart(
                    chronological_df, 'year', 'microplastic_concentration',
                    'Microplastic Concentration in Marine Environments',
                    height=400,
                    y_label='Particles per cubic meter'
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("""
                **Microplastics** are tiny plastic particles less than 5mm in size that result from the breakdown of larger plastics or are manufactured at that size.
                
                - Microplastics have been found in the deepest ocean trenches and highest mountain peaks
                - They have been detected in human blood, placenta, and lungs
                - Health effects on humans are still being studied, but they can carry harmful chemicals and pathogens
                """)
        
        # Chemical Pollution section
        if 'chemical_pollution_index' in df.columns:
            st.header("Chemical Pollution")
            
            fig = create_time_series_chart(
                chronological_df, 'year', 'chemical_pollution_index',
                'Global Chemical Pollution Index',
                height=400,
                y_label='Pollution Index (0-100)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Chemical Pollution** refers to the contamination of the environment with harmful chemical substances.
                
                - The chemical pollution index is a composite measure of soil, water, and air chemical contaminants
                - Higher values (closer to 100) indicate worse pollution levels
                - Chemical pollutants include pesticides, industrial chemicals, pharmaceuticals, and heavy metals
                - Many chemical pollutants are persistent and can bioaccumulate in living organisms
                """)
            
            # Chemical pollution status
            latest_year = max(df['year'])
            latest_chemical = df[df['year'] == latest_year]['chemical_pollution_index'].iloc[0]
            
            # Chemical pollution classification
            if latest_chemical > 75:
                st.error(f"⚠️ Current chemical pollution index ({latest_chemical:.1f}/100) indicates severe contamination of global environments with harmful chemicals.")
            elif latest_chemical > 50:
                st.warning(f"⚠️ Current chemical pollution index ({latest_chemical:.1f}/100) indicates significant contamination of global environments with harmful chemicals.")
            elif latest_chemical > 25:
                st.info(f"ℹ️ Current chemical pollution index ({latest_chemical:.1f}/100) indicates moderate contamination of global environments with harmful chemicals.")
            else:
                st.success(f"✅ Current chemical pollution index ({latest_chemical:.1f}/100) indicates relatively low contamination of global environments with harmful chemicals.")
        
        else:
            st.warning("Chemical pollution data not available")