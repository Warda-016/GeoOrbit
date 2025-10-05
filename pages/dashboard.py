import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from utils.data_manager import load_issues_data

def show_dashboard_page():
    st.set_page_config(page_title="Issues Dashboard", page_icon="📊", layout="wide")
    
    st.title("📊 Lahore Issues Analytics Dashboard")
    
    try:
        issues_df = load_issues_data()
        
        if issues_df.empty:
            st.info("📭 No issues data available. Start by reporting some issues!")
            return
        
        # Key Metrics
        show_key_metrics(issues_df)
        
        # Charts and Analytics
        col1, col2 = st.columns(2)
        
        with col1:
            show_issue_type_chart(issues_df)
            show_severity_distribution(issues_df)
        
        with col2:
            show_status_breakdown(issues_df)
            show_temporal_trends(issues_df)
        
        # Detailed analytics
        st.markdown("---")
        show_detailed_analytics(issues_df)
        
        # Recent issues and heat map
        col1, col2 = st.columns([2, 1])
        
        with col1:
            show_recent_issues_table(issues_df)
        
        with col2:
            show_priority_issues(issues_df)
            
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")

def show_key_metrics(df):
    st.subheader("📈 Key Metrics Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        total_issues = len(df)
        st.metric("Total Issues", total_issues)
    
    with col2:
        open_issues = len(df[df['status'] == 'Open'])
        st.metric("Open Issues", open_issues, 
                 delta=f"{(open_issues/total_issues*100):.1f}%" if total_issues > 0 else "0%")
    
    with col3:
        critical_issues = len(df[df['severity'] == 'Critical'])
        st.metric("Critical Issues", critical_issues,
                 delta="Urgent" if critical_issues > 0 else "None")
    
    with col4:
        resolved_issues = len(df[df['status'] == 'Resolved'])
        resolution_rate = (resolved_issues/total_issues*100) if total_issues > 0 else 0
        st.metric("Resolved Issues", resolved_issues, 
                 delta=f"{resolution_rate:.1f}% resolved")
    
    with col5:
        # Calculate average response time (mock calculation for demo)
        in_progress = len(df[df['status'] == 'In Progress'])
        st.metric("In Progress", in_progress)

def show_issue_type_chart(df):
    st.subheader("🏷️ Issues by Type")
    
    type_counts = df['type'].value_counts()
    
    fig = px.bar(
        x=type_counts.values,
        y=type_counts.index,
        orientation='h',
        title="Distribution of Issue Types",
        color=type_counts.values,
        color_continuous_scale='viridis'
    )
    
    fig.update_layout(
        showlegend=False,
        height=400,
        yaxis_title="Issue Type",
        xaxis_title="Number of Reports"
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_severity_distribution(df):
    st.subheader("⚠️ Severity Distribution")
    
    severity_counts = df['severity'].value_counts()
    
    colors = {
        'Low': '#28a745',
        'Medium': '#ffc107',
        'High': '#fd7e14', 
        'Critical': '#dc3545'
    }
    
    fig = px.pie(
        values=severity_counts.values,
        names=severity_counts.index,
        title="Issue Severity Breakdown",
        color=severity_counts.index,
        color_discrete_map=colors
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, use_container_width=True)

def show_status_breakdown(df):
    st.subheader("📋 Status Overview")
    
    status_counts = df['status'].value_counts()
    
    fig = px.pie(
        values=status_counts.values,
        names=status_counts.index,
        title="Current Status Distribution",
        hole=0.4
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    st.plotly_chart(fig, use_container_width=True)

def show_temporal_trends(df):
    st.subheader("📅 Reporting Trends")
    
    # Convert date column to datetime
    df['date_reported'] = pd.to_datetime(df['date_reported'], errors='coerce')
    
    # Group by date
    daily_reports = df.groupby(df['date_reported'].dt.date).size().reset_index()
    daily_reports.columns = ['Date', 'Reports']
    
    fig = px.line(
        daily_reports,
        x='Date',
        y='Reports',
        title="Daily Issue Reports",
        markers=True
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

def show_detailed_analytics(df):
    st.subheader("🔍 Detailed Analytics")
    
    tab1, tab2, tab3 = st.tabs(["Location Analysis", "Impact Analysis", "Response Metrics"])
    
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top affected areas (simplified)
            location_counts = df['location'].value_counts().head(10)
            
            fig = px.bar(
                x=location_counts.values,
                y=location_counts.index,
                orientation='h',
                title="Top 10 Affected Locations"
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Severity by location (sample analysis)
            location_severity = df.groupby(['location', 'severity']).size().reset_index(name='count')
            
            fig = px.bar(
                location_severity.head(20),
                x='location',
                y='count',
                color='severity',
                title="Severity Distribution by Location"
            )
            fig.update_layout(height=400, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            # Impact analysis
            impact_cols = ['health_impact', 'environmental_impact', 'economic_impact']
            if all(col in df.columns for col in impact_cols):
                impacts = df[impact_cols].sum()
                
                fig = px.bar(
                    x=impacts.index,
                    y=impacts.values,
                    title="Types of Impact Reported",
                    color=impacts.values
                )
                st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Population affected
            if 'affected_population' in df.columns:
                pop_counts = df['affected_population'].value_counts()
                
                fig = px.pie(
                    values=pop_counts.values,
                    names=pop_counts.index,
                    title="Population Impact Scale"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        # Response time analysis
        st.markdown("### Response Metrics")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_response = "2.3 days"  # Mock data
            st.metric("Avg Response Time", avg_response)
        
        with col2:
            resolution_rate = len(df[df['status'] == 'Resolved']) / len(df) * 100
            st.metric("Resolution Rate", f"{resolution_rate:.1f}%")
        
        with col3:
            escalated = len(df[df['severity'] == 'Critical'])
            st.metric("Escalated Issues", escalated)

def show_recent_issues_table(df):
    st.subheader("📋 Recent Issues")
    
    # Sort by date and get recent issues
    recent_issues = df.sort_values('date_reported', ascending=False).head(15)
    
    # Display table with key columns
    display_cols = ['id', 'title', 'type', 'severity', 'status', 'location', 'date_reported']
    display_df = recent_issues[display_cols].copy()
    
    # Format the display
    st.dataframe(
        display_df,
        use_container_width=True,
        column_config={
            'id': 'ID',
            'title': 'Issue Title',
            'type': 'Type',
            'severity': 'Severity',
            'status': 'Status',
            'location': 'Location',
            'date_reported': 'Date Reported'
        }
    )

def show_priority_issues(df):
    st.subheader("🚨 Priority Issues")
    
    # Get critical and high severity open issues
    priority_issues = df[
        (df['severity'].isin(['Critical', 'High'])) & 
        (df['status'] == 'Open')
    ].sort_values('severity', ascending=False)
    
    if priority_issues.empty:
        st.success("No high priority open issues! 🎉")
    else:
        for idx, issue in priority_issues.head(5).iterrows():
            severity_color = '#dc3545' if issue['severity'] == 'Critical' else '#fd7e14'
            
            st.markdown(f"""
            <div style='border-left: 4px solid {severity_color}; padding: 10px; margin: 10px 0; background-color: #f8f9fa;'>
                <strong>{issue['title']}</strong><br>
                <span style='color: {severity_color};'>●</span> {issue['severity']} - {issue['type']}<br>
                <small>📍 {issue['location']}</small><br>
                <small>📅 {issue['date_reported']}</small>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    show_dashboard_page()
