import folium
import pandas as pd
from folium import plugins

def create_lahore_map(center_lat=31.5497, center_lon=74.3436, zoom_start=11):
    """Create a base map of Lahore with proper styling"""
    
    # Create base map
    lahore_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=zoom_start,
        tiles='OpenStreetMap'
    )
    
    # Add different tile layers
    folium.TileLayer(
        tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
        attr='OpenStreetMap',
        name='Street Map',
        overlay=False,
        control=True
    ).add_to(lahore_map)
    
    folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
        attr='Google Satellite',
        name='Satellite',
        overlay=False,
        control=True
    ).add_to(lahore_map)
    
    # Add layer control
    folium.LayerControl().add_to(lahore_map)
    
    # Add some key Lahore landmarks for reference
    landmarks = [
        {"name": "Badshahi Mosque", "lat": 31.5888, "lon": 74.3142},
        {"name": "Lahore Fort", "lat": 31.5889, "lon": 74.3136},
        {"name": "Shalimar Gardens", "lat": 31.5857, "lon": 74.3635},
        {"name": "Liberty Market", "lat": 31.5204, "lon": 74.3587},
        {"name": "Mall Road", "lat": 31.5497, "lon": 74.3436}
    ]
    
    for landmark in landmarks:
        folium.CircleMarker(
            location=[landmark["lat"], landmark["lon"]],
            radius=3,
            popup=landmark["name"],
            color='blue',
            fill=True,
            fillColor='lightblue',
            fillOpacity=0.7,
            weight=1
        ).add_to(lahore_map)
    
    return lahore_map

def get_marker_color(issue_type, severity):
    """Get marker color based on issue type and severity"""
    
    # Base colors by type
    type_colors = {
        'Air Quality': 'gray',
        'Water Pollution': 'blue',
        'Waste Management': 'brown', 
        'Noise Pollution': 'purple',
        'Infrastructure': 'orange',
        'Healthcare Access': 'pink',
        'Public Safety': 'red',
        'Transportation': 'green',
        'Other': 'black'
    }
    
    base_color = type_colors.get(issue_type, 'black')
    
    # Modify based on severity
    if severity == 'Critical':
        return 'darkred'
    elif severity == 'High':
        return 'red'
    elif severity == 'Medium':
        return base_color
    else:  # Low
        return 'lightgreen'

def get_marker_icon(issue_type):
    """Get Font Awesome icon based on issue type"""
    
    type_icons = {
        'Air Quality': 'cloud',
        'Water Pollution': 'tint',
        'Waste Management': 'trash',
        'Noise Pollution': 'volume-up',
        'Infrastructure': 'road',
        'Healthcare Access': 'hospital',
        'Public Safety': 'shield-alt',
        'Transportation': 'bus',
        'Other': 'exclamation-triangle'
    }
    
    return type_icons.get(issue_type, 'exclamation-triangle')

def create_popup_content(issue):
    """Create HTML content for issue popup"""
    
    severity_colors = {
        'Low': '#28a745',
        'Medium': '#ffc107',
        'High': '#fd7e14',
        'Critical': '#dc3545'
    }
    
    color = severity_colors.get(issue['severity'], '#6c757d')
    
    popup_html = f"""
    <div style='width: 300px; font-family: Arial, sans-serif;'>
        <h4 style='margin: 0 0 10px 0; color: #333;'>{issue['title']}</h4>
        
        <div style='background-color: {color}; color: white; padding: 5px 10px; border-radius: 5px; margin-bottom: 10px; text-align: center;'>
            <strong>{issue['severity']} - {issue['type']}</strong>
        </div>
        
        <p style='margin: 5px 0;'><strong>Location:</strong> {issue['location']}</p>
        
        <p style='margin: 5px 0;'><strong>Status:</strong> 
            <span style='color: {"#28a745" if issue["status"] == "Resolved" else "#dc3545" if issue["status"] == "Open" else "#ffc107"};'>
                {issue['status']}
            </span>
        </p>
        
        <p style='margin: 5px 0;'><strong>Reported:</strong> {issue['date_reported']}</p>
        
        <p style='margin: 10px 0 5px 0;'><strong>Description:</strong></p>
        <p style='margin: 0; font-size: 12px; color: #666; max-height: 60px; overflow-y: auto;'>
            {issue['description'][:200]}{'...' if len(issue['description']) > 200 else ''}
        </p>
        
        <hr style='margin: 10px 0;'>
        <p style='margin: 0; font-size: 11px; color: #888;'>
            Issue ID: {issue['id']} | Click for details
        </p>
    </div>
    """
    
    return popup_html

def add_issue_markers(map_object, issues_df):
    """Add issue markers to the map"""
    
    if issues_df.empty:
        return map_object
    
    # Create marker cluster for better performance
    marker_cluster = plugins.MarkerCluster(
        name='Issue Markers',
        overlay=True,
        control=True
    ).add_to(map_object)
    
    for idx, issue in issues_df.iterrows():
        try:
            # Get marker properties
            color = get_marker_color(issue['type'], issue['severity'])
            icon = get_marker_icon(issue['type'])
            popup_content = create_popup_content(issue)
            
            # Create marker
            marker = folium.Marker(
                location=[float(issue['lat']), float(issue['lon'])],
                popup=folium.Popup(popup_content, max_width=320),
                tooltip=f"{issue['title']} - {issue['severity']}",
                icon=folium.Icon(
                    color=color,
                    icon=icon,
                    prefix='fa'
                )
            )
            
            marker.add_to(marker_cluster)
            
        except Exception as e:
            print(f"Error adding marker for issue {issue.get('id', 'unknown')}: {str(e)}")
            continue
    
    # Add legend
    add_legend(map_object)
    
    return map_object

def add_legend(map_object):
    """Add a legend to explain the marker colors"""
    
    legend_html = '''
    <div style="position: fixed; 
                top: 10px; right: 10px; width: 200px; height: auto; 
                background-color: white; border: 2px solid grey; z-index:9999; 
                font-size: 12px; padding: 10px">
    
    <h4 style="margin-top: 0;">Issue Severity</h4>
    <p><i class="fa fa-circle" style="color:lightgreen"></i> Low</p>
    <p><i class="fa fa-circle" style="color:orange"></i> Medium</p>
    <p><i class="fa fa-circle" style="color:red"></i> High</p>
    <p><i class="fa fa-circle" style="color:darkred"></i> Critical</p>
    
    <h4>Issue Types</h4>
    <p><i class="fa fa-cloud" style="color:gray"></i> Air Quality</p>
    <p><i class="fa fa-tint" style="color:blue"></i> Water Pollution</p>
    <p><i class="fa fa-trash" style="color:brown"></i> Waste Management</p>
    <p><i class="fa fa-volume-up" style="color:purple"></i> Noise Pollution</p>
    <p><i class="fa fa-road" style="color:orange"></i> Infrastructure</p>
    
    </div>
    '''
    
    map_object.get_root().html.add_child(folium.Element(legend_html))
    
    return map_object

def create_heat_map(issues_df):
    """Create a heat map of issue density"""
    
    if issues_df.empty:
        return create_lahore_map()
    
    # Create base map
    heat_map = create_lahore_map()
    
    # Prepare heat map data
    heat_data = [[row['lat'], row['lon']] for idx, row in issues_df.iterrows()]
    
    # Add heat map layer
    plugins.HeatMap(heat_data, radius=25, blur=15, max_zoom=18).add_to(heat_map)
    
    return heat_map

def add_drawing_tools(map_object):
    """Add drawing tools for area selection and measurement"""
    
    draw = plugins.Draw(
        export=True,
        position='topleft',
        draw_options={
            'polyline': True,
            'rectangle': True,
            'polygon': True,
            'circle': True,
            'marker': True,
            'circlemarker': False
        },
        edit_options={'edit': True}
    )
    
    draw.add_to(map_object)
    
    return map_object
