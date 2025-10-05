import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import json
import os
from utils.map_utils import create_lahore_map, add_issue_markers
from utils.data_manager import load_issues_data, save_issues_data
from utils.ai_analysis import generate_issue_summary
from utils.nasa_api import get_environmental_indicators, add_nasa_satellite_layer_to_map
from utils.ml_analysis import predict_issue_hotspots, predict_emerging_issues, generate_trend_forecast
from utils.auth import check_authentication, show_auth_sidebar, show_login_page, add_issue_to_user
from utils.export_data import export_to_csv, export_to_json, generate_summary_report, export_analytics_report
from utils.community_engagement import calculate_resolution_stats, calculate_impact_metrics, get_trending_issues

# Page configuration
st.set_page_config(
    page_title="Lahore Environmental & Social Issues Mapper",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("🌍 Lahore Environmental & Social Issues Mapper")
    st.markdown("Interactive mapping tool for environmental and social issues in Lahore, Pakistan")
    
    # Initialize session state
    if 'selected_issue' not in st.session_state:
        st.session_state.selected_issue = None
    if 'view_mode' not in st.session_state:
        st.session_state.view_mode = 'map'
    
    # Load issues data
    try:
        issues_df = load_issues_data()
        st.success(f"Loaded {len(issues_df)} issues from database")
    except Exception as e:
        st.error(f"Error loading issues data: {str(e)}")
        issues_df = pd.DataFrame()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Select View",
        ["Interactive Map", "NASA Environmental Data", "ML Predictions", "Report New Issue", "Issues Dashboard", "Export Data", "Login/Register", "About"]
    )
    
    show_auth_sidebar()
    
    if page == "Interactive Map":
        show_interactive_map(issues_df)
    elif page == "NASA Environmental Data":
        show_nasa_environmental_data()
    elif page == "ML Predictions":
        show_ml_predictions(issues_df)
    elif page == "Report New Issue":
        show_report_form()
    elif page == "Issues Dashboard":
        show_dashboard(issues_df)
    elif page == "Export Data":
        show_export_page(issues_df)
    elif page == "Login/Register":
        show_login_page()
    elif page == "About":
        show_about()

def show_interactive_map(issues_df):
    st.header("Interactive Map of Lahore")
    
    show_satellite = st.checkbox("Show NASA Satellite Imagery", value=False)
    show_predictions = st.checkbox("Show ML-Predicted Hotspots", value=False)
    
    # Create filters
    col1, col2, col3 = st.columns(3)
    
    with col1:
        issue_types = ["All"] + list(issues_df['type'].unique()) if not issues_df.empty else ["All"]
        selected_type = st.selectbox("Filter by Issue Type", issue_types)
    
    with col2:
        severity_levels = ["All"] + list(issues_df['severity'].unique()) if not issues_df.empty else ["All"]
        selected_severity = st.selectbox("Filter by Severity", severity_levels)
    
    with col3:
        status_options = ["All"] + list(issues_df['status'].unique()) if not issues_df.empty else ["All"]
        selected_status = st.selectbox("Filter by Status", status_options)
    
    # Filter data
    filtered_df = issues_df.copy()
    if selected_type != "All" and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df['type'] == selected_type]
    if selected_severity != "All" and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df['severity'] == selected_severity]
    if selected_status != "All" and not filtered_df.empty:
        filtered_df = filtered_df[filtered_df['status'] == selected_status]
    
    # Create and display map
    try:
        lahore_map = create_lahore_map()
        
        if show_satellite:
            lahore_map = add_nasa_satellite_layer_to_map(lahore_map)
        
        if not filtered_df.empty:
            lahore_map = add_issue_markers(lahore_map, filtered_df)
        
        if show_predictions and not issues_df.empty:
            hotspots = predict_issue_hotspots(issues_df)
            for hotspot in hotspots[:5]:
                folium.CircleMarker(
                    location=[hotspot['lat'], hotspot['lon']],
                    radius=15,
                    popup=f"Predicted Hotspot<br>Risk Score: {hotspot['risk_score']}<br>Type: {hotspot['primary_type']}",
                    color='red',
                    fill=True,
                    fillColor='red',
                    fillOpacity=0.3,
                    weight=2
                ).add_to(lahore_map)
        
        # Display map
        map_data = st_folium(lahore_map, width=1200, height=600)
        
        # Handle marker clicks
        if map_data['last_object_clicked_popup']:
            try:
                issue_id = int(map_data['last_object_clicked_popup'])
                selected_issue = issues_df[issues_df['id'] == issue_id].iloc[0]
                show_issue_details(selected_issue)
            except (ValueError, IndexError):
                pass
                
    except Exception as e:
        st.error(f"Error creating map: {str(e)}")
        st.info("Please ensure all required dependencies are installed.")

def show_issue_details(issue):
    st.markdown("---")
    st.subheader(f"Issue Details: {issue['title']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Description:** {issue['description']}")
        st.markdown(f"**Location:** {issue['location']}")
        st.markdown(f"**Reported Date:** {issue['date_reported']}")
        
        if st.button("Get AI Analysis", key=f"ai_analysis_{issue['id']}"):
            with st.spinner("Generating AI analysis..."):
                try:
                    analysis = generate_issue_summary(issue)
                    st.markdown("### AI Analysis")
                    st.markdown(analysis)
                except Exception as e:
                    st.error(f"Error generating analysis: {str(e)}")
    
    with col2:
        st.markdown(f"**Type:** {issue['type']}")
        st.markdown(f"**Severity:** {issue['severity']}")
        st.markdown(f"**Status:** {issue['status']}")
        
        severity_colors = {'Low': 'green', 'Medium': 'orange', 'High': 'red', 'Critical': 'darkred'}
        color = severity_colors.get(issue['severity'], 'blue')
        st.markdown(f"<div style='background-color: {color}; color: white; padding: 10px; border-radius: 5px; text-align: center;'><b>{issue['severity']} Priority</b></div>", unsafe_allow_html=True)

def show_report_form():
    st.header("Report New Issue")
    st.markdown("Help us identify and track environmental and social issues in Lahore")
    
    with st.form("issue_report_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Issue Title*", placeholder="Brief description of the issue")
            issue_type = st.selectbox("Issue Type*", [
                "Air Quality", "Water Pollution", "Waste Management", 
                "Noise Pollution", "Infrastructure", "Healthcare Access",
                "Public Safety", "Transportation", "Other"
            ])
            severity = st.selectbox("Severity Level*", ["Low", "Medium", "High", "Critical"])
            location = st.text_input("Location*", placeholder="Address or landmark in Lahore")
        
        with col2:
            description = st.text_area("Detailed Description*", 
                                     placeholder="Provide detailed information about the issue",
                                     height=100)
            contact_email = st.text_input("Contact Email (Optional)", 
                                        placeholder="your.email@example.com")
            
            # Location picker
            st.markdown("**Click on the map to select precise location:**")
            
        # Simple map for location selection
        try:
            report_map = create_lahore_map()
            map_data = st_folium(report_map, width=700, height=400)
            
            lat, lon = None, None
            if map_data['last_clicked']:
                lat = map_data['last_clicked']['lat']
                lon = map_data['last_clicked']['lng']
                st.success(f"Selected coordinates: {lat:.6f}, {lon:.6f}")
        except Exception as e:
            st.error(f"Error loading map: {str(e)}")
            lat, lon = 31.5497, 74.3436  # Default Lahore coordinates
        
        submitted = st.form_submit_button("Submit Issue Report")
        
        if submitted:
            if not all([title, issue_type, severity, location, description]):
                st.error("Please fill in all required fields marked with *")
            else:
                try:
                    # Create new issue
                    issues_df = load_issues_data()
                    new_id = max(issues_df['id']) + 1 if not issues_df.empty else 1
                    
                    new_issue = {
                        'id': new_id,
                        'title': title,
                        'type': issue_type,
                        'severity': severity,
                        'location': location,
                        'description': description,
                        'status': 'Open',
                        'date_reported': pd.Timestamp.now().strftime('%Y-%m-%d'),
                        'lat': lat or 31.5497,
                        'lon': lon or 74.3436,
                        'contact_email': contact_email
                    }
                    
                    # Add to dataframe and save
                    new_row_df = pd.DataFrame([new_issue])
                    updated_df = pd.concat([issues_df, new_row_df], ignore_index=True)
                    save_issues_data(updated_df)
                    
                    # Track issue for logged-in users
                    if check_authentication():
                        add_issue_to_user(st.session_state.user_email, new_id)
                    
                    st.success("✅ Issue reported successfully!")
                    st.balloons()
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error saving issue: {str(e)}")

def show_dashboard(issues_df):
    st.header("Issues Dashboard")
    
    if issues_df.empty:
        st.info("No issues data available. Start by reporting some issues!")
        return
    
    tab1, tab2, tab3 = st.tabs(["Overview", "Community Engagement", "Resolution Tracking"])
    
    with tab1:
        # Summary statistics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Issues", len(issues_df))
        with col2:
            open_issues = len(issues_df[issues_df['status'] == 'Open'])
            st.metric("Open Issues", open_issues)
        with col3:
            critical_issues = len(issues_df[issues_df['severity'] == 'Critical'])
            st.metric("Critical Issues", critical_issues)
        with col4:
            resolved_issues = len(issues_df[issues_df['status'] == 'Resolved'])
            st.metric("Resolved Issues", resolved_issues)
        
        # Charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Issues by Type")
            type_counts = issues_df['type'].value_counts()
            st.bar_chart(type_counts)
        
        with col2:
            st.subheader("Issues by Severity")
            severity_counts = issues_df['severity'].value_counts()
            st.bar_chart(severity_counts)
        
        # Recent issues table
        st.subheader("Recent Issues")
        recent_issues = issues_df.sort_values('date_reported', ascending=False).head(10)
        st.dataframe(recent_issues[['title', 'type', 'severity', 'status', 'location', 'date_reported']], 
                    use_container_width=True)
    
    with tab2:
        st.subheader("🤝 Community Engagement")
        st.markdown("Track community participation and trending issues")
        
        impact_metrics = calculate_impact_metrics(issues_df)
        
        if impact_metrics:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Engagement", impact_metrics['total_engagement'])
            with col2:
                st.metric("Upvotes", impact_metrics['upvotes'])
            with col3:
                st.metric("Comments", impact_metrics['comments'])
            with col4:
                st.metric("Followers", impact_metrics['follows'])
            
            st.markdown("---")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Trending Issues")
                trending = get_trending_issues(issues_df)
                
                if trending:
                    for i, issue in enumerate(trending[:5]):
                        st.markdown(f"""
                        **#{i+1} - {issue['title']}**  
                        Type: {issue['type']} | Severity: {issue['severity']}  
                        👍 {issue['upvotes']} upvotes | 💬 {issue['comments']} comments  
                        Engagement Score: {issue['engagement_score']}
                        ---
                        """)
                else:
                    st.info("No trending issues yet")
            
            with col2:
                st.markdown("#### Critical Issues Resolved")
                st.metric("Critical Resolved", impact_metrics['critical_resolved'])
                
                st.markdown("#### Severity Distribution")
                severity_dist = impact_metrics['severity_distribution']
                for severity, count in severity_dist.items():
                    if count > 0:
                        st.markdown(f"**{severity}:** {count}")
    
    with tab3:
        st.subheader("📊 Resolution Tracking")
        st.markdown("Monitor issue resolution progress and impact")
        
        resolution_stats = calculate_resolution_stats(issues_df)
        
        if resolution_stats:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Resolution Rate", f"{resolution_stats['resolution_rate']}%")
            with col2:
                st.metric("Recent 30-Day Rate", f"{resolution_stats['recent_resolution_rate']}%")
            with col3:
                progress = resolution_stats['resolved'] / resolution_stats['total_issues'] * 100
                st.metric("Progress", f"{progress:.0f}%")
            
            st.markdown("---")
            
            import plotly.graph_objects as go
            
            statuses = ['Resolved', 'In Progress', 'Open']
            values = [
                resolution_stats['resolved'],
                resolution_stats['in_progress'],
                resolution_stats['open']
            ]
            colors = ['#28a745', '#ffc107', '#dc3545']
            
            fig = go.Figure(data=[go.Pie(
                labels=statuses,
                values=values,
                marker=dict(colors=colors),
                hole=0.3
            )])
            
            fig.update_layout(
                title="Issue Status Distribution",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Resolution Timeline")
            df_timeline = issues_df[issues_df['status'] == 'Resolved'].copy()
            
            if not df_timeline.empty:
                df_timeline['date_reported'] = pd.to_datetime(df_timeline['date_reported'])
                df_timeline['month'] = df_timeline['date_reported'].dt.to_period('M')
                monthly_resolved = df_timeline.groupby('month').size().reset_index(name='count')
                monthly_resolved['month'] = monthly_resolved['month'].astype(str)
                
                import plotly.express as px
                fig = px.line(monthly_resolved, x='month', y='count',
                            title='Monthly Resolutions',
                            labels={'month': 'Month', 'count': 'Issues Resolved'})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No resolved issues yet")

def show_about():
    st.header("About This Project")
    st.markdown("""
    ### Lahore Environmental & Social Issues Mapper
    
    This application was developed for NASA Space Apps Challenge 2025, addressing the challenge:
    **"Data Pathway to Healthy Cities and Human Settlements"**
    
    #### Core Features:
    
    **🗺️ Interactive Mapping**
    - Real-time visualization of environmental and social issues across Lahore
    - NASA GIBS satellite imagery overlay with MODIS True Color imagery
    - ML-predicted hotspot visualization showing high-risk areas
    - Color-coded markers for different issue types and severity levels
    
    **🛰️ NASA Environmental Data Integration**
    - Live air quality forecasts using OpenWeatherMap Air Pollution API
    - Temperature and climate data tracking
    - NASA EONET environmental events monitoring
    - Real NASA satellite imagery from GIBS (Global Imagery Browse Services)
    
    **🤖 AI & Machine Learning**
    - OpenAI GPT-5 powered issue analysis and recommendations
    - ML-based hotspot prediction using clustering algorithms
    - Emerging issue pattern detection and trend analysis
    - 30-day forecast predictions for issue reporting trends
    - Issue correlation analysis to identify systemic problems
    
    **👥 User Authentication & Tracking**
    - Secure user registration and login system
    - Personal issue tracking for logged-in users
    - Follow your reported issues and their resolution status
    
    **📊 Data Export & Reporting**
    - Export data in CSV, JSON, and text report formats
    - Filtered exports by issue type, severity, or status
    - Comprehensive analytics reports with statistical summaries
    - Temporal analysis and geographic distribution insights
    
    **🤝 Community Engagement**
    - Resolution status tracking and metrics
    - Community impact indicators
    - Trending issues dashboard
    - Resolution timeline visualization
    - Progress monitoring and success metrics
    
    #### Issue Categories:
    - **Environmental**: Air Quality, Water Pollution, Waste Management, Noise Pollution
    - **Social**: Infrastructure, Healthcare Access, Public Safety, Transportation
    
    #### Technology Stack:
    - **Frontend**: Streamlit
    - **Mapping**: Folium with NASA GIBS integration
    - **AI Analysis**: OpenAI GPT-5
    - **Machine Learning**: Scikit-learn (DBSCAN clustering, Random Forest)
    - **Data Sources**: NASA EONET, NASA GIBS, OpenWeatherMap APIs
    - **Data Processing**: Pandas, NumPy
    - **Visualization**: Plotly, Matplotlib
    - **Authentication**: Secure password hashing with SHA-256
    
    #### Data Sources:
    - **NASA EONET**: Environmental event tracking
    - **NASA GIBS**: Satellite imagery (MODIS True Color)
    - **OpenWeatherMap**: Air quality and temperature data
    - **Community Reports**: User-submitted environmental and social issues
    
    #### How to Use:
    1. **Explore the Map**: Browse the interactive map with NASA satellite imagery
    2. **View NASA Data**: Check air quality forecasts and environmental events
    3. **Report Issues**: Submit new environmental or social issues with location
    4. **Get AI Insights**: Use AI analysis for detailed recommendations
    5. **Track ML Predictions**: View hotspot predictions and emerging trends
    6. **Monitor Progress**: Track resolution status and community impact
    7. **Export Data**: Download reports and analytics for further analysis
    8. **Create Account**: Register to track your submissions and follow issues
    
    This tool empowers citizens, urban planners, and policymakers to make data-driven decisions
    for creating healthier, more sustainable cities using cutting-edge NASA technology and AI.
    
    ---
    **Developed for NASA Space Apps Challenge 2025**  
    Integrating NASA Earth Observation data with community-driven reporting and AI analysis
    """)

def show_nasa_environmental_data():
    st.header("🛰️ NASA Environmental Data for Lahore")
    st.markdown("Live environmental monitoring using NASA satellite data and APIs")
    
    api_key_status = os.environ.get('OPENWEATHER_API_KEY', '')
    if not api_key_status or api_key_status == 'demo':
        st.info("💡 **Data Source Note**: Currently using NASA satellite observation-based estimates. Add an OPENWEATHER_API_KEY to enable real-time data from OpenWeatherMap API.")
    
    with st.spinner("Fetching NASA environmental data..."):
        indicators = get_environmental_indicators()
    
    if not indicators:
        st.error("Unable to fetch NASA data at this time. Please try again later.")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["Air Quality Forecast", "Temperature Data", "Environmental Events", "Satellite Imagery"])
    
    with tab1:
        st.subheader("5-Day Air Quality Forecast")
        st.markdown("*Forecasted air quality index (AQI) for Lahore region*")
        
        air_quality = indicators.get('air_quality', [])
        if air_quality:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                import plotly.graph_objects as go
                
                dates = [aq['date'] for aq in air_quality]
                aqi_values = [aq['aqi'] for aq in air_quality]
                colors = [aq['color'] for aq in air_quality]
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=dates, y=aqi_values,
                    mode='lines+markers',
                    name='AQI',
                    line=dict(width=3),
                    marker=dict(size=10, color=colors)
                ))
                
                fig.update_layout(
                    title="Air Quality Index Forecast",
                    xaxis_title="Date",
                    yaxis_title="AQI Value",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Current AQI")
                current = air_quality[0]
                st.markdown(f"""
                <div style='background-color: {current['color']}; color: white; padding: 20px; border-radius: 10px; text-align: center;'>
                    <h1 style='margin: 0; color: white;'>{current['aqi']}</h1>
                    <h3 style='margin: 10px 0; color: white;'>{current['category']}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### Pollutant Levels")
                st.metric("PM2.5", f"{current['pm25']} µg/m³")
                st.metric("NO2", f"{current['no2']} ppb")
                st.metric("O3", f"{current['o3']} ppb")
        else:
            st.info("No air quality data available")
    
    with tab2:
        st.subheader("Temperature & Climate Data")
        st.markdown("*30-day temperature trends from NASA MERRA-2 dataset*")
        
        temp_data = indicators.get('temperature')
        if temp_data:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                historical = temp_data.get('historical', [])
                if historical:
                    import plotly.express as px
                    
                    df_temp = pd.DataFrame(historical)
                    
                    fig = px.line(df_temp, x='date', y='temperature',
                                title='30-Day Temperature Trend',
                                labels={'temperature': 'Temperature (°C)', 'date': 'Date'})
                    fig.update_traces(line_color='red', line_width=2)
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("#### Current Temperature")
                st.metric("Temperature", f"{temp_data['current_temperature']}°C")
                st.markdown(f"**Location:** {temp_data['location']}")
                
                if historical:
                    avg_temp = sum(h['temperature'] for h in historical) / len(historical)
                    st.metric("30-Day Average", f"{avg_temp:.1f}°C")
        else:
            st.info("No temperature data available")
    
    with tab3:
        st.subheader("Environmental Events Near Lahore")
        st.markdown("*Real-time environmental events from NASA EONET API*")
        
        events = indicators.get('nearby_events', [])
        if events:
            for event in events[:10]:
                severity_colors = {
                    'Wildfires': '#ff6b6b',
                    'Severe Storms': '#4ecdc4',
                    'Volcanoes': '#e67e22'
                }
                color = severity_colors.get(event['category'], '#95a5a6')
                
                st.markdown(f"""
                <div style='border-left: 4px solid {color}; padding: 15px; margin: 10px 0; background-color: #f8f9fa;'>
                    <strong>{event['title']}</strong><br>
                    <span style='color: {color};'>●</span> {event['category']}<br>
                    <small>📍 Distance: {event['distance_km']} km from Lahore</small><br>
                    <small>📅 {event['date']}</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No major environmental events detected near Lahore")
    
    with tab4:
        st.subheader("NASA Satellite Imagery")
        st.markdown("*MODIS True Color Earth Imagery from NASA GIBS*")
        
        sat_info = indicators.get('satellite_info', {})
        if sat_info:
            st.markdown(f"""
            **Layer:** {sat_info['layer']}  
            **Date:** {sat_info['date']}  
            **Source:** {sat_info['info']}
            
            {sat_info['attribution']}
            """)
            
            st.info("💡 Enable 'Show NASA Satellite Imagery' checkbox on the Interactive Map page to view satellite layers overlaid on the map.")
        
        st.markdown("---")
        st.markdown(f"*Last updated: {indicators['last_updated']}*")

def show_ml_predictions(issues_df):
    st.header("🤖 ML-Based Issue Predictions & Analysis")
    st.markdown("Machine learning predictions to identify emerging patterns and hotspots")
    
    if issues_df.empty:
        st.info("No data available for ML analysis. Report some issues to enable predictions.")
        return
    
    if len(issues_df) < 10:
        st.warning("More data needed for accurate predictions. At least 10 issues required.")
        return
    
    tab1, tab2, tab3, tab4 = st.tabs(["Hotspot Predictions", "Emerging Issues", "Trend Forecast", "Issue Correlations"])
    
    with tab1:
        st.subheader("Predicted Issue Hotspots")
        st.markdown("*ML clustering identifies areas with high concentration of issues*")
        
        with st.spinner("Analyzing issue patterns..."):
            hotspots = predict_issue_hotspots(issues_df)
        
        if hotspots:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                hotspot_map = create_lahore_map()
                
                for i, hotspot in enumerate(hotspots[:10]):
                    color = 'darkred' if hotspot['risk_score'] > 50 else 'red' if hotspot['risk_score'] > 30 else 'orange'
                    
                    folium.CircleMarker(
                        location=[hotspot['lat'], hotspot['lon']],
                        radius=hotspot['risk_score'] / 3,
                        popup=f"<b>Hotspot #{i+1}</b><br>Risk: {hotspot['risk_score']}<br>Issues: {hotspot['issue_count']}<br>Type: {hotspot['primary_type']}",
                        tooltip=f"Risk Score: {hotspot['risk_score']}",
                        color=color,
                        fill=True,
                        fillColor=color,
                        fillOpacity=0.4,
                        weight=2
                    ).add_to(hotspot_map)
                
                st_folium(hotspot_map, width=700, height=500)
            
            with col2:
                st.markdown("#### Top Risk Areas")
                for i, hotspot in enumerate(hotspots[:5]):
                    st.markdown(f"""
                    **#{i+1} - Risk Score: {hotspot['risk_score']}**  
                    Issues: {hotspot['issue_count']}  
                    Primary Type: {hotspot['primary_type']}  
                    Avg Severity: {hotspot['avg_severity']}/4
                    ---
                    """)
        else:
            st.info("No hotspots detected with current data")
    
    with tab2:
        st.subheader("Emerging Issue Patterns")
        st.markdown("*Identifies issue types with increasing trend*")
        
        with st.spinner("Analyzing trends..."):
            emerging = predict_emerging_issues(issues_df)
        
        if emerging:
            import plotly.express as px
            
            df_emerging = pd.DataFrame(emerging)
            
            fig = px.bar(df_emerging, x='type', y='growth_rate',
                        color='growth_rate',
                        title='Issue Growth Rates (Last 30 Days)',
                        labels={'type': 'Issue Type', 'growth_rate': 'Growth Rate (%)'},
                        color_continuous_scale='Reds')
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Detailed Analysis")
            for issue in emerging:
                st.markdown(f"""
                **{issue['type']}** - {issue['trend']}  
                📈 Growth Rate: {issue['growth_rate']}%  
                📊 Recent Count: {issue['recent_count']} issues  
                ⚠️ Avg Severity: {issue['avg_severity']}/4
                ---
                """)
        else:
            st.success("No significant emerging patterns detected")
    
    with tab3:
        st.subheader("30-Day Trend Forecast")
        st.markdown("*Predicts future issue reporting trends*")
        
        with st.spinner("Generating forecast..."):
            forecast_data = generate_trend_forecast(issues_df, days_ahead=30)
        
        if forecast_data:
            import plotly.graph_objects as go
            
            forecast = forecast_data['forecast']
            df_forecast = pd.DataFrame(forecast)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_forecast['date'],
                y=df_forecast['predicted_issues'],
                mode='lines+markers',
                name='Predicted Issues',
                line=dict(color='royalblue', width=3),
                fill='tozeroy'
            ))
            
            fig.update_layout(
                title='Predicted Daily Issue Reports',
                xaxis_title='Date',
                yaxis_title='Number of Issues',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Daily Avg", f"{forecast_data['current_avg']:.1f}")
            with col2:
                trend = forecast_data['trend_direction'].title()
                st.metric("Trend Direction", trend)
            with col3:
                next_week_avg = sum(f['predicted_issues'] for f in forecast[:7]) / 7
                st.metric("Next Week Avg", f"{next_week_avg:.1f}")
        else:
            st.info("Insufficient data for forecast generation")
    
    with tab4:
        st.subheader("Issue Type Correlations")
        st.markdown("*Identifies which issues tend to occur together*")
        
        with st.spinner("Calculating correlations..."):
            from utils.ml_analysis import calculate_issue_correlation
            correlations = calculate_issue_correlation(issues_df)
        
        if correlations:
            st.markdown("#### Strongly Correlated Issues")
            st.markdown("*Issues that frequently occur in the same locations*")
            
            for corr in correlations[:10]:
                correlation_strength = "Strong" if corr['correlation'] > 60 else "Moderate" if corr['correlation'] > 40 else "Weak"
                
                st.markdown(f"""
                **{corr['type1']} ↔ {corr['type2']}**  
                Correlation: {corr['correlation']}% ({correlation_strength})  
                Co-occurrences: {corr['co_occurrences']} locations
                ---
                """)
            
            st.info("💡 Understanding correlations helps identify systemic issues that require coordinated solutions.")
        else:
            st.info("No significant correlations found")

def show_export_page(issues_df):
    st.header("📥 Export Data & Reports")
    st.markdown("Download issue data and generate comprehensive reports")
    
    if issues_df.empty:
        st.info("No data available to export. Report some issues first!")
        return
    
    tab1, tab2, tab3 = st.tabs(["Quick Export", "Filtered Export", "Analytics Reports"])
    
    with tab1:
        st.subheader("Export All Data")
        st.markdown(f"Export all {len(issues_df)} issues in your preferred format")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### CSV Format")
            csv_data = export_to_csv(issues_df)
            if csv_data:
                st.download_button(
                    label="📊 Download CSV",
                    data=csv_data,
                    file_name=f"lahore_issues_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            st.markdown("#### JSON Format")
            json_data = export_to_json(issues_df)
            if json_data:
                st.download_button(
                    label="📋 Download JSON",
                    data=json_data,
                    file_name=f"lahore_issues_{datetime.now().strftime('%Y%m%d')}.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        with col3:
            st.markdown("#### Summary Report")
            summary = generate_summary_report(issues_df)
            st.download_button(
                label="📄 Download Report",
                data=summary,
                file_name=f"lahore_issues_summary_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    with tab2:
        st.subheader("Export Filtered Data")
        st.markdown("Apply filters and export specific data subsets")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            filter_type = st.selectbox(
                "Filter by Issue Type",
                ["All"] + list(issues_df['type'].unique())
            )
        
        with col2:
            filter_severity = st.selectbox(
                "Filter by Severity",
                ["All"] + list(issues_df['severity'].unique())
            )
        
        with col3:
            filter_status = st.selectbox(
                "Filter by Status",
                ["All"] + list(issues_df['status'].unique())
            )
        
        from utils.export_data import create_filtered_export
        
        filters = {
            'type': filter_type,
            'severity': filter_severity,
            'status': filter_status
        }
        
        filtered_df = create_filtered_export(issues_df, filters)
        
        st.markdown(f"**Filtered Results:** {len(filtered_df)} issues")
        
        if not filtered_df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                csv_filtered = export_to_csv(filtered_df)
                if csv_filtered:
                    st.download_button(
                        label="📊 Download Filtered CSV",
                        data=csv_filtered,
                        file_name=f"lahore_issues_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
            
            with col2:
                json_filtered = export_to_json(filtered_df)
                if json_filtered:
                    st.download_button(
                        label="📋 Download Filtered JSON",
                        data=json_filtered,
                        file_name=f"lahore_issues_filtered_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            
            st.dataframe(filtered_df[['id', 'title', 'type', 'severity', 'status', 'location', 'date_reported']].head(20),
                        use_container_width=True)
    
    with tab3:
        st.subheader("Detailed Analytics Reports")
        st.markdown("Generate comprehensive statistical analysis reports")
        
        analytics_report = export_analytics_report(issues_df)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.text_area("Report Preview", analytics_report, height=400)
        
        with col2:
            st.download_button(
                label="📊 Download Full Analytics Report",
                data=analytics_report,
                file_name=f"lahore_issues_analytics_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain",
                use_container_width=True
            )
            
            st.markdown("---")
            st.markdown("#### Report Includes:")
            st.markdown("""
            - Temporal Analysis
            - Severity Breakdown
            - Geographic Distribution
            - Issue Type Trends
            - Resolution Metrics
            - Statistical Summaries
            """)

if __name__ == "__main__":
    main()
