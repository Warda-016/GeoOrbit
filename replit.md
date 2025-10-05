# Lahore Environmental & Social Issues Mapper

## Overview

The Lahore Environmental & Social Issues Mapper is an interactive web application built with Streamlit that enables citizens to report, track, and analyze environmental and social issues in Lahore, Pakistan. The platform combines geospatial mapping, AI-powered analysis, machine learning predictions, and NASA satellite data to provide comprehensive insights into urban challenges. Key features include interactive issue mapping, community engagement, severity tracking, AI-generated recommendations, hotspot predictions, and data export capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture

**Framework Choice: Streamlit**
- **Rationale**: Streamlit provides rapid development of data-driven web applications with minimal frontend code, ideal for prototyping and deploying ML/data science applications
- **Pros**: Fast development, automatic UI updates, built-in component library, excellent for data visualization
- **Cons**: Limited customization compared to traditional web frameworks, server-based rendering model
- **Multi-page Structure**: Uses Streamlit's native multi-page architecture with separate page modules (`pages/dashboard.py`, `pages/issue_details.py`, `pages/report_issue.py`)

**Interactive Mapping: Folium + Streamlit-Folium**
- **Rationale**: Folium generates interactive Leaflet.js maps in Python, with streamlit-folium providing seamless Streamlit integration
- **Features**: Multiple tile layers (OpenStreetMap, Google Satellite), marker clustering, landmark references, custom styling
- **Problem Addressed**: Need for interactive geospatial visualization of issues across Lahore

**Data Visualization: Plotly**
- **Rationale**: Plotly provides interactive charts and graphs for the analytics dashboard
- **Use Case**: Temporal trends, severity distributions, issue type breakdowns

### Backend Architecture

**Application Structure: Modular Utilities**
- **Design Pattern**: Separation of concerns with dedicated utility modules
- **Modules**:
  - `map_utils.py`: Map creation and marker management
  - `data_manager.py`: Data persistence and retrieval
  - `ai_analysis.py`: AI-powered issue analysis
  - `ml_analysis.py`: Machine learning predictions
  - `nasa_api.py`: External satellite data integration
  - `auth.py`: User authentication
  - `community_engagement.py`: Community features
  - `export_data.py`: Data export functionality

**Session State Management**
- **Approach**: Streamlit's built-in session state for maintaining user context across interactions
- **State Variables**: Selected issues, view modes, authentication status

### Data Storage

**File-Based JSON Storage**
- **Current Solution**: JSON files for data persistence
  - `data/lahore_issues.json`: Issue records
  - `data/users.json`: User accounts
  - `data/community_engagement.json`: Comments, upvotes, follows
- **Rationale**: Simple deployment without external database dependencies, suitable for prototype/small-scale deployment
- **Data Structure**: Pandas DataFrames converted to/from JSON for in-memory processing
- **Pros**: No database setup required, version controllable, easy backup
- **Cons**: Not scalable for high-volume production, lacks concurrent write handling, no relational integrity

**Data Schema (Issues)**
- Core fields: id, title, type, severity, location, description, status, date_reported, lat, lon
- Extended fields: affected_population, duration, health_impact, environmental_impact, economic_impact, urgency
- Flexible schema allows for additional fields as needed

### Authentication & Authorization

**Simple Hash-Based Authentication**
- **Method**: SHA-256 password hashing with email-based accounts
- **Storage**: User credentials in JSON file
- **Features**: Registration, login, password hashing, session management
- **Limitation**: No password reset mechanism, no role-based access control (RBAC)
- **User Data**: Tracks reported issues per user for community engagement

### AI/ML Integration

**OpenAI GPT Integration**
- **Model**: GPT-5 (as specified in code)
- **API Client**: Official OpenAI Python SDK
- **Use Cases**:
  - Issue summarization and analysis
  - Root cause identification
  - Health/environmental impact assessment
  - Recommendation generation
- **Rationale**: Leverages large language models for intelligent issue analysis without training custom models

**Machine Learning Predictions**
- **Framework**: scikit-learn
- **Algorithms**:
  - **DBSCAN Clustering**: Identifies geographic hotspots where issues cluster
  - **Random Forest (implied)**: For issue classification and prediction
- **Features**: Geospatial coordinates, issue types (label encoded), severity scores, temporal features (month, day of week)
- **Use Cases**: Hotspot prediction, emerging issue detection, trend forecasting
- **Rationale**: Provides predictive insights to help authorities allocate resources proactively

## External Dependencies

### Third-Party APIs

**NASA EONET API**
- **Purpose**: Fetches environmental events (wildfires, natural disasters) near Lahore
- **Endpoint**: `https://eonet.gsfc.nasa.gov/api/v3/events`
- **Authentication**: API key (defaults to DEMO_KEY)
- **Data Usage**: Enriches local issue data with satellite-detected environmental events
- **Geographic Filtering**: Calculates distance from Lahore coordinates to filter relevant events

**NASA GIBS WMS**
- **Purpose**: Provides satellite imagery layers for the map
- **Endpoint**: `https://gibs.earthdata.nasa.gov/wms/epsg4326/best/wms.cgi`
- **Usage**: Adds environmental data overlays to Folium maps

**OpenAI API**
- **Purpose**: AI-powered text analysis and generation
- **Model**: GPT-5
- **Authentication**: API key via environment variable `OPENAI_API_KEY`
- **Rate Limiting**: Managed by OpenAI's built-in limits
- **Token Budget**: Max completion tokens set to 512 for summaries

### Python Libraries

**Core Framework**
- `streamlit`: Web application framework
- `streamlit-folium`: Folium integration for Streamlit

**Data Processing**
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical operations

**Mapping & Geospatial**
- `folium`: Interactive map generation
- Distance calculations implemented manually (haversine formula)

**Machine Learning**
- `scikit-learn`: ML algorithms and preprocessing
  - `RandomForestClassifier`, `DBSCAN`, `LabelEncoder`

**AI Integration**
- `openai`: Official OpenAI SDK

**Visualization**
- `plotly`: Interactive charts (express and graph_objects)

**Utilities**
- `requests`: HTTP requests for NASA API
- `json`, `os`, `datetime`: Standard library utilities
- `hashlib`: Password hashing

### Configuration & Environment

**Environment Variables**
- `OPENAI_API_KEY`: Required for AI analysis features
- `NASA_API_KEY`: Optional (defaults to DEMO_KEY for limited access)

**File System Dependencies**
- Requires write access to `data/` directory for JSON storage
- Creates directory structure automatically if missing