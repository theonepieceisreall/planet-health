import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import folium_static
import time
import matplotlib.pyplot as plt
import os
from datetime import datetime
import requests

# Import data handlers
from data_handlers.climate import get_climate_data
from data_handlers.biodiversity import get_biodiversity_data
from data_handlers.pollution import get_pollution_data
from data_handlers.ecosystem import get_ecosystem_data

# Import visualizations
from visualizations.climate_viz import show_climate_visualizations
from visualizations.biodiversity_viz import show_biodiversity_visualizations
from visualizations.pollution_viz import show_pollution_visualizations
from visualizations.ecosystem_viz import show_ecosystem_visualizations
from visualizations.map_viz import show_global_indicators_map

# Import custom assets
from assets.logo import earth_logo_svg, header_html, card_html, footer_html

# Set page configuration
st.set_page_config(
    page_title="Planetary Health Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load and apply custom CSS
def load_css():
    with open(".streamlit/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Function to load logo and header
def load_header():
    return header_html.format(earth_logo_svg=earth_logo_svg)

# Function to create styled card
def create_card(title, content_function, *args, **kwargs):
    content = content_function(*args, **kwargs)
    return card_html.format(title=title, content=content)

# Main function
def main():
    # Load custom CSS
    load_css()
    
    # Sidebar navigation with improved styling
    with st.sidebar:
        st.image("https://i.imgur.com/Kq0bRJl.png", width=70)
        st.title("Planetary Health Dashboard")
        st.markdown("---")
        
        page = st.radio(
            "📊 Navigate to",
            ["Overview", "Climate Indicators", "Biodiversity Metrics", 
             "Pollution Levels", "Ecosystem Health", "Global Map View", 
             "Community Contributions"]
        )
        
        st.markdown("---")
        st.markdown("### 📚 Data Sources")
        st.markdown("""
        - NASA GISTEMP
        - NOAA Sea Level Data
        - Global Carbon Project
        - IUCN Red List
        - Global Forest Watch
        """)
        
        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.markdown("""
        This dashboard provides real-time data visualizations of key planetary health indicators.
        
        Data last updated: {}
        """.format(datetime.now().strftime("%Y-%m-%d")))
        
        # Add social media links
        st.markdown("---")
        
        social_media_html = """
        <div style="display: flex; justify-content: center; gap: 20px;">
            <a href="#" target="_blank" style="color: #1DA1F2;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/>
                </svg>
            </a>
            <a href="#" target="_blank" style="color: #4267B2;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M9 8h-3v4h3v12h5v-12h3.642l.358-4h-4v-1.667c0-.955.192-1.333 1.115-1.333h2.885v-5h-3.808c-3.596 0-5.192 1.583-5.192 4.615v3.385z"/>
                </svg>
            </a>
            <a href="#" target="_blank" style="color: #E1306C;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                </svg>
            </a>
        </div>
        """
        
        st.markdown(social_media_html, unsafe_allow_html=True)
    
    # Display appropriate page based on selection
    if page == "Overview":
        show_overview_page()
    elif page == "Climate Indicators":
        show_climate_page()
    elif page == "Biodiversity Metrics":
        show_biodiversity_page()
    elif page == "Pollution Levels":
        show_pollution_page()
    elif page == "Ecosystem Health":
        show_ecosystem_page()
    elif page == "Global Map View":
        show_map_page()
    elif page == "Community Contributions":
        show_community_page()
        
    # Add footer
    st.markdown(footer_html.format(date=datetime.now().strftime("%Y-%m-%d")), unsafe_allow_html=True)

# Overview page
def show_overview_page():
    # Display custom header
    st.markdown(load_header(), unsafe_allow_html=True)
    
    # Introduction card with categories
    dashboard_intro = """
    <div class="dashboard-intro">
        <p style="font-size: 1.2rem; line-height: 1.6; color: #2c3e50;">
            This dashboard provides comprehensive, real-time data visualizations of critical planetary health indicators.
            Use it to explore the current state of our planet's environmental systems and track changes over time.
        </p>
        <div style="display: flex; gap: 15px; margin-top: 15px;">
            <div style="background-color: #1AB394; color: white; padding: 15px; border-radius: 5px; flex: 1; text-align: center;">
                <h4 style="margin-top: 0;">Climate</h4>
                <p>Temperature, sea level, and ice coverage trends</p>
            </div>
            <div style="background-color: #1c4966; color: white; padding: 15px; border-radius: 5px; flex: 1; text-align: center;">
                <h4 style="margin-top: 0;">Biodiversity</h4>
                <p>Species distribution, extinction rates, and habitat changes</p>
            </div>
            <div style="background-color: #e67e22; color: white; padding: 15px; border-radius: 5px; flex: 1; text-align: center;">
                <h4 style="margin-top: 0;">Pollution</h4>
                <p>Air quality, greenhouse gases, and plastic pollution</p>
            </div>
            <div style="background-color: #27ae60; color: white; padding: 15px; border-radius: 5px; flex: 1; text-align: center;">
                <h4 style="margin-top: 0;">Ecosystems</h4>
                <p>Forests, coral reefs, wetlands, and soil health</p>
            </div>
        </div>
    </div>
    """
    
    st.markdown(dashboard_intro, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Get data for metrics
    climate_data = get_climate_data(limit=10)
    pollution_data = get_pollution_data(limit=10)
    biodiversity_data = get_biodiversity_data(limit=10)
    ecosystem_data = get_ecosystem_data(limit=10)
    
    # Key metrics section
    metrics_header = """
    <div style="padding: 10px;">
        <div class="planetary-metrics" style="display: flex; flex-wrap: wrap; gap: 20px; justify-content: space-between;">
    """
    
    st.markdown(
        card_html.format(
            title="Key Planetary Vital Signs",
            content=metrics_header
        ), 
        unsafe_allow_html=True
    )
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Display metrics
    with col1:
        latest_temp = climate_data['temperature_anomaly'].iloc[0]
        delta = latest_temp - climate_data['temperature_anomaly'].iloc[1]
        delta_color = "red" if delta > 0 else "green"
        delta_arrow = "↑" if delta > 0 else "↓"
        
        metric_html = f"""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
            <div style="font-size: 0.9rem; color: #7f8c8d; margin-bottom: 5px;">Global Temperature Anomaly</div>
            <div style="font-size: 1.8rem; font-weight: 600; color: #2c3e50;">{latest_temp:.2f}°C</div>
            <div style="font-size: 0.9rem; color: {delta_color};">
                {delta_arrow} {abs(delta):.2f}°C
            </div>
        </div>
        """
        
        st.markdown(metric_html, unsafe_allow_html=True)
    
    with col2:
        if 'co2_level' in pollution_data.columns:
            latest_co2 = pollution_data['co2_level'].iloc[0]
            delta = latest_co2 - pollution_data['co2_level'].iloc[1]
            delta_color = "red" if delta > 0 else "green"
            delta_arrow = "↑" if delta > 0 else "↓"
            
            co2_metric_html = f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <div style="font-size: 0.9rem; color: #7f8c8d; margin-bottom: 5px;">Atmospheric CO₂</div>
                <div style="font-size: 1.8rem; font-weight: 600; color: #2c3e50;">{latest_co2:.1f} ppm</div>
                <div style="font-size: 0.9rem; color: {delta_color};">
                    {delta_arrow} {abs(delta):.1f} ppm
                </div>
            </div>
            """
            
            st.markdown(co2_metric_html, unsafe_allow_html=True)
    
    with col3:
        if 'ecosystem_type' in ecosystem_data.columns and 'Forests' in ecosystem_data['ecosystem_type'].values:
            forest_data = ecosystem_data[ecosystem_data['ecosystem_type'] == 'Forests']
            if not forest_data.empty and 'forest_coverage_percent' in forest_data.columns:
                latest_forest = forest_data['forest_coverage_percent'].iloc[0]
                prev_forest = forest_data['forest_coverage_percent'].iloc[1] if len(forest_data) > 1 else latest_forest
                delta = latest_forest - prev_forest
                delta_color = "green" if delta > 0 else "red"
                delta_arrow = "↑" if delta > 0 else "↓"
                
                forest_metric_html = f"""
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                    <div style="font-size: 0.9rem; color: #7f8c8d; margin-bottom: 5px;">Global Forest Coverage</div>
                    <div style="font-size: 1.8rem; font-weight: 600; color: #2c3e50;">{latest_forest:.1f}%</div>
                    <div style="font-size: 0.9rem; color: {delta_color};">
                        {delta_arrow} {abs(delta):.1f}%
                    </div>
                </div>
                """
                
                st.markdown(forest_metric_html, unsafe_allow_html=True)
    
    with col4:
        if 'region' in biodiversity_data.columns:
            global_endangered = biodiversity_data.groupby('year')['endangered_species_count'].sum().reset_index()
            latest_endangered = global_endangered['endangered_species_count'].iloc[0]
            prev_endangered = global_endangered['endangered_species_count'].iloc[1] if len(global_endangered) > 1 else latest_endangered
            delta = latest_endangered - prev_endangered
            delta_color = "red" if delta > 0 else "green"
            delta_arrow = "↑" if delta > 0 else "↓"
            
            endangered_metric_html = f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);">
                <div style="font-size: 0.9rem; color: #7f8c8d; margin-bottom: 5px;">Endangered Species</div>
                <div style="font-size: 1.8rem; font-weight: 600; color: #2c3e50;">{latest_endangered:,.0f}</div>
                <div style="font-size: 0.9rem; color: {delta_color};">
                    {delta_arrow} {abs(delta):,.0f}
                </div>
            </div>
            """
            
            st.markdown(endangered_metric_html, unsafe_allow_html=True)
    
    metrics_footer = "</div></div>"
    st.markdown(metrics_footer, unsafe_allow_html=True)
    
    # Dashboard sections
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Climate preview section
    st.markdown(
        card_html.format(
            title="Climate Indicators",
            content="<div id='climate-preview'></div>"
        ),
        unsafe_allow_html=True
    )
    
    show_climate_visualizations(climate_data, preview_mode=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col3:
        view_climate_button = st.button("View detailed climate data", key="climate_button")
        if view_climate_button:
            st.session_state.page = "Climate Indicators"
            st.rerun()
    
    # Biodiversity preview section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        card_html.format(
            title="Biodiversity Metrics",
            content="<div id='biodiversity-preview'></div>"
        ),
        unsafe_allow_html=True
    )
    
    show_biodiversity_visualizations(biodiversity_data, preview_mode=True)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col3:
        view_biodiversity_button = st.button("View detailed biodiversity data", key="biodiversity_button")
        if view_biodiversity_button:
            st.session_state.page = "Biodiversity Metrics"
            st.rerun()
    
    # Map preview section
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        card_html.format(
            title="Global Map View",
            content="<div id='map-preview'></div>"
        ),
        unsafe_allow_html=True
    )
    
    show_global_indicators_map(height=400)
    
    col1, col2, col3 = st.columns([2, 2, 1])
    with col3:
        view_map_button = st.button("Explore interactive map", key="map_button")
        if view_map_button:
            st.session_state.page = "Global Map View"
            st.rerun()

# Climate page
def show_climate_page():
    # Display custom header
    st.markdown(
        header_html.format(earth_logo_svg=earth_logo_svg),
        unsafe_allow_html=True
    )
    
    # Introduction card
    climate_intro_content = """
    <p style="font-size: 1.1rem; line-height: 1.5;">
        This section provides detailed climate data including temperature anomalies, 
        sea level rise, and polar ice coverage trends. These indicators are critical 
        for understanding the pace and magnitude of global climate change.
    </p>
    <div style="display: flex; gap: 15px; margin-top: 15px; flex-wrap: wrap;">
        <div style="background-color: #e74c3c; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Temperature</h4>
            <p style="margin-bottom: 0;">Global warming patterns</p>
        </div>
        <div style="background-color: #3498db; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Sea Level</h4>
            <p style="margin-bottom: 0;">Ocean rise measurements</p>
        </div>
        <div style="background-color: #2980b9; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Ice Coverage</h4>
            <p style="margin-bottom: 0;">Polar ice extent changes</p>
        </div>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Climate Indicators",
            content=climate_intro_content
        ),
        unsafe_allow_html=True
    )
    
    # Get climate data
    climate_data = get_climate_data()
    
    # Show visualizations in a card
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        card_html.format(
            title="Climate Data Visualizations",
            content="<div id='climate-visualizations'></div>"
        ),
        unsafe_allow_html=True
    )
    
    # Show visualizations
    show_climate_visualizations(climate_data)
    
    # Add info section at the bottom
    st.markdown("<br>", unsafe_allow_html=True)
    
    climate_info_content = """
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div>
            <h4 style="color: #e74c3c;">Temperature Anomalies</h4>
            <p>Temperature anomalies show how much warmer or cooler a region is compared to the normal temperature for that region and time of year. The baseline period is typically 1951-1980.</p>
        </div>
        <div>
            <h4 style="color: #3498db;">Sea Level Rise</h4>
            <p>Sea level measurements track both global mean sea level rise and regional variations. The data comes from tide gauges and satellite measurements.</p>
        </div>
        <div>
            <h4 style="color: #2980b9;">Ice Coverage</h4>
            <p>Ice coverage tracks the extent of sea ice in the Arctic and Antarctic regions. The continued decline in Arctic sea ice is one of the most visible indicators of climate change.</p>
        </div>
    </div>
    <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
        <h4 style="margin-top: 0; color: #2c3e50;">Data Sources</h4>
        <p style="margin-bottom: 0;">
            Temperature data from NASA GISTEMP, sea level data from NOAA, and ice coverage data from the National Snow and Ice Data Center (NSIDC).
        </p>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Understanding Climate Data",
            content=climate_info_content
        ),
        unsafe_allow_html=True
    )

# Biodiversity page
def show_biodiversity_page():
    # Display custom header
    st.markdown(
        header_html.format(earth_logo_svg=earth_logo_svg),
        unsafe_allow_html=True
    )
    
    # Introduction card
    bio_intro_content = """
    <p style="font-size: 1.1rem; line-height: 1.5;">
        This section provides detailed biodiversity data including endangered species counts,
        extinction rates, and habitat loss across different regions. Biodiversity is crucial
        for ecosystem resilience and planetary health.
    </p>
    <div style="display: flex; gap: 15px; margin-top: 15px; flex-wrap: wrap;">
        <div style="background-color: #8e44ad; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Endangered Species</h4>
            <p style="margin-bottom: 0;">Extinction risk tracking</p>
        </div>
        <div style="background-color: #9b59b6; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Habitat Loss</h4>
            <p style="margin-bottom: 0;">Ecosystem destruction rates</p>
        </div>
        <div style="background-color: #8e44ad; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Species Discovery</h4>
            <p style="margin-bottom: 0;">New species identification</p>
        </div>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Biodiversity Metrics",
            content=bio_intro_content
        ),
        unsafe_allow_html=True
    )
    
    # Get biodiversity data
    biodiversity_data = get_biodiversity_data()
    
    # Show visualizations in a card
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        card_html.format(
            title="Biodiversity Data Visualizations",
            content="<div id='biodiversity-visualizations'></div>"
        ),
        unsafe_allow_html=True
    )
    
    # Show visualizations
    show_biodiversity_visualizations(biodiversity_data)
    
    # Add info section at the bottom
    st.markdown("<br>", unsafe_allow_html=True)
    
    bio_info_content = """
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div>
            <h4 style="color: #8e44ad;">Endangered Species</h4>
            <p>Endangered species are those at risk of extinction due to factors such as habitat loss, 
            climate change, and human activities. The IUCN Red List classifies species based on their 
            extinction risk: Extinct, Extinct in the Wild, Critically Endangered, Endangered, Vulnerable, etc.</p>
        </div>
        <div>
            <h4 style="color: #9b59b6;">Habitat Loss</h4>
            <p>Habitat loss is the process by which natural habitat becomes incapable of supporting native species.
            It is currently the primary cause of species extinction worldwide, with deforestation,
            agriculture, and urbanization being key drivers.</p>
        </div>
        <div>
            <h4 style="color: #8e44ad;">Species Discovery</h4>
            <p>Scientists continue to discover new species, especially in remote or unexplored regions.
            However, many species may go extinct before they are even discovered, contributing to 
            what scientists call "extinction debt" - the future ecological cost of current habitat destruction.</p>
        </div>
    </div>
    <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
        <h4 style="margin-top: 0; color: #2c3e50;">Take Action</h4>
        <p style="margin-bottom: 0;">
            Support conservation organizations, reduce your ecological footprint, and raise awareness
            about biodiversity loss to help protect the planet's incredible diversity of life.
        </p>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Understanding Biodiversity Data",
            content=bio_info_content
        ),
        unsafe_allow_html=True
    )

# Pollution page
def show_pollution_page():
    # Display custom header
    st.markdown(
        header_html.format(earth_logo_svg=earth_logo_svg),
        unsafe_allow_html=True
    )
    
    # Introduction card
    pollution_intro_content = """
    <p style="font-size: 1.1rem; line-height: 1.5;">
        This section provides detailed pollution data including greenhouse gas concentrations,
        air quality, and plastic pollution trends. Tracking pollution is essential for 
        understanding human impact on planetary systems.
    </p>
    <div style="display: flex; gap: 15px; margin-top: 15px; flex-wrap: wrap;">
        <div style="background-color: #e67e22; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Greenhouse Gases</h4>
            <p style="margin-bottom: 0;">Atmospheric concentrations</p>
        </div>
        <div style="background-color: #d35400; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Air Quality</h4>
            <p style="margin-bottom: 0;">PM2.5 and ozone levels</p>
        </div>
        <div style="background-color: #e67e22; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Ocean Plastic</h4>
            <p style="margin-bottom: 0;">Marine pollution accumulation</p>
        </div>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Pollution Levels",
            content=pollution_intro_content
        ),
        unsafe_allow_html=True
    )
    
    # Get pollution data
    pollution_data = get_pollution_data()
    
    # Show visualizations in a card
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        card_html.format(
            title="Pollution Data Visualizations",
            content="<div id='pollution-visualizations'></div>"
        ),
        unsafe_allow_html=True
    )
    
    # Show visualizations
    show_pollution_visualizations(pollution_data)
    
    # Add info section at the bottom
    st.markdown("<br>", unsafe_allow_html=True)
    
    info_content = """
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div>
            <h4 style="color: #e67e22;">Greenhouse Gases</h4>
            <p>Greenhouse gases like CO2, methane, and nitrous oxide trap heat in the atmosphere, 
            leading to global warming. CO2 levels have increased from about 280 ppm in pre-industrial times 
            to over 410 ppm today, primarily due to fossil fuel combustion.</p>
        </div>
        <div>
            <h4 style="color: #d35400;">Air Quality</h4>
            <p>Air quality is measured using pollutants like particulate matter (PM2.5 and PM10), 
            ground-level ozone, nitrogen dioxide, and sulfur dioxide. Poor air quality causes
            millions of premature deaths annually and harms ecosystems.</p>
        </div>
        <div>
            <h4 style="color: #e67e22;">Ocean Plastic</h4>
            <p>Plastic pollution in oceans is increasing exponentially, with millions of tons entering 
            marine environments annually. Microplastics have been found in the deepest ocean trenches
            and have entered food chains, with unknown long-term consequences.</p>
        </div>
    </div>
    <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
        <h4 style="margin-top: 0; color: #2c3e50;">Take Action</h4>
        <p style="margin-bottom: 0;">
            Reduce your carbon footprint, minimize single-use plastics, and support clean air policies
            to help address pollution at individual and systemic levels.
        </p>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Understanding Pollution Data",
            content=info_content
        ),
        unsafe_allow_html=True
    )

# Ecosystem page
def show_ecosystem_page():
    # Display custom header
    st.markdown(
        header_html.format(earth_logo_svg=earth_logo_svg),
        unsafe_allow_html=True
    )
    
    # Introduction card
    eco_intro_content = """
    <p style="font-size: 1.1rem; line-height: 1.5;">
        This section provides detailed ecosystem data including forest coverage,
        coral reef status, wetland conditions, and soil health. Healthy ecosystems
        provide essential services that sustain all life on Earth.
    </p>
    <div style="display: flex; gap: 15px; margin-top: 15px; flex-wrap: wrap;">
        <div style="background-color: #27ae60; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Forests</h4>
            <p style="margin-bottom: 0;">Coverage and deforestation</p>
        </div>
        <div style="background-color: #16a085; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Marine</h4>
            <p style="margin-bottom: 0;">Coral reefs and ocean health</p>
        </div>
        <div style="background-color: #27ae60; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Wetlands</h4>
            <p style="margin-bottom: 0;">Marshes, swamps, and bogs</p>
        </div>
        <div style="background-color: #16a085; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Soil</h4>
            <p style="margin-bottom: 0;">Carbon content and erosion</p>
        </div>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Ecosystem Health",
            content=eco_intro_content
        ),
        unsafe_allow_html=True
    )
    
    # Get ecosystem data
    ecosystem_data = get_ecosystem_data()
    
    # Show visualizations in a card
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        card_html.format(
            title="Ecosystem Data Visualizations",
            content="<div id='ecosystem-visualizations'></div>"
        ),
        unsafe_allow_html=True
    )
    
    # Show visualizations
    show_ecosystem_visualizations(ecosystem_data)
    
    # Add info section at the bottom
    st.markdown("<br>", unsafe_allow_html=True)
    
    eco_info_content = """
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div>
            <h4 style="color: #27ae60;">Forest Ecosystems</h4>
            <p>Forests cover about 31% of the world's land surface and are home to 80% of terrestrial biodiversity.
            They provide oxygen, store carbon, purify water, and support the livelihoods of 1.6 billion people.
            Primary forests with minimal human disturbance are particularly valuable for biodiversity.</p>
        </div>
        <div>
            <h4 style="color: #16a085;">Coral Reef Ecosystems</h4>
            <p>Coral reefs cover less than 1% of the ocean floor but support approximately 25% of marine species.
            They are threatened by warming oceans, which cause coral bleaching, as well as ocean acidification,
            pollution, and destructive fishing practices.</p>
        </div>
        <div>
            <h4 style="color: #27ae60;">Wetland Ecosystems</h4>
            <p>Wetlands include marshes, swamps, and bogs that are critical for water purification, flood control,
            carbon storage, and wildlife habitat. Over 35% of the world's wetlands have been lost since 1970,
            primarily due to drainage for agriculture and development.</p>
        </div>
        <div>
            <h4 style="color: #16a085;">Soil Health</h4>
            <p>Healthy soils are essential for food production, carbon sequestration, and water management.
            Soil degradation affects over 33% of the Earth's land surface, with erosion, nutrient depletion,
            and desertification threatening agricultural productivity and ecosystem function.</p>
        </div>
    </div>
    <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
        <h4 style="margin-top: 0; color: #2c3e50;">Ecosystem Services</h4>
        <p style="margin-bottom: 0;">
            Healthy ecosystems provide services valued at over $125 trillion per year, including climate regulation,
            water purification, pollination, and natural resources essential for human wellbeing and economic prosperity.
        </p>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Understanding Ecosystem Health",
            content=eco_info_content
        ),
        unsafe_allow_html=True
    )

# Map page
def show_map_page():
    # Display custom header
    st.markdown(
        header_html.format(earth_logo_svg=earth_logo_svg),
        unsafe_allow_html=True
    )
    
    # Introduction card
    map_intro_content = """
    <p style="font-size: 1.1rem; line-height: 1.5;">
        This interactive map shows various environmental indicators around the world.
        Select an indicator to view its global distribution and explore how different regions
        are experiencing environmental changes.
    </p>
    <div style="display: flex; gap: 15px; margin-top: 15px; flex-wrap: wrap;">
        <div style="background-color: #3498db; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Temperature Anomalies</h4>
            <p style="margin-bottom: 0;">Global warming patterns</p>
        </div>
        <div style="background-color: #9b59b6; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Air Quality</h4>
            <p style="margin-bottom: 0;">Pollution concentrations</p>
        </div>
        <div style="background-color: #16a085; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Deforestation</h4>
            <p style="margin-bottom: 0;">Forest loss rates</p>
        </div>
        <div style="background-color: #e74c3c; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Biodiversity</h4>
            <p style="margin-bottom: 0;">Species health status</p>
        </div>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Global Map View",
            content=map_intro_content
        ),
        unsafe_allow_html=True
    )
    
    # Indicator selection in a stylish card
    st.markdown("<br>", unsafe_allow_html=True)
    
    map_control_content = """
    <div style="padding: 5px 0;">
        <p style="margin-bottom: 10px;">Select an environmental indicator to display on the global map:</p>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Map Controls",
            content=map_control_content
        ),
        unsafe_allow_html=True
    )
    
    # Get indicator selection
    indicator = st.selectbox(
        "Environmental Indicator",
        ["Temperature Anomalies", "Air Quality Index", "Deforestation Rate", "Biodiversity Status"],
        index=0
    )
    
    # Map visualization in a card
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        card_html.format(
            title=f"Global {indicator} Map",
            content="<div id='global-map'></div>"
        ),
        unsafe_allow_html=True
    )
    
    # Show map
    show_global_indicators_map(indicator, height=600)
    
    # Add info section at the bottom
    st.markdown("<br>", unsafe_allow_html=True)
    
    map_help_content = """
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px;">
        <div>
            <h4 style="color: #3498db;">Navigation</h4>
            <ul>
                <li>Zoom in/out using the mouse wheel or the + and - controls</li>
                <li>Click and drag to pan around the map</li>
                <li>Click on markers to see detailed information for each location</li>
            </ul>
        </div>
        <div>
            <h4 style="color: #3498db;">Layers</h4>
            <ul>
                <li>Use the layer control in the top right to toggle between different data layers</li>
                <li>The heatmap shows the intensity of the selected indicator across regions</li>
                <li>Markers provide specific values for individual countries</li>
            </ul>
        </div>
        <div>
            <h4 style="color: #3498db;">Data Interpretation</h4>
            <ul>
                <li>Refer to the color legend to understand the severity scale</li>
                <li>Areas with darker/brighter colors indicate more extreme values</li>
                <li>Some regions may lack data due to limited monitoring</li>
            </ul>
        </div>
    </div>
    <div style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;">
        <h4 style="margin-top: 0; color: #2c3e50;">Data Sources</h4>
        <p style="margin-bottom: 0;">
            Map data is sourced from various international monitoring organizations including NASA, NOAA,
            Global Forest Watch, UNEP, and the IUCN. Data is presented at the country level to show global patterns.
        </p>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="How to Use This Map",
            content=map_help_content
        ),
        unsafe_allow_html=True
    )

# Community contributions page
def show_community_page():
    # Display custom header
    st.markdown(
        header_html.format(earth_logo_svg=earth_logo_svg),
        unsafe_allow_html=True
    )
    
    # Introduction card
    community_intro_content = """
    <p style="font-size: 1.1rem; line-height: 1.5;">
        Join our growing community of environmentally-conscious citizens, researchers, activists, and policymakers.
        Share your insights, contribute data, and collaborate on solutions to our planet's most pressing environmental challenges.
    </p>
    <div style="display: flex; gap: 15px; margin-top: 15px; flex-wrap: wrap;">
        <div style="background-color: #3498db; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Contribute Data</h4>
            <p style="margin-bottom: 0;">Share your local observations</p>
        </div>
        <div style="background-color: #9b59b6; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Join Projects</h4>
            <p style="margin-bottom: 0;">Participate in citizen science</p>
        </div>
        <div style="background-color: #16a085; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Discussion Forum</h4>
            <p style="margin-bottom: 0;">Exchange ideas and solutions</p>
        </div>
        <div style="background-color: #e74c3c; color: white; padding: 12px; border-radius: 5px; flex: 1; text-align: center; min-width: 180px;">
            <h4 style="margin-top: 0;">Resource Library</h4>
            <p style="margin-bottom: 0;">Access educational materials</p>
        </div>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Community Contributions",
            content=community_intro_content
        ),
        unsafe_allow_html=True
    )
    
    # Submit observations section
    st.markdown("<br>", unsafe_allow_html=True)
    
    observation_submit_content = """
    <p>
        Submit your local environmental observations to contribute to our global dataset.
        Whether you're tracking local weather patterns, monitoring wildlife, or observing changes
        in your local ecosystem, your data helps build a more complete picture of planetary health.
    </p>
    """
    
    st.markdown(
        card_html.format(
            title="Submit Environmental Observations",
            content=observation_submit_content
        ),
        unsafe_allow_html=True
    )
    
    # Observation form
    with st.form("observation_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Name (optional)")
            email = st.text_input("Email (optional)")
            location = st.text_input("Location", placeholder="City, Country")
            
        with col2:
            category = st.selectbox("Observation Category", 
                ["Climate", "Biodiversity", "Pollution", "Ecosystem", "Other"])
            date = st.date_input("Observation Date")
            
        description = st.text_area("Observation Description", 
            placeholder="Describe what you observed in detail...",
            height=150)
        
        file_upload = st.file_uploader("Upload Photos or Data Files (optional)", 
                                    type=["jpg", "png", "csv", "xlsx"])
        
        agree = st.checkbox("I agree that this observation can be used for research and displayed publicly (without personal information)")
        
        submit_button = st.form_submit_button("Submit Observation")
        
        if submit_button and agree and location and description:
            st.success("Thank you for your contribution! Your observation has been recorded.")
        elif submit_button:
            st.error("Please fill out the required fields and agree to the terms.")
    
    # Community projects section
    st.markdown("<br>", unsafe_allow_html=True)
    
    projects_content = """
    <p>
        Join active citizen science projects that are making a difference. These community-led
        initiatives contribute valuable data while bringing people together for environmental action.
    </p>
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 20px;">
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: #f8f9fa;">
            <h4 style="color: #3498db;">Global Bird Count</h4>
            <p>Help track bird populations and migration patterns through seasonal counting events.</p>
            <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                <span style="background-color: #e8f4f8; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem;">Biodiversity</span>
                <span style="background-color: #e8f4f8; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem;">Ongoing</span>
            </div>
        </div>
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: #f8f9fa;">
            <h4 style="color: #e74c3c;">Urban Heat Mapping</h4>
            <p>Document urban heat islands in your city to help develop cooling strategies and resilience plans.</p>
            <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                <span style="background-color: #f9ebea; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem;">Climate</span>
                <span style="background-color: #f9ebea; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem;">Summer 2025</span>
            </div>
        </div>
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; padding: 15px; background-color: #f8f9fa;">
            <h4 style="color: #16a085;">Microplastics Monitor</h4>
            <p>Collect samples from local waterways to help researchers track the spread of microplastics.</p>
            <div style="display: flex; justify-content: space-between; margin-top: 15px;">
                <span style="background-color: #e8f8f5; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem;">Pollution</span>
                <span style="background-color: #e8f8f5; padding: 3px 8px; border-radius: 4px; font-size: 0.8rem;">Monthly</span>
            </div>
        </div>
    </div>
    <div style="margin-top: 20px; text-align: center;">
        <a href="#" style="display: inline-block; background-color: #3498db; color: white; padding: 8px 15px; border-radius: 4px; text-decoration: none;">View All Projects</a>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Citizen Science Projects",
            content=projects_content
        ),
        unsafe_allow_html=True
    )
    
    # Discussion forum preview
    st.markdown("<br>", unsafe_allow_html=True)
    
    forum_content = """
    <p>
        Join the conversation with researchers, activists, and citizens around the world.
        Share ideas, ask questions, and collaborate on solutions to environmental challenges.
    </p>
    
    <div style="margin-top: 20px;">
        <div style="border-bottom: 1px solid #e0e0e0; padding-bottom: 15px; margin-bottom: 15px;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #3498db; color: white; display: flex; align-items: center; justify-content: center; margin-right: 15px;">JD</div>
                <div>
                    <div style="font-weight: 600;">Jane Doe</div>
                    <div style="font-size: 0.8rem; color: #7f8c8d;">Posted yesterday</div>
                </div>
            </div>
            <h4 style="margin-top: 0;">Local Solutions to Urban Heat Islands</h4>
            <p>I've been researching urban cooling strategies in my city. Has anyone implemented green roofs or urban forests with measurable temperature reductions?</p>
            <div style="font-size: 0.9rem; color: #7f8c8d;">12 replies • Climate Solutions</div>
        </div>
        
        <div style="border-bottom: 1px solid #e0e0e0; padding-bottom: 15px; margin-bottom: 15px;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #16a085; color: white; display: flex; align-items: center; justify-content: center; margin-right: 15px;">MS</div>
                <div>
                    <div style="font-weight: 600;">Michael Smith</div>
                    <div style="font-size: 0.8rem; color: #7f8c8d;">Posted 3 days ago</div>
                </div>
            </div>
            <h4 style="margin-top: 0;">Community Coral Restoration Progress</h4>
            <p>Our volunteer team has been working on coral restoration in the Pacific. Here are some early results and challenges we've encountered.</p>
            <div style="font-size: 0.9rem; color: #7f8c8d;">8 replies • Ecosystem Restoration</div>
        </div>
        
        <div style="padding-bottom: 15px;">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <div style="width: 40px; height: 40px; border-radius: 50%; background-color: #e74c3c; color: white; display: flex; align-items: center; justify-content: center; margin-right: 15px;">AL</div>
                <div>
                    <div style="font-weight: 600;">Dr. Ana Lopez</div>
                    <div style="font-size: 0.8rem; color: #7f8c8d;">Posted 1 week ago</div>
                </div>
            </div>
            <h4 style="margin-top: 0;">New Study on Biodiversity Loss in Tropical Regions</h4>
            <p>I'd like to share our recent research on biodiversity loss in tropical regions and discuss potential conservation strategies.</p>
            <div style="font-size: 0.9rem; color: #7f8c8d;">24 replies • Research & Science</div>
        </div>
    </div>
    
    <div style="margin-top: 20px; text-align: center;">
        <a href="#" style="display: inline-block; background-color: #3498db; color: white; padding: 8px 15px; border-radius: 4px; text-decoration: none;">Join the Discussion</a>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Discussion Forum",
            content=forum_content
        ),
        unsafe_allow_html=True
    )
    
    # Resources section
    st.markdown("<br>", unsafe_allow_html=True)
    
    resources_content = """
    <p>
        Access educational resources, research papers, and action guides to deepen your understanding
        and take effective environmental action.
    </p>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-top: 20px;">
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
            <div style="height: 120px; background-color: #3498db; display: flex; align-items: center; justify-content: center; color: white;">
                <span style="font-size: 2rem;">📚</span>
            </div>
            <div style="padding: 15px;">
                <h4 style="margin-top: 0;">Research Papers</h4>
                <p>Access the latest peer-reviewed research on climate change, biodiversity, and environmental solutions.</p>
                <a href="#" style="color: #3498db; text-decoration: none; font-weight: 500;">Browse Papers →</a>
            </div>
        </div>
        
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
            <div style="height: 120px; background-color: #9b59b6; display: flex; align-items: center; justify-content: center; color: white;">
                <span style="font-size: 2rem;">🎓</span>
            </div>
            <div style="padding: 15px;">
                <h4 style="margin-top: 0;">Educational Materials</h4>
                <p>Lesson plans, activities, and educational videos suitable for various ages and learning contexts.</p>
                <a href="#" style="color: #3498db; text-decoration: none; font-weight: 500;">View Materials →</a>
            </div>
        </div>
        
        <div style="border: 1px solid #e0e0e0; border-radius: 8px; overflow: hidden;">
            <div style="height: 120px; background-color: #27ae60; display: flex; align-items: center; justify-content: center; color: white;">
                <span style="font-size: 2rem;">🌱</span>
            </div>
            <div style="padding: 15px;">
                <h4 style="margin-top: 0;">Action Guides</h4>
                <p>Practical guides for individual and community action, from reducing your carbon footprint to advocacy.</p>
                <a href="#" style="color: #3498db; text-decoration: none; font-weight: 500;">Explore Guides →</a>
            </div>
        </div>
    </div>
    """
    
    st.markdown(
        card_html.format(
            title="Resource Library",
            content=resources_content
        ),
        unsafe_allow_html=True
    )
    
    # Newsletter signup
    st.markdown("<br>", unsafe_allow_html=True)
    
    newsletter_content = """
    <p style="font-size: 1.1rem; text-align: center; margin-bottom: 25px;">
        Stay updated with the latest environmental data, community projects, and action opportunities.
    </p>
    """
    
    st.markdown(
        card_html.format(
            title="Join Our Newsletter",
            content=newsletter_content
        ),
        unsafe_allow_html=True
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("newsletter_form"):
            email = st.text_input("Email Address")
            interests = st.multiselect("Areas of Interest", 
                ["Climate Change", "Biodiversity", "Pollution", "Ecosystem Restoration", 
                 "Sustainable Living", "Policy & Advocacy"])
            
            subscribe = st.form_submit_button("Subscribe")
            
            if subscribe and email:
                st.success("Thanks for subscribing! Check your email to confirm your subscription.")
            elif subscribe:
                st.error("Please enter your email address.")

# Run the app
if __name__ == "__main__":
    main()