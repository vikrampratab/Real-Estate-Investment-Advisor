import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="India Property Analytics", layout="wide", page_icon="🏢")

# 2. Optimized Data Loading & Analytics Logic
@st.cache_data
def load_and_analyze():
    path = r"C:\Users\Vikas\Desktop\Real Estate Investment Advisor Predicting Property Profitability & Future Value\india_housing_prices .csv"
    
    try:
        # Optimization: Only load necessary columns to save RAM and time
        needed_cols = ['City', 'Price_in_Lakhs', 'Nearby_Schools', 'Nearby_Hospitals', 'Locality', 'BHK', 'Size_in_SqFt']
        df = pd.read_csv(path, usecols=needed_cols)
    except FileNotFoundError:
        st.error("CSV File nahi mili! Path check karein.")
        st.stop()

    # Feature Engineering (Fast calculations)
    df['Infrastructure_Score'] = df['Nearby_Schools'] + df['Nearby_Hospitals']
    
    # Investment Logic
    city_avg = df.groupby('City')['Price_in_Lakhs'].transform('mean')
    df['Is_Value_Buy'] = (df['Price_in_Lakhs'] < city_avg) & (df['Infrastructure_Score'] >= 12)
    
    return df

# Start Loading
with st.spinner('Analyzing 2.5 Lakh properties...'):
    df = load_and_analyze()

# 3. Sidebar Filters (Full Digits & Word Labels)
st.sidebar.header("🔍 Market Explorer")

all_cities = sorted(df['City'].unique())
selected_city = st.sidebar.selectbox("Select City", all_cities)

# Filter city data once for performance
city_df = df[df['City'] == selected_city].copy()

# Dynamic Slider Range based on City
city_min_lakh = int(city_df['Price_in_Lakhs'].min())
city_max_lakh = int(city_df['Price_in_Lakhs'].max())

if city_min_lakh == city_max_lakh:
    city_max_lakh = city_min_lakh + 10

# Budget Slider with Full Values
budget_range = st.sidebar.slider(
    "Select Your Budget", 
    min_value=city_min_lakh * 100000, 
    max_value=city_max_lakh * 100000, 
    value=(city_min_lakh * 100000, city_max_lakh * 100000),
    step=500000,
    format="₹ %d"
)

# Filtering data
budget_min_lakh = budget_range[0] / 100000
budget_max_lakh = budget_range[1] / 100000
filtered_df = city_df[(city_df['Price_in_Lakhs'] >= budget_min_lakh) & (city_df['Price_in_Lakhs'] <= budget_max_lakh)]

# Word label for Sidebar
def get_label(val_lakh):
    if val_lakh >= 100: return f"{val_lakh/100:.2f} Cr"
    return f"{val_lakh:.0f} Lakh"

st.sidebar.info(f"Selected Range: {get_label(budget_min_lakh)} to {get_label(budget_max_lakh)}")

# 4. Main Dashboard UI
st.title("🏡 Indian Real Estate Decision Engine")
st.markdown(f"Currently analyzing **{selected_city}** market with Rule-based Financial Logic.")

# Helper for Metrics
def format_indian_currency(num_lakhs):
    num = round(num_lakhs * 100000)
    if num >= 10000000:
        return f"{num / 10000000:.2f} Crore"
    return f"{num / 100000:.2f} Lakh"

m1, m2, m3 = st.columns(3)

# Metric 1: Average Price
avg_price_lakhs = city_df['Price_in_Lakhs'].mean()
m1.metric("Avg Price in City", f"₹ {int(avg_price_lakhs * 100000):,}")
m1.caption(f"({format_indian_currency(avg_price_lakhs)})")

# Metric 2: Count
m2.metric("Properties in Budget", len(filtered_df))

# Metric 3: Value Buys
val_buy_count = filtered_df['Is_Value_Buy'].sum()
m3.metric("Value Buy Opportunities", val_buy_count)

st.divider()

# 5. Property Evaluator Tool
col1, col2 = st.columns([1, 1.2])

with col1:
    st.subheader("💡 Property Evaluator")
    current_val = st.number_input("Listing Price (Lakhs)", min_value=1.0, value=75.0)
    property_sqft = st.number_input("Area (SqFt)", min_value=100, value=1200)
    infra_input = st.slider("Infrastructure Score", 0, 20, 10)
    growth_rate = st.selectbox("Market Growth Rate (%)", [5, 7, 10, 12], index=1)
    
    analyze_btn = st.button("Generate Investment Report", use_container_width=True)

with col2:
    st.subheader("📈 Projection Results")
    if analyze_btn:
        future_val = current_val * ((1 + growth_rate/100) ** 5)
        
        if infra_input >= 12 and growth_rate >= 7:
            status, color = "🟢 RECOMMENDED", "green"
        elif infra_input >= 8:
            status, color = "🟡 STABLE INVESTMENT", "orange"
        else:
            status, color = "🔴 HIGH RISK", "red"
            
        st.markdown(f"### Verdict: :{color}[{status}]")
        
        res1, res2 = st.columns(2)
        res1.metric("Value in 5 Years", f"₹ {future_val:.2f} L", delta=f"{growth_rate}%")
        res2.metric("Price/SqFt Now", f"₹ {(current_val*100000)/property_sqft:.0f}")
        
        chart_df = pd.DataFrame({'Timeline': ['Current', 'In 5 Years'], 'Value': [current_val, future_val]})
        fig = px.bar(chart_df, x='Timeline', y='Value', color='Timeline', text_auto='.2f')
        st.plotly_chart(fig, use_container_width=True)

# 6. Market Insights Charts
st.divider()
st.subheader("📊 Market Trends & Insights")
t1, t2 = st.tabs(["Price Distribution", "Infra vs Price"])

with t1:
    fig1 = px.histogram(city_df, x="Price_in_Lakhs", nbins=50, title=f"Price Spread in {selected_city}")
    st.plotly_chart(fig1, use_container_width=True)

with t2:
    # Sampling for chart speed
    sample_size = min(2000, len(city_df))
    fig2 = px.scatter(city_df.sample(sample_size), 
                      x="Infrastructure_Score", 
                      y="Price_in_Lakhs", 
                      color="Is_Value_Buy",
                      hover_data=['Locality', 'BHK'],
                      title="Infrastructure vs Market Price")
    st.plotly_chart(fig2, use_container_width=True)