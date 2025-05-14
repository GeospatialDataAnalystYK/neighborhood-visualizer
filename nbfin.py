import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Zillow Neighborhoods Visualizer", layout="wide")
st.title("🗺️ Zillow Neighborhoods Visualizer")

# --- Load Data ---
@st.cache_data
def load_data():
    shapefile_path = 'Tracts_in_Neighborhoods.shp'  # Update with the correct path
    gdf = gpd.read_file(shapefile_path)
    gdf = gdf.to_crs(epsg=4326)  # Force reproject to WGS84
    gdf['Area_sqkm'] = gdf.geometry.area / 10**6  # Calculate area in square kilometers
    return gdf

data = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filter Options")
states = sorted(data['State'].unique())
selected_state = st.sidebar.selectbox("Select State", states)

counties = sorted(data[data['State'] == selected_state]['County'].unique())
selected_county = st.sidebar.selectbox("Select County", counties)

cities = sorted(data[(data['State'] == selected_state) & (data['County'] == selected_county)]['City'].unique())
selected_city = st.sidebar.selectbox("Select City", cities)

# --- Apply Filters ---
filtered_data = data[
    (data['State'] == selected_state) &
    (data['County'] == selected_county) &
    (data['City'] == selected_city)
]

# --- Extract Neighborhoods for Sidebar Navigation ---
neighborhood_names = sorted(filtered_data['Name'].unique())
selected_neighborhood = st.sidebar.selectbox("Jump to Neighborhood", [""] + neighborhood_names)

# --- Map Setup ---
st.subheader(f"Neighborhoods in {selected_city}, {selected_county}, {selected_state}")

if not filtered_data.empty:
    # Center the map on the centroid of the filtered data
    map_center = [filtered_data.geometry.centroid.y.mean(), 
                  filtered_data.geometry.centroid.x.mean()]

    m = folium.Map(location=map_center, 
                   zoom_start=12, tiles='cartodb positron')
    
    # --- Draw all neighborhoods (light blue) ---
    folium.GeoJson(
        data=filtered_data,
        style_function=lambda x: {
            'color': '#1f78b4',
            'weight': 1,
            'fillOpacity': 0.1
        },
        name="All Neighborhoods"
    ).add_to(m)

    # --- Draw the selected neighborhood in orange ---
    if selected_neighborhood:
        neighborhood_geom = filtered_data[filtered_data['Name'] == selected_neighborhood]
        
        if not neighborhood_geom.empty:
            map_center = [neighborhood_geom.geometry.centroid.y.mean(), 
                          neighborhood_geom.geometry.centroid.x.mean()]
            folium.GeoJson(
                data=neighborhood_geom,
                style_function=lambda x: {
                    'color': 'orange',
                    'weight': 2.5,
                    'fillOpacity': 0.5
                },
                tooltip=folium.GeoJsonTooltip(fields=["GEOID", "Name", "County", "City", "State"], 
                                              aliases=["Tract GEOID:", "Neighborhood:", "County:", "City:", "State:"],
                                              localize=True)
            ).add_to(m)

    # --- Display Map ---
    st_folium(m, width=1000, height=600)

else:
    st.warning("No neighborhoods found for the selected region. Try another one.")
