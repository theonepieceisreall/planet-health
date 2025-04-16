import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from utils import create_time_series_chart, create_bar_chart, create_pie_chart, format_number, get_color_from_value

def show_biodiversity_visualizations(df, preview_mode=False):
    """
    Display biodiversity data visualizations
    
    Args:
        df (pandas.DataFrame): Biodiversity data
        preview_mode (bool): If True, show a condensed preview
    """
    # Get the data sorted by region for regional comparisons
    sorted_by_region = df.sort_values('region')
    
    # Get the data in chronological order for time series
    chronological_df = df.sort_values('year')
    
    # Get most recent data for each region
    latest_year = df['year'].max()
    latest_data = df[df['year'] == latest_year]
    
    if preview_mode:
        # Abbreviated version for overview page
        col1, col2 = st.columns(2)
        
        with col1:
            # Endangered species trend
            if 'endangered_species_count' in df.columns:
                # Filter for just one region or global data for the preview
                if 'region' in df.columns:
                    # If we have multiple regions, just use the first one for preview
                    regions = df['region'].unique()
                    if len(regions) > 0:
                        region_df = chronological_df[chronological_df['region'] == regions[0]]
                        fig = create_time_series_chart(
                            region_df, 'year', 'endangered_species_count',
                            f'Endangered Species Trend ({regions[0]})',
                            height=300
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    fig = create_time_series_chart(
                        chronological_df, 'year', 'endangered_species_count',
                        'Endangered Species Trend',
                        height=300
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Endangered species data not available")
        
        with col2:
            # Conservation status visualization
            if 'conservation_status_index' in df.columns:
                if 'region' in df.columns and len(latest_data) > 0:
                    fig = px.bar(
                        latest_data.sort_values('conservation_status_index'),
                        x='region', 
                        y='conservation_status_index',
                        title=f'Conservation Status by Region ({latest_year})',
                        height=300,
                        color='conservation_status_index',
                        color_continuous_scale=['red', 'yellow', 'green']
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Region-based conservation status data not available")
            else:
                st.warning("Conservation status data not available")
    
    else:
        # Full detailed view
        st.header("Endangered Species")
        
        # Endangered species visualization
        if 'endangered_species_count' in df.columns and 'region' in df.columns:
            # Current endangered species by region
            fig = px.bar(
                latest_data.sort_values('endangered_species_count', ascending=False),
                x='region', 
                y='endangered_species_count',
                title=f'Endangered Species by Region ({latest_year})',
                height=450,
                color='endangered_species_count',
                color_continuous_scale=['green', 'yellow', 'red']
            )
            
            fig.update_layout(
                xaxis_title="Region",
                yaxis_title="Number of Endangered Species",
                xaxis={'categoryorder':'total descending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Endangered Species Count** shows the number of species at risk of extinction in each region.
                
                - Higher counts indicate greater biodiversity threats
                - These counts include mammals, birds, reptiles, amphibians, fish, and invertebrates
                - Main drivers include habitat loss, climate change, pollution, and overexploitation
                """)
            
            # Show trends for selected regions
            st.subheader("Endangered Species Trends by Region")
            
            # Get unique regions for multiselect
            regions = sorted(df['region'].unique())
            
            # If there are many regions, limit default selection to avoid overwhelming the chart
            default_regions = regions[:3] if len(regions) > 3 else regions
            
            selected_regions = st.multiselect(
                "Select regions to compare:",
                options=regions,
                default=default_regions
            )
            
            if selected_regions:
                # Filter data for selected regions
                filtered_df = chronological_df[chronological_df['region'].isin(selected_regions)]
                
                # Create time series with regions as color
                fig = px.line(
                    filtered_df,
                    x='year',
                    y='endangered_species_count',
                    color='region',
                    title='Endangered Species Trends by Region',
                    height=450,
                    markers=True
                )
                
                fig.update_layout(
                    xaxis_title="Year",
                    yaxis_title="Number of Endangered Species",
                    legend_title="Region"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Calculate and display change rates
                st.subheader("Change in Endangered Species (Last Decade)")
                
                # Get data from 10 years ago for comparison
                comparison_year = latest_year - 10
                nearest_year = df[df['year'] <= comparison_year]['year'].max()
                
                if not pd.isna(nearest_year):
                    comparison_data = df[df['year'] == nearest_year]
                    
                    if not comparison_data.empty:
                        change_data = []
                        
                        for region in selected_regions:
                            # Get current and previous counts
                            current = latest_data[latest_data['region'] == region]['endangered_species_count'].iloc[0] if not latest_data[latest_data['region'] == region].empty else 0
                            previous = comparison_data[comparison_data['region'] == region]['endangered_species_count'].iloc[0] if not comparison_data[comparison_data['region'] == region].empty else 0
                            
                            if previous > 0:
                                percent_change = ((current - previous) / previous) * 100
                            else:
                                percent_change = 0
                                
                            change_data.append({
                                'region': region,
                                'percent_change': percent_change,
                                'absolute_change': current - previous
                            })
                        
                        change_df = pd.DataFrame(change_data)
                        
                        # Display changes in a horizontal bar chart
                        fig = px.bar(
                            change_df.sort_values('percent_change'),
                            y='region',
                            x='percent_change',
                            title=f'Percent Change in Endangered Species ({nearest_year} to {latest_year})',
                            height=100 + 50 * len(selected_regions),  # Adjust height based on number of regions
                            color='percent_change',
                            color_continuous_scale=['green', 'yellow', 'red'],
                            text='percent_change'
                        )
                        
                        fig.update_traces(
                            texttemplate='%{text:.1f}%',
                            textposition='outside'
                        )
                        
                        fig.update_layout(
                            yaxis_title="",
                            xaxis_title="Percent Change (%)"
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
        
        else:
            st.warning("Endangered species data not available by region")
        
        # Extinction rate visualization
        st.header("Extinction Rates")
        
        if 'extinction_rate' in df.columns and 'region' in df.columns:
            # Filter for the latest year
            extinction_data = latest_data.sort_values('extinction_rate', ascending=False)
            
            fig = px.bar(
                extinction_data,
                x='region',
                y='extinction_rate',
                title=f'Species Extinction Rate by Region ({latest_year})',
                height=450,
                color='extinction_rate',
                color_continuous_scale=['green', 'yellow', 'red']
            )
            
            fig.update_layout(
                xaxis_title="Region",
                yaxis_title="Extinction Rate (species/year)",
                xaxis={'categoryorder':'total descending'}
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Extinction Rate** measures the number of species lost per year.
                
                - The natural "background" extinction rate is estimated at 1-5 species per year
                - Current rates are 100-1,000 times higher than the background rate
                - This acceleration represents the Earth's sixth mass extinction event
                """)
            
            # Global average extinction rate
            avg_extinction_rate = latest_data['extinction_rate'].mean()
            st.info(f"🌍 The current global average extinction rate is approximately **{avg_extinction_rate:.2f} species per year**, which is significantly higher than the natural background rate.")
        
        else:
            st.warning("Extinction rate data not available")
        
        # Habitat loss visualization
        st.header("Habitat Loss")
        
        if 'remaining_habitat_mil_hectares' in df.columns and 'annual_habitat_loss_mil_hectares' in df.columns and 'region' in df.columns:
            col1, col2 = st.columns(2)
            
            with col1:
                # Remaining habitat by region
                fig = px.bar(
                    latest_data.sort_values('remaining_habitat_mil_hectares', ascending=False),
                    x='region',
                    y='remaining_habitat_mil_hectares',
                    title=f'Remaining Habitat by Region ({latest_year})',
                    height=400,
                    color='remaining_habitat_mil_hectares',
                    color_continuous_scale=['red', 'yellow', 'green']
                )
                
                fig.update_layout(
                    xaxis_title="Region",
                    yaxis_title="Remaining Habitat (million hectares)",
                    xaxis={'categoryorder':'total descending'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Annual habitat loss by region
                fig = px.bar(
                    latest_data.sort_values('annual_habitat_loss_mil_hectares', ascending=False),
                    x='region',
                    y='annual_habitat_loss_mil_hectares',
                    title=f'Annual Habitat Loss Rate ({latest_year})',
                    height=400,
                    color='annual_habitat_loss_mil_hectares',
                    color_continuous_scale=['green', 'yellow', 'red']
                )
                
                fig.update_layout(
                    xaxis_title="Region",
                    yaxis_title="Annual Loss (million hectares/year)",
                    xaxis={'categoryorder':'total descending'}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Habitat Loss** measures the destruction of natural environments that support biodiversity.
                
                - Habitat loss is the primary driver of species extinction
                - Main causes include deforestation, agriculture expansion, urbanization, and infrastructure development
                - The rate of loss varies significantly by region and ecosystem type
                """)
            
            # Global habitat loss trends
            if 'habitat_fragmentation_index' in df.columns:
                # Get data for all regions combined by year
                yearly_data = chronological_df.groupby('year').agg({
                    'remaining_habitat_mil_hectares': 'sum',
                    'annual_habitat_loss_mil_hectares': 'sum',
                    'habitat_fragmentation_index': 'mean'
                }).reset_index()
                
                # Create combined chart showing remaining habitat and fragmentation index
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                
                # Add remaining habitat trace
                fig.add_trace(
                    go.Scatter(
                        x=yearly_data['year'],
                        y=yearly_data['remaining_habitat_mil_hectares'],
                        name="Remaining Habitat",
                        line=dict(color='green', width=3)
                    ),
                    secondary_y=False
                )
                
                # Add fragmentation index trace
                fig.add_trace(
                    go.Scatter(
                        x=yearly_data['year'],
                        y=yearly_data['habitat_fragmentation_index'],
                        name="Fragmentation Index",
                        line=dict(color='red', width=3, dash='dot')
                    ),
                    secondary_y=True
                )
                
                # Update layout
                fig.update_layout(
                    title="Global Habitat Loss and Fragmentation Trends",
                    height=450,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    hovermode="x unified"
                )
                
                # Update axes
                fig.update_xaxes(title_text="Year")
                fig.update_yaxes(title_text="Remaining Habitat (million hectares)", secondary_y=False)
                fig.update_yaxes(title_text="Fragmentation Index (0-100)", secondary_y=True)
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Explanation of fragmentation
                st.markdown("""
                **Habitat Fragmentation** occurs when large, continuous habitats are divided into smaller, isolated patches.
                
                - Fragmentation reduces habitat quality and prevents species movement
                - Isolated populations are more vulnerable to extinction
                - The fragmentation index measures the degree of habitat fragmentation (higher values = more fragmented)
                """)
                
                # Calculate total habitat loss and rate
                if len(yearly_data) >= 2:
                    first_year = yearly_data['year'].iloc[0]
                    last_year = yearly_data['year'].iloc[-1]
                    first_habitat = yearly_data['remaining_habitat_mil_hectares'].iloc[0]
                    last_habitat = yearly_data['remaining_habitat_mil_hectares'].iloc[-1]
                    
                    total_loss = first_habitat - last_habitat
                    percent_loss = (total_loss / first_habitat) * 100
                    annual_rate = total_loss / (last_year - first_year)
                    
                    st.error(f"🌳 Since {first_year}, we have lost approximately **{total_loss:.1f} million hectares** of natural habitat ({percent_loss:.1f}%), at an average rate of **{annual_rate:.1f} million hectares per year**.")
        
        else:
            st.warning("Habitat loss data not available")
        
        # Species discovery visualization
        if 'new_species_discovered' in df.columns and 'cumulative_known_species' in df.columns and 'estimated_total_species' in df.columns:
            st.header("Species Discovery")
            
            # Species discovery chart
            yearly_discovery_data = chronological_df.drop_duplicates('year').sort_values('year')
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            # Add known species trace
            fig.add_trace(
                go.Scatter(
                    x=yearly_discovery_data['year'],
                    y=yearly_discovery_data['cumulative_known_species'],
                    name="Known Species",
                    line=dict(color='blue', width=3)
                ),
                secondary_y=False
            )
            
            # Add new discoveries trace
            fig.add_trace(
                go.Bar(
                    x=yearly_discovery_data['year'],
                    y=yearly_discovery_data['new_species_discovered'],
                    name="New Species Discovered",
                    marker_color='green'
                ),
                secondary_y=True
            )
            
            # Update layout
            fig.update_layout(
                title="Species Discovery Trend",
                height=450,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                hovermode="x unified"
            )
            
            # Update axes
            fig.update_xaxes(title_text="Year")
            fig.update_yaxes(title_text="Cumulative Known Species", secondary_y=False)
            fig.update_yaxes(title_text="New Species Discovered per Year", secondary_y=True)
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Species discovery gap
            latest_known = yearly_discovery_data['cumulative_known_species'].iloc[-1]
            latest_estimated = yearly_discovery_data['estimated_total_species'].iloc[-1]
            discovery_gap = latest_estimated - latest_known
            discovery_percent = (latest_known / latest_estimated) * 100
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Show pie chart of known vs unknown species
                pie_data = pd.DataFrame([
                    {'category': 'Known Species', 'count': latest_known},
                    {'category': 'Undiscovered Species', 'count': discovery_gap}
                ])
                
                fig = px.pie(
                    pie_data,
                    values='count',
                    names='category',
                    title=f'Known vs. Undiscovered Species ({latest_year})',
                    color='category',
                    color_discrete_map={
                        'Known Species': 'blue',
                        'Undiscovered Species': 'gray'
                    },
                    height=350
                )
                
                fig.update_traces(
                    textposition='inside',
                    textinfo='percent+label',
                    hole=0.4
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Show metrics
                st.metric("Known Species", f"{latest_known:,}")
                st.metric("Estimated Total Species", f"{latest_estimated:,}")
                st.metric("Undiscovered Species", f"{discovery_gap:,}")
                
                # Show discovery rate explanation
                avg_recent_discoveries = yearly_discovery_data.tail(5)['new_species_discovered'].mean()
                years_to_discover_all = discovery_gap / avg_recent_discoveries if avg_recent_discoveries > 0 else float('inf')
                
                st.info(f"🔍 Scientists have identified approximately **{discovery_percent:.1f}%** of all estimated species on Earth.")
                
                if years_to_discover_all < float('inf'):
                    st.warning(f"🔍 At the current discovery rate of **{avg_recent_discoveries:,.0f}** species per year, it would take about **{years_to_discover_all:.0f}** years to discover all remaining species (assuming they don't go extinct first).")
            
            with st.expander("What does this mean?"):
                st.markdown("""
                **Species Discovery** tracks our knowledge of Earth's biodiversity.
                
                - New species are still being discovered at a rate of thousands per year
                - Scientists estimate we've only identified a fraction of all species on Earth
                - Most undiscovered species are likely invertebrates, fungi, and microorganisms
                - Many species may go extinct before they're even discovered
                """)
        
        else:
            st.warning("Species discovery data not available")