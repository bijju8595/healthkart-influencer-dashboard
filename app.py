import streamlit as st
import pandas as pd
import numpy as np

# --- Page Configuration ---
st.set_page_config(
    page_title="HealthKart Influencer Dashboard",
    
    layout="wide"
)

# --- Title ---
st.title("🚀 HealthKart Influencer Campaign Dashboard")
st.markdown("Track and visualize the ROI of influencer marketing campaigns.")

# --- Data Loading ---
@st.cache_data
def load_data():
    influencers = pd.read_csv('influencers.csv')
    tracking = pd.read_csv('tracking_data.csv')
    payouts = pd.read_csv('payouts.csv')
    posts = pd.read_csv('posts.csv')
    tracking['date'] = pd.to_datetime(tracking['date'])
    return influencers, tracking, payouts, posts

influencers, tracking, payouts, posts = load_data()


# --- Data Transformation & Metrics Calculation ---
# Aggregate revenue per influencer
influencer_revenue = tracking.groupby('influencer_id').agg(
    total_revenue=('revenue', 'sum'),
    total_orders=('orders', 'sum')
).reset_index()

# Merge dataframes to create a master performance view
performance_df = pd.merge(influencers, payouts, on='influencer_id', how='left')
performance_df = pd.merge(performance_df, influencer_revenue, on='influencer_id', how='left')

# Fill NaNs for influencers with no revenue/payouts
performance_df.fillna(0, inplace=True)

# Calculate ROAS (Return on Ad Spend)
# Assumption: The revenue in tracking_data is purely incremental. ROAS is therefore Incremental ROAS.
performance_df['roas'] = performance_df.apply(
    lambda row: row['total_revenue'] / row['total_payout'] if row['total_payout'] > 0 else 0,
    axis=1
)
performance_df['roas'] = performance_df['roas'].round(2)


# --- Sidebar Filters ---
st.sidebar.header("Filter Options")

# Campaign (Brand) Filter
campaigns = ['All'] + list(tracking['campaign'].unique())
selected_campaign = st.sidebar.selectbox("Select Campaign/Brand", campaigns)

# Platform Filter
platforms = ['All'] + list(influencers['platform'].unique())
selected_platform = st.sidebar.selectbox("Select Platform", platforms)

# Influencer Category Filter
categories = ['All'] + list(influencers['category'].unique())
selected_category = st.sidebar.selectbox("Select Influencer Category", categories)


# --- Filtering Logic ---
# Start with a copy of the main performance dataframe
filtered_performance = performance_df.copy()

# Apply Campaign/Brand filter
if selected_campaign != 'All':
    # Find which influencers were part of the selected campaign
    influencer_ids_in_campaign = tracking[tracking['campaign'] == selected_campaign]['influencer_id'].unique()
    # Filter the main dataframe to only include those influencers
    filtered_performance = filtered_performance[filtered_performance['influencer_id'].isin(influencer_ids_in_campaign)]

# Apply Platform filter
if selected_platform != 'All':
    filtered_performance = filtered_performance[filtered_performance['platform'] == selected_platform]

# Apply Influencer Category filter
if selected_category != 'All':
    filtered_performance = filtered_performance[filtered_performance['category'] == selected_category]


# --- Main Dashboard ---

# Key Performance Indicators (KPIs)
total_spend = filtered_performance['total_payout'].sum()
total_revenue = filtered_performance['total_revenue'].sum()
total_roas = total_revenue / total_spend if total_spend > 0 else 0

st.markdown("### Key Performance Indicators")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric(label="Total Spend (Payouts)", value=f"₹{total_spend:,.0f}")
kpi2.metric(label="Total Revenue", value=f"₹{total_revenue:,.0f}")
kpi3.metric(label="Overall Incremental ROAS", value=f"{total_roas:.2f}x")
kpi4.metric(label="Total Influencers", value=filtered_performance.shape[0])

st.markdown("<hr>", unsafe_allow_html=True)

# --- Visualizations & Insights ---
st.markdown("### Performance Analysis")
col1, col2 = st.columns((2, 1))

with col1:
    st.markdown("#### Top 10 Influencers by ROAS")
    top_roas = filtered_performance.sort_values('roas', ascending=False).head(10)
    st.dataframe(top_roas[['name', 'category', 'platform', 'total_revenue', 'total_payout', 'roas']], use_container_width=True)

with col2:
    st.markdown("#### Revenue by Platform")
    platform_revenue = filtered_performance.groupby('platform')['total_revenue'].sum()
    st.bar_chart(platform_revenue)

col3, col4 = st.columns((1, 1))
with col3:
    st.markdown("#### Revenue by Influencer Category")
    category_revenue = filtered_performance.groupby('category')['total_revenue'].sum()
    st.bar_chart(category_revenue)

with col4:
    st.markdown("#### Payout Basis Distribution")
    payout_basis = filtered_performance['basis'].value_counts()
    st.bar_chart(payout_basis)
    
st.markdown("<hr>", unsafe_allow_html=True)

# Detailed Influencer Performance Table
st.markdown("### All Influencer Data")
st.dataframe(filtered_performance)
