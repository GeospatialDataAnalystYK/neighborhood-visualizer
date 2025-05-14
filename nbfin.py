import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium
from folium.features import GeoJsonTooltip

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Zillow Neighborhoods Visualizer", layout="wide")
st.title("🗺️ Zillow Neighborhoods Visualizer")

# --- Load Data ---
@st.cache_data
def load_data():
    neighborhoods_path = 'Tracts_in_Neighborhoods.shp'  # Update with your actual path
    gdf = gpd.read_file(neighborhoods_path)
    gdf = gdf.to_crs(epsg=4326)  # Ensure it's in WGS84
    return gdf

data = load_data()

# --- Sidebar Configuration ---
with st.sidebar:
    # Display Fox Chase Logo
    st.image("fclogo2.png", use_container_width =True)
    st.header("Filter Options")
    
    # Dropdown Selections
    states = sorted(data['State'].unique())
    selected_state = st.selectbox("Select State", states)

    counties = sorted(data[data['State'] == selected_state]['County'].unique())
    selected_county = st.selectbox("Select County", counties)

    cities = sorted(data[(data['State'] == selected_state) & (data['County'] == selected_county)]['City'].unique())
    selected_city = st.selectbox("Select City", cities)

    neighborhoods = sorted(data[(data['State'] == selected_state) & 
                                (data['County'] == selected_county) & 
                                (data['City'] == selected_city)]['Name'].unique())

    selected_neighborhood = st.selectbox("Jump to Neighborhood", neighborhoods)

# --- Apply Filters ---
filtered_data = data[
    (data['State'] == selected_state) &
    (data['County'] == selected_county) &
    (data['City'] == selected_city)
]

# --- Map Setup ---
st.subheader(f"Neighborhoods in {selected_city}, {selected_county}, {selected_state}")

if not filtered_data.empty:
    m = folium.Map(
        location=[filtered_data.geometry.centroid.y.mean(), 
                 filtered_data.geometry.centroid.x.mean()], 
        zoom_start=12, 
        tiles='cartodb positron'
    )

    # Transparent Tracts
    folium.GeoJson(
        filtered_data,
        style_function=lambda feature: {
            'fillColor': 'transparent',
            'color': '#004080',
            'weight': 1.2
        },
        tooltip=GeoJsonTooltip(
            fields=["GEOID", "Name", "County", "City", "State"],
            aliases=["Tract GEOID:", "Neighborhood:", "County:", "City:", "State:"],
            localize=True
        )
    ).add_to(m)

    # Highlight selected neighborhood
    neighborhood_geom = filtered_data[filtered_data['Name'] == selected_neighborhood]
    if not neighborhood_geom.empty:
        folium.GeoJson(
            neighborhood_geom,
            style_function=lambda feature: {
                'fillColor': '#FFA500',
                'color': '#FFA500',
                'weight': 2,
                'fillOpacity': 0.5
            },
            tooltip=GeoJsonTooltip(
                fields=["GEOID", "Name", "County", "City", "State"],
                aliases=["Tract GEOID:", "Neighborhood:", "County:", "City:", "State:"],
                localize=True
            )
        ).add_to(m)
        
        # Center the map on the neighborhood
        centroid = neighborhood_geom.geometry.centroid.iloc[0]
        m.location = [centroid.y, centroid.x]
        m.zoom_start = 13

    # --- Display Map ---
    st_folium(m, width=1000, height=600)

else:
    st.warning("No neighborhoods found for the selected region. Try another one.")
