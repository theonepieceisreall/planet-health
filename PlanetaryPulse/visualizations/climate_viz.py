import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from utils import create_time_series_chart, create_bar_chart, create_gauge_chart, format_number, get_color_from_value

def show_climate_visualizations(df, preview_mode=False):
    """
    Display climate data visualizations
    
    Args:
        df (pandas.DataFrame): Climate data
        preview_mode (bool): If True, show a condensed preview
    """
    # Get the data in chronological order for time series
    chronological_df = df.sort_values('year')
    
    if preview_mode:
        # Abbreviated version for overview page
        col1, col2 = st.columns(2)
        
        with col1:
            # Temperature anomaly chart
            if 'temperature_anomaly' in df.columns:
                fig = create_time_series_chart(
                    chronological_df, 'year', 'temperature_anomaly',
                    'Global Temperature Anomaly Trend',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Temperature anomaly data not available")
        
        with col2:
            # Sea ice extent chart
            if 'arctic_ice_extent_mil_sq_km' in df.columns:
                fig = create_time_series_chart(
                    chronological_df, 'year', 'arctic_ice_extent_mil_sq_km',
                    'Arctic Sea Ice Extent Trend',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Sea ice data not available")
    
    else:
        # Full detailed view
        st.header("Temperature Trends")
        
        # Temperature anomaly visualization
        if 'temperature_anomaly' in df.columns:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Create temperature anomaly chart
                fig = create_time_series_chart(
                    chronological_df, 'year', 'temperature_anomaly',
                    'Global Temperature Anomaly (°C)',
                    height=400,
                    y_label='Temperature Anomaly (°C)'
                )
                
                # Add reference lines for Paris Agreement targets
                fig.add_shape(
                    type="line",
                    x0=min(chronological_df['year']),
                    y0=1.5,
                    x1=max(chronological_df['year']),
                    y1=1.5,
                    line=dict(color="orange", width=2, dash="dash"),
                    name="1.5°C Target"
                )
                
                fig.add_shape(
                    type="line",
                    x0=min(chronological_df['year']),
                    y0=2.0,
                    x1=max(chronological_df['year']),
                    y1=2.0,
                    line=dict(color="red", width=2, dash="dash"),
                    name="2.0°C Limit"
                )
                
                # Add annotations for target lines
                fig.add_annotation(
                    x=max(chronological_df['year']),
                    y=1.5,
                    text="1.5°C Target",
                    showarrow=False,
                    yshift=10,
                    font=dict(color="orange")
                )
                
                fig.add_annotation(
                    x=max(chronological_df['year']),
                    y=2.0,
                    text="2.0°C Limit",
                    showarrow=False,
                    yshift=10,
                    font=dict(color="red")
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("What does this mean?"):
                    st.markdown("""
                    **Temperature Anomaly** shows how much warmer or cooler the Earth is compared to a baseline period (1951-1980).
                    
                    - The trend demonstrates the pace of global warming
                    - The 1.5°C and 2.0°C lines represent the Paris Agreement targets to limit warming
                    - Crossing these thresholds risks severe climate impacts
                    """)
            
            with col2:
                # Current status gauge
                latest_year = max(df['year'])
                latest_temp = df[df['year'] == latest_year]['temperature_anomaly'].iloc[0]
                
                threshold_ranges = [
                    (0, 1.0, "green"),
                    (1.0, 1.5, "yellow"),
                    (1.5, 3.0, "red"),
                ]
                
                fig = create_gauge_chart(
                    latest_temp, 
                    f"Current Anomaly ({latest_year})",
                    min_val=0,
                    max_val=3.0,
                    threshold_ranges=threshold_ranges
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Temperature statistics
                avg_temp = np.mean(df['temperature_anomaly'])
                max_temp = np.max(df['temperature_anomaly'])
                min_temp = np.min(df['temperature_anomaly'])
                
                st.metric("Average Anomaly", f"{avg_temp:.2f}°C")
                st.metric("Maximum Anomaly", f"{max_temp:.2f}°C")
                st.metric("Minimum Anomaly", f"{min_temp:.2f}°C")
        
        else:
            st.warning("Temperature anomaly data not available")
        
        # Sea level trends
        st.header("Sea Level Rise")
        
        if 'sea_level_rise_mm' in df.columns:
            # Create sea level chart
            fig = create_time_series_chart(
                chronological_df.dropna(subset=['sea_level_rise_mm']), 
                'year', 'sea_level_rise_mm',
                'Global Mean Sea Level Rise',
                height=400,
                y_label='Sea Level Rise (mm)'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Sea Level Rise** measures the increase in mean sea level relative to a baseline.
                
                - Rising seas threaten coastal communities and ecosystems
                - Main contributors are thermal expansion of seawater and melting ice sheets
                - The rate of rise has accelerated in recent decades
                """)
            
            # Sea level rise rate calculation
            if len(chronological_df) >= 2:
                recent_years = chronological_df.tail(10)
                if len(recent_years) >= 2:
                    first_year = recent_years['year'].iloc[0]
                    last_year = recent_years['year'].iloc[-1]
                    first_level = recent_years['sea_level_rise_mm'].iloc[0]
                    last_level = recent_years['sea_level_rise_mm'].iloc[-1]
                    
                    years_diff = last_year - first_year
                    if years_diff > 0:
                        avg_rate = (last_level - first_level) / years_diff
                        
                        st.info(f"💧 The average rate of sea level rise over the past {years_diff} years is **{avg_rate:.2f} mm per year**.")
        
        else:
            st.warning("Sea level data not available")
        
        # Sea ice extent
        st.header("Sea Ice Extent")
        
        if 'arctic_ice_extent_mil_sq_km' in df.columns and 'antarctic_ice_extent_mil_sq_km' in df.columns:
            # Create ice extent plots
            col1, col2 = st.columns(2)
            
            with col1:
                fig = create_time_series_chart(
                    chronological_df, 'year', 'arctic_ice_extent_mil_sq_km',
                    'Arctic Sea Ice Extent',
                    height=350,
                    y_label='Ice Extent (million sq km)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = create_time_series_chart(
                    chronological_df, 'year', 'antarctic_ice_extent_mil_sq_km',
                    'Antarctic Sea Ice Extent',
                    height=350,
                    y_label='Ice Extent (million sq km)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Total ice chart
            if 'total_ice_extent_mil_sq_km' in df.columns:
                fig = create_time_series_chart(
                    chronological_df, 'year', 'total_ice_extent_mil_sq_km',
                    'Total Global Sea Ice Extent',
                    height=400,
                    y_label='Ice Extent (million sq km)'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                with st.expander("What does this mean?"):
                    st.markdown("""
                    **Sea Ice Extent** measures the area of ocean covered by ice.
                    
                    - Arctic sea ice is declining rapidly due to warming
                    - Antarctic sea ice shows more variability but has begun declining in recent years
                    - Sea ice loss accelerates warming through the ice-albedo feedback loop
                    - Loss of sea ice affects marine ecosystems and global climate patterns
                    """)
                
                # Ice loss calculation
                if len(chronological_df) >= 2:
                    first_year = chronological_df['year'].iloc[0]
                    last_year = chronological_df['year'].iloc[-1]
                    first_ice = chronological_df['total_ice_extent_mil_sq_km'].iloc[0]
                    last_ice = chronological_df['total_ice_extent_mil_sq_km'].iloc[-1]
                    
                    ice_change = last_ice - first_ice
                    ice_percent = (ice_change / first_ice) * 100
                    
                    if ice_change < 0:
                        st.error(f"❄️ Global sea ice has decreased by **{abs(ice_change):.1f} million sq km** ({abs(ice_percent):.1f}%) since {first_year}.")
                    else:
                        st.success(f"❄️ Global sea ice has increased by **{ice_change:.1f} million sq km** ({ice_percent:.1f}%) since {first_year}.")
        
        else:
            st.warning("Sea ice data not available")
        
        # Summary metrics
        st.header("Climate Indicators Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'temperature_anomaly' in df.columns:
                recent_df = chronological_df.tail(10)
                trend = (recent_df['temperature_anomaly'].iloc[-1] - recent_df['temperature_anomaly'].iloc[0]) / len(recent_df)
                
                if trend > 0:
                    st.error(f"🌡️ Temperature warming at **{trend:.3f}°C per year** (recent trend)")
                else:
                    st.success(f"🌡️ Temperature cooling at **{abs(trend):.3f}°C per year** (recent trend)")
            
        with col2:
            if 'sea_level_rise_mm' in df.columns and not chronological_df['sea_level_rise_mm'].isna().all():
                recent_df = chronological_df.dropna(subset=['sea_level_rise_mm']).tail(10)
                if len(recent_df) >= 2:
                    years_diff = recent_df['year'].iloc[-1] - recent_df['year'].iloc[0]
                    if years_diff > 0:
                        rate = (recent_df['sea_level_rise_mm'].iloc[-1] - recent_df['sea_level_rise_mm'].iloc[0]) / years_diff
                        st.warning(f"🌊 Sea level rising at **{rate:.2f} mm per year** (recent trend)")
        
        with col3:
            if 'arctic_ice_extent_mil_sq_km' in df.columns:
                recent_df = chronological_df.tail(10)
                trend = (recent_df['arctic_ice_extent_mil_sq_km'].iloc[-1] - recent_df['arctic_ice_extent_mil_sq_km'].iloc[0]) / len(recent_df)
                
                if trend < 0:
                    st.error(f"🧊 Arctic ice declining at **{abs(trend):.2f} million sq km per year**")
                else:
                    st.success(f"🧊 Arctic ice growing at **{trend:.2f} million sq km per year**")