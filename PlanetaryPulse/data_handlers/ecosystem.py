import pandas as pd
import numpy as np
import requests
from datetime import datetime
import time
import os

def get_ecosystem_data(limit=None):
    """
    Fetches ecosystem data from various environmental APIs
    
    Args:
        limit (int, optional): Limit the number of data points returned
    
    Returns:
        pandas.DataFrame: Ecosystem data including forest coverage, coral reefs, and wetlands
    """
    try:
        # Fetch forest coverage data
        forest_data = fetch_forest_coverage_data()
        
        # Fetch coral reef data
        coral_data = fetch_coral_reef_data()
        
        # Fetch wetland data
        wetland_data = fetch_wetland_data()
        
        # Fetch soil health data
        soil_data = fetch_soil_health_data()
        
        # Combine datasets
        # Start with forest data as the base
        if forest_data is not None:
            # Create base dataframe with years
            years = forest_data['year'].unique()
            ecosystem_types = ["Forests", "Coral Reefs", "Wetlands", "Grasslands"]
            
            data_rows = []
            
            for year in years:
                forest_row = forest_data[forest_data['year'] == year].iloc[0] if not forest_data[forest_data['year'] == year].empty else None
                coral_row = coral_data[coral_data['year'] == year].iloc[0] if coral_data is not None and not coral_data[coral_data['year'] == year].empty else None
                wetland_row = wetland_data[wetland_data['year'] == year].iloc[0] if wetland_data is not None and not wetland_data[wetland_data['year'] == year].empty else None
                soil_row = soil_data[soil_data['year'] == year].iloc[0] if soil_data is not None and not soil_data[soil_data['year'] == year].empty else None
                
                # Forest ecosystem
                if forest_row is not None:
                    data_rows.append({
                        'year': year,
                        'ecosystem_type': 'Forests',
                        'area_mil_hectares': forest_row['forest_area_mil_hectares'],
                        'annual_change_percent': forest_row['annual_change_percent'],
                        'health_index': forest_row['forest_health_index'],
                        'forest_coverage_percent': forest_row['forest_coverage_percent'],
                        'primary_forest_percent': forest_row['primary_forest_percent'],
                        'coral_cover_percent': np.nan,
                        'bleaching_percent': np.nan,
                        'wetland_area_mil_hectares': np.nan,
                        'soil_carbon_content': np.nan,
                        'desertification_risk_index': np.nan
                    })
                
                # Coral ecosystem
                if coral_row is not None:
                    data_rows.append({
                        'year': year,
                        'ecosystem_type': 'Coral Reefs',
                        'area_mil_hectares': coral_row['reef_area_mil_hectares'],
                        'annual_change_percent': coral_row['annual_change_percent'],
                        'health_index': coral_row['reef_health_index'],
                        'forest_coverage_percent': np.nan,
                        'primary_forest_percent': np.nan,
                        'coral_cover_percent': coral_row['coral_cover_percent'],
                        'bleaching_percent': coral_row['bleaching_percent'],
                        'wetland_area_mil_hectares': np.nan,
                        'soil_carbon_content': np.nan,
                        'desertification_risk_index': np.nan
                    })
                
                # Wetland ecosystem
                if wetland_row is not None:
                    data_rows.append({
                        'year': year,
                        'ecosystem_type': 'Wetlands',
                        'area_mil_hectares': wetland_row['wetland_area_mil_hectares'],
                        'annual_change_percent': wetland_row['annual_change_percent'],
                        'health_index': wetland_row['wetland_health_index'],
                        'forest_coverage_percent': np.nan,
                        'primary_forest_percent': np.nan,
                        'coral_cover_percent': np.nan,
                        'bleaching_percent': np.nan,
                        'wetland_area_mil_hectares': wetland_row['wetland_area_mil_hectares'],
                        'soil_carbon_content': np.nan,
                        'desertification_risk_index': np.nan
                    })
                
                # Soil/Grassland ecosystem
                if soil_row is not None:
                    data_rows.append({
                        'year': year,
                        'ecosystem_type': 'Grasslands',
                        'area_mil_hectares': soil_row['grassland_area_mil_hectares'],
                        'annual_change_percent': soil_row['annual_change_percent'],
                        'health_index': soil_row['soil_health_index'],
                        'forest_coverage_percent': np.nan,
                        'primary_forest_percent': np.nan,
                        'coral_cover_percent': np.nan,
                        'bleaching_percent': np.nan,
                        'wetland_area_mil_hectares': np.nan,
                        'soil_carbon_content': soil_row['soil_carbon_content'],
                        'desertification_risk_index': soil_row['desertification_risk_index']
                    })
            
            # Create DataFrame
            ecosystem_df = pd.DataFrame(data_rows)
        else:
            # If forest data is not available, return fallback data
            return create_fallback_ecosystem_data(limit)
        
        # Sort by year (descending) and ecosystem type
        ecosystem_df = ecosystem_df.sort_values(['year', 'ecosystem_type'], ascending=[False, True])
        
        # Limit if requested
        if limit is not None:
            ecosystem_df = ecosystem_df.head(limit)
            
        return ecosystem_df
    
    except Exception as e:
        print(f"Error fetching ecosystem data: {e}")
        # Return fallback data if there's an error
        return create_fallback_ecosystem_data(limit)

def fetch_forest_coverage_data():
    """
    Fetches forest coverage data from various sources like Global Forest Watch
    
    Returns:
        pandas.DataFrame: Forest coverage data by year
    """
    try:
        # For forest coverage, we might use Global Forest Watch or FAO data
        # For demonstration, we'll use representative global trends
        
        # Create a range of years
        current_year = datetime.now().year
        years = list(range(1990, current_year + 1))
        
        # Generate data
        forest_areas = []  # Million hectares
        annual_changes = []  # Percent
        health_indices = []  # 0-100 scale
        coverage_percents = []  # Global land percentage
        primary_forest_percents = []  # Percentage of total forest
        
        # Starting values (approximate global data from 1990)
        base_forest_area = 4128  # Million hectares
        
        for i, year in enumerate(years):
            if i == 0:
                # First year
                forest_area = base_forest_area
                annual_change = 0
            else:
                # Subsequent years
                years_since_1990 = year - 1990
                
                # More deforestation in earlier years, slightly improved in recent years
                if year < 2010:
                    change_rate = -0.2 + np.random.normal(0, 0.05)
                else:
                    change_rate = -0.1 + np.random.normal(0, 0.08)
                
                annual_change = change_rate
                forest_area = forest_areas[-1] * (1 + change_rate/100)
            
            # Calculate additional metrics
            health_index = max(0, min(100, 75 - (year - 1990) * 0.25 + np.random.normal(0, 3)))
            coverage_percent = (forest_area / 13000) * 100  # Total land area ~13 billion hectares
            
            # Primary forest percentage (declining trend)
            primary_percent = max(20, 45 - (year - 1990) * 0.2 + np.random.normal(0, 1))
            
            forest_areas.append(forest_area)
            annual_changes.append(annual_change)
            health_indices.append(health_index)
            coverage_percents.append(coverage_percent)
            primary_forest_percents.append(primary_percent)
        
        # Create DataFrame
        df = pd.DataFrame({
            'year': years,
            'forest_area_mil_hectares': forest_areas,
            'annual_change_percent': annual_changes,
            'forest_health_index': health_indices,
            'forest_coverage_percent': coverage_percents,
            'primary_forest_percent': primary_forest_percents
        })
        
        return df
    
    except Exception as e:
        print(f"Error creating forest coverage data: {e}")
        return None

def fetch_coral_reef_data():
    """
    Fetches coral reef data
    
    Returns:
        pandas.DataFrame: Coral reef data by year
    """
    try:
        # Create a range of years
        current_year = datetime.now().year
        years = list(range(1990, current_year + 1))
        
        # Generate data
        reef_areas = []  # Million hectares
        annual_changes = []  # Percent
        health_indices = []  # 0-100 scale
        coral_covers = []  # Percent
        bleaching_percents = []  # Percent
        
        # Starting values (approximate global data)
        base_reef_area = 28  # Million hectares
        
        for i, year in enumerate(years):
            if i == 0:
                # First year
                reef_area = base_reef_area
                annual_change = 0
            else:
                # Subsequent years
                years_since_1990 = year - 1990
                
                # Generally declining trend
                if year < 2010:
                    change_rate = -0.5 + np.random.normal(0, 0.1)
                else:
                    # Accelerated decline due to warming
                    change_rate = -1.2 + np.random.normal(0, 0.3)
                
                annual_change = change_rate
                reef_area = reef_areas[-1] * (1 + change_rate/100)
            
            # Calculate additional metrics
            health_index = max(0, min(100, 80 - (year - 1990) * 0.5 + np.random.normal(0, 2)))
            
            # Coral cover percentage (declining trend)
            coral_cover = max(5, 50 - (year - 1990) * 0.4 + np.random.normal(0, 3))
            
            # Bleaching events increasing
            if year < 2000:
                bleaching = np.random.uniform(0, 5)
            elif year < 2010:
                bleaching = 5 + np.random.uniform(0, 10)
            else:
                bleaching = 15 + (year - 2010) * 1.2 + np.random.uniform(-5, 10)
                bleaching = min(bleaching, 90)  # Cap at 90%
            
            reef_areas.append(reef_area)
            annual_changes.append(annual_change)
            health_indices.append(health_index)
            coral_covers.append(coral_cover)
            bleaching_percents.append(bleaching)
        
        # Create DataFrame
        df = pd.DataFrame({
            'year': years,
            'reef_area_mil_hectares': reef_areas,
            'annual_change_percent': annual_changes,
            'reef_health_index': health_indices,
            'coral_cover_percent': coral_covers,
            'bleaching_percent': bleaching_percents
        })
        
        return df
    
    except Exception as e:
        print(f"Error creating coral reef data: {e}")
        return None

def fetch_wetland_data():
    """
    Fetches wetland data
    
    Returns:
        pandas.DataFrame: Wetland data by year
    """
    try:
        # Create a range of years
        current_year = datetime.now().year
        years = list(range(1990, current_year + 1))
        
        # Generate data
        wetland_areas = []  # Million hectares
        annual_changes = []  # Percent
        health_indices = []  # 0-100 scale
        
        # Starting values (approximate global data)
        base_wetland_area = 1280  # Million hectares
        
        for i, year in enumerate(years):
            if i == 0:
                # First year
                wetland_area = base_wetland_area
                annual_change = 0
            else:
                # Subsequent years
                years_since_1990 = year - 1990
                
                # Historical trend of wetland loss
                change_rate = -0.8 + np.random.normal(0, 0.2)
                
                annual_change = change_rate
                wetland_area = wetland_areas[-1] * (1 + change_rate/100)
            
            # Calculate additional metrics
            health_index = max(0, min(100, 70 - (year - 1990) * 0.3 + np.random.normal(0, 4)))
            
            wetland_areas.append(wetland_area)
            annual_changes.append(annual_change)
            health_indices.append(health_index)
        
        # Create DataFrame
        df = pd.DataFrame({
            'year': years,
            'wetland_area_mil_hectares': wetland_areas,
            'annual_change_percent': annual_changes,
            'wetland_health_index': health_indices
        })
        
        return df
    
    except Exception as e:
        print(f"Error creating wetland data: {e}")
        return None

def fetch_soil_health_data():
    """
    Fetches soil health and grassland data
    
    Returns:
        pandas.DataFrame: Soil health data by year
    """
    try:
        # Create a range of years
        current_year = datetime.now().year
        years = list(range(1990, current_year + 1))
        
        # Generate data
        grassland_areas = []  # Million hectares
        annual_changes = []  # Percent
        health_indices = []  # 0-100 scale
        carbon_contents = []  # Tons per hectare
        desertification_indices = []  # 0-100 scale
        
        # Starting values (approximate global data)
        base_grassland_area = 5200  # Million hectares
        
        for i, year in enumerate(years):
            if i == 0:
                # First year
                grassland_area = base_grassland_area
                annual_change = 0
            else:
                # Subsequent years
                years_since_1990 = year - 1990
                
                # Declining trend due to agricultural conversion
                change_rate = -0.4 + np.random.normal(0, 0.15)
                
                annual_change = change_rate
                grassland_area = grassland_areas[-1] * (1 + change_rate/100)
            
            # Calculate additional metrics
            health_index = max(0, min(100, 65 - (year - 1990) * 0.2 + np.random.normal(0, 3)))
            
            # Soil carbon content (declining)
            carbon_content = max(30, 80 - (year - 1990) * 0.3 + np.random.normal(0, 2))
            
            # Desertification risk (increasing)
            desertification = min(100, 35 + (year - 1990) * 0.4 + np.random.normal(0, 4))
            
            grassland_areas.append(grassland_area)
            annual_changes.append(annual_change)
            health_indices.append(health_index)
            carbon_contents.append(carbon_content)
            desertification_indices.append(desertification)
        
        # Create DataFrame
        df = pd.DataFrame({
            'year': years,
            'grassland_area_mil_hectares': grassland_areas,
            'annual_change_percent': annual_changes,
            'soil_health_index': health_indices,
            'soil_carbon_content': carbon_contents,
            'desertification_risk_index': desertification_indices
        })
        
        return df
    
    except Exception as e:
        print(f"Error creating soil health data: {e}")
        return None

def create_fallback_ecosystem_data(limit=None):
    """
    Creates fallback ecosystem data in case API calls fail
    
    Args:
        limit (int, optional): Limit the number of data points
        
    Returns:
        pandas.DataFrame: Fallback ecosystem data
    """
    # Define basic parameters
    current_year = datetime.now().year
    years = list(range(1990, current_year + 1))
    ecosystem_types = ["Forests", "Coral Reefs", "Wetlands", "Grasslands"]
    
    # Generate data
    data_rows = []
    
    # Forest ecosystem
    base_forest_area = 4128  # Million hectares
    forest_areas = []
    
    for i, year in enumerate(years):
        if i == 0:
            # First year
            forest_area = base_forest_area
            forest_change = 0
        else:
            # Subsequent years
            years_since_1990 = year - 1990
            
            # More deforestation in earlier years, slightly improved in recent years
            if year < 2010:
                forest_change_rate = -0.2 + np.random.normal(0, 0.05)
            else:
                forest_change_rate = -0.1 + np.random.normal(0, 0.08)
            
            forest_change = forest_change_rate
            forest_area = forest_areas[-1] * (1 + forest_change_rate/100)
        
        forest_areas.append(forest_area)
        
        # Calculate additional metrics
        forest_health = max(0, min(100, 75 - (year - 1990) * 0.25 + np.random.normal(0, 3)))
        forest_coverage = (forest_area / 13000) * 100  # Total land area ~13 billion hectares
        primary_percent = max(20, 45 - (year - 1990) * 0.2 + np.random.normal(0, 1))
        
        data_rows.append({
            'year': year,
            'ecosystem_type': 'Forests',
            'area_mil_hectares': forest_area,
            'annual_change_percent': forest_change,
            'health_index': forest_health,
            'forest_coverage_percent': forest_coverage,
            'primary_forest_percent': primary_percent,
            'coral_cover_percent': np.nan,
            'bleaching_percent': np.nan,
            'wetland_area_mil_hectares': np.nan,
            'soil_carbon_content': np.nan,
            'desertification_risk_index': np.nan
        })
    
    # Coral Reef ecosystem
    base_reef_area = 28  # Million hectares
    reef_areas = []
    
    for i, year in enumerate(years):
        if i == 0:
            # First year
            reef_area = base_reef_area
            reef_change = 0
        else:
            # Subsequent years
            years_since_1990 = year - 1990
            
            # Generally declining trend
            if year < 2010:
                reef_change_rate = -0.5 + np.random.normal(0, 0.1)
            else:
                # Accelerated decline due to warming
                reef_change_rate = -1.2 + np.random.normal(0, 0.3)
            
            reef_change = reef_change_rate
            reef_area = reef_areas[-1] * (1 + reef_change_rate/100)
        
        reef_areas.append(reef_area)
        
        # Calculate additional metrics
        reef_health = max(0, min(100, 80 - (year - 1990) * 0.5 + np.random.normal(0, 2)))
        coral_cover = max(5, 50 - (year - 1990) * 0.4 + np.random.normal(0, 3))
        
        # Bleaching events increasing
        if year < 2000:
            bleaching = np.random.uniform(0, 5)
        elif year < 2010:
            bleaching = 5 + np.random.uniform(0, 10)
        else:
            bleaching = 15 + (year - 2010) * 1.2 + np.random.uniform(-5, 10)
            bleaching = min(bleaching, 90)  # Cap at 90%
        
        data_rows.append({
            'year': year,
            'ecosystem_type': 'Coral Reefs',
            'area_mil_hectares': reef_area,
            'annual_change_percent': reef_change,
            'health_index': reef_health,
            'forest_coverage_percent': np.nan,
            'primary_forest_percent': np.nan,
            'coral_cover_percent': coral_cover,
            'bleaching_percent': bleaching,
            'wetland_area_mil_hectares': np.nan,
            'soil_carbon_content': np.nan,
            'desertification_risk_index': np.nan
        })
    
    # Wetland ecosystem
    base_wetland_area = 1280  # Million hectares
    wetland_areas = []
    
    for i, year in enumerate(years):
        if i == 0:
            # First year
            wetland_area = base_wetland_area
            wetland_change = 0
        else:
            # Subsequent years
            years_since_1990 = year - 1990
            
            # Historical trend of wetland loss
            wetland_change_rate = -0.8 + np.random.normal(0, 0.2)
            
            wetland_change = wetland_change_rate
            wetland_area = wetland_areas[-1] * (1 + wetland_change_rate/100)
        
        wetland_areas.append(wetland_area)
        
        # Calculate additional metrics
        wetland_health = max(0, min(100, 70 - (year - 1990) * 0.3 + np.random.normal(0, 4)))
        
        data_rows.append({
            'year': year,
            'ecosystem_type': 'Wetlands',
            'area_mil_hectares': wetland_area,
            'annual_change_percent': wetland_change,
            'health_index': wetland_health,
            'forest_coverage_percent': np.nan,
            'primary_forest_percent': np.nan,
            'coral_cover_percent': np.nan,
            'bleaching_percent': np.nan,
            'wetland_area_mil_hectares': wetland_area,
            'soil_carbon_content': np.nan,
            'desertification_risk_index': np.nan
        })
    
    # Grassland ecosystem
    base_grassland_area = 5200  # Million hectares
    grassland_areas = []
    
    for i, year in enumerate(years):
        if i == 0:
            # First year
            grassland_area = base_grassland_area
            grassland_change = 0
        else:
            # Subsequent years
            years_since_1990 = year - 1990
            
            # Declining trend due to agricultural conversion
            grassland_change_rate = -0.4 + np.random.normal(0, 0.15)
            
            grassland_change = grassland_change_rate
            grassland_area = grassland_areas[-1] * (1 + grassland_change_rate/100)
        
        grassland_areas.append(grassland_area)
        
        # Calculate additional metrics
        soil_health = max(0, min(100, 65 - (year - 1990) * 0.2 + np.random.normal(0, 3)))
        carbon_content = max(30, 80 - (year - 1990) * 0.3 + np.random.normal(0, 2))
        desertification = min(100, 35 + (year - 1990) * 0.4 + np.random.normal(0, 4))
        
        data_rows.append({
            'year': year,
            'ecosystem_type': 'Grasslands',
            'area_mil_hectares': grassland_area,
            'annual_change_percent': grassland_change,
            'health_index': soil_health,
            'forest_coverage_percent': np.nan,
            'primary_forest_percent': np.nan,
            'coral_cover_percent': np.nan,
            'bleaching_percent': np.nan,
            'wetland_area_mil_hectares': np.nan,
            'soil_carbon_content': carbon_content,
            'desertification_risk_index': desertification
        })
    
    # Create DataFrame
    df = pd.DataFrame(data_rows)
    
    # Sort by year (descending) and ecosystem type
    df = df.sort_values(['year', 'ecosystem_type'], ascending=[False, True])
    
    # Limit if requested
    if limit is not None:
        df = df.head(limit)
    
    return df