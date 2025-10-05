import streamlit as st
import pandas as pd
from utils.ai_analysis import generate_issue_analysis, generate_recommendations
from utils.data_manager import load_issues_data, update_issue_status

def show_issue_details_page():
    st.set_page_config(page_title="Issue Details", page_icon="📋")
    
    st.title("📋 Issue Details")
    
    # Get issue ID from query params
    query_params = st.experimental_get_query_params()
    issue_id = query_params.get('id', [None])[0]
    
    if not issue_id:
        st.error("No issue ID provided")
        return
    
    try:
        issue_id = int(issue_id)
        issues_df = load_issues_data()
        
        if issue_id not in issues_df['id'].values:
            st.error("Issue not found")
            return
        
        issue = issues_df[issues_df['id'] == issue_id].iloc[0]
        
        # Display issue information
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.header(issue['title'])
            st.markdown(f"**Location:** {issue['location']}")
            st.markdown(f"**Description:** {issue['description']}")
            st.markdown(f"**Reported on:** {issue['date_reported']}")
            
            # AI Analysis section
            st.subheader("AI Analysis & Recommendations")
            
            col_a, col_b = st.columns(2)
            
            with col_a:
                if st.button("Generate Analysis"):
                    with st.spinner("Analyzing issue..."):
                        try:
                            analysis = generate_issue_analysis(issue)
                            st.markdown("### Analysis")
                            st.markdown(analysis)
                        except Exception as e:
                            st.error(f"Error generating analysis: {str(e)}")
            
            with col_b:
                if st.button("Get Recommendations"):
                    with st.spinner("Generating recommendations..."):
                        try:
                            recommendations = generate_recommendations(issue)
                            st.markdown("### Recommendations")
                            st.markdown(recommendations)
                        except Exception as e:
                            st.error(f"Error generating recommendations: {str(e)}")
        
        with col2:
            st.subheader("Issue Status")
            
            # Status indicators
            severity_colors = {
                'Low': '#28a745',
                'Medium': '#ffc107', 
                'High': '#fd7e14',
                'Critical': '#dc3545'
            }
            
            color = severity_colors.get(issue['severity'], '#6c757d')
            
            st.markdown(f"""
            <div style='background-color: {color}; color: white; padding: 15px; border-radius: 10px; text-align: center; margin-bottom: 20px;'>
                <h3 style='margin: 0; color: white;'>{issue['severity']}</h3>
                <p style='margin: 0; color: white;'>Severity Level</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**Type:** {issue['type']}")
            st.markdown(f"**Current Status:** {issue['status']}")
            st.markdown(f"**Coordinates:** {issue['lat']:.4f}, {issue['lon']:.4f}")
            
            # Admin controls (simplified)
            st.subheader("Update Status")
            new_status = st.selectbox(
                "Change Status:",
                ["Open", "In Progress", "Resolved", "Closed"],
                index=["Open", "In Progress", "Resolved", "Closed"].index(issue['status'])
            )
            
            if st.button("Update Status"):
                try:
                    update_issue_status(issue_id, new_status)
                    st.success(f"Status updated to: {new_status}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error updating status: {str(e)}")
    
    except Exception as e:
        st.error(f"Error loading issue details: {str(e)}")

if __name__ == "__main__":
    show_issue_details_page()
