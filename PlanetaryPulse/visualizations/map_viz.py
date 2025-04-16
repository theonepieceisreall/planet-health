import streamlit as st
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import folium_static
import plotly.express as px
import plotly.graph_objects as go
from utils import get_country_coordinates

def show_global_indicators_map(indicator="Temperature Anomalies", height=600):
    """
    Display a global map with various environmental indicators
    
    Args:
        indicator (str): The indicator to display on the map
        height (int): Height of the map in pixels
    """
    # Default center of map
    default_lat, default_lon = 20.0, 0.0
    default_zoom = 2
    
    # Create the map
    m = folium.Map(
        location=[default_lat, default_lon],
        zoom_start=default_zoom,
        tiles="CartoDB positron"
    )
    
    # Get country coordinates
    country_coords = get_country_coordinates()
    
    if indicator == "Temperature Anomalies":
        # Create temperature anomalies map
        create_temperature_anomaly_map(m, country_coords)
    elif indicator == "Air Quality Index":
        # Create air quality map
        create_air_quality_map(m, country_coords)
    elif indicator == "Deforestation Rate":
        # Create deforestation map
        create_deforestation_map(m, country_coords)
    elif indicator == "Biodiversity Status":
        # Create biodiversity status map
        create_biodiversity_map(m, country_coords)
    else:
        # Default to climate overview showing multiple indicators
        create_climate_overview_map(m, country_coords)
    
    # Add legend title based on indicator
    legend_title = f"{indicator} by Country"
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    # Display the map
    folium_static(m, width=None, height=height)
    
    # Show tip for using the map
    st.caption("💡 **Tip:** Hover over markers to see values. Use the controls in the upper right to toggle layers.")
    
    return m

def create_temperature_anomaly_map(m, country_coords):
    """
    Create a map showing temperature anomalies
    
    Args:
        m (folium.Map): Folium map object
        country_coords (dict): Dictionary of country coordinates
    """
    # Create marker cluster for temperature anomalies
    marker_cluster = MarkerCluster(name="Temperature Anomalies").add_to(m)
    
    # Create a list to hold heatmap data
    heat_data = []
    
    # Sample temperature anomaly data by country
    # In a real application, this would come from an API
    temp_anomalies = {
        "United States": 1.5,
        "Russia": 2.5,
        "China": 1.1,
        "Brazil": 0.9,
        "Australia": 1.8,
        "India": 0.7,
        "Canada": 2.3,
        "Saudi Arabia": 1.6,
        "Argentina": 1.0,
        "Kazakhstan": 2.1,
        "Algeria": 1.4,
        "Democratic Republic of the Congo": 0.8,
        # More countries...
    }
    
    # Determine min and max values for color scaling
    min_temp = min(temp_anomalies.values()) if temp_anomalies else 0
    max_temp = max(temp_anomalies.values()) if temp_anomalies else 3
    
    # Function to determine color based on temperature anomaly
    def get_color(value):
        if value < 0.5:
            return 'green'
        elif value < 1.0:
            return 'yellowgreen'
        elif value < 1.5:
            return 'yellow'
        elif value < 2.0:
            return 'orange'
        else:
            return 'red'
    
    # Add markers for each country
    for country, anomaly in temp_anomalies.items():
        if country in country_coords:
            lat, lon = country_coords[country]
            
            # Create popup content
            popup_content = f"""
            <div style="width: 200px">
                <h4>{country}</h4>
                <p><b>Temperature Anomaly:</b> {anomaly:.1f}°C</p>
                <p><b>Status:</b> {get_anomaly_interpretation(anomaly)}</p>
            </div>
            """
            
            # Add marker to cluster
            folium.CircleMarker(
                location=[lat, lon],
                radius=max(5, min(15, anomaly * 5)),  # Size based on anomaly
                color=get_color(anomaly),
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{country}: {anomaly:.1f}°C"
            ).add_to(marker_cluster)
            
            # Add data point for heat map
            heat_data.append([lat, lon, anomaly])
    
    # Create heatmap layer
    HeatMap(
        heat_data,
        name="Temperature Heatmap",
        radius=30,
        blur=20,
        gradient={
            '0.2': 'blue',
            '0.4': 'lime',
            '0.6': 'yellow',
            '0.8': 'orange',
            '1.0': 'red'
        },
        min_opacity=0.5
    ).add_to(m)
    
    # Add legend to explain colors
    add_temperature_legend(m)

def create_air_quality_map(m, country_coords):
    """
    Create a map showing air quality index
    
    Args:
        m (folium.Map): Folium map object
        country_coords (dict): Dictionary of country coordinates
    """
    # Create marker cluster for air quality
    marker_cluster = MarkerCluster(name="Air Quality Index").add_to(m)
    
    # Create a list to hold heatmap data
    heat_data = []
    
    # Sample air quality data by country
    # In a real application, this would come from an API
    aqi_data = {
        "China": 145,
        "India": 168,
        "United States": 47,
        "Indonesia": 120,
        "Pakistan": 175,
        "Brazil": 65,
        # More countries...
    }
    
    # Function to determine color based on AQI
    def get_aqi_color(aqi):
        if aqi <= 50:
            return 'green'
        elif aqi <= 100:
            return 'yellow'
        elif aqi <= 150:
            return 'orange'
        elif aqi <= 200:
            return 'red'
        elif aqi <= 300:
            return 'purple'
        else:
            return 'maroon'
    
    # Add markers for each country
    for country, aqi in aqi_data.items():
        if country in country_coords:
            lat, lon = country_coords[country]
            
            # Create popup content
            popup_content = f"""
            <div style="width: 200px">
                <h4>{country}</h4>
                <p><b>Air Quality Index:</b> {aqi}</p>
                <p><b>Category:</b> {get_aqi_category(aqi)}</p>
            </div>
            """
            
            # Add marker to cluster
            folium.CircleMarker(
                location=[lat, lon],
                radius=max(5, min(20, aqi / 10)),  # Size based on AQI
                color=get_aqi_color(aqi),
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{country}: AQI {aqi}"
            ).add_to(marker_cluster)
            
            # Add data point for heat map
            heat_data.append([lat, lon, min(aqi, 300) / 300])  # Normalize for heatmap
    
    # Create heatmap layer
    HeatMap(
        heat_data,
        name="AQI Heatmap",
        radius=30,
        blur=20,
        gradient={
            '0.2': 'green',
            '0.4': 'yellow',
            '0.6': 'orange',
            '0.8': 'red',
            '1.0': 'purple'
        },
        min_opacity=0.5
    ).add_to(m)
    
    # Add legend to explain colors
    add_aqi_legend(m)

def create_deforestation_map(m, country_coords):
    """
    Create a map showing deforestation rates
    
    Args:
        m (folium.Map): Folium map object
        country_coords (dict): Dictionary of country coordinates
    """
    # Create marker cluster for deforestation data
    marker_cluster = MarkerCluster(name="Deforestation Rates").add_to(m)
    
    # Create a list to hold heatmap data
    heat_data = []
    
    # Sample deforestation data by country (annual forest loss percentage)
    # In a real application, this would come from an API
    deforestation_data = {
        "Brazil": 0.48,
        "Indonesia": 0.63,
        "Democratic Republic of the Congo": 0.34,
        "Bolivia": 0.52,
        "Malaysia": 0.41,
        # More countries...
    }
    
    # Function to determine color based on deforestation rate
    def get_deforestation_color(rate):
        if rate <= 0:
            return 'green'  # Reforestation
        elif rate <= 0.2:
            return 'yellowgreen'
        elif rate <= 0.4:
            return 'yellow'
        elif rate <= 0.6:
            return 'orange'
        else:
            return 'red'
    
    # Add markers for each country
    for country, rate in deforestation_data.items():
        if country in country_coords:
            lat, lon = country_coords[country]
            
            # Create popup content
            popup_content = f"""
            <div style="width: 220px">
                <h4>{country}</h4>
                <p><b>Annual Forest Change Rate:</b> {rate:.2f}%</p>
                <p><b>Status:</b> {get_deforestation_interpretation(rate)}</p>
            </div>
            """
            
            # Add marker to cluster
            folium.CircleMarker(
                location=[lat, lon],
                radius=max(5, min(20, abs(rate) * 20)),  # Size based on rate
                color=get_deforestation_color(rate),
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{country}: {rate:.2f}%/year"
            ).add_to(marker_cluster)
            
            # Add data point for heat map (normalize to 0-1 range)
            normalized_value = min(1, (rate + 0.2) / 1.2)  # Adjust to include negative values
            heat_data.append([lat, lon, normalized_value])
    
    # Create heatmap layer
    HeatMap(
        heat_data,
        name="Deforestation Heatmap",
        radius=30,
        blur=20,
        gradient={
            '0.1': 'darkgreen',
            '0.3': 'green',
            '0.5': 'yellow',
            '0.7': 'orange',
            '0.9': 'red'
        },
        min_opacity=0.5
    ).add_to(m)
    
    # Add legend to explain colors
    add_deforestation_legend(m)

def create_biodiversity_map(m, country_coords):
    """
    Create a map showing biodiversity status
    
    Args:
        m (folium.Map): Folium map object
        country_coords (dict): Dictionary of country coordinates
    """
    # Create marker cluster for biodiversity data
    marker_cluster = MarkerCluster(name="Biodiversity Status").add_to(m)
    
    # Create a list to hold heatmap data
    heat_data = []
    
    # Sample biodiversity health score data by country (0-100 scale, higher is better)
    # In a real application, this would come from an API
    biodiversity_data = {
        "Brazil": 67,
        "Indonesia": 63,
        "Colombia": 76,
        "Madagascar": 54,
        "Peru": 73,
        # More countries...
    }
    
    # Function to determine color based on biodiversity score
    def get_biodiversity_color(score):
        if score >= 75:
            return 'green'
        elif score >= 60:
            return 'yellowgreen'
        elif score >= 45:
            return 'yellow'
        elif score >= 30:
            return 'orange'
        else:
            return 'red'
    
    # Add markers for each country
    for country, score in biodiversity_data.items():
        if country in country_coords:
            lat, lon = country_coords[country]
            
            # Create popup content
            popup_content = f"""
            <div style="width: 220px">
                <h4>{country}</h4>
                <p><b>Biodiversity Health Score:</b> {score}/100</p>
                <p><b>Status:</b> {get_biodiversity_interpretation(score)}</p>
            </div>
            """
            
            # Add marker to cluster
            folium.CircleMarker(
                location=[lat, lon],
                radius=max(5, min(15, score / 10)),  # Size based on score
                color=get_biodiversity_color(score),
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(popup_content, max_width=300),
                tooltip=f"{country}: Score {score}/100"
            ).add_to(marker_cluster)
            
            # Add data point for heat map
            normalized_value = score / 100  # Already on 0-100 scale
            heat_data.append([lat, lon, normalized_value])
    
    # Create heatmap layer
    HeatMap(
        heat_data,
        name="Biodiversity Heatmap",
        radius=30,
        blur=20,
        gradient={
            '0.2': 'red',
            '0.4': 'orange',
            '0.6': 'yellow',
            '0.8': 'yellowgreen',
            '1.0': 'green'
        },
        min_opacity=0.5
    ).add_to(m)
    
    # Add legend to explain colors
    add_biodiversity_legend(m)

def create_climate_overview_map(m, country_coords):
    """
    Create a map showing multiple climate indicators
    
    Args:
        m (folium.Map): Folium map object
        country_coords (dict): Dictionary of country coordinates
    """
    # Use temperature anomaly data as the default overview
    create_temperature_anomaly_map(m, country_coords)

def add_temperature_legend(m):
    """
    Add a legend for temperature anomaly colors
    
    Args:
        m (folium.Map): Folium map object
    """
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 180px; height: 150px; 
                border:2px solid grey; z-index:9999; font-size:12px;
                background-color: white; padding: 10px; border-radius: 5px">
        <div style="text-align: center; margin-bottom: 5px"><b>Temperature Anomaly</b></div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: green; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Less than 0.5°C</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: yellowgreen; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>0.5°C to 1.0°C</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: yellow; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>1.0°C to 1.5°C</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: orange; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>1.5°C to 2.0°C</div>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background-color: red; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Over 2.0°C</div>
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))

def add_aqi_legend(m):
    """
    Add a legend for air quality index colors
    
    Args:
        m (folium.Map): Folium map object
    """
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 180px; height: 180px; 
                border:2px solid grey; z-index:9999; font-size:12px;
                background-color: white; padding: 10px; border-radius: 5px">
        <div style="text-align: center; margin-bottom: 5px"><b>Air Quality Index</b></div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: green; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Good (0-50)</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: yellow; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Moderate (51-100)</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: orange; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Unhealthy for Sensitive Groups (101-150)</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: red; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Unhealthy (151-200)</div>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background-color: purple; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Very Unhealthy (201-300)</div>
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))

def add_deforestation_legend(m):
    """
    Add a legend for deforestation rate colors
    
    Args:
        m (folium.Map): Folium map object
    """
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 180px; height: 180px; 
                border:2px solid grey; z-index:9999; font-size:12px;
                background-color: white; padding: 10px; border-radius: 5px">
        <div style="text-align: center; margin-bottom: 5px"><b>Forest Change Rate</b></div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: green; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Reforestation (≤ 0%)</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: yellowgreen; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Low Loss (0-0.2%)</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: yellow; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Moderate Loss (0.2-0.4%)</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: orange; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>High Loss (0.4-0.6%)</div>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background-color: red; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Severe Loss (>0.6%)</div>
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))

def add_biodiversity_legend(m):
    """
    Add a legend for biodiversity status colors
    
    Args:
        m (folium.Map): Folium map object
    """
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; right: 50px; width: 180px; height: 180px; 
                border:2px solid grey; z-index:9999; font-size:12px;
                background-color: white; padding: 10px; border-radius: 5px">
        <div style="text-align: center; margin-bottom: 5px"><b>Biodiversity Health</b></div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: green; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Very Good (75-100)</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: yellowgreen; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Good (60-75)</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: yellow; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Moderate (45-60)</div>
        </div>
        <div style="display: flex; align-items: center; margin-bottom: 5px">
            <div style="background-color: orange; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Poor (30-45)</div>
        </div>
        <div style="display: flex; align-items: center;">
            <div style="background-color: red; width: 15px; height: 15px; margin-right: 5px"></div>
            <div>Critical (<30)</div>
        </div>
    </div>
    """
    
    m.get_root().html.add_child(folium.Element(legend_html))

def get_anomaly_interpretation(anomaly):
    """
    Get an interpretation of a temperature anomaly value
    
    Args:
        anomaly (float): Temperature anomaly in °C
        
    Returns:
        str: Interpretation of the anomaly
    """
    if anomaly < 0.5:
        return "Minor warming"
    elif anomaly < 1.0:
        return "Moderate warming"
    elif anomaly < 1.5:
        return "Significant warming"
    elif anomaly < 2.0:
        return "Severe warming"
    else:
        return "Extreme warming"

def get_aqi_category(aqi):
    """
    Get the category for an Air Quality Index value
    
    Args:
        aqi (int): Air Quality Index value
        
    Returns:
        str: Air quality category
    """
    if aqi <= 50:
        return "Good"
    elif aqi <= 100:
        return "Moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"
    elif aqi <= 200:
        return "Unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy"
    else:
        return "Hazardous"

def get_deforestation_interpretation(rate):
    """
    Get an interpretation of a deforestation rate
    
    Args:
        rate (float): Annual deforestation rate in percentage
        
    Returns:
        str: Interpretation of the rate
    """
    if rate <= -0.1:
        return "Strong reforestation"
    elif rate <= 0:
        return "Slight reforestation"
    elif rate <= 0.2:
        return "Low deforestation"
    elif rate <= 0.4:
        return "Moderate deforestation"
    elif rate <= 0.6:
        return "High deforestation"
    else:
        return "Severe deforestation"

def get_biodiversity_interpretation(score):
    """
    Get an interpretation of a biodiversity health score
    
    Args:
        score (int): Biodiversity health score (0-100)
        
    Returns:
        str: Interpretation of the score
    """
    if score >= 75:
        return "Very good biodiversity health"
    elif score >= 60:
        return "Good biodiversity health"
    elif score >= 45:
        return "Moderate biodiversity health"
    elif score >= 30:
        return "Poor biodiversity health"
    else:
        return "Critical biodiversity health"