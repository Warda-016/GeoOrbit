import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import streamlit as st
from datetime import datetime, timedelta

def prepare_ml_features(issues_df):
    """
    Prepare features for ML analysis from issues data
    """
    if issues_df.empty:
        return None, None, None
    
    df = issues_df.copy()
    
    df['month'] = pd.to_datetime(df['date_reported'], errors='coerce').dt.month
    df['day_of_week'] = pd.to_datetime(df['date_reported'], errors='coerce').dt.dayofweek
    
    type_encoder = LabelEncoder()
    df['type_encoded'] = type_encoder.fit_transform(df['type'])
    
    severity_mapping = {'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4}
    df['severity_score'] = df['severity'].map(severity_mapping)
    
    features = df[['lat', 'lon', 'type_encoded', 'severity_score', 'month', 'day_of_week']].fillna(0)
    
    return features, type_encoder, df

def predict_issue_hotspots(issues_df, grid_resolution=0.01):
    """
    Predict potential issue hotspots using ML clustering
    Returns locations likely to have future issues
    """
    try:
        if issues_df.empty or len(issues_df) < 10:
            return []
        
        features, type_encoder, df = prepare_ml_features(issues_df)
        if features is None:
            return []
        
        from sklearn.cluster import DBSCAN
        
        location_data = df[['lat', 'lon']].values
        
        clustering = DBSCAN(eps=0.02, min_samples=3).fit(location_data)
        df['cluster'] = clustering.labels_
        
        hotspots = []
        for cluster_id in set(clustering.labels_):
            if cluster_id == -1:
                continue
            
            cluster_points = df[df['cluster'] == cluster_id]
            
            if len(cluster_points) >= 3:
                center_lat = cluster_points['lat'].mean()
                center_lon = cluster_points['lon'].mean()
                
                issue_count = len(cluster_points)
                severity_avg = cluster_points['severity_score'].mean()
                most_common_type = cluster_points['type'].mode().iloc[0] if not cluster_points['type'].mode().empty else 'Mixed'
                
                risk_score = (issue_count * 0.4 + severity_avg * 0.6) * 10
                
                hotspots.append({
                    'lat': center_lat,
                    'lon': center_lon,
                    'issue_count': int(issue_count),
                    'risk_score': round(risk_score, 2),
                    'primary_type': most_common_type,
                    'avg_severity': round(severity_avg, 2)
                })
        
        hotspots.sort(key=lambda x: x['risk_score'], reverse=True)
        return hotspots
    
    except Exception as e:
        st.warning(f"Error predicting hotspots: {str(e)}")
        return []

def predict_emerging_issues(issues_df):
    """
    Identify emerging issue patterns using time series analysis
    """
    try:
        if issues_df.empty or len(issues_df) < 20:
            return []
        
        df = issues_df.copy()
        df['date_reported'] = pd.to_datetime(df['date_reported'], errors='coerce')
        df = df.dropna(subset=['date_reported'])
        
        df['week'] = df['date_reported'].dt.isocalendar().week
        df['year'] = df['date_reported'].dt.year
        
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_issues = df[df['date_reported'] >= recent_cutoff]
        
        older_cutoff = datetime.now() - timedelta(days=60)
        older_issues = df[(df['date_reported'] >= older_cutoff) & (df['date_reported'] < recent_cutoff)]
        
        emerging = []
        
        for issue_type in df['type'].unique():
            recent_count = len(recent_issues[recent_issues['type'] == issue_type])
            older_count = len(older_issues[older_issues['type'] == issue_type])
            
            if older_count > 0:
                growth_rate = ((recent_count - older_count) / older_count) * 100
            elif recent_count > 0:
                growth_rate = 100
            else:
                growth_rate = 0
            
            if growth_rate > 20 and recent_count >= 3:
                avg_severity = recent_issues[recent_issues['type'] == issue_type]['severity'].map({
                    'Low': 1, 'Medium': 2, 'High': 3, 'Critical': 4
                }).mean()
                
                emerging.append({
                    'type': issue_type,
                    'recent_count': int(recent_count),
                    'growth_rate': round(growth_rate, 1),
                    'avg_severity': round(avg_severity, 2) if not pd.isna(avg_severity) else 2.0,
                    'trend': 'Increasing' if growth_rate > 50 else 'Rising'
                })
        
        emerging.sort(key=lambda x: x['growth_rate'], reverse=True)
        return emerging
    
    except Exception as e:
        st.warning(f"Error analyzing emerging issues: {str(e)}")
        return []

def predict_resolution_time(issue_data):
    """
    Predict estimated resolution time based on issue characteristics
    Uses simple heuristics based on severity and type
    """
    severity_days = {
        'Low': 7,
        'Medium': 5,
        'High': 3,
        'Critical': 1
    }
    
    base_days = severity_days.get(issue_data.get('severity', 'Medium'), 5)
    
    type_multipliers = {
        'Air Quality': 1.5,
        'Water Pollution': 1.3,
        'Waste Management': 0.8,
        'Infrastructure': 2.0,
        'Healthcare Access': 1.8,
        'Public Safety': 0.7,
        'Transportation': 1.2
    }
    
    multiplier = type_multipliers.get(issue_data.get('type', 'Other'), 1.0)
    
    estimated_days = int(base_days * multiplier)
    
    return {
        'estimated_days': estimated_days,
        'priority': 'High' if estimated_days <= 2 else 'Medium' if estimated_days <= 5 else 'Normal',
        'confidence': 'Moderate'
    }

def generate_trend_forecast(issues_df, days_ahead=30):
    """
    Forecast issue trends for the next N days
    """
    try:
        if issues_df.empty or len(issues_df) < 10:
            return None
        
        df = issues_df.copy()
        df['date_reported'] = pd.to_datetime(df['date_reported'], errors='coerce')
        df = df.dropna(subset=['date_reported'])
        
        daily_counts = df.groupby(df['date_reported'].dt.date).size().reset_index()
        daily_counts.columns = ['date', 'count']
        
        recent_avg = daily_counts['count'].tail(7).mean()
        
        trend_direction = 'stable'
        if len(daily_counts) > 14:
            recent_7_avg = daily_counts['count'].tail(7).mean()
            previous_7_avg = daily_counts['count'].tail(14).head(7).mean()
            
            if recent_7_avg > previous_7_avg * 1.2:
                trend_direction = 'increasing'
            elif recent_7_avg < previous_7_avg * 0.8:
                trend_direction = 'decreasing'
        
        forecast = []
        current_date = datetime.now()
        
        for i in range(days_ahead):
            forecast_date = current_date + timedelta(days=i)
            
            if trend_direction == 'increasing':
                predicted_count = int(recent_avg * (1 + 0.02 * i))
            elif trend_direction == 'decreasing':
                predicted_count = max(1, int(recent_avg * (1 - 0.02 * i)))
            else:
                predicted_count = int(recent_avg)
            
            forecast.append({
                'date': forecast_date.strftime('%Y-%m-%d'),
                'predicted_issues': predicted_count,
                'trend': trend_direction
            })
        
        return {
            'forecast': forecast,
            'current_avg': round(recent_avg, 1),
            'trend_direction': trend_direction
        }
    
    except Exception as e:
        st.warning(f"Error generating forecast: {str(e)}")
        return None

def calculate_issue_correlation(issues_df):
    """
    Calculate correlations between different issue types
    Identifies which issues tend to occur together
    """
    try:
        if issues_df.empty or len(issues_df) < 20:
            return []
        
        df = issues_df.copy()
        
        location_grid = {}
        for _, issue in df.iterrows():
            grid_key = (round(issue['lat'], 2), round(issue['lon'], 2))
            if grid_key not in location_grid:
                location_grid[grid_key] = []
            location_grid[grid_key].append(issue['type'])
        
        correlations = []
        issue_types = df['type'].unique()
        
        for i, type1 in enumerate(issue_types):
            for type2 in issue_types[i+1:]:
                co_occurrence = 0
                type1_count = 0
                type2_count = 0
                
                for location, types in location_grid.items():
                    has_type1 = type1 in types
                    has_type2 = type2 in types
                    
                    if has_type1:
                        type1_count += 1
                    if has_type2:
                        type2_count += 1
                    if has_type1 and has_type2:
                        co_occurrence += 1
                
                if type1_count > 0 and type2_count > 0:
                    correlation_score = (co_occurrence / min(type1_count, type2_count)) * 100
                    
                    if correlation_score > 20:
                        correlations.append({
                            'type1': type1,
                            'type2': type2,
                            'correlation': round(correlation_score, 1),
                            'co_occurrences': co_occurrence
                        })
        
        correlations.sort(key=lambda x: x['correlation'], reverse=True)
        return correlations
    
    except Exception as e:
        st.warning(f"Error calculating correlations: {str(e)}")
        return []
