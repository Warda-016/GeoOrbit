import pandas as pd
import json
import os
from datetime import datetime
import streamlit as st

DATA_FILE = "data/lahore_issues.json"

def ensure_data_directory():
    """Ensure the data directory exists"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

def load_issues_data():
    """Load issues data from JSON file"""
    ensure_data_directory()
    
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if data:
                df = pd.DataFrame(data)
                # Ensure required columns exist
                required_columns = [
                    'id', 'title', 'type', 'severity', 'location', 
                    'description', 'status', 'date_reported', 'lat', 'lon'
                ]
                
                for col in required_columns:
                    if col not in df.columns:
                        df[col] = None
                
                return df
            else:
                return pd.DataFrame(columns=get_default_columns())
        else:
            # Create initial data file with sample data
            return create_initial_data()
            
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame(columns=get_default_columns())

def get_default_columns():
    """Get default column structure for issues data"""
    return [
        'id', 'title', 'type', 'severity', 'urgency', 'location', 
        'description', 'affected_population', 'duration', 'time_of_day',
        'health_impact', 'environmental_impact', 'economic_impact',
        'recurring_issue', 'reported_before', 'multiple_locations',
        'contact_name', 'contact_email', 'contact_phone', 'follow_up',
        'status', 'date_reported', 'lat', 'lon'
    ]

def create_initial_data():
    """Create initial sample data for demonstration"""
    
    # Start with empty DataFrame - no mock data
    df = pd.DataFrame(columns=get_default_columns())
    save_issues_data(df)
    return df

def save_issues_data(df):
    """Save issues data to JSON file"""
    ensure_data_directory()
    
    try:
        # Convert DataFrame to records and save
        data = df.to_dict('records')
        
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        return True
        
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

def update_issue_status(issue_id, new_status):
    """Update the status of a specific issue"""
    try:
        df = load_issues_data()
        
        if issue_id in df['id'].values:
            df.loc[df['id'] == issue_id, 'status'] = new_status
            df.loc[df['id'] == issue_id, 'last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            save_issues_data(df)
            return True
        else:
            st.error(f"Issue with ID {issue_id} not found")
            return False
            
    except Exception as e:
        st.error(f"Error updating issue status: {str(e)}")
        return False

def get_issue_by_id(issue_id):
    """Get a specific issue by ID"""
    try:
        df = load_issues_data()
        
        if issue_id in df['id'].values:
            return df[df['id'] == issue_id].iloc[0]
        else:
            return None
            
    except Exception as e:
        st.error(f"Error retrieving issue: {str(e)}")
        return None

def get_issues_by_type(issue_type):
    """Get all issues of a specific type"""
    try:
        df = load_issues_data()
        return df[df['type'] == issue_type]
        
    except Exception as e:
        st.error(f"Error filtering issues by type: {str(e)}")
        return pd.DataFrame()

def get_issues_by_severity(severity):
    """Get all issues of a specific severity level"""
    try:
        df = load_issues_data()
        return df[df['severity'] == severity]
        
    except Exception as e:
        st.error(f"Error filtering issues by severity: {str(e)}")
        return pd.DataFrame()

def get_issues_by_status(status):
    """Get all issues with a specific status"""
    try:
        df = load_issues_data()
        return df[df['status'] == status]
        
    except Exception as e:
        st.error(f"Error filtering issues by status: {str(e)}")
        return pd.DataFrame()

def get_recent_issues(days=7):
    """Get issues reported in the last N days"""
    try:
        df = load_issues_data()
        
        if df.empty:
            return df
        
        df['date_reported'] = pd.to_datetime(df['date_reported'], errors='coerce')
        cutoff_date = datetime.now() - pd.Timedelta(days=days)
        
        return df[df['date_reported'] >= cutoff_date]
        
    except Exception as e:
        st.error(f"Error retrieving recent issues: {str(e)}")
        return pd.DataFrame()

def get_issues_statistics():
    """Get summary statistics for all issues"""
    try:
        df = load_issues_data()
        
        if df.empty:
            return {}
        
        stats = {
            'total_issues': len(df),
            'open_issues': len(df[df['status'] == 'Open']),
            'resolved_issues': len(df[df['status'] == 'Resolved']),
            'critical_issues': len(df[df['severity'] == 'Critical']),
            'by_type': df['type'].value_counts().to_dict(),
            'by_severity': df['severity'].value_counts().to_dict(),
            'by_status': df['status'].value_counts().to_dict()
        }
        
        return stats
        
    except Exception as e:
        st.error(f"Error calculating statistics: {str(e)}")
        return {}

def export_issues_data(format='csv'):
    """Export issues data in specified format"""
    try:
        df = load_issues_data()
        
        if format.lower() == 'csv':
            return df.to_csv(index=False)
        elif format.lower() == 'json':
            return df.to_json(orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
            
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")
        return None

def search_issues(query, search_fields=['title', 'description', 'location']):
    """Search issues by text query in specified fields"""
    try:
        df = load_issues_data()
        
        if df.empty or not query.strip():
            return df
        
        # Create a combined search field
        search_text = df[search_fields].fillna('').apply(
            lambda x: ' '.join(x.astype(str)).lower(), axis=1
        )
        
        # Filter by query
        mask = search_text.str.contains(query.lower(), na=False)
        return df[mask]
        
    except Exception as e:
        st.error(f"Error searching issues: {str(e)}")
        return pd.DataFrame()

def validate_issue_data(issue_data):
    """Validate issue data before saving"""
    required_fields = ['title', 'type', 'severity', 'location', 'description']
    
    for field in required_fields:
        if not issue_data.get(field):
            return False, f"Missing required field: {field}"
    
    valid_severities = ['Low', 'Medium', 'High', 'Critical']
    if issue_data.get('severity') not in valid_severities:
        return False, f"Invalid severity level. Must be one of: {valid_severities}"
    
    valid_statuses = ['Open', 'In Progress', 'Resolved', 'Closed']
    if issue_data.get('status', 'Open') not in valid_statuses:
        return False, f"Invalid status. Must be one of: {valid_statuses}"
    
    return True, "Valid"

def backup_data():
    """Create a backup of the current data"""
    try:
        if os.path.exists(DATA_FILE):
            backup_file = f"{DATA_FILE}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            with open(DATA_FILE, 'r') as src, open(backup_file, 'w') as dst:
                dst.write(src.read())
            
            return backup_file
        
    except Exception as e:
        st.error(f"Error creating backup: {str(e)}")
        return None
