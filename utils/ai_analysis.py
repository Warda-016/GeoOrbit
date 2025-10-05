import os
import json
from openai import OpenAI
import streamlit as st

# the newest OpenAI model is "gpt-5" which was released August 7, 2025.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "default_key")

# This is using OpenAI's API, which points to OpenAI's API servers and requires your own API key.
openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_issue_summary(issue_data):
    """Generate a comprehensive summary of an issue using AI"""
    try:
        prompt = f"""
        Analyze the following environmental/social issue report from Lahore, Pakistan and provide a comprehensive summary:
        
        Title: {issue_data.get('title', 'N/A')}
        Type: {issue_data.get('type', 'N/A')}
        Severity: {issue_data.get('severity', 'N/A')}
        Location: {issue_data.get('location', 'N/A')}
        Description: {issue_data.get('description', 'N/A')}
        
        Please provide:
        1. A brief summary of the issue
        2. Potential causes and contributing factors
        3. Health and environmental impacts
        4. Urgency assessment
        5. Similar issues that commonly occur in urban areas like Lahore
        
        Keep the response informative but concise (200-300 words).
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=512
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating summary: {str(e)}"

def generate_issue_analysis(issue_data):
    """Generate detailed analysis of an issue"""
    try:
        prompt = f"""
        As an urban planning and environmental expert, provide a detailed analysis of this issue from Lahore:
        
        Issue Details:
        - Title: {issue_data.get('title', 'N/A')}
        - Type: {issue_data.get('type', 'N/A')}
        - Severity: {issue_data.get('severity', 'N/A')}
        - Location: {issue_data.get('location', 'N/A')}
        - Description: {issue_data.get('description', 'N/A')}
        - Duration: {issue_data.get('duration', 'N/A')}
        
        Provide analysis on:
        1. Root cause analysis - What are the likely underlying causes?
        2. Impact assessment - Who and what is affected?
        3. Risk evaluation - What are the short and long-term risks?
        4. Systemic connections - How does this relate to broader urban challenges?
        5. Priority assessment - Why should this be prioritized?
        
        Focus on Lahore's specific urban context and challenges.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1024
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating analysis: {str(e)}"

def generate_recommendations(issue_data):
    """Generate actionable recommendations for addressing the issue"""
    try:
        prompt = f"""
        Based on this issue report from Lahore, Pakistan, provide specific, actionable recommendations:
        
        Issue: {issue_data.get('title', 'N/A')}
        Type: {issue_data.get('type', 'N/A')}
        Severity: {issue_data.get('severity', 'N/A')}
        Location: {issue_data.get('location', 'N/A')}
        Description: {issue_data.get('description', 'N/A')}
        
        Provide recommendations for:
        
        **Immediate Actions** (Next 1-7 days):
        - What can be done right now to mitigate harm?
        - Who should be contacted immediately?
        
        **Short-term Solutions** (1-3 months):
        - What practical steps can resolve this specific issue?
        - Which local authorities or departments should be involved?
        
        **Long-term Prevention** (6+ months):
        - How can similar issues be prevented in the future?
        - What systemic changes are needed?
        
        **Community Actions**:
        - How can local residents help?
        - What can individuals do to contribute to the solution?
        
        Consider Lahore's local government structure, resources, and common urban challenges.
        Be specific and practical in your recommendations.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1024
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating recommendations: {str(e)}"

def analyze_issue_trends(issues_df):
    """Analyze trends across multiple issues using AI"""
    try:
        if issues_df.empty:
            return "No data available for trend analysis."
        
        # Prepare summary data for AI analysis
        summary_stats = {
            'total_issues': len(issues_df),
            'types': issues_df['type'].value_counts().to_dict(),
            'severities': issues_df['severity'].value_counts().to_dict(),
            'statuses': issues_df['status'].value_counts().to_dict(),
            'recent_trends': issues_df['type'].tail(20).value_counts().to_dict()
        }
        
        prompt = f"""
        Analyze the following environmental and social issues data from Lahore, Pakistan:
        
        Summary Statistics: {json.dumps(summary_stats, indent=2)}
        
        Provide insights on:
        1. Most critical issue types that need immediate attention
        2. Patterns and trends you observe
        3. Areas where the city seems to be struggling most
        4. Potential correlations between different types of issues
        5. Strategic recommendations for city planners and officials
        
        Focus on actionable insights that could help improve urban planning and issue resolution in Lahore.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1024
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error analyzing trends: {str(e)}"

def generate_issue_category_insights(issue_type, issues_df):
    """Generate insights specific to a category of issues"""
    try:
        category_issues = issues_df[issues_df['type'] == issue_type]
        
        if category_issues.empty:
            return f"No {issue_type} issues found in the database."
        
        # Get sample descriptions for context
        sample_descriptions = category_issues['description'].head(5).tolist()
        locations = category_issues['location'].value_counts().head(10).to_dict()
        
        prompt = f"""
        Analyze {issue_type} issues in Lahore based on the following data:
        
        Total {issue_type} issues: {len(category_issues)}
        Most affected locations: {json.dumps(locations, indent=2)}
        
        Sample issue descriptions:
        {chr(10).join(f"- {desc[:200]}..." for desc in sample_descriptions)}
        
        Provide specific insights about {issue_type} issues in Lahore:
        
        1. Common patterns in these issues
        2. Geographic hotspots and why they might be affected
        3. Seasonal or temporal patterns (if applicable)
        4. Root causes specific to {issue_type} in urban Pakistan
        5. Best practices for prevention and resolution
        6. Stakeholders who should be involved in solutions
        
        Make recommendations specific to Lahore's urban context and infrastructure.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1024
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating category insights: {str(e)}"

def generate_priority_assessment(issues_df):
    """Generate AI-powered priority assessment for issues"""
    try:
        if issues_df.empty:
            return "No issues to assess."
        
        # Focus on open issues only
        open_issues = issues_df[issues_df['status'] == 'Open']
        
        if open_issues.empty:
            return "No open issues requiring priority assessment."
        
        # Prepare data for analysis
        priority_data = []
        for _, issue in open_issues.head(20).iterrows():  # Limit to top 20 for analysis
            priority_data.append({
                'id': issue['id'],
                'title': issue['title'],
                'type': issue['type'],
                'severity': issue['severity'],
                'description': issue['description'][:200],
                'location': issue['location']
            })
        
        prompt = f"""
        As an urban crisis management expert, assess the priority of these open issues in Lahore:
        
        {json.dumps(priority_data, indent=2)}
        
        Rank these issues by priority considering:
        1. Public health and safety impact
        2. Number of people potentially affected
        3. Environmental consequences
        4. Economic implications
        5. Urgency of intervention needed
        6. Risk of escalation if left unaddressed
        
        Provide:
        1. Top 5 highest priority issues with brief justification
        2. Issues that should be grouped together for efficient resolution
        3. Resources and expertise needed for top priorities
        4. Timeline recommendations for addressing each priority level
        
        Consider Lahore's specific challenges including population density, monsoon season, infrastructure limitations, and available municipal resources.
        """
        
        response = openai_client.chat.completions.create(
            model="gpt-5",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=1024
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating priority assessment: {str(e)}"
