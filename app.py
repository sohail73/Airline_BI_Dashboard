import streamlit as st
import pandas as pd
import plotly.express as px
from database import DB

# Page Configuration
st.set_page_config(page_title="SkyBI: Airline Analytics", page_icon="✈", layout="wide")

# Database Connection Initialization
@st.cache_resource
def get_db_connection():
    return DB()

db = get_db_connection()

st.title("✈SkyBI: Commercial Airline Intelligence System")
st.markdown("---")

# Sidebar Controls
st.sidebar.header("Filter Controls")

cities = db.fetch_city_names()
selected_source = st.sidebar.selectbox("Source City", options=["All"] + cities)

# Destination smart filter
dest_options = [c for c in cities if c != selected_source] if selected_source != "All" else cities
selected_dest = st.sidebar.selectbox("Destination City", options=["All"] + dest_options)

selected_class = st.sidebar.radio("Travel Class", options=["All", "Economy", "Business"])

# Fetch Data based on Filters
df = db.fetch_filtered_flights(selected_source, selected_dest, selected_class)

if df.empty:
    st.warning("Constraints ke mutabik koi data mil nahi raha.")
    st.stop()

# Tabs Setup
tab1, tab2 = st.tabs(["Business Analyst Insights", "Product Manager Strategy"])

# TAB 1: BUSINESS ANALYST

with tab1:
    st.subheader("Financial Performance & Competitor Landscape")

    c1, c2, c3 = st.columns(3)
    c1.metric("Total Active Routes", f"{len(df):,}")
    c2.metric("Average Ticket Fare", f"₹{df['price'].mean():,.2f}")
    c3.metric("Highest Fare Observed", f"₹{df['price'].max():,}")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("##### Market Share by Airline Volume")
        df_freq = db.fetch_airline_frequency()
        fig_pie = px.pie(df_freq, values='Count', names='airline', hole=0.4,
                         color_discrete_sequence=px.colors.qualitative.Safe)
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.markdown("##### Competitor Price Distribution")
        fig_box = px.box(df, x='airline', y='price', color='airline',
                         color_discrete_sequence=px.colors.qualitative.Safe)
        fig_box.update_layout(showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

# TAB 2: PRODUCT MANAGER
with tab2:
    st.subheader("Customer Behavior & Advance Booking Patterns")

    col3, col4 = st.columns(2)

    with col3:
        st.markdown("##### Dynamic Pricing Curve (Price vs Days Left)")
        df_days = db.fetch_price_vs_days_left()
        fig_line = px.line(df_days, x='days_left', y='avg_price',
                           labels={'days_left': 'Days Left Before Flight', 'avg_price': 'Average Fare (INR)'})
        fig_line.update_traces(line_color='#EF4444', line_width=3)
        fig_line.update_xaxes(autorange="reversed")
        st.plotly_chart(fig_line, use_container_width=True)

    with col4:
        st.markdown("##### Layover Stops Impact on Fares")
        df_stops = db.fetch_stops_pricing()
        fig_bar = px.bar(df_stops, x='stops', y='avg_price', color='stops', text_auto='.2s')
        fig_bar.update_layout(showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)

# RAW DATA HUB
st.markdown("---")
with st.expander("Executive Data Export & Preview"):
    st.dataframe(df.head(100), use_container_width=True)

    csv_data = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Filtered Data (.CSV)",
        data=csv_data,
        file_name="SkyBI_Filtered_Report.csv",
        mime="text/csv"
    )