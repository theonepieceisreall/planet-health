import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from utils import create_time_series_chart, create_bar_chart, create_pie_chart, format_number, get_color_from_value

def show_ecosystem_visualizations(df, preview_mode=False):
    """
    Display ecosystem data visualizations
    
    Args:
        df (pandas.DataFrame): Ecosystem data
        preview_mode (bool): If True, show a condensed preview
    """
    # Get unique ecosystem types
    ecosystem_types = df['ecosystem_type'].unique() if 'ecosystem_type' in df.columns else []
    
    # Get the data in chronological order for time series
    chronological_df = df.sort_values(['year', 'ecosystem_type'])
    
    # Get the latest year data
    latest_year = df['year'].max()
    latest_data = df[df['year'] == latest_year]
    
    if preview_mode:
        # Abbreviated version for overview page
        col1, col2 = st.columns(2)
        
        with col1:
            # Forest coverage chart
            forest_data = chronological_df[chronological_df['ecosystem_type'] == 'Forests'] if 'ecosystem_type' in df.columns else chronological_df
            
            if 'forest_coverage_percent' in df.columns and not forest_data.empty:
                fig = create_time_series_chart(
                    forest_data, 'year', 'forest_coverage_percent',
                    'Global Forest Coverage Trend',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            elif 'area_mil_hectares' in df.columns and 'ecosystem_type' in df.columns and 'Forests' in ecosystem_types:
                forest_df = chronological_df[chronological_df['ecosystem_type'] == 'Forests']
                fig = create_time_series_chart(
                    forest_df, 'year', 'area_mil_hectares',
                    'Forest Area Trend',
                    height=300
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Forest coverage data not available")
        
        with col2:
            # Ecosystem health comparison
            if 'health_index' in df.columns and 'ecosystem_type' in df.columns and len(ecosystem_types) > 0:
                # Get latest year health indices by ecosystem type
                eco_health_df = latest_data.groupby('ecosystem_type')['health_index'].mean().reset_index()
                
                fig = px.bar(
                    eco_health_df.sort_values('health_index'),
                    x='ecosystem_type',
                    y='health_index',
                    title=f'Ecosystem Health Comparison ({latest_year})',
                    height=300,
                    color='health_index',
                    color_continuous_scale=['red', 'yellow', 'green']
                )
                
                fig.update_layout(
                    xaxis_title="Ecosystem Type",
                    yaxis_title="Health Index (0-100)"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Ecosystem health comparison data not available")
    
    else:
        # Full detailed view
        st.header("Ecosystem Area Trends")
        
        # Area trends visualization
        if 'area_mil_hectares' in df.columns and 'ecosystem_type' in df.columns and len(ecosystem_types) > 0:
            # Create overview of all ecosystem area trends
            eco_area_by_year = chronological_df.pivot(index='year', columns='ecosystem_type', values='area_mil_hectares').reset_index()
            
            # Create a multi-line chart showing area trends for all ecosystem types
            fig = go.Figure()
            
            for ecosystem_type in ecosystem_types:
                if ecosystem_type in eco_area_by_year.columns:
                    fig.add_trace(
                        go.Scatter(
                            x=eco_area_by_year['year'],
                            y=eco_area_by_year[ecosystem_type],
                            name=ecosystem_type,
                            line=dict(width=3),
                            marker=dict(size=8)
                        )
                    )
            
            # Update layout
            fig.update_layout(
                title='Ecosystem Area Trends by Type',
                xaxis_title='Year',
                yaxis_title='Area (million hectares)',
                legend_title='Ecosystem Type',
                height=500,
                hovermode="x unified",
                template="plotly_white"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Ecosystem Area Trends** show how the total area of each ecosystem type has changed over time.
                
                - Declining trends indicate habitat loss
                - Most natural ecosystems are declining due to human activities
                - Rate of decline varies by ecosystem type and region
                - Area alone doesn't capture fragmentation or quality changes
                """)
            
            # Create pie chart showing current ecosystem distribution
            if not latest_data.empty:
                eco_areas = latest_data.groupby('ecosystem_type')['area_mil_hectares'].sum().reset_index()
                
                fig = create_pie_chart(
                    eco_areas,
                    'area_mil_hectares',
                    'ecosystem_type',
                    f'Global Ecosystem Distribution ({latest_year})',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.warning("Ecosystem area trend data not available")
        
        # Forest systems visualization
        st.header("Forest Ecosystems")
        
        if 'ecosystem_type' in df.columns and 'Forests' in ecosystem_types:
            # Filter for forest data
            forest_df = chronological_df[chronological_df['ecosystem_type'] == 'Forests']
            latest_forest = latest_data[latest_data['ecosystem_type'] == 'Forests']
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Forest coverage percent
                if 'forest_coverage_percent' in df.columns and not forest_df['forest_coverage_percent'].isna().all():
                    fig = create_time_series_chart(
                        forest_df, 'year', 'forest_coverage_percent',
                        'Global Forest Coverage (% of land area)',
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # If percent not available, show absolute area
                    fig = create_time_series_chart(
                        forest_df, 'year', 'area_mil_hectares',
                        'Global Forest Area',
                        height=350,
                        y_label='Million Hectares'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Primary forest percentage
                if 'primary_forest_percent' in df.columns and not forest_df['primary_forest_percent'].isna().all():
                    fig = create_time_series_chart(
                        forest_df, 'year', 'primary_forest_percent',
                        'Primary Forest (% of total forest)',
                        height=350
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    with st.expander("What is primary forest?"):
                        st.markdown("""
                        **Primary forests** are naturally regenerated forests of native species with no clearly visible signs of human activity and where ecological processes are not significantly disturbed.
                        
                        These forests have high biodiversity value and provide crucial ecosystem services. They are declining faster than overall forest cover due to logging and conversion.
                        """)
                
                # Forest health if available
                elif 'health_index' in df.columns and not forest_df['health_index'].isna().all():
                    fig = create_time_series_chart(
                        forest_df, 'year', 'health_index',
                        'Forest Ecosystem Health Index',
                        height=350,
                        y_label='Health Index (0-100)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Annual change visualization
            if 'annual_change_percent' in df.columns and not forest_df['annual_change_percent'].isna().all():
                fig = create_time_series_chart(
                    forest_df, 'year', 'annual_change_percent',
                    'Annual Forest Change Rate',
                    height=400,
                    y_label='Annual Change (%)'
                )
                
                # Add zero reference line
                fig.add_shape(
                    type="line",
                    x0=min(forest_df['year']),
                    y0=0,
                    x1=max(forest_df['year']),
                    y1=0,
                    line=dict(color="black", width=1, dash="dash"),
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Forest status explanation
                if not latest_forest.empty:
                    current_change = latest_forest['annual_change_percent'].iloc[0]
                    
                    if current_change < -0.5:
                        st.error(f"🌲 Forests are currently declining at a rate of **{abs(current_change):.2f}% per year**, resulting in significant biodiversity loss and reduced carbon sequestration capacity.")
                    elif current_change < 0:
                        st.warning(f"🌲 Forests are currently declining at a rate of **{abs(current_change):.2f}% per year**, though the rate of loss has slowed compared to previous decades.")
                    elif current_change == 0:
                        st.info(f"🌲 Forest area is currently stable with no net change.")
                    else:
                        st.success(f"🌲 Forests are currently increasing at a rate of **{current_change:.2f}% per year**, largely due to reforestation and afforestation efforts.")
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Forest Ecosystems** are crucial for biodiversity, carbon storage, and water regulation.
                
                - Forests cover about 31% of the global land area
                - Approximately 420 million hectares of forest have been lost since 1990
                - Primary (old-growth) forests have the highest biodiversity and carbon storage
                - Main causes of deforestation include agriculture, logging, and development
                """)
        
        else:
            st.warning("Forest ecosystem data not available")
        
        # Marine ecosystems visualization
        st.header("Marine Ecosystems")
        
        if 'ecosystem_type' in df.columns and 'Coral Reefs' in ecosystem_types:
            # Filter for coral reef data
            coral_df = chronological_df[chronological_df['ecosystem_type'] == 'Coral Reefs']
            latest_coral = latest_data[latest_data['ecosystem_type'] == 'Coral Reefs']
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Coral reef area
                fig = create_time_series_chart(
                    coral_df, 'year', 'area_mil_hectares',
                    'Global Coral Reef Area',
                    height=350,
                    y_label='Million Hectares'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Coral cover percentage
                if 'coral_cover_percent' in df.columns and not coral_df['coral_cover_percent'].isna().all():
                    fig = create_time_series_chart(
                        coral_df, 'year', 'coral_cover_percent',
                        'Live Coral Cover Percentage',
                        height=350,
                        y_label='Live Coral Cover (%)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Bleaching visualization
            if 'bleaching_percent' in df.columns and not coral_df['bleaching_percent'].isna().all():
                fig = create_time_series_chart(
                    coral_df, 'year', 'bleaching_percent',
                    'Coral Bleaching Prevalence',
                    height=400,
                    y_label='Bleaching Prevalence (%)'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Bleaching explanation
                if not latest_coral.empty:
                    current_bleaching = latest_coral['bleaching_percent'].iloc[0]
                    
                    if current_bleaching > 30:
                        st.error(f"🐠 **{current_bleaching:.1f}%** of global coral reefs are currently experiencing bleaching, indicating severe heat stress and threatening reef survival.")
                    elif current_bleaching > 10:
                        st.warning(f"🐠 **{current_bleaching:.1f}%** of global coral reefs are currently experiencing bleaching, indicating significant heat stress.")
                    else:
                        st.info(f"🐠 **{current_bleaching:.1f}%** of global coral reefs are currently experiencing bleaching, which is within historical ranges but still concerning.")
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Coral Reef Ecosystems** are among the most diverse and threatened marine environments.
                
                - Coral reefs cover less than 1% of the ocean floor but support about 25% of marine species
                - Coral bleaching occurs when ocean temperatures rise, causing corals to expel their symbiotic algae
                - Repeated or prolonged bleaching can lead to coral death
                - Major threats include climate change, ocean acidification, pollution, and overfishing
                """)
        
        else:
            st.warning("Coral reef ecosystem data not available")
        
        # Wetland ecosystems
        st.header("Wetland Ecosystems")
        
        if 'ecosystem_type' in df.columns and 'Wetlands' in ecosystem_types:
            # Filter for wetland data
            wetland_df = chronological_df[chronological_df['ecosystem_type'] == 'Wetlands']
            latest_wetland = latest_data[latest_data['ecosystem_type'] == 'Wetlands']
            
            # Wetland area trends
            if 'wetland_area_mil_hectares' in df.columns and not wetland_df['wetland_area_mil_hectares'].isna().all():
                fig = create_time_series_chart(
                    wetland_df, 'year', 'wetland_area_mil_hectares',
                    'Global Wetland Area',
                    height=400,
                    y_label='Million Hectares'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate total wetland loss
                if len(wetland_df) >= 2:
                    first_year = wetland_df['year'].min()
                    last_year = wetland_df['year'].max()
                    first_area = wetland_df[wetland_df['year'] == first_year]['wetland_area_mil_hectares'].iloc[0]
                    last_area = wetland_df[wetland_df['year'] == last_year]['wetland_area_mil_hectares'].iloc[0]
                    
                    area_change = last_area - first_area
                    percent_change = (area_change / first_area) * 100
                    
                    if area_change < 0:
                        st.error(f"🌊 Since {first_year}, we have lost approximately **{abs(area_change):.1f} million hectares** of wetlands ({abs(percent_change):.1f}%).")
                    else:
                        st.success(f"🌊 Since {first_year}, we have gained approximately **{area_change:.1f} million hectares** of wetlands ({percent_change:.1f}%).")
            
            # Wetland health if available
            if 'health_index' in df.columns and not wetland_df['health_index'].isna().all():
                fig = create_time_series_chart(
                    wetland_df, 'year', 'health_index',
                    'Wetland Ecosystem Health',
                    height=350,
                    y_label='Health Index (0-100)'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Wetland Ecosystems** include marshes, swamps, bogs, and similar areas that are saturated with water.
                
                - Wetlands are critical for water purification, flood control, and carbon storage
                - They provide habitat for many species, including endangered and migratory birds
                - Global wetland area has decreased by over 35% since 1970
                - Main causes of wetland loss include drainage for agriculture, urban development, and pollution
                """)
        
        else:
            st.warning("Wetland ecosystem data not available")
        
        # Soil/Grassland ecosystems
        st.header("Soil and Grassland Ecosystems")
        
        if 'ecosystem_type' in df.columns and 'Grasslands' in ecosystem_types:
            # Filter for grassland data
            grassland_df = chronological_df[chronological_df['ecosystem_type'] == 'Grasslands']
            latest_grassland = latest_data[latest_data['ecosystem_type'] == 'Grasslands']
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Grassland area
                fig = create_time_series_chart(
                    grassland_df, 'year', 'area_mil_hectares',
                    'Global Grassland Area',
                    height=350,
                    y_label='Million Hectares'
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Soil carbon content
                if 'soil_carbon_content' in df.columns and not grassland_df['soil_carbon_content'].isna().all():
                    fig = create_time_series_chart(
                        grassland_df, 'year', 'soil_carbon_content',
                        'Soil Carbon Content',
                        height=350,
                        y_label='Tons per Hectare'
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            # Desertification risk
            if 'desertification_risk_index' in df.columns and not grassland_df['desertification_risk_index'].isna().all():
                fig = create_time_series_chart(
                    grassland_df, 'year', 'desertification_risk_index',
                    'Desertification Risk Index',
                    height=400,
                    y_label='Risk Index (0-100)'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Desertification explanation
                if not latest_grassland.empty:
                    current_risk = latest_grassland['desertification_risk_index'].iloc[0]
                    
                    if current_risk > 70:
                        st.error(f"🏜️ Current desertification risk index is **{current_risk:.1f}/100**, indicating extremely high vulnerability to land degradation and desertification.")
                    elif current_risk > 50:
                        st.warning(f"🏜️ Current desertification risk index is **{current_risk:.1f}/100**, indicating high vulnerability to land degradation and desertification.")
                    elif current_risk > 30:
                        st.info(f"🏜️ Current desertification risk index is **{current_risk:.1f}/100**, indicating moderate vulnerability to land degradation and desertification.")
                    else:
                        st.success(f"🏜️ Current desertification risk index is **{current_risk:.1f}/100**, indicating relatively low vulnerability to land degradation and desertification.")
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Soil and Grassland Ecosystems** form vast landscapes that are critical for carbon storage, water cycling, and food production.
                
                - Grasslands cover about 40% of Earth's land surface
                - Soils store more carbon than the atmosphere and all plants combined
                - Desertification is the degradation of drylands, affecting over 3 billion people globally
                - Causes include climate change, overgrazing, deforestation, and poor agricultural practices
                """)
        
        else:
            st.warning("Soil and grassland ecosystem data not available")
        
        # Overall ecosystem health summary
        st.header("Ecosystem Health Summary")
        
        if 'health_index' in df.columns and 'ecosystem_type' in df.columns:
            # Get average health index by ecosystem type
            ecosystem_health = latest_data.groupby('ecosystem_type')['health_index'].mean().reset_index()
            
            # Create health index visualization
            fig = px.bar(
                ecosystem_health.sort_values('health_index'),
                x='ecosystem_type',
                y='health_index',
                title=f'Ecosystem Health Index Comparison ({latest_year})',
                height=400,
                color='health_index',
                color_continuous_scale=['red', 'yellow', 'green']
            )
            
            fig.update_layout(
                xaxis_title="Ecosystem Type",
                yaxis_title="Health Index (0-100)"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Identify most and least healthy ecosystems
            if not ecosystem_health.empty:
                most_healthy = ecosystem_health.loc[ecosystem_health['health_index'].idxmax()]
                least_healthy = ecosystem_health.loc[ecosystem_health['health_index'].idxmin()]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"💪 **{most_healthy['ecosystem_type']}** are currently the healthiest ecosystem type with a health index of **{most_healthy['health_index']:.1f}/100**.")
                
                with col2:
                    st.warning(f"⚠️ **{least_healthy['ecosystem_type']}** are currently the most threatened ecosystem type with a health index of only **{least_healthy['health_index']:.1f}/100**.")
            
            # Calculate overall ecosystem health trend
            yearly_health = chronological_df.groupby(['year']).agg({'health_index': 'mean'}).reset_index()
            
            if len(yearly_health) >= 2:
                first_health = yearly_health['health_index'].iloc[0]
                last_health = yearly_health['health_index'].iloc[-1]
                
                health_change = last_health - first_health
                
                if health_change < -10:
                    st.error(f"📉 Overall ecosystem health has declined significantly by **{abs(health_change):.1f} points** since monitoring began.")
                elif health_change < 0:
                    st.warning(f"📉 Overall ecosystem health has declined by **{abs(health_change):.1f} points** since monitoring began.")
                elif health_change == 0:
                    st.info(f"➡️ Overall ecosystem health has remained stable since monitoring began.")
                else:
                    st.success(f"📈 Overall ecosystem health has improved by **{health_change:.1f} points** since monitoring began.")
        
        else:
            st.warning("Ecosystem health index data not available")