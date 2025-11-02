import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import requests
import pandas as pd

# Set page config
st.set_page_config(page_title="Interactive World Map", layout="wide")

# Initialize session state
if 'view' not in st.session_state:
    st.session_state.view = 'world'
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = None
if 'show_dialog' not in st.session_state:
    st.session_state.show_dialog = False

def show_world_map():
    """Display interactive world map"""
    st.title("🌍 Interactive World Map")
    
    # Create world map using plotly express
    df = px.data.gapminder().query("year == 2007")
    
    fig = px.choropleth(
        df,
        locations="iso_alpha",
        hover_name="country",
        color_discrete_sequence=["lightblue"],
        projection="natural earth"
    )
    
    fig.update_geos(
        visible=True,
        showcountries=True,
        countrycolor="darkgray",
        showcoastlines=True,
        coastlinecolor="darkgray",
        showland=True,
        landcolor="lightblue",
        showocean=True,
        oceancolor="lightcyan"
    )
    
    fig.update_layout(
        height=600,
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False
    )
    
    # Display map and capture click events
    selected_points = st.plotly_chart(fig, use_container_width=True, on_select="rerun")
    
    # Handle click events
    if selected_points and selected_points.selection and selected_points.selection.points:
        point_data = selected_points.selection.points[0]
        if 'hovertext' in point_data:
            st.session_state.selected_country = point_data['hovertext']
            st.session_state.show_dialog = True
            st.rerun()

def show_country_map(country):
    """Display country map with states"""
    st.title(f"🗺️ Interactive {country} Map")
    
    if st.button("← Back to World Map"):
        st.session_state.view = 'world'
        st.session_state.selected_country = None
        st.rerun()
    
    if country.lower() == 'india':
        # Fetch India GeoJSON
        geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        response = requests.get(geojson_url)
        india_geojson = response.json()
        
        # Extract state names
        state_names = [feature['properties']['ST_NM'] for feature in india_geojson['features']]
        
        # Create dataframe
        india_states = pd.DataFrame({
            'state': state_names,
            'value': [1] * len(state_names)
        })
        
        # Create choropleth map
        fig = go.Figure(data=go.Choropleth(
            geojson=india_geojson,
            featureidkey='properties.ST_NM',
            locations=india_states['state'],
            z=india_states['value'],
            colorscale=[[0, 'lightblue'], [1, 'lightblue']],
            autocolorscale=False,
            showscale=False,
            marker_line_color='darkgray',
            marker_line_width=1,
            hovertemplate='<b>%{location}</b><extra></extra>'
        ))
        
        # Focus on India
        fig.update_geos(
            visible=False,
            center=dict(lon=78.9629, lat=22.5937),
            projection_scale=4.5
        )
        
        fig.update_layout(
            geo=dict(bgcolor='rgba(240,240,240,1)'),
            height=600,
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"State-level data for {country} is not currently available. Only India is supported.")
        if st.button("Go Back"):
            st.session_state.view = 'world'
            st.session_state.selected_country = None
            st.rerun()

# Main app logic
if st.session_state.show_dialog:
    # Show dialog
    st.title("🌍 Interactive World Map")
    
    with st.container():
        st.info(f"**Explore {st.session_state.selected_country}**")
        st.write("Do you want to go inside this country to see its states?")
        
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("✅ OK", use_container_width=True):
                st.session_state.view = 'country'
                st.session_state.show_dialog = False
                st.rerun()
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_dialog = False
                st.session_state.selected_country = None
                st.rerun()
    
    # Still show the world map in background
    df = px.data.gapminder().query("year == 2007")
    fig = px.choropleth(
        df,
        locations="iso_alpha",
        hover_name="country",
        color_discrete_sequence=["lightblue"],
        projection="natural earth"
    )
    fig.update_layout(height=600, margin=dict(l=0, r=0, t=0, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.view == 'world':
    show_world_map()
elif st.session_state.view == 'country':
    show_country_map(st.session_state.selected_country)
