import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import json
import os

ENGAGEMENT_FILE = "data/community_engagement.json"

def ensure_engagement_file():
    """Ensure engagement file exists"""
    os.makedirs(os.path.dirname(ENGAGEMENT_FILE), exist_ok=True)
    if not os.path.exists(ENGAGEMENT_FILE):
        with open(ENGAGEMENT_FILE, 'w') as f:
            json.dump({
                'comments': [],
                'upvotes': {},
                'follows': {}
            }, f)

def load_engagement_data():
    """Load community engagement data"""
    ensure_engagement_file()
    try:
        with open(ENGAGEMENT_FILE, 'r') as f:
            return json.load(f)
    except:
        return {'comments': [], 'upvotes': {}, 'follows': {}}

def save_engagement_data(data):
    """Save community engagement data"""
    ensure_engagement_file()
    with open(ENGAGEMENT_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_comment(issue_id, user_email, comment_text):
    """Add a comment to an issue"""
    data = load_engagement_data()
    
    comment = {
        'issue_id': issue_id,
        'user_email': user_email,
        'comment': comment_text,
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    data['comments'].append(comment)
    save_engagement_data(data)
    return True

def get_issue_comments(issue_id):
    """Get all comments for an issue"""
    data = load_engagement_data()
    return [c for c in data['comments'] if c['issue_id'] == issue_id]

def upvote_issue(issue_id, user_email):
    """Upvote an issue"""
    data = load_engagement_data()
    
    issue_key = str(issue_id)
    if issue_key not in data['upvotes']:
        data['upvotes'][issue_key] = []
    
    if user_email not in data['upvotes'][issue_key]:
        data['upvotes'][issue_key].append(user_email)
        save_engagement_data(data)
        return True
    return False

def get_upvote_count(issue_id):
    """Get upvote count for an issue"""
    data = load_engagement_data()
    issue_key = str(issue_id)
    return len(data['upvotes'].get(issue_key, []))

def follow_issue(issue_id, user_email):
    """Follow an issue for updates"""
    data = load_engagement_data()
    
    issue_key = str(issue_id)
    if issue_key not in data['follows']:
        data['follows'][issue_key] = []
    
    if user_email not in data['follows'][issue_key]:
        data['follows'][issue_key].append(user_email)
        save_engagement_data(data)
        return True
    return False

def get_follow_count(issue_id):
    """Get follow count for an issue"""
    data = load_engagement_data()
    issue_key = str(issue_id)
    return len(data['follows'].get(issue_key, []))

def calculate_resolution_stats(issues_df):
    """Calculate resolution statistics"""
    if issues_df.empty:
        return None
    
    total = len(issues_df)
    resolved = len(issues_df[issues_df['status'] == 'Resolved'])
    in_progress = len(issues_df[issues_df['status'] == 'In Progress'])
    open_issues = len(issues_df[issues_df['status'] == 'Open'])
    
    resolution_rate = (resolved / total * 100) if total > 0 else 0
    
    df = issues_df.copy()
    df['date_reported'] = pd.to_datetime(df['date_reported'], errors='coerce')
    
    recent_30_days = df[df['date_reported'] >= datetime.now() - timedelta(days=30)]
    if not recent_30_days.empty:
        recent_resolved = len(recent_30_days[recent_30_days['status'] == 'Resolved'])
        recent_total = len(recent_30_days)
        recent_resolution_rate = (recent_resolved / recent_total * 100) if recent_total > 0 else 0
    else:
        recent_resolution_rate = 0
    
    return {
        'total_issues': total,
        'resolved': resolved,
        'in_progress': in_progress,
        'open': open_issues,
        'resolution_rate': round(resolution_rate, 1),
        'recent_resolution_rate': round(recent_resolution_rate, 1)
    }

def calculate_impact_metrics(issues_df):
    """Calculate community impact metrics"""
    if issues_df.empty:
        return None
    
    engagement_data = load_engagement_data()
    
    total_upvotes = sum(len(votes) for votes in engagement_data['upvotes'].values())
    total_comments = len(engagement_data['comments'])
    total_follows = sum(len(follows) for follows in engagement_data['follows'].values())
    
    severity_impact = {
        'Critical': 0,
        'High': 0,
        'Medium': 0,
        'Low': 0
    }
    
    for _, issue in issues_df.iterrows():
        severity = issue['severity']
        if severity in severity_impact:
            severity_impact[severity] += 1
    
    critical_resolved = len(issues_df[
        (issues_df['severity'] == 'Critical') & 
        (issues_df['status'] == 'Resolved')
    ])
    
    return {
        'total_engagement': total_upvotes + total_comments + total_follows,
        'upvotes': total_upvotes,
        'comments': total_comments,
        'follows': total_follows,
        'critical_resolved': critical_resolved,
        'severity_distribution': severity_impact
    }

def get_trending_issues(issues_df, days=7):
    """Get trending issues based on recent engagement"""
    if issues_df.empty:
        return []
    
    engagement_data = load_engagement_data()
    
    recent_date = datetime.now() - timedelta(days=days)
    recent_comments = [c for c in engagement_data['comments'] 
                      if datetime.strptime(c['timestamp'], '%Y-%m-%d %H:%M:%S') >= recent_date]
    
    issue_engagement = {}
    for comment in recent_comments:
        issue_id = comment['issue_id']
        if issue_id not in issue_engagement:
            issue_engagement[issue_id] = 0
        issue_engagement[issue_id] += 1
    
    for issue_id, upvoters in engagement_data['upvotes'].items():
        iid = int(issue_id)
        if iid not in issue_engagement:
            issue_engagement[iid] = 0
        issue_engagement[iid] += len(upvoters) * 0.5
    
    sorted_issues = sorted(issue_engagement.items(), key=lambda x: x[1], reverse=True)
    
    trending = []
    for issue_id, score in sorted_issues[:10]:
        issue_row = issues_df[issues_df['id'] == issue_id]
        if not issue_row.empty:
            issue = issue_row.iloc[0]
            trending.append({
                'id': issue_id,
                'title': issue['title'],
                'type': issue['type'],
                'severity': issue['severity'],
                'engagement_score': round(score, 1),
                'upvotes': get_upvote_count(issue_id),
                'comments': len(get_issue_comments(issue_id))
            })
    
    return trending
