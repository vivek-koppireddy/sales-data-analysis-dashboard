import os
import time
import random
import datetime
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import hashlib
import io
import database as db

# ---------------------------------------------------------
# Page Setup & Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Vortex Sales Analytics Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize SQLite database schema
db.init_db()

# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "auth_mode" not in st.session_state:
    st.session_state.auth_mode = "login"
if "active_data" not in st.session_state:
    st.session_state.active_data = None
if "data_source" not in st.session_state:
    st.session_state.data_source = None
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False
if "simulation_speed" not in st.session_state:
    st.session_state.simulation_speed = 1.0
if "simulated_orders" not in st.session_state:
    st.session_state.simulated_orders = []
if "live_session_revenue" not in st.session_state:
    st.session_state.live_session_revenue = 0.0
if "live_session_orders" not in st.session_state:
    st.session_state.live_session_orders = 0
if "notifications" not in st.session_state:
    st.session_state.notifications = [
        "🔔 System ready. Welcome to Vortex Sales Hub.",
        "💡 Tip: Filter by Region or Category using the sidebar."
    ]
if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

# ---------------------------------------------------------
# Custom Theme & Styling Injection
# ---------------------------------------------------------
def inject_custom_styling(theme="Dark"):
    if theme == "Dark":
        bg_css = """
        html, body {
            background: #050508 !important;
            color: #e2e8f0 !important;
        }
        [data-testid="stAppViewContainer"] {
            background: linear-gradient(125deg, #050508 0%, #0a0618 30%, #08111f 60%, #050508 100%) !important;
            min-height: 100vh;
            position: relative;
            overflow: hidden;
        }
        [data-testid="stAppViewContainer"]::before {
            content: '';
            position: fixed;
            top: -40%;
            left: -20%;
            width: 70vw;
            height: 70vw;
            background: radial-gradient(ellipse at center, rgba(99,102,241,0.12) 0%, transparent 65%);
            pointer-events: none;
            z-index: 0;
            animation: floatOrb1 18s ease-in-out infinite alternate;
        }
        [data-testid="stAppViewContainer"]::after {
            content: '';
            position: fixed;
            bottom: -30%;
            right: -15%;
            width: 60vw;
            height: 60vw;
            background: radial-gradient(ellipse at center, rgba(6,182,212,0.08) 0%, transparent 65%);
            pointer-events: none;
            z-index: 0;
            animation: floatOrb2 22s ease-in-out infinite alternate;
        }
        @keyframes floatOrb1 {
            0%   { transform: translate(0px,0px) scale(1); }
            100% { transform: translate(60px, 40px) scale(1.15); }
        }
        @keyframes floatOrb2 {
            0%   { transform: translate(0px,0px) scale(1); }
            100% { transform: translate(-50px,-30px) scale(1.2); }
        }
        div[data-testid="stForm"] {
            background: linear-gradient(145deg, rgba(255,255,255,0.055) 0%, rgba(255,255,255,0.025) 100%) !important;
            backdrop-filter: blur(40px) saturate(180%) !important;
            -webkit-backdrop-filter: blur(40px) saturate(180%) !important;
            border: 1px solid rgba(255,255,255,0.12) !important;
            box-shadow: 0 30px 80px rgba(0,0,0,0.6) !important;
        }
        div[data-testid="stMetric"] {
            background: linear-gradient(145deg, rgba(99,102,241,0.08) 0%, rgba(6,182,212,0.04) 100%) !important;
            border: 1px solid rgba(99,102,241,0.2) !important;
            box-shadow: 0 4px 24px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.06) !important;
        }
        div[data-testid="stMetricValue"] > div {
            background: linear-gradient(135deg, #a5b4fc, #67e8f9) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
        }
        div[data-testid="stMetricLabel"] > div {
            color: #94a3b8 !important;
        }
        .feed-item {
            color: #38bdf8 !important;
            border-bottom: 1px solid rgba(255,255,255,0.04) !important;
        }
        .live-feed-container {
            background: linear-gradient(180deg, rgba(5,5,20,0.8) 0%, rgba(10,10,30,0.8) 100%) !important;
            border: 1px solid rgba(56,189,248,0.15) !important;
        }
        """
    else:
        bg_css = """
        html, body {
            background: #f8fafc !important;
            color: #1e293b !important;
        }
        [data-testid="stAppViewContainer"] {
            background: #f1f5f9 !important;
            min-height: 100vh;
        }
        div[data-testid="stForm"] {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 10px 30px rgba(0,0,0,0.05) !important;
        }
        div[data-testid="stMetric"] {
            background: #ffffff !important;
            border: 1px solid #e2e8f0 !important;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05) !important;
        }
        div[data-testid="stMetricValue"] > div {
            background: linear-gradient(135deg, #4f46e5, #0ea5e9) !important;
            -webkit-background-clip: text !important;
            -webkit-text-fill-color: transparent !important;
            background-clip: text !important;
            color: #4f46e5 !important;
        }
        div[data-testid="stMetricLabel"] > div {
            color: #64748b !important;
        }
        .feed-item {
            color: #0f172a !important;
            border-bottom: 1px solid #e2e8f0 !important;
        }
        .live-feed-container {
            background: #ffffff !important;
            border: 1px solid #cbd5e1 !important;
        }
        """
        
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Space+Grotesk:wght@400;500;600;700&display=swap');
    
    html, body {{
        font-family: 'Inter', sans-serif !important;
        margin: 0; padding: 0;
    }}
    {bg_css}
    
    /* Common styling elements */
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="manage-app-button"],
    .stDeployButton,
    [data-testid="stAppDeployButton"],
    [data-testid="stMainMenuButton"],
    [data-testid="stMainMenu"],
    #MainMenu,
    [class*="viewerBadge"],
    footer {{
        visibility: hidden !important;
        display: none !important;
    }}
    
    /* Make stToolbar container visible layout-wise but invisible content-wise */
    [data-testid="stToolbar"] {{
        visibility: hidden !important;
        display: flex !important;
        background: transparent !important;
    }}
    
    /* Ensure the sidebar toggle button is always visible and has a high z-index */
    [data-testid="stSidebarCollapseButton"],
    [data-testid="stExpandSidebarButton"],
    [data-testid="collapsedControl"],
    button[aria-label="Open sidebar"],
    button[aria-label="Close sidebar"] {{
        visibility: visible !important;
        display: inline-flex !important;
        z-index: 999999 !important;
        opacity: 1 !important;
        transform: none !important;
        pointer-events: auto !important;
    }}
    
    /* Force sidebar container to viewport height and allow internal scrolling */
    [data-testid="stSidebar"] {{
        height: 100vh !important;
    }}
    [data-testid="stSidebar"] > div:first-child {{
        max-height: 100vh !important;
        overflow-y: auto !important;
    }}
    
    [data-testid="stHeader"] {{
        background: transparent !important;
    }}
    [data-testid="stAppViewBlockContainer"] {{
        padding-top: 1.5rem !important;
    }}
    
    /* Metrics panel card overrides */
    div[data-testid="stMetric"] {{
        border-radius: 16px !important;
        padding: 20px 16px !important;
        transition: all 0.3s ease !important;
    }}
    div[data-testid="stMetric"]:hover {{
        transform: translateY(-4px) !important;
    }}
    
    /* Radio toggle bar overrides */
    div[data-testid="stRadio"] > div[role="radiogroup"] {{
        flex-direction: row !important;
        background: rgba(99, 102, 241, 0.05) !important;
        padding: 6px !important;
        border-radius: 12px !important;
        border: 1px solid rgba(99, 102, 241, 0.15) !important;
        gap: 6px !important;
        justify-content: center !important;
    }}
    div[data-testid="stRadio"] > div[role="radiogroup"] label {{
        background: transparent !important;
        border: none !important;
        padding: 8px 16px !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        cursor: pointer !important;
        transition: all 0.2s ease !important;
    }}
    div[data-testid="stRadio"] > div[role="radiogroup"] label:hover {{
        background: rgba(99, 102, 241, 0.1) !important;
    }}
    div[data-testid="stRadio"] > div[role="radiogroup"] label[data-checked="true"] {{
        background: linear-gradient(135deg, #4f46e5 0%, #6366f1 100%) !important;
        color: #ffffff !important;
        box-shadow: 0 4px 12px rgba(79, 70, 229, 0.3) !important;
    }}
    div[data-testid="stRadio"] > div[role="radiogroup"] > label > div:first-child {{
        display: none !important;
    }}
    
    /* Live Indicator */
    .indicator-box {{
        display: flex;
        align-items: center;
        background: rgba(34,197,94,0.08);
        border: 1px solid rgba(34,197,94,0.25);
        padding: 10px 16px;
        border-radius: 10px;
        margin-bottom: 12px;
    }}
    .indicator-dot {{
        height: 10px; width: 10px;
        background: #22c55e;
        border-radius: 50%;
        margin-right: 10px;
        box-shadow: 0 0 8px #22c55e;
        animation: pulseLive 1.8s ease-in-out infinite;
    }}
    @keyframes pulseLive {{
        0%, 100% {{ opacity: 1; transform: scale(1); }}
        50%       {{ opacity: 0.7; transform: scale(1.15); }}
    }}
    
    /* Live feed ticker */
    .live-feed-container {{
        border-radius: 12px;
        padding: 12px;
        max-height: 240px;
        overflow-y: auto;
        font-family: monospace;
        font-size: 12px;
    }}
    .feed-item {{
        padding: 5px 0;
        line-height: 1.4;
    }}
    .feed-item:last-child {{ border-bottom: none !important; }}
    
    /* Printing optimization */
    @media print {{
        [data-testid="stSidebar"], .stButton, header, footer, button, .global_csv_uploader {{
            display: none !important;
        }}
        [data-testid="stAppViewBlockContainer"] {{
            width: 100% !important;
            padding: 0 !important;
        }}
    }}
    </style>
    """, unsafe_allow_html=True)

# ---------------------------------------------------------
# Dynamic Data Enrichment & Formatting Engine
# ---------------------------------------------------------
def enrich_and_prepare_data(df):
    """Enriches the dataframe with all missing business columns for the premium BI dashboard."""
    expected_columns = [
        "Order_ID", "Order_Date", "Year", "Month", "Product",
        "Category", "Region", "Sales", "Quantity", "Order_Type"
    ]
    
    # Handle single column import anomalies
    if len(df.columns) == 1:
        combined = df.columns[0]
        if combined.replace(" ", "") == "Order_IDOrder_DateYearMonthProductCategoryRegionSalesQuantityOrder_Type":
            df.columns = expected_columns
            
    for col in expected_columns:
        if col not in df.columns:
            df[col] = np.nan

    # Parse and cleanse types
    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
    
    # Impute dates if missing
    df.loc[df["Order_Date"].isna(), "Order_Date"] = pd.to_datetime("2024-01-01")
    df.loc[df["Year"].isna() & df["Order_Date"].notna(), "Year"] = df["Order_Date"].dt.year
    df.loc[df["Month"].isna() & df["Order_Date"].notna(), "Month"] = df["Order_Date"].dt.month
    
    df["Order_ID"] = df["Order_ID"].astype(str).str.strip()
    df["Order_Type"] = df["Order_Type"].fillna("Online")
    
    df = df.dropna(subset=["Order_ID", "Sales", "Quantity"])
    df = df.drop_duplicates()
    
    # Deterministic generation helper based on order attributes
    def get_hash_num(val, max_val):
        return int(hashlib.md5(str(val).encode('utf-8')).hexdigest(), 16) % max_val

    # Imputed Business Entities
    customers = [
        "Apex Corp", "Summit Industries", "Global Tech", "Apex Solutions", "Quantum Systems",
        "Helix Health", "Vortex Media", "Starlight Co", "Beacon Logistics", "Omega Trading",
        "Alpha Partners", "Delta Corp", "Genesis Holdings", "Eclipse Enterprises", "Nova Retail"
    ]
    customer_segments = ["Enterprise", "Mid-Market", "SMB", "Public Sector"]
    
    region_reps = {
        "North": ["Elena Fisher", "David Miller"],
        "South": ["Sarah Connor", "John Smith"],
        "East": ["Alex Mercer", "Maya Lin"],
        "West": ["Jane Doe", "Marcus Vance"]
    }
    all_reps = ["Elena Fisher", "David Miller", "Sarah Connor", "John Smith", "Alex Mercer", "Maya Lin", "Jane Doe", "Marcus Vance"]
    payments = ["Credit Card", "Bank Transfer", "PayPal", "Cash"]
    
    geo_map = {
        "North": {"Country": "India", "State": "Delhi", "City": "New Delhi", "Lat": 28.6139, "Lon": 77.2090},
        "South": {"Country": "India", "State": "Karnataka", "City": "Bengaluru", "Lat": 12.9716, "Lon": 77.5946},
        "East": {"Country": "India", "State": "West Bengal", "City": "Kolkata", "Lat": 22.5726, "Lon": 88.3639},
        "West": {"Country": "India", "State": "Maharashtra", "City": "Mumbai", "Lat": 19.0760, "Lon": 72.8777}
    }
    
    category_margins = {
        "Electronics": 0.35,
        "Accessories": 0.50,
        "Office": 0.40,
        "Office Furniture": 0.45,
        "Furniture": 0.30
    }
    
    # Imputation collections
    cust_list, cust_id_list, segment_list = [], [], []
    rep_list, pay_list = [], []
    country_list, state_list, city_list, lat_list, lon_list = [], [], [], [], []
    cost_list, discount_list, tax_list, refunded_list = [], [], [], []
    shipping_status_list, shipping_days_list, target_list = [], [], []
    
    for idx, row in df.iterrows():
        order_id = row["Order_ID"]
        region = row["Region"] if pd.notna(row["Region"]) and row["Region"] in ["North", "South", "East", "West"] else "North"
        category = row["Category"] if pd.notna(row["Category"]) else "Other"
        sales = row["Sales"]
        qty = row["Quantity"]
        
        # Customers
        c_idx = get_hash_num(order_id, len(customers))
        cust_name = row["Customer"] if "Customer" in df.columns and pd.notna(row["Customer"]) else customers[c_idx]
        cust_list.append(cust_name)
        cust_id = row["Customer_ID"] if "Customer_ID" in df.columns and pd.notna(row["Customer_ID"]) else f"CUST-{1000 + c_idx}"
        cust_id_list.append(cust_id)
        seg_idx = get_hash_num(cust_name, len(customer_segments))
        segment_list.append(row["Customer_Segment"] if "Customer_Segment" in df.columns and pd.notna(row["Customer_Segment"]) else customer_segments[seg_idx])
        
        # Representatives
        reps = region_reps.get(region, all_reps)
        rep_idx = get_hash_num(order_id, len(reps))
        rep_name = row["Sales_Rep"] if "Sales_Rep" in df.columns and pd.notna(row["Sales_Rep"]) else reps[rep_idx]
        rep_list.append(rep_name)
        
        # Payment Methods
        pay_idx = get_hash_num(order_id + "pay", len(payments))
        pay_list.append(row["Payment_Method"] if "Payment_Method" in df.columns and pd.notna(row["Payment_Method"]) else payments[pay_idx])
        
        # Geography
        g_info = geo_map.get(region, geo_map["North"])
        country_list.append(row["Country"] if "Country" in df.columns and pd.notna(row["Country"]) else g_info["Country"])
        state_list.append(row["State"] if "State" in df.columns and pd.notna(row["State"]) else g_info["State"])
        city_list.append(row["City"] if "City" in df.columns and pd.notna(row["City"]) else g_info["City"])
        lat_list.append(row["Latitude"] if "Latitude" in df.columns and pd.notna(row["Latitude"]) else g_info["Lat"])
        lon_list.append(row["Longitude"] if "Longitude" in df.columns and pd.notna(row["Longitude"]) else g_info["Lon"])
        
        # Margin & Costs
        margin = category_margins.get(category, 0.40)
        margin_var = (get_hash_num(order_id + "margin", 10) - 5) / 100.0
        final_margin = max(0.30, min(0.50, margin + margin_var))
        cost_val = row["Cost"] if "Cost" in df.columns and pd.notna(row["Cost"]) else sales * (1.0 - final_margin)
        cost_list.append(cost_val)
        
        # Discounts & Taxes
        disc_pct = get_hash_num(order_id + "disc", 16) / 100.0
        discount_list.append(row["Discount"] if "Discount" in df.columns and pd.notna(row["Discount"]) else sales * disc_pct)
        tax_list.append(row["Tax"] if "Tax" in df.columns and pd.notna(row["Tax"]) else sales * 0.18)
        
        # Refunds (approx 5% return rate)
        refund_status = (get_hash_num(order_id + "refund", 100) < 5)
        refunded_list.append(row["Refunded"] if "Refunded" in df.columns and pd.notna(row["Refunded"]) else refund_status)
        
        # Shipping Status & duration
        if refund_status:
            ship_status = "Returned"
        else:
            ship_idx = get_hash_num(order_id + "ship", 10)
            ship_status = "Delivered" if ship_idx < 7 else ("Shipped" if ship_idx < 9 else "Processing")
            
        shipping_status_list.append(row["Shipping_Status"] if "Shipping_Status" in df.columns and pd.notna(row["Shipping_Status"]) else ship_status)
        ship_days = get_hash_num(order_id + "days", 7) + 1
        shipping_days_list.append(row["Shipping_Time_Days"] if "Shipping_Time_Days" in df.columns and pd.notna(row["Shipping_Time_Days"]) else ship_days)
        target_list.append(sales * 1.25)
        
    df["Customer"] = cust_list
    df["Customer_ID"] = cust_id_list
    df["Customer_Segment"] = segment_list
    df["Sales_Rep"] = rep_list
    df["Payment_Method"] = pay_list
    df["Country"] = country_list
    df["State"] = state_list
    df["City"] = city_list
    df["Latitude"] = lat_list
    df["Longitude"] = lon_list
    df["Cost"] = cost_list
    df["Discount"] = discount_list
    df["Tax"] = tax_list
    df["Refunded"] = refunded_list
    df["Shipping_Status"] = shipping_status_list
    df["Shipping_Time_Days"] = shipping_days_list
    df["Target"] = target_list
    
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Day"] = df["Order_Date"].dt.day
    df["Week"] = df["Order_Date"].dt.isocalendar().week
    
    return df

# ---------------------------------------------------------
# Dataset Loader
# ---------------------------------------------------------
def load_default_dataset():
    """Reads the local CSV sample. Fails over to synthetic generator if file missing."""
    sample_path = os.path.join(os.path.dirname(__file__), "sample_sales_data.csv")
    if os.path.exists(sample_path):
        try:
            df = pd.read_csv(sample_path)
            return df, "Local CSV File (sample_sales_data.csv)"
        except Exception:
            pass

    # High fidelity synthetic fallback generator
    np.random.seed(1337)
    categories = {
        "Electronics": [
            ("MacBook Pro 16", 189999.0), ("iPhone 15 Pro", 119999.0), 
            ("Noise Cancelling Headphones", 24999.0), ("Webcam Streamer HD", 8999.0), 
            ("Smart Watch Active", 19999.0), ("Curved Gaming Monitor 32", 44999.0)
        ],
        "Accessories": [
            ("Wireless Ergonomic Mouse", 3499.0), ("Mechanical Keyboard RGB", 9999.0),
            ("USB-C Travel Hub", 5499.0), ("Aluminum Desk Stand", 2999.0),
            ("Portable SSD 2TB", 14999.0), ("Fast GaN Charger 100W", 3999.0)
        ],
        "Office Furniture": [
            ("Ergonomic Mesh Chair", 21999.0), ("Motorized Standing Desk", 34999.0),
            ("Dual Arm Monitor Mount", 6999.0), ("LED Smart Lamp Pro", 4499.0)
        ]
    }
    regions = ["North", "South", "East", "West"]
    order_types = ["Online", "Offline"]
    
    rows = []
    start_date = pd.to_datetime("2024-01-01")
    for i in range(150):
        order_id = str(1001 + i)
        days_offset = np.random.randint(0, 500)
        order_date = start_date + pd.Timedelta(days=days_offset)
        category = random.choice(list(categories.keys()))
        prod_info = random.choice(categories[category])
        product_name = prod_info[0]
        price = float(prod_info[1])
        region = random.choice(regions)
        qty = random.randint(1, 4)
        sales = price * qty
        order_type = random.choice(order_types)
        
        rows.append({
            "Order_ID": order_id,
            "Order_Date": order_date,
            "Year": order_date.year,
            "Month": order_date.month,
            "Product": product_name,
            "Category": category,
            "Region": region,
            "Sales": sales,
            "Quantity": qty,
            "Order_Type": order_type
        })
        
    df = pd.DataFrame(rows)
    return df, "Synthetic Corporate Dataset"

# Load initial data if none exists
if st.session_state.active_data is None:
    df, src = load_default_dataset()
    st.session_state.active_data = enrich_and_prepare_data(df)
    st.session_state.data_source = src

# ---------------------------------------------------------
# Dynamic Ticker Generator for Simulations
# ---------------------------------------------------------
def generate_single_order(current_df):
    categories = {
        "Electronics": [
            ("MacBook Pro 16", 189999.0), ("iPhone 15 Pro", 119999.0), 
            ("Noise Cancelling Headphones", 24999.0), ("Webcam Streamer HD", 8999.0), 
            ("Smart Watch Active", 19999.0), ("Curved Gaming Monitor 32", 44999.0)
        ],
        "Accessories": [
            ("Wireless Ergonomic Mouse", 3499.0), ("Mechanical Keyboard RGB", 9999.0),
            ("USB-C Travel Hub", 5499.0), ("Aluminum Desk Stand", 2999.0),
            ("Portable SSD 2TB", 14999.0), ("Fast GaN Charger 100W", 3999.0)
        ],
        "Office Furniture": [
            ("Ergonomic Mesh Chair", 21999.0), ("Motorized Standing Desk", 34999.0),
            ("Dual Arm Monitor Mount", 6999.0), ("LED Smart Lamp Pro", 4499.0)
        ]
    }
    regions = ["North", "South", "East", "West"]
    order_types = ["Online", "Offline"]
    
    if not current_df.empty:
        try:
            last_id = int(current_df["Order_ID"].astype(float).max())
            next_id = str(last_id + 1)
        except Exception:
            next_id = str(np.random.randint(5000, 9999))
        
        last_date = pd.to_datetime(current_df["Order_Date"]).max()
        if pd.isna(last_date):
            last_date = pd.to_datetime("2025-06-01")
        next_date = last_date + pd.Timedelta(hours=np.random.randint(1, 12))
    else:
        next_id = "1001"
        next_date = pd.to_datetime("2025-01-01")
        
    category = random.choice(list(categories.keys()))
    prod_info = random.choice(categories[category])
    product_name = prod_info[0]
    price = float(prod_info[1])
    region = random.choice(regions)
    qty = random.randint(1, 3)
    sales = price * qty
    order_type = random.choice(order_types)
    
    new_row = {
        "Order_ID": next_id,
        "Order_Date": next_date,
        "Year": next_date.year,
        "Month": next_date.month,
        "Product": product_name,
        "Category": category,
        "Region": region,
        "Sales": sales,
        "Quantity": qty,
        "Order_Type": order_type
    }
    return pd.DataFrame([new_row])

# ---------------------------------------------------------
# Login/Signup Render Page
# ---------------------------------------------------------
def render_auth_page():
    st.markdown("<div style='height:30px'></div>", unsafe_allow_html=True)
    _, col_center, _ = st.columns([1, 1.4, 1])
    with col_center:
        if st.session_state.auth_mode == "login":
            with st.form("login_form", clear_on_submit=False):
                st.markdown("""
                <div class="auth-logo-ring">⚡</div>
                <div class="auth-brand-title" style="text-align:center; font-family:'Space Grotesk',sans-serif; font-size:26px; font-weight:700; background:linear-gradient(135deg, #c7d2fe, #67e8f9); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">VORTEX SALES HUB</div>
                <div class="auth-brand-subtitle" style="text-align:center; font-size:13px; color:#94a3b8; margin-bottom:20px;">Intelligence-driven enterprise analytics</div>
                """, unsafe_allow_html=True)
                username = st.text_input("USERNAME", placeholder="your.name", label_visibility="visible")
                password = st.text_input("PASSWORD", type="password", placeholder="••••••••", label_visibility="visible")
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                submit = st.form_submit_button("🔐 Sign In to Workspace", use_container_width=True)

                if submit:
                    username = (username or "").strip()
                    if not username or not password:
                        st.error("⚠️ Username and password are required.")
                    elif db.authenticate_user(username, password):
                        st.session_state.authenticated = True
                        st.session_state.username = username
                        st.toast(f"👋 Welcome back, {username}!")
                        st.success(f"Welcome back, {username}! Loading dashboard...")
                        time.sleep(0.7)
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please try again.")

            st.markdown("""
            <div class="auth-divider" style="display:flex; align-items:center; gap:12px; margin:20px 0;">
                <div class="auth-divider-line" style="flex:1; height:1px; background:rgba(255,255,255,0.07);"></div>
                <div class="auth-divider-text" style="font-size:12px; color:#64748b;">New here?</div>
                <div class="auth-divider-line" style="flex:1; height:1px; background:rgba(255,255,255,0.07);"></div>
            </div>""", unsafe_allow_html=True)

            if st.button("Create Account →", use_container_width=True, key="goto_signup"):
                st.session_state.auth_mode = "signup"
                st.rerun()

        else:
            with st.form("signup_form", clear_on_submit=False):
                st.markdown("""
                <div class="auth-logo-ring">🚀</div>
                <div class="auth-brand-title" style="text-align:center; font-family:'Space Grotesk',sans-serif; font-size:26px; font-weight:700; background:linear-gradient(135deg, #c7d2fe, #67e8f9); -webkit-background-clip:text; -webkit-text-fill-color:transparent;">CREATE ACCOUNT</div>
                <div class="auth-brand-subtitle" style="text-align:center; font-size:13px; color:#94a3b8; margin-bottom:20px;">Register an administrator account</div>
                """, unsafe_allow_html=True)
                new_username = st.text_input("USERNAME", placeholder="choose username", label_visibility="visible")
                new_password = st.text_input("PASSWORD", type="password", placeholder="min. 6 characters", label_visibility="visible")
                confirm_password = st.text_input("CONFIRM PASSWORD", type="password", placeholder="repeat password", label_visibility="visible")
                st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
                submit = st.form_submit_button("🚀 Create Workspace Account", use_container_width=True)

                if submit:
                    new_username = (new_username or "").strip()
                    if len(new_username) < 3:
                        st.error("⚠️ Username must be at least 3 characters.")
                    elif len(new_password) < 6:
                        st.error("⚠️ Password must be at least 6 characters.")
                    elif new_password != confirm_password:
                        st.error("⚠️ Passwords do not match.")
                    else:
                        success, message = db.register_user(new_username, new_password)
                        if success:
                            st.success(f"✅ {message}")
                            st.session_state.auth_mode = "login"
                            time.sleep(1.0)
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")

            st.markdown("""
            <div class="auth-divider" style="display:flex; align-items:center; gap:12px; margin:20px 0;">
                <div class="auth-divider-line" style="flex:1; height:1px; background:rgba(255,255,255,0.07);"></div>
                <div class="auth-divider-text" style="font-size:12px; color:#64748b;">Have an account?</div>
                <div class="auth-divider-line" style="flex:1; height:1px; background:rgba(255,255,255,0.07);"></div>
            </div>""", unsafe_allow_html=True)

            if st.button("← Back to Sign In", use_container_width=True, key="goto_login"):
                st.session_state.auth_mode = "login"
                st.rerun()

# ---------------------------------------------------------
# Application Router
# ---------------------------------------------------------
if not st.session_state.authenticated:
    inject_custom_styling("Dark")
    render_auth_page()
else:
    # Set theme from session state
    inject_custom_styling(st.session_state.theme)
    
    # ---------------------------------------------------------
    # GLOBAL FILTER SIDEBAR
    # ---------------------------------------------------------
    with st.sidebar:
        st.markdown(f"### ⚡ Welcome, {st.session_state.username}")
        st.caption(f"Resource Node: {st.session_state.data_source}")
        
        st.markdown("---")
        
        # Reset and Logout buttons
        col_out1, col_out2 = st.columns(2)
        with col_out1:
            if st.button("Reset Session", use_container_width=True):
                df_temp, src_temp = load_default_dataset()
                st.session_state.active_data = enrich_and_prepare_data(df_temp)
                st.session_state.data_source = src_temp
                st.session_state.live_session_revenue = 0.0
                st.session_state.live_session_orders = 0
                st.session_state.simulated_orders = []
                st.session_state.simulation_running = False
                st.session_state.notifications = ["🔔 Workspace state reset to default sandbox."]
                st.toast("✅ Workspace state reset successfully.")
                time.sleep(0.7)
                st.rerun()
        with col_out2:
            if st.button("Sign Out", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.username = ""
                st.session_state.simulation_running = False
                st.toast("👋 Signed out successfully.")
                time.sleep(0.7)
                st.rerun()
                
        st.markdown("---")
        st.markdown("### 🔍 Global Filters")
        
        raw_df = st.session_state.active_data
        raw_df["Parsed_Date"] = pd.to_datetime(raw_df["Order_Date"])
        min_date = raw_df["Parsed_Date"].min().to_pydatetime()
        max_date = raw_df["Parsed_Date"].max().to_pydatetime()
        
        # Date range picker
        selected_date_range = st.date_input(
            "Order Date Window",
            value=(min_date.date(), max_date.date()),
            min_value=min_date.date(),
            max_value=max_date.date()
        )
        
        if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
            start_date, end_date = selected_date_range
        elif isinstance(selected_date_range, tuple) and len(selected_date_range) == 1:
            start_date = selected_date_range[0]
            end_date = max_date.date()
        else:
            start_date = min_date.date()
            end_date = max_date.date()
            
        # Multi-select filters
        all_categories = sorted(raw_df["Category"].dropna().unique().tolist())
        selected_cats = st.multiselect("Category", all_categories, default=all_categories)
        
        all_products = sorted(raw_df["Product"].dropna().unique().tolist())
        selected_prods = st.multiselect("Product", all_products, default=all_products)
        
        all_customers = sorted(raw_df["Customer"].dropna().unique().tolist())
        selected_custs = st.multiselect("Customer", all_customers, default=all_customers)
        
        all_regions = sorted(raw_df["Region"].dropna().unique().tolist())
        selected_regions = st.multiselect("Region", all_regions, default=all_regions)
        
        all_reps = sorted(raw_df["Sales_Rep"].dropna().unique().tolist())
        selected_reps = st.multiselect("Sales Representative", all_reps, default=all_reps)
        
        all_payments = sorted(raw_df["Payment_Method"].dropna().unique().tolist())
        selected_payments = st.multiselect("Payment Method", all_payments, default=all_payments)
        
        all_channels = sorted(raw_df["Order_Type"].dropna().unique().tolist())
        selected_channels = st.multiselect("Sales Channel", all_channels, default=all_channels)
        
        # Filter matching rows
        filtered_df = raw_df[
            (raw_df["Category"].isin(selected_cats)) &
            (raw_df["Product"].isin(selected_prods)) &
            (raw_df["Customer"].isin(selected_custs)) &
            (raw_df["Region"].isin(selected_regions)) &
            (raw_df["Sales_Rep"].isin(selected_reps)) &
            (raw_df["Payment_Method"].isin(selected_payments)) &
            (raw_df["Order_Type"].isin(selected_channels)) &
            (raw_df["Parsed_Date"].dt.date >= start_date) &
            (raw_df["Parsed_Date"].dt.date <= end_date)
        ]
        
        # ---------------------------------------------------------
        # PERSONALIZATION SETTINGS IN SIDEBAR
        # ---------------------------------------------------------
        st.markdown("---")
        st.markdown("### ⚙️ Personalization Options")
        
        theme_choice = st.selectbox("Dashboard Style", ["Sleek Dark Mode", "Enterprise Light Mode"], index=0 if st.session_state.theme == "Dark" else 1)
        prev_theme = st.session_state.theme
        st.session_state.theme = "Dark" if theme_choice == "Sleek Dark Mode" else "Light"
        if prev_theme != st.session_state.theme:
            st.rerun()
            
        st.markdown("**Section Toggles:**")
        show_kpi_blocks = st.checkbox("KPI Highlights & Health Indicator", value=True)
        show_ai_insights = st.checkbox("AI Executive Summary", value=True)
        show_targets_goals = st.checkbox("Budget & Targets", value=True)
        show_sales_product = st.checkbox("Product Trends & Inventory Alerts", value=True)
        show_cust_geo = st.checkbox("Customer CLV & Interactive Map", value=True)
        show_flows_diagram = st.checkbox("Interactive Flow Diagram (Sankey)", value=True)
        show_financials = st.checkbox("Tax, Refund & Lead Funnel", value=True)
        
        st.markdown("**Widget Sequence:**")
        layout_seq = st.selectbox(
            "Priority Layout Preset",
            [
                "Standard Layout",
                "Insights-First Layout",
                "Finance-First Layout",
                "Geography-First Layout"
            ]
        )
        
        if st.button("💾 Save Dashboard Layout"):
            st.toast("✅ Layout preset successfully saved to session workspace.")
            
        # Fullscreen trigger
        fullscreen_js = """
        <script>
        function goFullscreen() {
            var elem = window.parent.document.documentElement;
            if (elem.requestFullscreen) {
                elem.requestFullscreen();
            } else if (elem.webkitRequestFullscreen) { /* Safari */
                elem.webkitRequestFullscreen();
            } else if (elem.msRequestFullscreen) { /* IE11 */
                elem.msRequestFullscreen();
            }
        }
        </script>
        <button onclick="goFullscreen()" style="
            width: 100%;
            background: rgba(99, 102, 241, 0.15);
            color: #6366f1;
            border: 1px solid rgba(99, 102, 241, 0.3);
            border-radius: 10px;
            padding: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            margin-top: 10px;
        ">🖥️ Fullscreen View</button>
        """
        st.components.v1.html(fullscreen_js, height=45)

    # ---------------------------------------------------------
    # GLOBAL DATA CONTEXT BAR (Upload / Load Sample)
    # ---------------------------------------------------------
    col_uploader, col_load = st.columns([2.5, 1])
    
    with col_uploader:
        uploaded_file = st.file_uploader("Upload Sales Dataset (CSV format)", type=["csv"], key="global_csv_uploader")
        if uploaded_file is not None:
            try:
                uploaded_df = pd.read_csv(uploaded_file)
                expected_cols = ["Order_ID", "Sales", "Quantity", "Product"]
                missing = [c for c in expected_cols if c not in uploaded_df.columns]
                if missing:
                    st.error(f"Missing required columns in CSV: {', '.join(missing)}")
                else:
                    enriched_df = enrich_and_prepare_data(uploaded_df)
                    st.session_state.active_data = enriched_df
                    st.session_state.data_source = f"Uploaded File ({uploaded_file.name})"
                    st.toast(f"✅ Loaded successfully! Enriched {len(enriched_df)} transaction records.")
                    st.success(f"Loaded and enriched {len(enriched_df)} records from {uploaded_file.name}.")
                    st.session_state.notifications.insert(0, f"🔔 Loaded new custom dataset ({uploaded_file.name}) containing {len(enriched_df)} rows.")
                    time.sleep(0.8)
                    st.rerun()
            except Exception as e:
                st.error(f"Error reading CSV: {str(e)}")
                
    with col_load:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("🔄 Load Sample Data", use_container_width=True, key="load_sample_btn"):
            with st.spinner("Loading Enterprise Dataset..."):
                time.sleep(1.0) # Visual buffer
                df_temp, src_temp = load_default_dataset()
                enriched_df = enrich_and_prepare_data(df_temp)
                st.session_state.active_data = enriched_df
                st.session_state.data_source = src_temp
                st.toast(f"✅ Sample dataset loaded successfully ({len(enriched_df)} records).")
                st.success(f"✅ Sample dataset loaded successfully ({len(enriched_df)} records).")
                st.session_state.notifications.insert(0, f"🔔 Sandbox sample dataset loaded successfully ({len(enriched_df)} rows).")
                time.sleep(0.8)
                st.rerun()

    st.markdown("---")

    # ---------------------------------------------------------
    # MAIN NAVIGATION TABS
    # ---------------------------------------------------------
    navigation_page = st.radio(
        "Navigation Bar",
        [
            "📊 Executive Hub",
            "📈 Sales & Products",
            "👥 Customers & Geography",
            "⚡ Real-Time Ops",
            "🛠️ Custom Report Builder",
            "📂 Data Workspace"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.markdown("---")

    if filtered_df.empty:
        st.warning("⚠️ No records matched the selected query parameters. Please broaden your sidebar filters.")
    else:
        # Theme configuration for Plotly elements
        plotly_theme = "plotly_dark" if st.session_state.theme == "Dark" else "plotly"
        text_color_css = "white" if st.session_state.theme == "Dark" else "black"

        # ---------------------------------------------------------
        # 1. EXECUTIVE HUB TAB
        # ---------------------------------------------------------
        if navigation_page == "📊 Executive Hub":
            st.title("📊 Executive Sales Overview")
            st.write("C-Suite summary of commercial revenue, organizational health index, AI-driven insights, and leaderboards.")
            
            # --- Calculations ---
            total_rev = filtered_df["Sales"].sum()
            total_orders = filtered_df["Order_ID"].nunique()
            total_qty = filtered_df["Quantity"].sum()
            avg_order = total_rev / total_orders if total_orders > 0 else 0.0
            
            total_cost = filtered_df["Cost"].sum()
            gross_profit = total_rev - total_cost
            profit_margin = (gross_profit / total_rev * 100) if total_rev > 0 else 0.0
            
            total_cust = filtered_df["Customer_ID"].nunique()
            cust_counts = filtered_df.groupby("Customer_ID")["Order_ID"].nunique()
            returning_cust = (cust_counts > 1).sum()
            retention_rate = (returning_cust / total_cust * 100) if total_cust > 0 else 0.0
            
            # Target Calculation
            total_months = max(1, raw_df["Order_Date"].dt.to_period("M").nunique())
            avg_monthly_sales = raw_df["Sales"].sum() / total_months
            selected_days = max(1, (filtered_df["Order_Date"].max() - filtered_df["Order_Date"].min()).days)
            selected_months = max(0.5, selected_days / 30.4)
            period_target = avg_monthly_sales * 1.25 * selected_months
            target_achievement = (total_rev / period_target * 100) if period_target > 0 else 0.0
            
            # MoM & YoY calculation on full dataset
            df_monthly = raw_df.groupby(raw_df["Order_Date"].dt.to_period("M"))["Sales"].sum().reset_index().sort_values("Order_Date")
            if len(df_monthly) >= 2:
                mom_val = ((df_monthly.iloc[-1]["Sales"] - df_monthly.iloc[-2]["Sales"]) / df_monthly.iloc[-2]["Sales"]) * 100
                mom_str = f"▲ +{mom_val:.1f}%" if mom_val >= 0 else f"▼ {mom_val:.1f}%"
            else:
                mom_str = "Baseline"
                
            df_ym = raw_df.groupby(["Year", "Month"])["Sales"].sum().reset_index().sort_values(["Year", "Month"])
            if len(df_ym) >= 13:
                l_row = df_ym.iloc[-1]
                prev_y_row = df_ym[(df_ym["Year"] == l_row["Year"] - 1) & (df_ym["Month"] == l_row["Month"])]
                if not prev_y_row.empty:
                    yoy_val = ((l_row["Sales"] - prev_y_row.iloc[0]["Sales"]) / prev_y_row.iloc[0]["Sales"]) * 100
                    yoy_str = f"▲ +{yoy_val:.1f}%" if yoy_val >= 0 else f"▼ {yoy_val:.1f}%"
                else:
                    yoy_str = "N/A"
            else:
                yoy_str = "N/A"
                
            # Refund Rate
            refunded_sales = filtered_df[filtered_df["Refunded"] == True]["Sales"].sum()
            refund_rate = (refunded_sales / total_rev * 100) if total_rev > 0 else 0.0
            
            # Business Health Score
            health_score = 0.35 * min(100.0, target_achievement) + 0.35 * (profit_margin * 2.0) + 0.15 * (retention_rate * 2.0) + 0.15 * max(0.0, (100.0 - refund_rate * 10.0))
            health_score = max(0.0, min(100.0, health_score))
            
            # Define widgets/blocks
            def widget_kpi_highlights():
                st.markdown("### 🏆 Core Metrics Highlights")
                col_k1, col_k2, col_k3, col_k4 = st.columns(4)
                col_k1.metric("Gross Sales Revenue", f"₹{total_rev:,.2f}", mom_str + " MoM")
                col_k2.metric("Total Order Volume", f"{total_orders:,}", yoy_str + " YoY")
                col_k3.metric("Product Units Sold", f"{total_qty:,}")
                col_k4.metric("Avg Order Value (AOV)", f"₹{avg_order:,.2f}")
                
                col_k5, col_k6, col_k7, col_k8 = st.columns(4)
                col_k5.metric("Gross Profit", f"₹{gross_profit:,.2f}")
                col_k6.metric("Profit Margin (%)", f"{profit_margin:.2f}%")
                col_k7.metric("Total Customers", f"{total_cust:,}")
                col_k8.metric("Returning Customers", f"{returning_cust:,}")

                col_k9, col_k10, col_k11, col_k12 = st.columns(4)
                col_k9.metric("Customer Retention Rate", f"{retention_rate:.2f}%")
                col_k10.metric("MoM Growth", mom_str)
                col_k11.metric("YoY Growth", yoy_str)
                col_k12.metric("Business Health Score", f"{health_score:.1f}/100")
                
            def widget_ai_insights():
                st.markdown("### 🤖 AI Executive Insights Panel")
                
                # Fetch key variables for dynamic AI summaries
                cat_contrib = filtered_df.groupby("Category")["Sales"].sum()
                top_cat = cat_contrib.idxmax() if not cat_contrib.empty else "N/A"
                top_cat_pct = (cat_contrib.max() / total_rev * 100) if total_rev > 0 else 0.0
                
                reg_contrib = filtered_df.groupby("Region")["Sales"].sum()
                top_reg = reg_contrib.idxmax() if not reg_contrib.empty else "N/A"
                top_reg_pct = (reg_contrib.max() / total_rev * 100) if total_rev > 0 else 0.0

                # Calculate fastest growing region dynamically
                reg_growth_str = f"{top_reg} Region is the fastest-growing market by {top_reg_pct:.1f}% of total sales"
                try:
                    df_reg_monthly = filtered_df.groupby(["Region", filtered_df["Order_Date"].dt.to_period("M")])["Sales"].sum().reset_index()
                    if df_reg_monthly["Order_Date"].nunique() >= 2:
                        periods = sorted(df_reg_monthly["Order_Date"].unique())
                        p_prev, p_curr = periods[-2], periods[-1]
                        growth_rates = {}
                        for reg in filtered_df["Region"].unique():
                            s_prev = df_reg_monthly[(df_reg_monthly["Region"] == reg) & (df_reg_monthly["Order_Date"] == p_prev)]["Sales"].sum()
                            s_curr = df_reg_monthly[(df_reg_monthly["Region"] == reg) & (df_reg_monthly["Order_Date"] == p_curr)]["Sales"].sum()
                            if s_prev > 0:
                                growth_rates[reg] = ((s_curr - s_prev) / s_prev) * 100
                        if growth_rates:
                            fastest_reg = max(growth_rates, key=growth_rates.get)
                            fastest_growth = growth_rates[fastest_reg]
                            reg_growth_str = f"{fastest_reg} Region is the fastest-growing market by {fastest_growth:.1f}% MoM"
                except Exception:
                    pass
                
                status_color = "green" if health_score >= 80 else ("orange" if health_score >= 50 else "red")
                
                with st.expander("✨ Automated Executive Briefing (Click to expand/collapse)", expanded=True):
                    st.write(f"""
                    - **Revenue Status**: Total sales of **₹{total_rev:,.2f}** achieved with a gross margin of **{profit_margin:.2f}%**.
                    - **Product Distribution**: **{top_cat}** represents your largest category sales driver, contributing **{top_cat_pct:.1f}%** of total sales.
                    - **Territory Leader**: **{reg_growth_str}**.
                    - **Operational Health**: The organizational composite score is <span style='color:{status_color}; font-weight:700;'>{health_score:.1f}/100</span>. Refund rates are well-managed at **{refund_rate:.2f}%**.
                    - **Strategic Action Plan**: Focus promotional campaigns on secondary channels, as online sales account for the majority of customer orders. Average Order Value (AOV) is robust at **₹{avg_order:,.2f}**.
                    """, unsafe_allow_html=True)
                    
            def widget_targets_goals():
                st.markdown("### 🎯 Sales Targets & Goal Tracking")
                col_g1, col_g2 = st.columns(2)
                
                with col_g1:
                    # Health Score Gauge
                    fig_health = go.Figure(go.Indicator(
                        mode = "gauge+number",
                        value = health_score,
                        title = {'text': "Business Health Score"},
                        gauge = {
                            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': text_color_css},
                            'bar': {'color': "#6366f1"},
                            'bgcolor': "rgba(0,0,0,0)",
                            'borderwidth': 2,
                            'steps': [
                                {'range': [0, 50], 'color': 'rgba(239, 68, 68, 0.12)'},
                                {'range': [50, 80], 'color': 'rgba(245, 158, 11, 0.12)'},
                                {'range': [80, 100], 'color': 'rgba(16, 185, 129, 0.12)'}
                            ]
                        }
                    ))
                    fig_health.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': text_color_css}, height=180, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig_health, use_container_width=True)
                    
                with col_g2:
                    # Target achievement gauge
                    fig_target = go.Figure(go.Indicator(
                        mode = "gauge+number+delta",
                        value = total_rev,
                        delta = {'reference': period_target, 'position': "top", 'valueformat': "₹,.0f"},
                        title = {'text': "Revenue Target Achievement"},
                        gauge = {
                            'axis': {'range': [0, max(period_target * 1.5, total_rev * 1.1)], 'tickwidth': 1, 'tickcolor': text_color_css},
                            'bar': {'color': "#10b981"},
                            'bgcolor': "rgba(0,0,0,0)",
                            'borderwidth': 2,
                            'steps': [
                                {'range': [0, period_target], 'color': 'rgba(239, 68, 68, 0.12)'},
                                {'range': [period_target, period_target * 1.5], 'color': 'rgba(16, 185, 129, 0.12)'}
                            ]
                        }
                    ))
                    fig_target.update_layout(paper_bgcolor="rgba(0,0,0,0)", font={'color': text_color_css}, height=180, margin=dict(l=20, r=20, t=30, b=20))
                    st.plotly_chart(fig_target, use_container_width=True)
                    
            def widget_financials():
                st.markdown("### 🏦 Financial Breakdown & Funnel")
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    # Waterfall chart: sales -> discounts -> tax -> cost -> profit
                    fig_waterfall = go.Figure(go.Waterfall(
                        name = "Revenue Bridge",
                        orientation = "v",
                        measure = ["relative", "relative", "relative", "relative", "total"],
                        x = ["Gross Sales", "Discounts", "Taxes", "Cost of Goods", "Net Profit"],
                        textposition = "outside",
                        text = [f"+₹{total_rev:,.0f}", f"-₹{filtered_df['Discount'].sum():,.0f}", f"+₹{filtered_df['Tax'].sum():,.0f}", f"-₹{total_cost:,.0f}", f"₹{gross_profit:,.0f}"],
                        y = [total_rev, -filtered_df["Discount"].sum(), filtered_df["Tax"].sum(), -total_cost, 0],
                        connector = {"line":{"color":"rgb(63, 63, 63)"}},
                        decreasing = {"marker":{"color":"#ef4444"}},
                        increasing = {"marker":{"color":"#10b981"}},
                        totals = {"marker":{"color":"#6366f1"}}
                    ))
                    fig_waterfall.update_layout(
                        title = "Financial Value Bridge",
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        font={'color': text_color_css},
                        height=280,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig_waterfall, use_container_width=True)
                    
                with col_f2:
                    # Sales Funnel
                    leads = int(total_orders * 5)
                    opps = int(total_orders * 2.5)
                    quotes = int(total_orders * 1.5)
                    closed = int(total_orders)
                    delivered = int(filtered_df[filtered_df["Shipping_Status"] == "Delivered"]["Order_ID"].nunique())
                    
                    fig_funnel = go.Figure(go.Funnel(
                        y = ["Leads Generated", "Opportunities", "Quotes Sent", "Closed Orders", "Orders Delivered"],
                        x = [leads, opps, quotes, closed, delivered],
                        textinfo = "value+percent initial",
                        marker = {"color": ["#6366f1", "#4f46e5", "#3b82f6", "#10b981", "#059669"]}
                    ))
                    fig_funnel.update_layout(
                        title = "Lead-to-Order Conversion Pipeline",
                        paper_bgcolor="rgba(0,0,0,0)",
                        font={'color': text_color_css},
                        height=280,
                        margin=dict(l=20, r=20, t=40, b=20)
                    )
                    st.plotly_chart(fig_funnel, use_container_width=True)
                    
            def widget_leaderboards():
                st.markdown("### 👥 Performance Leaderboards")
                col_l1, col_l2 = st.columns(2)
                
                with col_l1:
                    st.markdown("🏆 **Top 5 Sales Representatives**")
                    rep_sales = filtered_df.groupby("Sales_Rep").agg({"Sales": "sum", "Order_ID": "count"}).reset_index()
                    rep_sales.columns = ["Sales Representative", "Total Generated (₹)", "Closed Deals"]
                    rep_sales = rep_sales.sort_values("Total Generated (₹)", ascending=False).head(5)
                    st.dataframe(
                        rep_sales,
                        column_config={
                            "Total Generated (₹)": st.column_config.NumberColumn("Total Generated", format="₹%,.2f")
                        },
                        use_container_width=True,
                        hide_index=True
                    )
                    
                with col_l2:
                    st.markdown("🏢 **Top 5 Customers Leaderboard**")
                    cust_sales = filtered_df.groupby("Customer").agg({"Sales": "sum", "Order_ID": "count"}).reset_index()
                    cust_sales.columns = ["Customer", "Lifetime Sales (₹)", "Order Count"]
                    cust_sales = cust_sales.sort_values("Lifetime Sales (₹)", ascending=False).head(5)
                    st.dataframe(
                        cust_sales,
                        column_config={
                            "Lifetime Sales (₹)": st.column_config.NumberColumn("Lifetime Sales", format="₹%,.2f")
                        },
                        use_container_width=True,
                        hide_index=True
                    )

            # Reordering/Sequence execution
            sequence_map = {
                "Standard Layout": [widget_kpi_highlights, widget_ai_insights, widget_targets_goals, widget_financials, widget_leaderboards],
                "Insights-First Layout": [widget_ai_insights, widget_kpi_highlights, widget_targets_goals, widget_financials, widget_leaderboards],
                "Finance-First Layout": [widget_targets_goals, widget_financials, widget_kpi_highlights, widget_ai_insights, widget_leaderboards],
                "Geography-First Layout": [widget_leaderboards, widget_kpi_highlights, widget_ai_insights, widget_targets_goals, widget_financials]
            }
            
            blocks = sequence_map.get(layout_seq, sequence_map["Standard Layout"])
            
            for b in blocks:
                if b == widget_kpi_highlights and show_kpi_blocks:
                    b()
                elif b == widget_ai_insights and show_ai_insights:
                    b()
                elif b == widget_targets_goals and show_targets_goals:
                    b()
                elif b == widget_financials and show_financials:
                    b()
                elif b == widget_leaderboards:
                    b()
                st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

        # ---------------------------------------------------------
        # 2. SALES & PRODUCT TAB
        # ---------------------------------------------------------
        elif navigation_page == "📈 Sales & Products":
            st.title("📈 Sales Trends & Product Performance")
            st.write("Chronological trend regression, best-sellers, heatmaps, and low stock alerts.")
            
            if show_sales_product:
                st.markdown("### 🔍 Historical Trends & Predictive Modeling")
                
                # Forecasting & Trends
                col_tr1, col_tr2 = st.columns([2, 1])
                with col_tr1:
                    st.markdown("#### Chronological Revenue Trend")
                    trend_type = st.selectbox("Select Trend Interval", ["Daily", "Weekly", "Monthly", "Quarterly", "Yearly"], index=2)
                    
                    if trend_type == "Daily":
                        trend_df = filtered_df.groupby(filtered_df["Order_Date"].dt.date)["Sales"].sum().reset_index()
                        trend_df.columns = ["Period", "Sales"]
                    elif trend_type == "Weekly":
                        trend_df = filtered_df.groupby(filtered_df["Order_Date"].dt.to_period("W"))["Sales"].sum().reset_index()
                        trend_df.columns = ["Period", "Sales"]
                        trend_df["Period"] = trend_df["Period"].astype(str)
                    elif trend_type == "Monthly":
                        trend_df = filtered_df.groupby(filtered_df["Order_Date"].dt.to_period("M"))["Sales"].sum().reset_index()
                        trend_df.columns = ["Period", "Sales"]
                        trend_df["Period"] = trend_df["Period"].astype(str)
                    elif trend_type == "Quarterly":
                        trend_df = filtered_df.groupby(filtered_df["Order_Date"].dt.to_period("Q"))["Sales"].sum().reset_index()
                        trend_df.columns = ["Period", "Sales"]
                        trend_df["Period"] = trend_df["Period"].astype(str)
                    else: # Yearly
                        trend_df = filtered_df.groupby(filtered_df["Order_Date"].dt.year)["Sales"].sum().reset_index()
                        trend_df.columns = ["Period", "Sales"]

                    fig_trend = px.area(
                        trend_df, x="Period", y="Sales",
                        labels={"Period": trend_type, "Sales": "Sales Revenue (₹)"},
                        template=plotly_theme
                    )
                    fig_trend.update_traces(line=dict(color="#6366f1", width=3))
                    fig_trend.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        margin=dict(l=10, r=10, t=10, b=10),
                        height=280
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                with col_tr2:
                    st.markdown("#### Predictive Sales Forecasting")
                    horizon_days = st.selectbox("Forecast Horizon (Days)", [30, 60, 90], index=0)
                    
                    df_daily = filtered_df.copy()
                    df_daily["Date_Only"] = df_daily["Order_Date"].dt.date
                    daily_sales = df_daily.groupby("Date_Only")["Sales"].sum().sort_index()
                    
                    if len(daily_sales) < 5:
                        st.warning("Insufficient chronological spread to generate predictions. Requires 5+ days.")
                    else:
                        min_date = daily_sales.index.min()
                        x_days = np.array([(d - min_date).days for d in daily_sales.index])
                        y_sales = daily_sales.values
                        
                        coeffs = np.polyfit(x_days, y_sales, 1)
                        trend_func = np.poly1d(coeffs)
                        slope = coeffs[0]
                        
                        future_x = np.array([x_days[-1] + i for i in range(1, horizon_days + 1)])
                        future_dates = [min_date + pd.Timedelta(days=int(x)) for x in future_x]
                        future_y = np.clip(trend_func(future_x), a_min=0, a_max=None)
                        
                        residuals = y_sales - trend_func(x_days)
                        se = np.std(residuals) if len(residuals) > 1 else 0
                        
                        upper_band = future_y + 1.96 * se
                        lower_band = np.clip(future_y - 1.96 * se, a_min=0, a_max=None)
                        
                        fig_fore = go.Figure()
                        fig_fore.add_trace(go.Scatter(x=daily_sales.index, y=y_sales, mode="lines", name="Historical Daily", line=dict(color="#6366f1", width=2)))
                        fig_fore.add_trace(go.Scatter(x=future_dates, y=future_y, mode="lines", name="Forecast", line=dict(color="#f59e0b", width=2, dash="dot")))
                        fig_fore.add_trace(go.Scatter(
                            x=list(future_dates) + list(future_dates)[::-1],
                            y=list(upper_band) + list(lower_band)[::-1],
                            fill='toself',
                            fillcolor='rgba(245, 158, 11, 0.15)',
                            line=dict(color='rgba(255,255,255,0)'),
                            hoverinfo="skip",
                            showlegend=True,
                            name="95% Confidence Band"
                        ))
                        
                        fig_fore.update_layout(
                            template=plotly_theme,
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            height=250,
                            margin=dict(l=10, r=10, t=10, b=10)
                        )
                        st.plotly_chart(fig_fore, use_container_width=True)
                        st.caption(f"Daily Incremental Revenue Slope: **₹{slope:,.2f}/day**")
                        
                st.markdown("---")
                st.markdown("### 🍕 Product Shares & Profitability Analysis")
                col_sh1, col_sh2 = st.columns(2)
                
                with col_sh1:
                    st.markdown("#### Category Contribution Share (Donut)")
                    cat_sales = filtered_df.groupby("Category")["Sales"].sum().reset_index()
                    fig_pie = px.pie(cat_sales, values="Sales", names="Category", hole=0.6, template=plotly_theme)
                    fig_pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=280, margin=dict(l=10, r=10, t=20, b=10))
                    st.plotly_chart(fig_pie, use_container_width=True)
                    
                with col_sh2:
                    st.markdown("#### Product Profitability Mapping")
                    prod_profits = filtered_df.groupby("Product").agg({"Sales": "sum", "Cost": "sum", "Quantity": "sum"}).reset_index()
                    prod_profits["Profit"] = prod_profits["Sales"] - prod_profits["Cost"]
                    prod_profits["Profit Margin %"] = prod_profits["Profit"] / prod_profits["Sales"] * 100
                    
                    fig_scatter = px.scatter(
                        prod_profits, x="Quantity", y="Profit", size="Sales", color="Product",
                        hover_name="Product", labels={"Quantity": "Units Sold", "Profit": "Net Profit (₹)"},
                        template=plotly_theme
                    )
                    fig_scatter.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=280, margin=dict(l=10, r=10, t=20, b=10))
                    st.plotly_chart(fig_scatter, use_container_width=True)

                st.markdown("---")
                st.markdown("#### Best & Worst Seller Products")
                prod_sales = filtered_df.groupby("Product")["Sales"].sum().reset_index()
                top_sellers = prod_sales.sort_values("Sales", ascending=False).head(5)
                bottom_sellers = prod_sales.sort_values("Sales", ascending=True).head(5)
                
                col_bs1, col_bs2 = st.columns(2)
                with col_bs1:
                    st.markdown("🏆 **Top 5 Best Sellers**")
                    st.dataframe(top_sellers, column_config={"Sales": st.column_config.NumberColumn("Total Sales", format="₹%,.2f")}, use_container_width=True, hide_index=True)
                with col_bs2:
                    st.markdown("⚠️ **Top 5 Worst Sellers**")
                    st.dataframe(bottom_sellers, column_config={"Sales": st.column_config.NumberColumn("Total Sales", format="₹%,.2f")}, use_container_width=True, hide_index=True)
                    
                st.markdown("---")
                st.markdown("### 🌡️ Regional Performance Heatmap & Catalog Visibility")
                col_hp1, col_hp2 = st.columns(2)
                
                with col_hp1:
                    st.markdown("#### Product Category Sales Pivot")
                    heatmap_pivot = st.radio("Pivot Category Sales By", ["Region", "Month"], horizontal=True)
                    if heatmap_pivot == "Region":
                        heatmap_df = filtered_df.pivot_table(values="Sales", index="Category", columns="Region", aggfunc="sum").fillna(0)
                    else:
                        heatmap_df = filtered_df.pivot_table(values="Sales", index="Category", columns="Month", aggfunc="sum").fillna(0)
                        month_names = {1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr", 5:"May", 6:"Jun", 7:"Jul", 8:"Aug", 9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"}
                        heatmap_df.columns = [month_names.get(c, f"M{c}") for c in heatmap_df.columns]

                    fig_heatmap = px.imshow(
                        heatmap_df,
                        labels=dict(x=heatmap_pivot, y="Category", color="Revenue"),
                        color_continuous_scale="Viridis",
                        template=plotly_theme
                    )
                    fig_heatmap.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=280, margin=dict(l=10, r=10, t=20, b=10))
                    st.plotly_chart(fig_heatmap, use_container_width=True)
                    
                with col_hp2:
                    st.markdown("#### 🚨 Inventory Status & Alerts")
                    # Calculate deterministic inventory
                    def get_hash_num(val, max_val):
                        return int(hashlib.md5(str(val).encode('utf-8')).hexdigest(), 16) % max_val
                        
                    inv_rows = []
                    for prod in filtered_df["Product"].unique():
                        prod_subset = filtered_df[filtered_df["Product"] == prod]
                        qty_sold = prod_subset["Quantity"].sum()
                        init_stock = 25 + get_hash_num(prod + "stock", 60)
                        curr_stock = max(0, init_stock - qty_sold)
                        status = "Low Stock" if curr_stock < 15 else "In Stock"
                        inv_rows.append({
                            "Product": prod,
                            "Category": prod_subset["Category"].iloc[0],
                            "Sold Qty": qty_sold,
                            "Current Stock": curr_stock,
                            "Status": status
                        })
                    inv_df = pd.DataFrame(inv_rows).sort_values("Current Stock")
                    
                    low_stock_items = inv_df[inv_df["Status"] == "Low Stock"]["Product"].tolist()
                    if low_stock_items:
                        st.error(f"🚨 **Low Stock Alert (< 15 units):** {', '.join(low_stock_items)}")
                    else:
                        st.success("✅ **All product inventory status healthy.**")
                        
                    st.dataframe(inv_df, use_container_width=True, hide_index=True, height=200)

        # ---------------------------------------------------------
        # 3. CUSTOMERS & GEOGRAPHY TAB
        # ---------------------------------------------------------
        elif navigation_page == "👥 Customers & Geography":
            st.title("👥 Customer Cohorts & Geographical Distribution")
            st.write("Customer Segmentation profiles, Lifetime Value mapping, and interactive regional maps.")
            
            if show_cust_geo:
                col_g1, col_g2 = st.columns([1, 1.2])
                with col_g1:
                    st.markdown("#### Customer Segmentation Share")
                    segment_df = filtered_df.groupby("Customer_Segment")["Sales"].sum().reset_index()
                    fig_donut = px.pie(segment_df, values="Sales", names="Customer_Segment", hole=0.5, template=plotly_theme)
                    fig_donut.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=320, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_donut, use_container_width=True)
                    
                with col_g2:
                    st.markdown("#### Interactive Geographical Distribution Map")
                    city_sales = filtered_df.groupby(["City", "Latitude", "Longitude", "State"])["Sales"].sum().reset_index()
                    fig_map = px.scatter_mapbox(
                        city_sales, lat="Latitude", lon="Longitude", size="Sales",
                        color="Sales", hover_name="City", hover_data=["State", "Sales"],
                        color_continuous_scale="Viridis", size_max=30, zoom=3.2,
                        mapbox_style="carto-darkmatter" if st.session_state.theme == "Dark" else "carto-positron",
                        template=plotly_theme
                    )
                    fig_map.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=320, paper_bgcolor="rgba(0,0,0,0)")
                    st.plotly_chart(fig_map, use_container_width=True)
                    
                st.markdown("---")
                st.markdown("#### 👤 Customer Lifecycle & CLV Profiles")
                customer_profiles = filtered_df.groupby("Customer").agg({
                    "Customer_ID": "first",
                    "Customer_Segment": "first",
                    "Sales": ["sum", "mean"],
                    "Order_ID": "nunique",
                    "City": "first"
                }).reset_index()
                customer_profiles.columns = ["Customer Name", "Customer ID", "Segment", "Lifetime Value (CLV)", "Avg Order Value", "Purchase Frequency (Orders)", "Base City"]
                customer_profiles = customer_profiles.sort_values("Lifetime Value (CLV)", ascending=False)
                st.dataframe(
                    customer_profiles,
                    column_config={
                        "Lifetime Value (CLV)": st.column_config.NumberColumn("Lifetime Value (CLV)", format="₹%,.2f"),
                        "Avg Order Value": st.column_config.NumberColumn("Avg Order Value", format="₹%,.2f"),
                        "Purchase Frequency (Orders)": st.column_config.NumberColumn("Purchase Frequency (Orders)")
                    },
                    use_container_width=True,
                    hide_index=True
                )
                
                st.markdown("---")
                
                # Sankey Flow Diagram
                if show_flows_diagram:
                    st.markdown("### 🌊 Sankey Flow Dynamics")
                    
                    chans = filtered_df["Order_Type"].unique().tolist()
                    regs = filtered_df["Region"].unique().tolist()
                    cats = filtered_df["Category"].unique().tolist()
                    pays = filtered_df["Payment_Method"].unique().tolist()
                    
                    nodes_list = chans + regs + cats + pays
                    n_indices = {n: idx for idx, n in enumerate(nodes_list)}
                    
                    src_nodes, tgt_nodes, flows_val = [], [], []
                    
                    # Channels -> Regions
                    c_to_r = filtered_df.groupby(["Order_Type", "Region"])["Sales"].sum().reset_index()
                    for _, r in c_to_r.iterrows():
                        src_nodes.append(n_indices[r["Order_Type"]])
                        tgt_nodes.append(n_indices[r["Region"]])
                        flows_val.append(r["Sales"])
                        
                    # Regions -> Categories
                    r_to_c = filtered_df.groupby(["Region", "Category"])["Sales"].sum().reset_index()
                    for _, r in r_to_c.iterrows():
                        src_nodes.append(n_indices[r["Region"]])
                        tgt_nodes.append(n_indices[r["Category"]])
                        flows_val.append(r["Sales"])
                        
                    # Categories -> Payment Methods
                    c_to_p = filtered_df.groupby(["Category", "Payment_Method"])["Sales"].sum().reset_index()
                    for _, r in c_to_p.iterrows():
                        src_nodes.append(n_indices[r["Category"]])
                        tgt_nodes.append(n_indices[r["Payment_Method"]])
                        flows_val.append(r["Sales"])
                        
                    fig_sankey = go.Figure(data=[go.Sankey(
                        node = dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=nodes_list, color="#6366f1"),
                        link = dict(source=src_nodes, target=tgt_nodes, value=flows_val, color="rgba(99,102,241,0.2)")
                    )])
                    fig_sankey.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        font={'color': text_color_css},
                        height=300,
                        margin=dict(l=10, r=10, t=10, b=10)
                    )
                    st.plotly_chart(fig_sankey, use_container_width=True)

        # ---------------------------------------------------------
        # 4. REAL-TIME OPS TAB
        # ---------------------------------------------------------
        elif navigation_page == "⚡ Real-Time Ops":
            st.title("⚡ Real-Time Feed & Live Simulator")
            st.write("Continuous transaction updates, live system notifications, and terminal activity feed.")
            
            # Streaming active indicator
            if st.session_state.simulation_running:
                st.markdown("""
                    <div class="indicator-box">
                        <div class="indicator-dot"></div>
                        <span style="font-weight:600; color:#22c55e;">LIVE DEPLOYMENT STREAM RUNNING</span>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="indicator-box" style="background:rgba(239,68,68,0.08); border-color:rgba(239,68,68,0.2);">
                        <div class="indicator-dot" style="background-color:#ef4444; box-shadow:0 0 8px #ef4444; animation:none;"></div>
                        <span style="font-weight:600; color:#ef4444;">STREAM PAUSED</span>
                    </div>
                """, unsafe_allow_html=True)
                
            # Broadcast pacing controls
            col_c1, col_c2, col_c3 = st.columns([1, 1, 1])
            with col_c1:
                if st.session_state.simulation_running:
                    if st.button("Pause Broadcast Feed", use_container_width=True):
                        st.session_state.simulation_running = False
                        st.rerun()
                else:
                    if st.button("Resume Broadcast Feed", use_container_width=True):
                        st.session_state.simulation_running = True
                        st.rerun()
            with col_c2:
                st.session_state.simulation_speed = st.slider("Tick Pace (Seconds)", 0.5, 3.0, st.session_state.simulation_speed, step=0.5)
            with col_c3:
                if st.button("Clear Stream Cache", use_container_width=True):
                    st.session_state.live_session_revenue = 0.0
                    st.session_state.live_session_orders = 0
                    st.session_state.simulated_orders = []
                    st.session_state.simulation_running = False
                    st.session_state.notifications = ["🔔 Ticker cache wiped. System ready."]
                    st.toast("✅ Simulation cache cleared.")
                    time.sleep(0.7)
                    st.rerun()
                    
            # Auto-Refresh Toggle
            auto_refresh = st.checkbox("Auto-Refresh Dashboard every 30 seconds", value=False)
            if auto_refresh:
                st.session_state.auto_refresh = True
                refresh_js = """
                <script>
                setTimeout(function(){
                    var buttons = window.parent.document.getElementsByTagName('button');
                    for (var i = 0; i < buttons.length; i++) {
                        if (buttons[i].textContent.includes('🔄 Refresh Page')) {
                            buttons[i].click();
                            break;
                        }
                    }
                }, 30000);
                </script>
                """
                st.components.v1.html(refresh_js, height=0)
            else:
                st.session_state.auto_refresh = False
                
            if st.button("🔄 Refresh Page", key="hidden_refresh_btn"):
                st.toast("🔄 Dashboard refreshed successfully.")
                st.rerun()

            # Execute simulation tick
            if st.session_state.simulation_running:
                new_ord = generate_single_order(st.session_state.active_data)
                # Enrich new row
                new_ord = enrich_and_prepare_data(new_ord)
                
                # Concat
                st.session_state.active_data = pd.concat([st.session_state.active_data, new_ord], ignore_index=True)
                
                # Ticker calculations
                rev_gain = float(new_ord["Sales"].iloc[0])
                st.session_state.live_session_revenue += rev_gain
                st.session_state.live_session_orders += 1
                
                ticker_line = f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Order #{new_ord['Order_ID'].iloc[0]} | Product: {new_ord['Product'].iloc[0]} ({new_ord['Category'].iloc[0]}) | Sales: ₹{rev_gain:,.2f} | Customer: {new_ord['Customer'].iloc[0]}"
                st.session_state.simulated_orders.insert(0, ticker_line)
                
                # Notifications
                st.session_state.notifications.insert(0, f"🔔 [Live] Order #{new_ord['Order_ID'].iloc[0]} received for ₹{rev_gain:,.2f}.")
                
                if len(st.session_state.simulated_orders) > 20:
                    st.session_state.simulated_orders.pop()
                if len(st.session_state.notifications) > 20:
                    st.session_state.notifications.pop()
                    
            st.markdown("---")
            col_rm1, col_rm2 = st.columns(2)
            with col_rm1:
                st.metric("Live Session Billings", f"₹{st.session_state.live_session_revenue:,.2f}")
            with col_rm2:
                st.metric("Live Session Orders", f"{st.session_state.live_session_orders:,}")
                
            st.markdown("---")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                st.markdown("#### Live Terminal Broadcast Ticker")
                feed_html = ""
                if not st.session_state.simulated_orders:
                    feed_html = "<div class='feed-item' style='color:#64748b;'>Waiting for simulator activity...</div>"
                else:
                    for item in st.session_state.simulated_orders:
                        feed_html += f"<div class='feed-item'>{item}</div>"
                st.markdown(f'<div class="live-feed-container">{feed_html}</div>', unsafe_allow_html=True)
                
            with col_t2:
                st.markdown("#### Live Activity Notifications")
                notif_html = ""
                for n in st.session_state.notifications[:10]:
                    notif_html += f"<div class='feed-item' style='color:#10b981;'>{n}</div>"
                st.markdown(f'<div class="live-feed-container">{notif_html}</div>', unsafe_allow_html=True)
                
            if st.session_state.simulation_running:
                time.sleep(st.session_state.simulation_speed)
                st.rerun()

        # ---------------------------------------------------------
        # 5. CUSTOM REPORT BUILDER TAB
        # ---------------------------------------------------------
        elif navigation_page == "🛠️ Custom Report Builder":
            st.title("🛠️ Custom Ad-hoc Report Builder")
            st.write("Select reporting axes, choose chart formats, and render custom sales reports.")
            
            col_b1, col_b2, col_b3 = st.columns(3)
            with col_b1:
                x_axis = st.selectbox("Select X-Axis", ["Category", "Region", "Sales_Rep", "Payment_Method", "Order_Type", "Customer_Segment", "Shipping_Status"])
            with col_b2:
                y_axis = st.selectbox("Select Y-Axis Metric", ["Sales", "Quantity", "Cost", "Discount", "Tax", "Shipping_Time_Days"])
            with col_b3:
                chart_type = st.selectbox("Visual Chart Representation", ["Bar Chart", "Line Chart", "Area Chart", "Scatter Plot", "Pie Donut Chart"])
                
            # Aggregate ad-hoc
            agg_df = filtered_df.groupby(x_axis)[y_axis].sum().reset_index()
            
            st.markdown("---")
            st.markdown(f"#### Custom Analysis: {y_axis} by {x_axis}")
            
            if chart_type == "Bar Chart":
                fig_c = px.bar(agg_df, x=x_axis, y=y_axis, color=x_axis, template=plotly_theme)
            elif chart_type == "Line Chart":
                fig_c = px.line(agg_df, x=x_axis, y=y_axis, markers=True, template=plotly_theme)
            elif chart_type == "Area Chart":
                fig_c = px.area(agg_df, x=x_axis, y=y_axis, template=plotly_theme)
            elif chart_type == "Scatter Plot":
                fig_c = px.scatter(filtered_df, x=x_axis, y=y_axis, size="Quantity", color="Category", template=plotly_theme)
            else:
                fig_c = px.pie(agg_df, values=y_axis, names=x_axis, hole=0.6, template=plotly_theme)
                
            fig_c.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", height=320)
            st.plotly_chart(fig_c, use_container_width=True)

            csv_report = agg_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Report Data (CSV)",
                data=csv_report,
                file_name=f"custom_report_{y_axis.lower()}_by_{x_axis.lower()}.csv",
                mime="text/csv",
                use_container_width=True
            )

        # ---------------------------------------------------------
        # 6. DATA WORKSPACE TAB
        # ---------------------------------------------------------
        elif navigation_page == "📂 Data Workspace":
            st.title("📂 Data Workspace")
            st.write("Browse enriched catalog files, filter entries, and export formats to CSV, Excel, or PDF reports.")
            
            # Operational stats
            tot_rows = len(filtered_df)
            completeness = (filtered_df.notna().sum().sum() / filtered_df.size * 100.0) if filtered_df.size > 0 else 100.0
            avg_bill = filtered_df["Sales"].mean() if tot_rows > 0 else 0.0
            
            col_ds1, col_ds2, col_ds3 = st.columns(3)
            col_ds1.metric("Selected Record Volume", f"{tot_rows:,}")
            col_ds2.metric("Enriched Data Completeness", f"{completeness:.1f}%")
            col_ds3.metric("Segment Average Invoice", f"₹{avg_bill:,.2f}")
            
            st.markdown("---")
            st.markdown("#### Document Export Utilities")
            
            col_ex1, col_ex2, col_ex3 = st.columns(3)
            with col_ex1:
                # CSV Export
                csv_buf = filtered_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Export Filtered Data (CSV)",
                    data=csv_buf,
                    file_name="vortex_workspace_export.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            with col_ex2:
                # Excel Export
                excel_buf = io.BytesIO()
                with pd.ExcelWriter(excel_buf, engine='openpyxl') as writer:
                    filtered_df.to_excel(writer, index=False, sheet_name='Sales Data')
                st.download_button(
                    label="📥 Export Filtered Data (Excel)",
                    data=excel_buf.getvalue(),
                    file_name="vortex_workspace_export.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with col_ex3:
                # Print/Save to PDF trigger
                print_js = """
                <button onclick="window.print()" style="
                    width: 100%;
                    background: #6366f1;
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 10.5px;
                    font-weight: 600;
                    cursor: pointer;
                    box-shadow: 0 4px 14px rgba(99, 102, 241, 0.3);
                ">🖨️ Print Dashboard / Save PDF</button>
                """
                st.components.v1.html(print_js, height=50)
                
            st.markdown("---")
            st.markdown("#### Data Catalog Browser")
            
            # Interactive Search, Sorting, and Column Toggles
            search_query = st.text_input("Quick Product Search...", "").strip()
            
            col_set1, col_set2 = st.columns([2, 1])
            with col_set1:
                visible_columns = st.multiselect(
                    "Column Visibility Toggle",
                    options=filtered_df.columns.tolist(),
                    default=["Order_ID", "Order_Date", "Customer", "Product", "Category", "Region", "Sales", "Quantity", "Order_Type", "Shipping_Status"]
                )
            with col_set2:
                sort_col = st.selectbox("Sort Dataset By", ["Order_Date", "Sales", "Quantity", "Order_ID"], index=0)
                
            browsing_df = filtered_df.copy()
            if search_query:
                browsing_df = browsing_df[browsing_df["Product"].str.contains(search_query, case=False, na=False)]
                
            browsing_df = browsing_df.sort_values(sort_col, ascending=False)
            
            # Pagination
            page_size = 15
            total_pages = max(1, int(np.ceil(len(browsing_df) / page_size)))
            selected_page = st.number_input("Page selector", min_value=1, max_value=total_pages, value=1, step=1, label_visibility="collapsed")
            
            start_idx = (selected_page - 1) * page_size
            end_idx = start_idx + page_size
            page_df = browsing_df[visible_columns].iloc[start_idx:end_idx]
            
            st.markdown(f"Showing page **{selected_page}** of **{total_pages}** ({len(browsing_df)} total entries)")
            st.dataframe(
                page_df,
                column_config={
                    "Sales": st.column_config.NumberColumn("Billing Value", format="₹%,.2f"),
                    "Cost": st.column_config.NumberColumn("Cost", format="₹%,.2f"),
                    "Discount": st.column_config.NumberColumn("Discount", format="₹%,.2f"),
                    "Tax": st.column_config.NumberColumn("Tax", format="₹%,.2f"),
                    "Quantity": st.column_config.NumberColumn("Quantity"),
                    "Order_Date": st.column_config.DateColumn("Date")
                },
                use_container_width=True
            )
