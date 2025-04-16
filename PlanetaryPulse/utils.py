import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from datetime import datetime, timedelta
import os
import folium
from folium.plugins import HeatMap
from streamlit_folium import folium_static
import base64
from io import BytesIO
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

def format_number(num, precision=1):
    """
    Format a number with appropriate suffixes (K, M, B, T) and precision
    
    Args:
        num (float): Number to format
        precision (int): Decimal precision
    
    Returns:
        str: Formatted number
    """
    if num is None or np.isnan(num):
        return "N/A"
    
    if abs(num) < 1_000:
        return f"{num:.{precision}f}"
    elif abs(num) < 1_000_000:
        return f"{num/1_000:.{precision}f}K"
    elif abs(num) < 1_000_000_000:
        return f"{num/1_000_000:.{precision}f}M"
    elif abs(num) < 1_000_000_000_000:
        return f"{num/1_000_000_000:.{precision}f}B"
    else:
        return f"{num/1_000_000_000_000:.{precision}f}T"

def get_color_from_value(value, min_val, max_val, reverse=False):
    """
    Get a color on a red-yellow-green scale based on a value
    
    Args:
        value (float): Value to map to a color
        min_val (float): Minimum value in range
        max_val (float): Maximum value in range
        reverse (bool): If True, reverse the color scale (green for low, red for high)
        
    Returns:
        str: Hex color code
    """
    if value is None or np.isnan(value):
        return "#CCCCCC"  # Gray for missing values
    
    # Normalize the value to be between 0 and 1
    normalized = (value - min_val) / (max_val - min_val)
    normalized = max(0, min(1, normalized))  # Clamp between 0 and 1
    
    # If reversed, flip the normalized value
    if reverse:
        normalized = 1 - normalized
    
    # Red-Yellow-Green color scale
    if normalized < 0.5:
        # Red to Yellow (0 to 0.5 normalized)
        r = 255
        g = int(255 * (normalized * 2))
        b = 0
    else:
        # Yellow to Green (0.5 to 1 normalized)
        r = int(255 * (1 - (normalized - 0.5) * 2))
        g = 255
        b = 0
    
    # Convert to hex
    return f"#{r:02x}{g:02x}{b:02x}"

def get_arrow_from_change(change):
    """
    Get an appropriate arrow symbol based on a change value
    
    Args:
        change (float): Change value
        
    Returns:
        str: Arrow symbol
    """
    if change is None or np.isnan(change):
        return "➡️"  # Neutral for missing values
    
    if change > 1:
        return "⬆️"  # Significant increase
    elif change > 0:
        return "↗️"  # Moderate increase
    elif change == 0:
        return "➡️"  # No change
    elif change > -1:
        return "↘️"  # Moderate decrease
    else:
        return "⬇️"  # Significant decrease

def display_trend_indicator(current, previous, is_better_when_higher=True):
    """
    Display a trend indicator with arrow and appropriate coloring
    
    Args:
        current (float): Current value
        previous (float): Previous value
        is_better_when_higher (bool): If True, higher values are better
    
    Returns:
        str: HTML for the trend indicator
    """
    if current is None or previous is None or np.isnan(current) or np.isnan(previous):
        return "No trend data"
    
    change = current - previous
    percent_change = (change / abs(previous)) * 100 if previous != 0 else 0
    
    if is_better_when_higher:
        is_improving = change > 0
    else:
        is_improving = change < 0
    
    arrow = get_arrow_from_change(change)
    color = "green" if is_improving else "red"
    
    return f"{arrow} <span style='color:{color}'>{abs(percent_change):.1f}%</span>"

def round_to_significant(x, sig=2):
    """
    Round a number to a specified number of significant figures
    
    Args:
        x (float): Number to round
        sig (int): Number of significant figures
        
    Returns:
        float: Rounded number
    """
    if x == 0:
        return 0
    
    return round(x, sig - int(np.floor(np.log10(abs(x)))) - 1)

def create_time_series_chart(df, x_col, y_col, title, color=None, y_label=None, legend_title=None, height=400):
    """
    Create a time series chart using Plotly
    
    Args:
        df (pandas.DataFrame): Data frame with the data
        x_col (str): Column name for x-axis
        y_col (str): Column name for y-axis
        title (str): Chart title
        color (str, optional): Column name for color
        y_label (str, optional): Label for y-axis
        legend_title (str, optional): Title for legend
        height (int, optional): Chart height
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    if color:
        fig = px.line(
            df, x=x_col, y=y_col, title=title, color=color, 
            height=height, markers=True
        )
    else:
        fig = px.line(
            df, x=x_col, y=y_col, title=title, 
            height=height, markers=True
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title=x_col.capitalize(),
        yaxis_title=y_label if y_label else y_col.replace('_', ' ').capitalize(),
        hovermode="x unified",
        legend_title=legend_title if legend_title else "",
        template="plotly_white",
    )
    
    # Update traces
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )
    
    return fig

def create_bar_chart(df, x_col, y_col, title, color=None, color_discrete_map=None, y_label=None, height=400):
    """
    Create a bar chart using Plotly
    
    Args:
        df (pandas.DataFrame): Data frame with the data
        x_col (str): Column name for x-axis
        y_col (str): Column name for y-axis
        title (str): Chart title
        color (str, optional): Column name for color
        color_discrete_map (dict, optional): Color mapping
        y_label (str, optional): Label for y-axis
        height (int, optional): Chart height
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    if color and color_discrete_map:
        fig = px.bar(
            df, x=x_col, y=y_col, title=title, color=color,
            color_discrete_map=color_discrete_map,
            height=height
        )
    elif color:
        fig = px.bar(
            df, x=x_col, y=y_col, title=title, color=color,
            height=height
        )
    else:
        fig = px.bar(
            df, x=x_col, y=y_col, title=title,
            height=height
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title=x_col.replace('_', ' ').capitalize(),
        yaxis_title=y_label if y_label else y_col.replace('_', ' ').capitalize(),
        template="plotly_white",
    )
    
    return fig

def create_pie_chart(df, values, names, title, height=400):
    """
    Create a pie chart using Plotly
    
    Args:
        df (pandas.DataFrame): Data frame with the data
        values (str): Column name for values
        names (str): Column name for names/labels
        title (str): Chart title
        height (int, optional): Chart height
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    fig = px.pie(
        df, values=values, names=names, title=title,
        height=height
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': title,
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        template="plotly_white",
    )
    
    # Update traces
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hole=0.4,
    )
    
    return fig

def create_gauge_chart(value, title, min_val=0, max_val=100, threshold_ranges=None, height=300):
    """
    Create a gauge chart using Plotly
    
    Args:
        value (float): Value to display
        title (str): Chart title
        min_val (float, optional): Minimum value for the gauge
        max_val (float, optional): Maximum value for the gauge
        threshold_ranges (list, optional): List of tuples with threshold ranges and colors
        height (int, optional): Chart height
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure
    """
    if threshold_ranges is None:
        # Default is a three-color gauge (red, yellow, green)
        threshold_ranges = [
            (min_val, min_val + (max_val - min_val) / 3, "red"),
            (min_val + (max_val - min_val) / 3, min_val + 2 * (max_val - min_val) / 3, "yellow"),
            (min_val + 2 * (max_val - min_val) / 3, max_val, "green"),
        ]
    
    # Create steps for the gauge
    steps = []
    for i, (low, high, color) in enumerate(threshold_ranges):
        steps.append({
            'range': [low, high],
            'color': color,
            'thickness': 0.75,
            'line': {
                'color': "white",
                'width': 2
            }
        })
    
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [min_val, max_val]},
            'bar': {'color': "darkblue"},
            'steps': steps,
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    # Update layout
    fig.update_layout(
        height=height,
        margin=dict(l=20, r=20, t=40, b=20),
    )
    
    return fig

def get_country_coordinates():
    """
    Get country center coordinates for map visualizations
    
    Returns:
        dict: Dictionary with country names as keys and [lat, lon] coordinates as values
    """
    # This is a simplified list of country coordinates
    return {
        "Afghanistan": [33.93911, 67.709953],
        "Albania": [41.153332, 20.168331],
        "Algeria": [28.033886, 1.659626],
        "Angola": [-11.202692, 17.873887],
        "Argentina": [-38.416097, -63.616672],
        "Australia": [-25.274398, 133.775136],
        "Austria": [47.516231, 14.550072],
        "Bangladesh": [23.684994, 90.356331],
        "Belarus": [53.709807, 27.953389],
        "Belgium": [50.503887, 4.469936],
        "Bolivia": [-16.290154, -63.588653],
        "Brazil": [-14.235004, -51.92528],
        "Cambodia": [12.565679, 104.990963],
        "Cameroon": [7.369722, 12.354722],
        "Canada": [56.130366, -106.346771],
        "Chile": [-35.675147, -71.542969],
        "China": [35.86166, 104.195397],
        "Colombia": [4.570868, -74.297333],
        "Costa Rica": [9.748917, -83.753428],
        "Cuba": [21.521757, -77.781167],
        "Democratic Republic of the Congo": [-4.038333, 21.758664],
        "Denmark": [56.26392, 9.501785],
        "Ecuador": [-1.831239, -78.183406],
        "Egypt": [26.820553, 30.802498],
        "Ethiopia": [9.145, 40.489673],
        "Finland": [61.92411, 25.748151],
        "France": [46.227638, 2.213749],
        "Germany": [51.165691, 10.451526],
        "Ghana": [7.946527, -1.023194],
        "Greece": [39.074208, 21.824312],
        "Guatemala": [15.783471, -90.230759],
        "Honduras": [15.199999, -86.241905],
        "Hungary": [47.162494, 19.503304],
        "Iceland": [64.963051, -19.020835],
        "India": [20.593684, 78.96288],
        "Indonesia": [-0.789275, 113.921327],
        "Iran": [32.427908, 53.688046],
        "Iraq": [33.223191, 43.679291],
        "Ireland": [53.41291, -8.24389],
        "Israel": [31.046051, 34.851612],
        "Italy": [41.87194, 12.56738],
        "Japan": [36.204824, 138.252924],
        "Kazakhstan": [48.019573, 66.923684],
        "Kenya": [-0.023559, 37.906193],
        "Madagascar": [-18.766947, 46.869107],
        "Malaysia": [4.210484, 101.975766],
        "Mexico": [23.634501, -102.552784],
        "Morocco": [31.791702, -7.09262],
        "Myanmar": [21.913965, 95.956223],
        "Nepal": [28.394857, 84.124008],
        "Netherlands": [52.132633, 5.291266],
        "New Zealand": [-40.900557, 174.885971],
        "Nigeria": [9.081999, 8.675277],
        "North Korea": [40.339852, 127.510093],
        "Norway": [60.472024, 8.468946],
        "Pakistan": [30.375321, 69.345116],
        "Peru": [-9.189967, -75.015152],
        "Philippines": [12.879721, 121.774017],
        "Poland": [51.919438, 19.145136],
        "Portugal": [39.399872, -8.224454],
        "Romania": [45.943161, 24.96676],
        "Russia": [61.52401, 105.318756],
        "Saudi Arabia": [23.885942, 45.079162],
        "Serbia": [44.016521, 21.005859],
        "Singapore": [1.352083, 103.819836],
        "South Africa": [-30.559482, 22.937506],
        "South Korea": [35.907757, 127.766922],
        "Spain": [40.463667, -3.74922],
        "Sri Lanka": [7.873054, 80.771797],
        "Sudan": [12.862807, 30.217636],
        "Sweden": [60.128161, 18.643501],
        "Switzerland": [46.818188, 8.227512],
        "Syria": [34.802075, 38.996815],
        "Taiwan": [23.69781, 120.960515],
        "Thailand": [15.870032, 100.992541],
        "Turkey": [38.963745, 35.243322],
        "Ukraine": [48.379433, 31.16558],
        "United Arab Emirates": [23.424076, 53.847818],
        "United Kingdom": [55.378051, -3.435973],
        "United States": [37.09024, -95.712891],
        "Venezuela": [6.42375, -66.58973],
        "Vietnam": [14.058324, 108.277199],
        "Zimbabwe": [-19.015438, 29.154857]
    }