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

# --- Basemap Selector ---
basemap_choice = st.sidebar.selectbox("Select Basemap", ["OpenStreetMap", "CartoDB positron", "Stamen Terrain", "Stamen Toner"])

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
                   zoom_start=12, tiles=basemap_choice)

    # --- Add Neighborhoods to the map ---
    for _, row in filtered_data.iterrows():
        # Create a GeoJson object
        geo_json = folium.GeoJson(
            row.geometry,
            name=row['Name'],
            style_function=lambda x: {
                'color': '#1f78b4',   # Blue color for neighborhoods
                'weight': 1.5,        # Thinner borders
                'fillOpacity': 0.2
            },
            highlight_function=lambda x: {'weight': 2.5, 'color': '#08519c'}
        )

        # Create a Popup and bind it
        popup_content = f"""
        <b>Name:</b> {row['Name']}<br>
        <b>County:</b> {row['County']}<br>
        <b>City:</b> {row['City']}<br>
        <b>GEOID:</b> {row['GEOID']}<br>
        """
        popup = folium.Popup(popup_content, max_width=300)
        popup.add_to(geo_json)

        # Add to map
        geo_json.add_to(m)

    # --- Add Tracts with Black Thin Borders ---
    folium.GeoJson(
        filtered_data,
        name='Tracts',
        style_function=lambda x: {
            'color': 'black',
            'weight': 0.15,
            'fillOpacity': 0
        }
    ).add_to(m)

    # --- Display Map ---
    st_folium(m, width=1000, height=600)
else:
    st.warning("No neighborhoods found for the selected region. Try another one.")
