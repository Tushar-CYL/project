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
import secrets
import hashlib
import json
import jwt

# Page Configuration
st.set_page_config(
    page_title="AdSync Dashboard",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded"
)

# Modern 3D-style CSS
st.markdown("""
<style>
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' https://accounts.google.com;">
    
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

# Load configuration from YAML
@st.cache_resource
def load_yaml_config():
    try:
        with open("google-ads.yaml") as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        st.error("Configuration file not found. Please ensure google-ads.yaml exists.")
        st.stop()

yaml_config = load_yaml_config()

# OAuth Configuration
CLIENT_CONFIG = {
    "web": {
        "client_id": yaml_config['client_id'],
        "client_secret": yaml_config['client_secret'],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://accounts.google.com/o/oauth2/token"
    }
}
REDIRECT_URI = "https://your-deployment-url.com"  # Update this
SCOPES = [
    "https://www.googleapis.com/auth/adwords",
    "openid",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/userinfo.email"
]

def get_google_ads_client(credentials):
    config = {
        "developer_token": yaml_config['developer_token'],
        "client_id": yaml_config['client_id'],
        "client_secret": yaml_config['client_secret'],
        "refresh_token": credentials['refresh_token'],
        "use_proto_plus": yaml_config['use_proto_plus']
    }
    return GoogleAdsClient.load_from_dict(config)

def handle_oauth():
    query_params = st.query_params.to_dict()
    
    if 'code' in query_params and 'state' in query_params:
        try:
            state_json = base64.urlsafe_b64decode(query_params['state'].encode('utf-8')).decode('utf-8')
            state_data = json.loads(state_json)
            code_verifier = state_data.get('code_verifier')
            
            flow = Flow.from_client_config(
                client_config=CLIENT_CONFIG,
                scopes=SCOPES,
                redirect_uri=REDIRECT_URI
            )
            
            flow.fetch_token(
                code=query_params['code'],
                code_verifier=code_verifier
            )
            
            credentials = flow.credentials
            id_info = jwt.decode(credentials.id_token, options={"verify_signature": False})
            
            # Store user-specific session data
            st.session_state['user'] = {
                'credentials': {
                    "token": credentials.token,
                    "refresh_token": credentials.refresh_token,
                    "id_token": credentials.id_token
                },
                'user_info': id_info,
                'authenticated': True
            }
            
            st.query_params.clear()
            st.rerun()
            
        except Exception as e:
            st.error(f"Authentication error: {str(e)}")
            return None

    if 'user' not in st.session_state or not st.session_state.user.get('authenticated'):
        code_verifier = secrets.token_urlsafe(96)[:128]
        code_challenge = base64.urlsafe_b64encode(
            hashlib.sha256(code_verifier.encode('utf-8')).digest()
        ).decode('utf-8').rstrip('=')
        
        state_data = {'code_verifier': code_verifier}
        state_json = json.dumps(state_data)
        state_param = base64.urlsafe_b64encode(state_json.encode('utf-8')).decode('utf-8')
        
        flow = Flow.from_client_config(
            client_config=CLIENT_CONFIG,
            scopes=SCOPES,
            redirect_uri=REDIRECT_URI
        )
        
        auth_url, _ = flow.authorization_url(
            prompt="consent",
            access_type="offline",
            code_challenge=code_challenge,
            code_challenge_method="S256",
            state=state_param,
            login_hint=st.session_state.get('user', {}).get('user_info', {}).get('email', '')
        )
        
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

    return st.session_state.user['credentials']

def get_accessible_customers(client):
    try:
        customer_service = client.get_service("CustomerService")
        response = customer_service.list_accessible_customers()
        return [cid.split('/')[1] for cid in response.resource_names]
    except GoogleAdsException as ex:
        st.error(f"Google Ads API error: {ex.error.code().name}")
        st.error(ex.error.message)
        return []

@st.cache_data(ttl=300)
def fetch_campaign_data(_client, customer_id, start_date, end_date):
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

def main():
    credentials = handle_oauth()
    
    if credentials and 'user' in st.session_state:
        client = get_google_ads_client(credentials)
        user_id = st.session_state.user['user_info']['sub']
        
        # User-specific session management
        user_key = f"user_{user_id}"
        
        if f"{user_key}_customers" not in st.session_state:
            with st.spinner("Loading accounts..."):
                customers = get_accessible_customers(client)
                if customers:
                    st.session_state[f"{user_key}_customers"] = customers
                else:
                    st.error("No accessible Google Ads accounts found")

        if f"{user_key}_customers" in st.session_state:
            # Sidebar controls
            st.sidebar.markdown(f"### Welcome, {st.session_state.user['user_info'].get('name', 'User')}")
            
            if st.sidebar.button("Logout"):
                for key in list(st.session_state.keys()):
                    if key.startswith(user_key) or key == 'user':
                        del st.session_state[key]
                st.rerun()
            
            customer_id = st.sidebar.selectbox(
                "Select Account", 
                st.session_state[f"{user_key}_customers"]
            )
            
            # Date selection
            st.sidebar.markdown("### Date Range")
            col1, col2 = st.sidebar.columns(2)
            start_date = col1.date_input("Start Date", datetime.today() - timedelta(days=30))
            end_date = col2.date_input("End Date", datetime.today())
            
            if st.sidebar.button("Fetch Data"):
                with st.spinner("Loading campaign data..."):
                    df = fetch_campaign_data(client, customer_id, start_date, end_date)
                    if not df.empty:
                        st.session_state[f"{user_key}_data"] = df
                        st.session_state[f"{user_key}_data_loaded"] = True
                    else:
                        st.warning("No data found for selected period")
                        st.session_state[f"{user_key}_data_loaded"] = False
            
            if st.session_state.get(f"{user_key}_data_loaded"):
                df = st.session_state[f"{user_key}_data"]
                
                # Display metrics
                st.markdown("### Campaign Performance")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Total Spend", f"${df['Cost'].sum():,.2f}")
                col2.metric("Conversions", f"{df['Conversions'].sum():,.0f}")
                col3.metric("Avg. CTR", f"{df['CTR (%)'].mean():.2f}%")
                col4.metric("Avg. CPC", f"${df['Avg. CPC'].mean():.2f}")
                
                # Display data
                st.dataframe(df)
                
            else:
                st.info("Select an account and date range, then click 'Fetch Data'")

if __name__ == "__main__":
    main()
