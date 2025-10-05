import streamlit as st
import pandas as pd
from datetime import datetime
from utils.data_manager import load_issues_data, save_issues_data
from utils.map_utils import create_lahore_map
from streamlit_folium import st_folium

def show_report_issue_page():
    st.set_page_config(page_title="Report Issue", page_icon="📝")

    st.title("📝 Report Environmental or Social Issue")
    st.markdown("Help improve Lahore by reporting issues in your area")

    # Issue reporting form
    with st.form("comprehensive_issue_form"):
        st.subheader("Issue Information")

        col1, col2 = st.columns(2)

        with col1:
            title = st.text_input(
                "Issue Title*",
                placeholder="e.g., 'Sewage overflow on Main Boulevard'",
                help="Provide a clear, concise title"
            )

            issue_type = st.selectbox(
                "Issue Category*",
                [
                    "Air Quality",
                    "Water Pollution", 
                    "Waste Management",
                    "Noise Pollution",
                    "Infrastructure",
                    "Healthcare Access",
                    "Public Safety",
                    "Transportation",
                    "Illegal Construction",
                    "Power Outages",
                    "Other"
                ],
                help="Select the category that best describes your issue"
            )

            severity = st.selectbox(
                "Severity Level*",
                ["Low", "Medium", "High", "Critical"],
                help="Low: Minor inconvenience, Critical: Immediate health/safety risk"
            )

            urgency = st.selectbox(
                "Response Urgency",
                ["Not Urgent", "Moderate", "Urgent", "Emergency"],
                help="How quickly does this need attention?"
            )

        with col2:
            location = st.text_input(
                "Location Details*",
                placeholder="Street address, landmarks, or area name",
                help="Be as specific as possible"
            )

            affected_population = st.selectbox(
                "People Affected",
                ["Individual", "Few People (2-10)", "Many People (11-50)", 
                 "Large Group (50+)", "Entire Neighborhood"]
            )

            duration = st.selectbox(
                "Issue Duration",
                ["Just Started", "Few Days", "Few Weeks", "Few Months", "Ongoing for Years"]
            )

            time_of_day = st.multiselect(
                "When is this issue most noticeable?",
                ["Morning", "Afternoon", "Evening", "Night", "All Day"]
            )

        st.subheader("Detailed Description")
        description = st.text_area(
            "Describe the issue in detail*",
            placeholder="What exactly is happening? How is it affecting you and others? Any specific details that might help?",
            height=120,
            help="The more detail you provide, the better we can understand and address the issue"
        )

        # Additional details
        col1, col2 = st.columns(2)

        with col1:
            health_impact = st.checkbox("This issue affects public health")
            environmental_impact = st.checkbox("This issue harms the environment")
            economic_impact = st.checkbox("This issue has economic consequences")

        with col2:
            recurring_issue = st.checkbox("This is a recurring problem")
            reported_before = st.checkbox("I've reported this issue before")
            multiple_locations = st.checkbox("This issue exists in multiple locations")

        # Contact information
        st.subheader("Contact Information (Optional)")
        col1, col2 = st.columns(2)

        with col1:
            contact_name = st.text_input("Your Name")
            contact_email = st.text_input("Email Address")

        with col2:
            contact_phone = st.text_input("Phone Number")
            follow_up = st.checkbox("I want updates on this issue")

        # Location picker
        st.subheader("Precise Location")
        st.markdown("Click on the map to mark the exact location of the issue:")

        try:
            location_map = create_lahore_map()
            map_data = st_folium(location_map, width=700, height=400)

            lat, lon = 31.5497, 74.3436  # Default Lahore coordinates
            if map_data['last_clicked']:
                lat = map_data['last_clicked']['lat']
                lon = map_data['last_clicked']['lng']
                st.success(f"📍 Location selected: {lat:.6f}, {lon:.6f}")
        except Exception as e:
            st.error(f"Map loading error: {str(e)}")

        # Submit form
        st.markdown("---")
        submitted = st.form_submit_button("🚀 Submit Issue Report", use_container_width=True)

        if submitted:
            # Validate required fields
            if not all([title, issue_type, severity, location, description]):
                st.error("❌ Please fill in all required fields marked with *")
            else:
                try:
                    # Load existing data
                    issues_df = load_issues_data()
                    new_id = max(issues_df['id']) + 1 if not issues_df.empty else 1

                    # Create new issue record
                    new_issue = {
                        'id': new_id,
                        'title': title,
                        'type': issue_type,
                        'severity': severity,
                        'urgency': urgency,
                        'location': location,
                        'description': description,
                        'affected_population': affected_population,
                        'duration': duration,
                        'time_of_day': ', '.join(time_of_day) if time_of_day else 'Not specified',
                        'health_impact': health_impact,
                        'environmental_impact': environmental_impact,
                        'economic_impact': economic_impact,
                        'recurring_issue': recurring_issue,
                        'reported_before': reported_before,
                        'multiple_locations': multiple_locations,
                        'contact_name': contact_name,
                        'contact_email': contact_email,
                        'contact_phone': contact_phone,
                        'follow_up': follow_up,
                        'status': 'Open',
                        'date_reported': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'lat': lat,
                        'lon': lon
                    }

                    # Add to DataFrame and save
                    new_row_df = pd.DataFrame([new_issue])
                    updated_df = pd.concat([issues_df, new_row_df], ignore_index=True)
                    save_issues_data(updated_df)

                    # Success message
                    st.success("✅ Issue reported successfully!")
                    st.balloons()

                    # Show issue ID for tracking
                    st.info(f"📋 Your issue has been assigned ID: **{new_id}**. Please save this for future reference.")

                    # Reset form by rerunning
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error saving issue report: {str(e)}")

    # Help section
    with st.expander("ℹ️ Reporting Guidelines"):
        st.markdown("""
        ### How to Report Effectively:

        **📝 Be Specific:**
        - Use clear, descriptive titles
        - Provide exact locations with landmarks
        - Include specific times when applicable

        **📊 Choose Appropriate Severity:**
        - **Low:** Minor inconveniences, aesthetic issues
        - **Medium:** Issues affecting quality of life
        - **High:** Problems posing health or safety risks  
        - **Critical:** Immediate dangers requiring urgent attention

        **📍 Location Tips:**
        - Click the map to mark exact locations
        - Use nearby landmarks for reference
        - Include street names and area details

        **🔄 Follow Up:**
        - Provide contact information for updates
        - Check back periodically for status changes
        - Report additional details if discovered later
        """)

if __name__ == "__main__":
    show_report_issue_page()
