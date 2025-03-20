import streamlit as st
import pandas as pd
import yaml
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from google_auth_oauthlib.flow import Flow
import base64

# Page Configuration
st.set_page_config(
    page_title="AdSync Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Modern 3D-style background and enhanced UI
# Modern Dark Blue Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Poppins', sans-serif;
    }
    
    .main {
        background: #0a192f; /* Dark blue background */
        color: #ffffff; /* White text */
        padding: 1rem;
    }
    
    .stApp {
        background: #0a192f; /* Dark blue background */
        color: #ffffff; /* White text */
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #112240; /* Darker blue for sidebar */
    }
    
    .sidebar .sidebar-content {
        background-color: #112240; /* Darker blue for sidebar */
        color: #ffffff; /* White text */
    }
    
    /* Cards with 3D effect */
    .metric-card {
        background: #112240; /* Darker blue for cards */
        border-radius: 15px;
        padding: 24px;
        margin: 10px 0;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease-in-out;
        position: relative;
        z-index: 1;
        overflow: hidden;
        color: #ffffff; /* White text */
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        right: 0;
        width: 100px;
        height: 100px;
        background: linear-gradient(225deg, rgba(66, 153, 225, 0.1) 0%, rgba(255, 255, 255, 0) 50%);
        border-radius: 0 0 0 100%;
        z-index: -1;
    }
    
    /* Metric styling */
    .metric-title {
        color: #a8b2d1; /* Light blue-gray for titles */
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #ffffff; /* White text */
        margin-bottom: 8px;
    }
    
    .metric-change {
        font-size: 13px;
        font-weight: 500;
        padding: 4px 8px;
        border-radius: 12px;
        display: inline-block;
    }
    
    .metric-change.positive {
        background-color: rgba(72, 187, 120, 0.1);
        color: #48bb78;
    }
    
    .metric-change.negative {
        background-color: rgba(245, 101, 101, 0.1);
        color: #f56565;
    }
    
    /* Chart containers */
    .chart-container {
        background: #112240; /* Darker blue for charts */
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        color: #ffffff; /* White text */
    }
    
    .chart-title {
        color: #ffffff; /* White text */
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #233554; /* Darker blue border */
    }
    
    /* Table styling */
    .stDataFrame {
        background: #112240; /* Darker blue for tables */
        border-radius: 15px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        color: #ffffff; /* White text */
    }
    
    /* Button styling */
    .stButton>button {
        background-color: #4299e1;
        color: white;
        border-radius: 12px;
        padding: 10px 25px;
        font-weight: 500;
        border: none;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #3182ce;
        box-shadow: 0 4px 12px rgba(66, 153, 225, 0.3);
        transform: translateY(-2px);
    }
    
    /* Custom header */
    .dashboard-header {
        display: flex;
        align-items: center;
        margin-bottom: 30px;
    }
    
    .dashboard-logo {
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(90deg, #4299e1, #9f7aea);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-right: 10px;
    }
    
    .dashboard-subtitle {
        color: #a8b2d1; /* Light blue-gray for subtitles */
        font-size: 16px;
        font-weight: 400;
    }
    
    /* Plotly chart styling */
    .stPlotlyChart {
        background: #112240; /* Darker blue for charts */
        border-radius: 15px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        padding: 20px;
        transition: all 0.3s ease;
    }
    
    .stPlotlyChart:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
    }
    
    /* Login page styling */
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100vh;
        background: #0a192f;
    }
    
    .login-box {
        background: #112240;
        padding: 40px;
        border-radius: 15px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
        text-align: center;
        max-width: 400px;
        width: 100%;
    }
    
    .login-box h2 {
        color: #ffffff;
        margin-bottom: 20px;
    }
    
    .login-box p {
        color: #a8b2d1;
        margin-bottom: 30px;
    }
    
    .google-login-button {
        background-color: #4285F4;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 10px 25px;
        font-weight: 500;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .google-login-button:hover {
        background-color: #357ABD;
        box-shadow: 0 4px 12px rgba(66, 133, 244, 0.3);
        transform: translateY(-2px);
    }
    
    .google-login-button img {
        width: 20px;
        margin-right: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Function to generate icons as base64 for SVG icons
def get_icon_base64(icon_name):
    icons = {
        "money": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="6" x2="12" y2="12"></line><path d="M12 12L16 16"></path></svg>''',
        "click": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3L22 4"></path><path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"></path></svg>''',
        "conversion": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>''',
        "cost": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="1" x2="12" y2="23"></line><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path></svg>''',
        "dashboard": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>''',
        "empty": '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>'''
    }
    return base64.b64encode(icons[icon_name].encode('utf-8')).decode()

# Load configuration from YAML
@st.cache_resource
def load_yaml_config():
    try:
        with open("google-ads.yaml") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        return None

yaml_config = load_yaml_config()

# OAuth Configuration
if yaml_config:
    CLIENT_CONFIG = {
        "web": {
            "client_id": yaml_config['client_id'],
            "client_secret": yaml_config['client_secret'],
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://accounts.google.com/o/oauth2/token"
        }
    }
    REDIRECT_URI = "http://localhost:8501"
    SCOPES = ["https://www.googleapis.com/auth/adwords"]
else:
    st.error("Configuration file not found. Please ensure google-ads.yaml exists.")
    st.stop()

def get_google_ads_client(credentials):
    config = {
        "developer_token": yaml_config['developer_token'],
        "client_id": yaml_config['client_id'],
        "client_secret": yaml_config['client_secret'],
        "refresh_token": credentials['refresh_token'],
        "login_customer_id": yaml_config['login_customer_id'],
        "use_proto_plus": yaml_config['use_proto_plus']
    }
    return GoogleAdsClient.load_from_dict(config)

def handle_oauth():
    flow = Flow.from_client_config(
        client_config=CLIENT_CONFIG,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    
    query_params = st.query_params.to_dict()
    if 'code' not in query_params and 'credentials' not in st.session_state:
        auth_url, _ = flow.authorization_url()
        st.markdown(f"""
        <div class="login-container">
            <div class="login-box">
                <h2>Welcome to AdSync</h2>
                <p>Please log in with your Google Ads account to continue</p>
                <a href="{auth_url}" target="_self" class="google-login-button">
                    <img src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" alt="Google logo">
                    Login with Google
                </a>
            </div>
        </div>
        """, unsafe_allow_html=True)
        return None
    elif 'code' in query_params and 'credentials' not in st.session_state:
        flow.fetch_token(code=query_params['code'])
        credentials = flow.credentials
        st.session_state['credentials'] = {
            "token": credentials.token,
            "refresh_token": credentials.refresh_token
        }
        st.query_params.clear()
        st.rerun()
    return st.session_state.get('credentials')

@st.cache_data(ttl=3600)
def get_accessible_customers(_client):  # Changed parameter name with underscore
    try:
        customer_service = _client.get_service("CustomerService")
        response = customer_service.list_accessible_customers()
        return [cid.split('/')[1] for cid in response.resource_names]
    except GoogleAdsException as ex:
        st.error(f"Google Ads API error: {ex.error.code().name}")
        st.error(ex.error.message)
        return []

@st.cache_data(ttl=300)
def fetch_campaign_data(_client, customer_id, start_date, end_date):  # Changed parameter name
    try:
        ga_service = _client.get_service("GoogleAdsService")
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                segments.date,
                metrics.impressions,
                metrics.clicks,
                metrics.ctr,
                metrics.average_cpc,
                metrics.conversions,
                metrics.conversions_value,
                metrics.cost_micros,
                metrics.search_impression_share
            FROM campaign
            WHERE segments.date BETWEEN '{start_date}' AND '{end_date}'
        """
        
        response = ga_service.search_stream(customer_id=customer_id, query=query)
        
        data = []
        for batch in response:
            for row in batch.results:
                data.append({
                    "Campaign ID": row.campaign.id,
                    "Campaign Name": row.campaign.name,
                    "Status": row.campaign.status.name,
                    "Date": row.segments.date,
                    "Impressions": row.metrics.impressions,
                    "Clicks": row.metrics.clicks,
                    "CTR (%)": row.metrics.ctr * 100,
                    "Avg. CPC": row.metrics.average_cpc / 1e6,
                    "Conversions": row.metrics.conversions,
                    "Cost": row.metrics.cost_micros / 1e6,
                    "Impression Share (%)": row.metrics.search_impression_share * 100 if row.metrics.search_impression_share else 0
                })
        return pd.DataFrame(data)
    except GoogleAdsException as ex:
        st.error(f"Google Ads API error: {ex.error.code().name}")
        st.error(ex.error.message)
        return pd.DataFrame()

def format_status(status):
    status_class = "active" if status == "ENABLED" else "paused" if status == "PAUSED" else "removed"
    return f'<span class="pill-status {status_class.lower()}">{status.title()}</span>'

def main():
    # Handle OAuth and get credentials
    credentials = handle_oauth()
    
    if credentials:
        client = get_google_ads_client(credentials)
        
        if 'customers' not in st.session_state:
            with st.spinner("Loading accounts..."):
                customers = get_accessible_customers(client)
                if customers:
                    st.session_state.customers = customers
                else:
                    st.error("No accessible Google Ads accounts found")

        if 'customers' in st.session_state:
            st.sidebar.markdown("### Account Settings")
            customer_id = st.sidebar.selectbox("Select Account", st.session_state.customers)
            
            st.sidebar.markdown("### Date Range")
            col1, col2 = st.sidebar.columns(2)
            start_date = col1.date_input("Start Date", datetime.today() - timedelta(days=30))
            end_date = col2.date_input("End Date", datetime.today())
            
            # Quick date presets
            st.sidebar.markdown("### Quick Select")
            date_cols = st.sidebar.columns(3)
            if date_cols[0].button("Last 7 Days"):
                start_date = datetime.today() - timedelta(days=7)
                end_date = datetime.today()
                st.session_state.date_range = (start_date, end_date)
                st.rerun()
            if date_cols[1].button("Last 30 Days"):
                start_date = datetime.today() - timedelta(days=30)
                end_date = datetime.today()
                st.session_state.date_range = (start_date, end_date)
                st.rerun()
            if date_cols[2].button("This Month"):
                today = datetime.today()
                start_date = datetime(today.year, today.month, 1)
                end_date = today
                st.session_state.date_range = (start_date, end_date)
                st.rerun()
            
            fetch_button = st.sidebar.button("Fetch Data", use_container_width=True)
            
            # Fetch data when button is clicked
            if fetch_button:
                with st.spinner("Fetching campaign data..."):
                    df = fetch_campaign_data(client, customer_id, start_date, end_date)
                    if not df.empty:
                        st.session_state.df = df
                        st.session_state.data_loaded = True
                    else:
                        st.warning("No data found for selected period")
                        st.session_state.data_loaded = False

            if st.session_state.get('data_loaded'):
                df = st.session_state.df
                
                # Create tabs with modern styling
                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "📊 Overview", 
                    "🚀 Campaigns", 
                    "🔄 Conversions",
                    "⭐ Quality",
                    "🔍 Advanced"
                ])

                with tab1:
                    # Summary metrics in a more attractive grid layout with 3D style
                    st.markdown("### Campaign Performance")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-title">Total Spend</div>
                                <div class="metric-icon">💰</div>
                                <div class="metric-value">${df['Cost'].sum():,.2f}</div>
                                <div class="metric-change positive">↗ 8.2% vs last period</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-title">Conversions</div>
                                <div class="metric-icon">🎯</div>
                                <div class="metric-value">{df['Conversions'].sum():,.0f}</div>
                                <div class="metric-change positive">↗ 16% vs last period</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-title">Avg. CTR</div>
                                <div class="metric-icon">👆</div>
                                <div class="metric-value">{df['CTR (%)'].mean():.2f}%</div>
                                <div class="metric-change negative">↘ 2.1% vs last period</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col4:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-title">Avg. CPC</div>
                                <div class="metric-icon">💲</div>
                                <div class="metric-value">${df['Avg. CPC'].mean():.2f}</div>
                                <div class="metric-change positive">↗ 4.7% vs last period</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Additional summary metrics
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-title">Cost Per Conversion</div>
                                <div class="metric-value">${df['Cost'].sum() / max(df['Conversions'].sum(), 1):,.2f}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-title">Total Impressions</div>
                                <div class="metric-value">{df['Impressions'].sum():,.0f}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        st.markdown(f"""
                            <div class="metric-card">
                                <div class="metric-title">Total Clicks</div>
                                <div class="metric-value">{df['Clicks'].sum():,.0f}</div>
                            </div>
                        """, unsafe_allow_html=True)
                    
                    # Create modern charts
                    st.markdown("### Performance Trends")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown('<div class="chart-title">Spend & Conversion Trend</div>', unsafe_allow_html=True)
                        # Prepare data for the trend chart
                        trend_df = df.groupby('Date').agg({
                            'Cost': 'sum',
                            'Conversions': 'sum'
                        }).reset_index()
                        
                        # Create a more modern area chart
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=trend_df['Date'], 
                            y=trend_df['Cost'],
                            name='Cost',
                            line=dict(color='#4299e1', width=3),
                            mode='lines',
                            fill='tozeroy',
                            fillcolor='rgba(66, 153, 225, 0.2)'
                        ))
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(
                                showgrid=False,
                                title=None
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(0,0,0,0.05)',
                                title=None
                            ),
                            margin=dict(l=20, r=20, t=20, b=20),
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            ),
                            hovermode='x unified'
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown('<div class="chart-title">Campaign Performance</div>', unsafe_allow_html=True)
                        
                        # Create a modern donut chart
                        campaign_df = df.groupby('Campaign Name').agg({
                            'Cost': 'sum',
                            'Conversions': 'sum'
                        }).reset_index()
                        
                        fig = px.pie(
                            campaign_df, 
                            names='Campaign Name', 
                            values='Cost',
                            hole=0.6,
                            color_discrete_sequence=px.colors.qualitative.Set2
                        )
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=20, r=20, t=20, b=20),
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=-0.3,
                                xanchor="center",
                                x=0.5
                            )
                        )
                        
                        # Add a text label in the center
                        fig.add_annotation(
                            text=f"${campaign_df['Cost'].sum():,.2f}",
                            font=dict(size=22, color='#2d3748', family="Poppins"),
                            showarrow=False,
                            x=0.5,
                            y=0.5
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # KPI trends
                    st.markdown("### KPI Analysis")
                    col1, col2, col3 = st.columns([1,2,1])
                    
                    with col2:
                        # Create a combined metrics chart
                        metrics_df = df.groupby('Date').agg({
                            'CTR (%)': 'mean',
                            'Conversions': 'sum',
                            'Clicks': 'sum'
                        }).reset_index()
                        
                        fig = go.Figure()
                        
                        # Add bars for clicks
                        fig.add_trace(go.Bar(
                            x=metrics_df['Date'],
                            y=metrics_df['Clicks'],
                            name='Clicks',
                            marker_color='rgba(102, 126, 234, 0.6)'
                        ))
                        
                        # Add line for CTR
                        fig.add_trace(go.Scatter(
                            x=metrics_df['Date'],
                            y=metrics_df['CTR (%)'],
                            name='CTR (%)',
                            mode='lines+markers',
                            marker=dict(size=8, color='#f56565'),
                            line=dict(width=3, color='#f56565'),
                            yaxis='y2'
                        ))
                        
                        # Add line for Conversions
                        fig.add_trace(go.Scatter(
                            x=metrics_df['Date'],
                            y=metrics_df['Conversions'],
                            name='Conversions',
                            mode='lines+markers',
                            marker=dict(size=8, color='#48bb78'),
                            line=dict(width=3, color='#48bb78', dash='dot'),
                            yaxis='y3'
                        ))
                        
                        # Update layout for multiple y-axes
                        fig.update_layout(
                            title='Clicks, CTR & Conversions Over Time',
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(
                                showgrid=False,
                                title=None
                            ),
                            yaxis=dict(
                                title='Clicks',
                                showgrid=True,
                                gridcolor='rgba(0,0,0,0.05)',
                                side='left'
                            ),
                            yaxis2=dict(
                                title='CTR (%)',
                                overlaying='y',
                                side='right',
                                showgrid=False
                            ),
                            yaxis3=dict(
                                title='Conversions',
                                overlaying='y',
                                side='right',
                                position=0.85,
                                showgrid=False
                            ),
                            margin=dict(l=20, r=20, t=40, b=20),
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            ),
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)

                with tab2:
                    # Campaign Analysis Tab
                    st.markdown("### Campaign Performance Analysis")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="chart-title">Cost vs Conversions</div>', unsafe_allow_html=True)
                        campaign_metrics = df.groupby('Campaign Name').agg({
                            'Cost': 'sum',
                            'Conversions': 'sum',
                            'Clicks': 'sum',
                            'Impressions': 'sum'
                        }).reset_index()
                        
                        fig = px.bar(
                            campaign_metrics,
                            x='Campaign Name',
                            y=['Cost', 'Conversions'],
                            barmode='group',
                            color_discrete_sequence=['#4299e1', '#48bb78'],
                            template='plotly_white'
                        )
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(
                                showgrid=False,
                                title=None
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(0,0,0,0.05)',
                                title=None
                            ),
                            margin=dict(l=20, r=20, t=20, b=60),
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            )
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown('<div class="chart-title">CTR Distribution</div>', unsafe_allow_html=True)
                        
                        fig = px.box(
                            df,
                            x='Campaign Name',
                            y='CTR (%)',
                            color='Campaign Name',
                            color_discrete_sequence=px.colors.qualitative.Pastel,
                            points="all"
                        )
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(
                                showgrid=False,
                                title=None
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(0,0,0,0.05)',
                                title='CTR (%)'
                            ),
                            margin=dict(l=20, r=20, t=20, b=60),
                            showlegend=False
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Campaign comparison table with enhanced styling
                    st.markdown("### Campaign Metrics Comparison")
                    
                    campaign_summary = df.groupby('Campaign Name').agg({
                        'Cost': 'sum',
                        'Impressions': 'sum',
                        'Clicks': 'sum',
                        'Conversions': 'sum',
                        'CTR (%)': 'mean',
                        'Avg. CPC': 'mean',
                        'Status': 'first'
                    }).reset_index()
                    
                    # Calculate additional metrics
                    campaign_summary['Cost Per Conv.'] = campaign_summary['Cost'] / campaign_summary['Conversions'].replace(0, 1)
                    campaign_summary['Conv. Rate (%)'] = campaign_summary['Conversions'] / campaign_summary['Clicks'].replace(0, 1) * 100
                    
                    # Format the status column with colored pills
                    campaign_summary['Status'] = campaign_summary['Status'].apply(format_status)
                    
                    # Display the styled table
                    st.markdown(f"""
                    <div class="chart-container">
                        {campaign_summary.style.format({
                            'Cost': '${:,.2f}',
                            'CTR (%)': '{:.2f}%',
                            'Avg. CPC': '${:.2f}',
                            'Cost Per Conv.': '${:.2f}',
                            'Conv. Rate (%)': '{:.2f}%',
                            'Impressions': '{:,.0f}',
                            'Clicks': '{:,.0f}',
                            'Conversions': '{:,.1f}'
                        }).to_html()}
                    </div>
                    """, unsafe_allow_html=True)

                with tab3:
                    # Conversions Tab
                    st.markdown("### Conversion Analysis")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="chart-title">Conversion Funnel</div>', unsafe_allow_html=True)
                        
                        funnel_df = df.groupby('Campaign Name').agg({
                            'Impressions': 'sum',
                            'Clicks': 'sum',
                            'Conversions': 'sum'
                        }).reset_index()
                        
                        # Create modern funnel chart
                        fig = go.Figure()
                        
                        for _, row in funnel_df.iterrows():
                            fig.add_trace(go.Funnel(
                                name=row['Campaign Name'],
                                y=['Impressions', 'Clicks', 'Conversions'],
                                x=[row['Impressions'], row['Clicks'], row['Conversions']],
                                textposition="inside",
                                textinfo="value+percent initial",
                                opacity=0.8,
                                marker=dict(
                                    line=dict(width=1, color='rgba(0,0,0,0.2)')
                                ),
                                connector=dict(line=dict(width=1, color='rgba(0,0,0,0.2)'))
                            ))
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=20, r=20, t=20, b=20)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown('<div class="chart-title">Cost per Conversion</div>', unsafe_allow_html=True)
                        
                        # Enhanced scatter plot
                        fig = px.scatter(
                            df.groupby(['Campaign Name', 'Date']).agg({
                                'Cost': 'sum',
                                'Conversions': 'sum',
                                'Impressions': 'sum'
                            }).reset_index(),
                            x='Cost',
                            y='Conversions',
                            color='Campaign Name',
                            size='Impressions',
                            size_max=30,
                            hover_data=['Date'],
                            template='plotly_white'
                        )
                        
                        # Add diagonal lines representing cost per conversion benchmarks
                        max_cost = df['Cost'].sum() * 1.2
                        max_conv = df['Conversions'].sum() * 1.2
                        
                        # Add CPC reference lines
                        for cpc in [1, 5, 10, 20, 50]:
                            fig.add_shape(
                                type="line",
                                x0=0, y0=0,
                                x1=max_cost, y1=max_cost/cpc,
                                line=dict(
                                    color="rgba(0,0,0,0.2)",
                                    width=1,
                                    dash="dot",
                                ),
                            )
                            # Add label
                            fig.add_annotation(
                                x=max_cost*0.8,
                                y=(max_cost*0.8)/cpc,
                                text=f"${cpc} CPA",
                                showarrow=False,
                                font=dict(size=10, color="rgba(0,0,0,0.5)")
                            )
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(0,0,0,0.05)',
                                title='Cost ($)'
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(0,0,0,0.05)',
                                title='Conversions'
                            ),
                            margin=dict(l=20, r=20, t=20, b=20)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Conversion metrics breakdown
                    st.markdown("### Conversion Rate Analysis")
                    
                    col1, col2, col3 = st.columns([1,2,1])
                    with col2:
                        # Get conversion rates by day of week
                        df['Date'] = pd.to_datetime(df['Date'])
                        df['Day of Week'] = df['Date'].dt.day_name()
                        
                        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
                        
                        dow_df = df.groupby('Day of Week').agg({
                            'Clicks': 'sum',
                            'Conversions': 'sum',
                            'Cost': 'sum'
                        }).reset_index()
                        
                        dow_df['Conversion Rate'] = (dow_df['Conversions'] / dow_df['Clicks'] * 100).round(2)
                        dow_df['CPA'] = (dow_df['Cost'] / dow_df['Conversions']).round(2)
                        dow_df = dow_df.sort_values(by='Day of Week', key=lambda x: pd.Categorical(x, categories=day_order))
                        
                        fig = go.Figure()
                        
                        # Add bars for conversion rate
                        fig.add_trace(go.Bar(
                            x=dow_df['Day of Week'],
                            y=dow_df['Conversion Rate'],
                            name='Conversion Rate (%)',
                            marker_color='rgba(72, 187, 120, 0.7)',
                            hovertemplate='%{y:.2f}%<extra></extra>'
                        ))
                        
                        # Add line for CPA
                        fig.add_trace(go.Scatter(
                            x=dow_df['Day of Week'],
                            y=dow_df['CPA'],
                            name='CPA ($)',
                            mode='lines+markers',
                            marker=dict(size=10, color='#e53e3e'),
                            line=dict(width=3, color='#e53e3e'),
                            yaxis='y2',
                            hovertemplate='$%{y:.2f}<extra></extra>'
                        ))
                        
                        fig.update_layout(
                            title='Conversion Rate & CPA by Day of Week',
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(
                                showgrid=False,
                                title=None,
                                categoryorder='array',
                                categoryarray=day_order
                            ),
                            yaxis=dict(
                                title='Conversion Rate (%)',
                                showgrid=True,
                                gridcolor='rgba(0,0,0,0.05)',
                                side='left',
                                range=[0, max(dow_df['Conversion Rate']) * 1.2]
                            ),
                            yaxis2=dict(
                                title='CPA ($)',
                                overlaying='y',
                                side='right',
                                showgrid=False,
                                range=[0, max(dow_df['CPA']) * 1.2]
                            ),
                            margin=dict(l=20, r=60, t=40, b=20),
                            legend=dict(
                                orientation="h",
                                yanchor="bottom",
                                y=1.02,
                                xanchor="right",
                                x=1
                            ),
                            hovermode='x unified'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)

                with tab4:
                    # Quality Score Tab
                    st.markdown("### Quality & Impression Share Analysis")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="chart-title">Impression Share Distribution</div>', unsafe_allow_html=True)
                        
                        fig = px.histogram(
                            df,
                            x='Impression Share (%)',
                            nbins=20,
                            color_discrete_sequence=['#4CAF50'],
                            opacity=0.8,
                            marginal='box',
                            template='plotly_white'
                        )
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(0,0,0,0.05)',
                                title='Impression Share (%)'
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(0,0,0,0.05)',
                                title='Count'
                            ),
                            margin=dict(l=20, r=20, t=20, b=20),
                            bargap=0.1
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown('<div class="chart-title">Campaign Quality Overview</div>', unsafe_allow_html=True)
                        
                        # Enhanced scatter plot for quality metrics
                        campaign_quality = df.groupby('Campaign Name').agg({
                            'CTR (%)': 'mean',
                            'Impression Share (%)': 'mean',
                            'Conversions': 'sum'
                        }).reset_index()
                        
                        fig = px.scatter(
                            campaign_quality,
                            x='CTR (%)',
                            y='Impression Share (%)',
                            color='Campaign Name',
                            size='Conversions',
                            size_max=40,
                            hover_name='Campaign Name',
                            template='plotly_white'
                        )
                        
                        # Add quadrant lines
                        fig.add_shape(
                            type="line",
                            x0=campaign_quality['CTR (%)'].mean(),
                            y0=0,
                            x1=campaign_quality['CTR (%)'].mean(),
                            y1=100,
                            line=dict(
                                color="rgba(0,0,0,0.2)",
                                width=1,
                                dash="dash",
                            )
                        )
                        
                        fig.add_shape(
                            type="line",
                            x0=0,
                            y0=campaign_quality['Impression Share (%)'].mean(),
                            x1=campaign_quality['CTR (%)'].max() * 1.2,
                            y1=campaign_quality['Impression Share (%)'].mean(),
                            line=dict(
                                color="rgba(0,0,0,0.2)",
                                width=1,
                                dash="dash",
                            )
                        )
                        
                        # Add quadrant labels
                        avg_ctr = campaign_quality['CTR (%)'].mean()
                        avg_is = campaign_quality['Impression Share (%)'].mean()
                        max_ctr = campaign_quality['CTR (%)'].max() * 1.1
                        
                        fig.add_annotation(
                            x=avg_ctr/2, y=avg_is/2,
                            text="Low CTR<br>Low Imp. Share",
                            showarrow=False,
                            font=dict(size=10, color="rgba(0,0,0,0.5)")
                        )
                        
                        fig.add_annotation(
                            x=avg_ctr/2, y=avg_is + (100-avg_is)/2,
                            text="Low CTR<br>High Imp. Share",
                            showarrow=False,
                            font=dict(size=10, color="rgba(0,0,0,0.5)")
                        )
                        
                        fig.add_annotation(
                            x=avg_ctr + (max_ctr-avg_ctr)/2, y=avg_is/2,
                            text="High CTR<br>Low Imp. Share",
                            showarrow=False,
                            font=dict(size=10, color="rgba(0,0,0,0.5)")
                        )
                        
                        fig.add_annotation(
                            x=avg_ctr + (max_ctr-avg_ctr)/2, y=avg_is + (100-avg_is)/2,
                            text="High CTR<br>High Imp. Share",
                            showarrow=False,
                            font=dict(size=10, color="rgba(0,0,0,0.5)")
                        )
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(0,0,0,0.05)',
                                title='CTR (%)'
                            ),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor='rgba(0,0,0,0.05)',
                                title='Impression Share (%)'
                            ),
                            margin=dict(l=20, r=20, t=20, b=20)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Campaign quality score summary
                    st.markdown("### Campaign Optimization Opportunities")
                    
                    # Calculate performance scores
                    campaign_opp = df.groupby('Campaign Name').agg({
                        'CTR (%)': 'mean',
                        'Impression Share (%)': 'mean',
                        'Conversions': 'sum',
                        'Cost': 'sum',
                        'Clicks': 'sum'
                    }).reset_index()
                    
                    campaign_opp['Conv. Rate (%)'] = (campaign_opp['Conversions'] / campaign_opp['Clicks'] * 100).round(2)
                    campaign_opp['CPA'] = (campaign_opp['Cost'] / campaign_opp['Conversions']).round(2)
                    
                    # Create radar chart for campaign quality visualization
                    fig = go.Figure()
                    
                    # Normalize metrics for radar chart
                    norm_cols = ['CTR (%)', 'Impression Share (%)', 'Conv. Rate (%)']
                    max_vals = campaign_opp[norm_cols].max()
                    
                    for _, row in campaign_opp.iterrows():
                        normalized = [row[col]/max_vals[col]*100 for col in norm_cols]
                        
                        fig.add_trace(go.Scatterpolar(
                            r=normalized + [normalized[0]],  # Close the polygon
                            theta=norm_cols + [norm_cols[0]],  # Close the polygon
                            fill='toself',
                            name=row['Campaign Name'],
                            opacity=0.7
                        ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 100]
                            ),
                            angularaxis=dict(
                                showticklabels=True,
                                ticks=""
                            )
                        ),
                        showlegend=True,
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        margin=dict(l=80, r=80, t=20, b=20),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=-0.2,
                            xanchor="center",
                            x=0.5
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)

                with tab5:
                    # Advanced Analytics Tab
                    st.markdown("### Advanced Performance Analysis")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown('<div class="chart-title">Impression Share Treemap</div>', unsafe_allow_html=True)
                        
                        fig = px.treemap(
                            df,
                            path=['Campaign Name'],
                            values='Impressions',
                            color='Impression Share (%)',
                            color_continuous_scale='Blues',
                            hover_data=['Clicks', 'CTR (%)', 'Cost']
                        )
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=20, r=20, t=20, b=20)
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown('<div class="chart-title">Performance Heatmap</div>', unsafe_allow_html=True)
                        
                        # Create a more detailed heatmap with proper date formatting
                        # Convert date to datetime if it's not already
                        if not pd.api.types.is_datetime64_any_dtype(df['Date']):
                            df['Date'] = pd.to_datetime(df['Date'])
                        
                        # Format date for better display
                        df['Date_Formatted'] = df['Date'].dt.strftime('%b %d')
                        
                        # Create pivot table
                        heatmap_df = df.pivot_table(
                            index='Campaign Name',
                            columns='Date_Formatted',
                            values='Conversions',
                            aggfunc='sum'
                        )
                        
                        # Sort columns by date
                        date_order = pd.to_datetime(df['Date']).sort_values().dt.strftime('%b %d').unique()
                        heatmap_df = heatmap_df.reindex(columns=date_order)
                        
                        fig = px.imshow(
                            heatmap_df,
                            color_continuous_scale='Viridis',
                            aspect="auto",
                            text_auto='.1f'
                        )
                        
                        fig.update_layout(
                            plot_bgcolor='rgba(0,0,0,0)',
                            paper_bgcolor='rgba(0,0,0,0)',
                            xaxis=dict(
                                title=None,
                                side='top'
                            ),
                            yaxis=dict(
                                title=None
                            ),
                            margin=dict(l=20, r=20, t=40, b=20),
                            coloraxis_colorbar=dict(
                                title='Conversions'
                            )
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Raw data explorer with modern styling
                    st.markdown("### Raw Data Explorer")
                    with st.expander("View Full Dataset"):
                        # Create a search filter
                        search_term = st.text_input("Search campaigns", "")
                        
                        # Filter data if search term is provided
                        filtered_df = df
                        if search_term:
                            filtered_df = df[df['Campaign Name'].str.contains(search_term, case=False)]
                        
                        # Display the filtered dataframe
                        st.dataframe(filtered_df, use_container_width=True)
                        
                        # Add export functionality
                        if st.button("Export Data as CSV"):
                            csv = filtered_df.to_csv(index=False)
                            st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name="google_ads_data.csv",
                                mime="text/csv"
                            )
            else:
                # Empty state display when no data is loaded
                st.markdown("""
                <div class="empty-state">
                    <div class="empty-state-icon">📊</div>
                    <h3>No Data Loaded</h3>
                    <p class="empty-state-text">Select an account and date range, then click "Fetch Data" to load your Google Ads performance data.</p>
                </div>
                """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
