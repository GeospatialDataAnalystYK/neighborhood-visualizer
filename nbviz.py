import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import st_folium

# --- Streamlit Page Setup ---
st.set_page_config(page_title="Neighborhood Visualizer", layout="wide")
st.title("🗺️ Zillow Neighborhoods Visualizer")

# --- Load Data ---
@st.cache_data
def load_data():
    shapefile_path = 'Tracts_in_Neighborhoods.shp'  # Update with the correct path
    gdf = gpd.read_file(shapefile_path)
    gdf = gdf.to_crs(epsg=4326)  # Force reproject to WGS84
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

# --- Map Setup ---
st.subheader(f"Neighborhoods in {selected_city}, {selected_county}, {selected_state}")

if not filtered_data.empty:
    m = folium.Map(location=[filtered_data.geometry.centroid.y.mean(), 
                             filtered_data.geometry.centroid.x.mean()], 
                   zoom_start=12, tiles='cartodb positron')

    # --- Add neighborhoods to the map ---
    for _, row in filtered_data.iterrows():
        folium.GeoJson(
            row.geometry,
            name=row['Name'],
            tooltip=f"""
            <b>Name:</b> {row['Name']}<br>
            <b>County:</b> {row['County']}<br>
            <b>City:</b> {row['City']}<br>
            <b>GEOID:</b> {row['GEOID']}<br>
            """
        ).add_to(m)

    # --- Display Map ---
    st_folium(m, width=1000, height=600)
else:
    st.warning("No neighborhoods found for the selected region. Try another one.")
