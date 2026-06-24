import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Set page layout and title
st.set_page_config(
    page_title="Sales Data Analysis Dashboard",
    page_icon="📊",
    layout="wide",
)

# Function to load sales data from CSV
@st.cache_data
def load_sales_data(uploaded_file):
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as error:
        st.error(f"Error loading CSV file: {error}")
        return None

    expected_columns = [
        "Order_ID",
        "Order_Date",
        "Year",
        "Month",
        "Product",
        "Category",
        "Region",
        "Sales",
        "Quantity",
        "Order_Type",
    ]

    if len(df.columns) == 1:
        combined = df.columns[0]
        if combined.replace(" ", "") == "Order_IDOrder_DateYearMonthProductCategoryRegionSalesQuantityOrder_Type":
            df.columns = expected_columns

    for col in expected_columns:
        if col not in df.columns:
            df[col] = np.nan

    df["Sales"] = pd.to_numeric(df["Sales"], errors="coerce")
    df["Quantity"] = pd.to_numeric(df["Quantity"], errors="coerce")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")

    df["Year"] = pd.to_numeric(df["Year"], errors="coerce")
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
    df.loc[df["Year"].isna() & df["Order_Date"].notna(), "Year"] = df["Order_Date"].dt.year
    df.loc[df["Month"].isna() & df["Order_Date"].notna(), "Month"] = df["Order_Date"].dt.month

    df["Order_ID"] = df["Order_ID"].astype(str).str.strip()
    df["Order_Type"] = df["Order_Type"].fillna("Unknown")

    df["Month"] = df["Month"].astype("Int64")
    df["Year"] = df["Year"].astype("Int64")

    df = df.dropna(subset=["Order_ID", "Sales", "Quantity"])
    df = df.drop_duplicates()
    return df

# KPI calculation functions
@st.cache_data
def calculate_kpis(df):
    total_revenue = df["Sales"].sum()
    total_orders = df["Order_ID"].nunique()
    total_quantity = df["Quantity"].sum()
    average_sales = total_revenue / total_orders if total_orders > 0 else 0
    return total_revenue, total_orders, total_quantity, average_sales

@st.cache_data
def data_health(df):
    missing_pct = round(df.isna().mean().mean() * 100, 1)
    duplicate_orders = int(df.duplicated(subset=["Order_ID"]).sum())
    unique_products = int(df["Product"].nunique(dropna=True))
    return missing_pct, duplicate_orders, unique_products

@st.cache_data
def aggregate_sales(df):
    sales_by_year = df.groupby("Year")["Sales"].sum().sort_index()
    sales_by_month = df.groupby("Month")["Sales"].sum().reindex(range(1, 13), fill_value=0)
    top_products = df.groupby("Product")["Sales"].sum().nlargest(10)
    order_type_counts = df["Order_Type"].fillna("Unknown").value_counts()
    category_sales = df.groupby("Category")["Sales"].sum().sort_values(ascending=False)
    region_sales = df.groupby("Region")["Sales"].sum().sort_values(ascending=False)
    return sales_by_year, sales_by_month, top_products, order_type_counts, category_sales, region_sales

# Plot functions
def plot_yearly_sales(sales_by_year):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(sales_by_year.index.astype(str), sales_by_year.values, color="#2f54eb")
    ax.set_title("Year-wise Sales")
    ax.set_xlabel("Year")
    ax.set_ylabel("Revenue")
    ax.grid(alpha=0.2)
    return fig

def plot_monthly_trend(sales_by_month):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(sales_by_month.index, sales_by_month.values, marker="o", color="#ff6b6b")
    ax.set_title("Monthly Sales Trend")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    ax.set_xticks(range(1, 13))
    ax.grid(alpha=0.2)
    return fig

def plot_order_type(order_type_counts):
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(order_type_counts.values, labels=order_type_counts.index, autopct="%1.1f%%", startangle=140)
    ax.set_title("Online vs Offline Orders")
    return fig

def plot_quantity_vs_sales(df):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.scatter(df["Quantity"], df["Sales"], alpha=0.6, color="#1e90ff")
    ax.set_title("Quantity vs Sales")
    ax.set_xlabel("Quantity")
    ax.set_ylabel("Sales")
    ax.grid(alpha=0.2)
    return fig

def plot_top_products(top_products):
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top_products.index[::-1], top_products.values[::-1], color="#34c759")
    ax.set_title("Top 10 Selling Products")
    ax.set_xlabel("Revenue")
    plt.tight_layout()
    return fig

def plot_category_sales(category_sales):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(category_sales.index, category_sales.values, color="#ff9f1a")
    ax.set_title("Sales by Category")
    ax.set_xlabel("Category")
    ax.set_ylabel("Revenue")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig

def plot_region_sales(region_sales):
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(region_sales.index, region_sales.values, color="#ff4757")
    ax.set_title("Sales by Region")
    ax.set_xlabel("Region")
    ax.set_ylabel("Revenue")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    return fig

def plot_sales_forecast(df):
    df["InvoiceDate"] = pd.to_datetime(
        df["Year"].astype(int).astype(str) + "-" + df["Month"].astype(int).astype(str) + "-01",
        errors="coerce",
    )
    monthly_sales = df.dropna(subset=["InvoiceDate"]).groupby("InvoiceDate")["Sales"].sum().sort_index()
    x = np.arange(len(monthly_sales))
    y = monthly_sales.values

    if len(x) < 3:
        return None, None, None

    coefficients = np.polyfit(x, y, 1)
    trend = np.poly1d(coefficients)
    forecast_steps = 3
    forecast_x = np.arange(len(monthly_sales), len(monthly_sales) + forecast_steps)
    forecast_y = trend(forecast_x)
    future_dates = pd.date_range(monthly_sales.index.max() + pd.offsets.MonthBegin(1), periods=forecast_steps, freq="MS")

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_sales.index, y, marker="o", label="Historical Sales", color="#2f54eb")
    ax.plot(future_dates, forecast_y, marker="o", linestyle="--", label="Forecast", color="#ff9f1a")
    ax.set_title("Sales Forecast")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue")
    ax.legend()
    ax.grid(alpha=0.2)
    plt.tight_layout()
    forecast_df = pd.DataFrame({"Month": future_dates.strftime("%Y-%m"), "Forecasted Sales": forecast_y})
    return fig, forecast_df, coefficients

# Page title and description
st.title("Sales Data Analysis Dashboard")
st.markdown(
    "Use this professional sales dashboard to analyze sales performance with actionable KPIs, data quality insights, and interactive charts."
)

sample_data_path = os.path.join(os.path.dirname(__file__), "sample_sales_data.csv")

if "sales_data" not in st.session_state:
    st.session_state.sales_data = None
    st.session_state.data_source = None

uploaded_file = st.file_uploader("Upload Sales CSV file", type=["csv"])
load_sample = st.button("Load Sample Data")

if uploaded_file is not None:
    data = load_sales_data(uploaded_file)
    st.session_state.sales_data = data
    st.session_state.data_source = "Uploaded File"
elif load_sample:
    if os.path.exists(sample_data_path):
        data = load_sales_data(sample_data_path)
        st.session_state.sales_data = data
        st.session_state.data_source = "Sample Data"
    else:
        st.error(f"Sample data file not found at: {sample_data_path}")
        data = None
else:
    data = st.session_state.sales_data

if data is not None and not data.empty:
    data_source_text = st.session_state.data_source or "Loaded Data"
    st.success(f"{data_source_text} loaded successfully.")

    total_revenue, total_orders, total_quantity, average_sales = calculate_kpis(data)
    missing_pct, duplicate_orders, unique_products = data_health(data)
    sales_by_year, sales_by_month, top_products, order_type_counts, category_sales, region_sales = aggregate_sales(data)

    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col1.metric("Total Sales Revenue", f"₹{total_revenue:,.2f}")
    kpi_col2.metric("Total Orders", f"{total_orders:,}")
    kpi_col3.metric("Total Quantity Sold", f"{total_quantity:,}")
    kpi_col4.metric("Avg Sales / Order", f"₹{average_sales:,.2f}")

    health_col1, health_col2, health_col3 = st.columns(3)
    health_col1.metric("Data Completeness", f"{100 - missing_pct:.1f}%")
    health_col2.metric("Duplicate Orders", f"{duplicate_orders}")
    health_col3.metric("Unique Products", f"{unique_products}")

    with st.expander("Show Data Preview"):
        st.dataframe(data.head(10))

    if st.checkbox("Show sales charts", value=True):
        chart_tab1, chart_tab2 = st.tabs(["Summary", "Advanced"])

        with chart_tab1:
            st.subheader("Sales Trends")
            st.pyplot(plot_yearly_sales(sales_by_year))
            st.pyplot(plot_monthly_trend(sales_by_month))
            st.pyplot(plot_order_type(order_type_counts))

        with chart_tab2:
            st.subheader("Product and Regional Insights")
            st.pyplot(plot_top_products(top_products))
            st.pyplot(plot_category_sales(category_sales))
            st.pyplot(plot_region_sales(region_sales))

    if st.checkbox("Show sales forecast", value=True):
        forecast_chart, forecast_df, coefficients = plot_sales_forecast(data)
        if forecast_chart is not None:
            st.subheader("3-month Sales Forecast")
            st.pyplot(forecast_chart)
            st.dataframe(forecast_df)
            st.write(
                f"Forecast line slope: {coefficients[0]:.2f} (revenue trend per time step)"
            )
        else:
            st.warning("Not enough historical data for forecast. Provide at least 3 months of sales data.")
else:
    st.info("Upload a sales CSV file or load the sample data to start analysis.")
