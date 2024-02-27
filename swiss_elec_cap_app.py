import streamlit as st
import pandas as pd
import plotly.express as px
import json
from copy import deepcopy

# First some MPG Data Exploration
@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    return df

rpp_df_raw = load_data(path="./data/renewable_power_plants_CH.csv")
rpp_df = deepcopy(rpp_df_raw)

# Add title and header
st.title("Renewable Power Plants in Switzerland")
st.header("RPP Data Exploration")

# Widgets: checkbox (you can replace st.xx with st.sidebar.xx)
if st.checkbox("Show Dataframe"):
    st.subheader("This is my dataset:")
    st.dataframe(data=rpp_df)
    # st.table(data=mpg_df)


# Load GeoJSON data locally
geojson_path = "./data/georef-switzerland-kanton.geojson"
with open(geojson_path, 'r') as file:
    geojson_data = json.load(file)

cantons_dict = {
'TG':'Thurgau', 
'GR':'Graubünden', 
'LU':'Luzern', 
'BE':'Bern', 
'VS':'Valais',                
'BL':'Basel-Landschaft', 
'SO':'Solothurn', 
'VD':'Vaud', 
'SH':'Schaffhausen', 
'ZH':'Zürich', 
'AG':'Aargau', 
'UR':'Uri', 
'NE':'Neuchâtel', 
'TI':'Ticino', 
'SG':'St. Gallen', 
'GE':'Genève',
'GL':'Glarus', 
'JU':'Jura', 
'ZG':'Zug', 
'OW':'Obwalden', 
'FR':'Fribourg', 
'SZ':'Schwyz', 
'AR':'Appenzell Ausserrhoden', 
'AI':'Appenzell Innerrhoden', 
'NW':'Nidwalden', 
'BS':'Basel-Stadt'}

# Map 'canton' column to corresponding values
rpp_df['canton_name'] = rpp_df['canton'].map(cantons_dict)

# Widgets: selectbox
selected_energy_source = st.selectbox("Choose an Energy Source", ["All"] + sorted(rpp_df['energy_source_level_2'].unique()))

# Filter data for the selected energy source
if selected_energy_source == "All":
    total_capacity_per_canton_source = rpp_df.groupby(['canton_name', 'energy_source_level_2'])['electrical_capacity'].sum().reset_index()
else:
    source_data = rpp_df[rpp_df['energy_source_level_2'] == selected_energy_source]
    total_capacity_per_canton_source = source_data.groupby(['canton_name', 'energy_source_level_2'])['electrical_capacity'].sum().reset_index()

# Sort the DataFrame in descending order of total energy capacity
total_capacity_per_canton_source = total_capacity_per_canton_source.sort_values(by='electrical_capacity', ascending=False)

# Create a stacked bar chart using Plotly Express
fig = px.bar(total_capacity_per_canton_source, 
             x='canton_name', 
             y='electrical_capacity', 
             color='energy_source_level_2',
             title=f'Total Electrical Capacity by Canton ({selected_energy_source} Energy Source)',
             labels={'electrical_capacity': 'Total Electrical Capacity', 'energy_source_level_2': 'Energy Source'},
             color_discrete_map={"Hydro": "#1f77b4", "Wind": "#ff7f0e", "Solar": "#2ca02c", "Bioenergy": "#d62728"}
             )

# Update layout for better visibility
fig.update_layout(barmode='stack', xaxis_tickangle=-45)

# Show the stacked bar chart
st.plotly_chart(fig)

# Widgets: selectbox for map
selected_energy_source_map = st.selectbox("Choose an Energy Source for Map", ["All"] + sorted(rpp_df['energy_source_level_2'].unique()))

# Maps header
st.header("Map of Switzerland")

# Filter data for the selected energy source
if selected_energy_source_map == "All":
    map_data = rpp_df.groupby('canton_name')['electrical_capacity'].sum().reset_index()
else:
    source_data_map = rpp_df[rpp_df['energy_source_level_2'] == selected_energy_source_map]
    map_data = source_data_map.groupby('canton_name')['electrical_capacity'].sum().reset_index()

# Display choropleth map using Plotly Express
map_figure = px.choropleth_mapbox(
    map_data,
    geojson=geojson_data,
    locations='canton_name',
    featureidkey="properties.kan_name",
    color='electrical_capacity',
    hover_name='canton_name',
    color_continuous_scale="Viridis",
    opacity=0.5,
    mapbox_style='carto-positron',
    center=dict(lon=8, lat=47),
    zoom=6,
    title=f'Total Electrical Capacity for {selected_energy_source_map} by Canton',
    labels={'electrical_capacity': f'{selected_energy_source_map} Electrical Capacity'}
)

# Update the color axis title
map_figure.update_layout(coloraxis_colorbar_title=f'{selected_energy_source_map} Capacity')

# Show the choropleth map
st.plotly_chart(map_figure)

# Widgets: selectbox for bubble chart
selected_energy_source_bubble = st.selectbox("Choose an Energy Source for Bubble Chart", ["All"] + sorted(rpp_df['energy_source_level_2'].unique()))

# Another header for bubble chart
if selected_energy_source_bubble == "All":
    st.header(f'Bubble Chart of Renewable Energy Capacity in Switzerland')
else:
    st.header(f'Bubble Chart of Renewable Energy Capacity for {selected_energy_source_bubble} in Switzerland')

# Create bubble chart for the selected energy source
if selected_energy_source_bubble == "All":
    # Display bubble chart for all data
    bubble_map = px.scatter_geo(
        rpp_df,
        lat='lat',
        lon='lon',
        size='electrical_capacity',
        color='canton_name',
        hover_name='project_name',
        size_max=50,
        template='plotly',
        title=f'Bubble Chart of Electrical Capacity in Switzerland',
        projection='natural earth',
    )
else:
    # Display bubble chart for the selected energy source
    bubble_map = px.scatter_geo(
        rpp_df[rpp_df['energy_source_level_2'] == selected_energy_source_bubble],
        lat='lat',
        lon='lon',
        size='electrical_capacity',
        color='canton_name',
        hover_name='project_name',
        size_max=50,
        template='plotly',
        title=f'Bubble Chart of Electrical Capacity for {selected_energy_source_bubble} in Switzerland',
        projection='natural earth',
    )

bubble_map.update_geos(fitbounds='locations', visible=False)
bubble_map.update_layout(height=700, width=1000)

# Show bubble chart
st.plotly_chart(bubble_map)

# Widgets: selectbox for pie charts
selected_canton_pie = st.selectbox("Choose a Canton for Pie Chart", ["All"] + sorted(rpp_df['canton_name'].unique()))

# Create pie chart for the selected canton or for all of Switzerland
if selected_canton_pie == "All":
    switzerland_data_pie = rpp_df.groupby('energy_source_level_2')['electrical_capacity'].sum().reset_index()
    fig_pie = px.pie(switzerland_data_pie, values='electrical_capacity', names='energy_source_level_2',
                     title=f'Switzerland - Renewable Energy Capacity Distribution',
                     labels={'electrical_capacity': 'Capacity'},
                     template='plotly_dark',
                     hover_data=['electrical_capacity'],  # Add actual value to hover data
                     )
else:
    canton_data_pie = rpp_df[rpp_df['canton_name'] == selected_canton_pie]
    fig_pie = px.pie(canton_data_pie, values='electrical_capacity', names='energy_source_level_2',
                     title=f'{selected_canton_pie} - Renewable Energy Capacity Distribution',
                     labels={'electrical_capacity': 'Capacity'},
                     template='plotly_dark',
                     hover_data=['electrical_capacity'],  # Add actual value to hover data
                     )

# Display both percentage and actual value in hover information
fig_pie.update_traces(textinfo='percent+value')

# Pie chart header
if selected_canton_pie == "All":
    st.header(f'Renewable Energy Capacity Distribution in Switzerland')
else:
    st.header(f'Renewable Energy Capacity Distribution in {selected_canton_pie}')

# Show pie chart
st.plotly_chart(fig_pie)