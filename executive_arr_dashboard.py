"""
Executive ARR Dashboard - Single Page Design
Follows dashboard research: screenfit design, clear visual hierarchy, actionable insights

Installation:
pip install streamlit plotly pandas openpyxl

Usage:
streamlit run executive_arr_dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta

# Page configuration for executive viewing
st.set_page_config(
    page_title="ARR Executive Dashboard",
    page_icon="📊", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Executive-focused CSS
st.markdown("""
<style>
    /* Remove extra spacing */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    
    .header-title {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        text-align: center;
    }
    
    .header-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1rem;
        text-align: center;
        margin: 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
        height: 120px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    
    .metric-title {
        font-size: 0.75rem;
        color: #6b7280;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1f2937;
        margin-bottom: 0.25rem;
    }
    
    .metric-change {
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .positive { color: #059669; }
    .negative { color: #dc2626; }
    
    /* Chart containers */
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and prepare data"""
    try:
        excel_file = 'cleaned_arr_data/saas_arr_complete.xlsx'
        arr_summary_df = pd.read_excel(excel_file, sheet_name='ARR_Monthly_Summary')
        arr_rollforward_df = pd.read_excel(excel_file, sheet_name='ARR_Rollforward')
        subscriptions_df = pd.read_excel(excel_file, sheet_name='Subscriptions')
        
        # Convert dates
        arr_summary_df['month_date'] = pd.to_datetime(arr_summary_df['month_date'])
        
        return arr_summary_df, arr_rollforward_df, subscriptions_df
    except Exception as e:
        st.error(f"Data loading error: {e}")
        return None, None, None

def create_executive_metrics(arr_summary_df):
    """Create executive summary metrics"""
    latest = arr_summary_df.iloc[-1]
    previous = arr_summary_df.iloc[-2] if len(arr_summary_df) > 1 else latest
    
    # Calculate changes
    arr_change = latest['current_arr'] - previous['current_arr']
    customer_change = latest['active_customers'] - previous['active_customers']
    
    return {
        'current_arr': latest['current_arr'],
        'arr_change': arr_change,
        'arr_growth_rate': latest['arr_growth_rate'],
        'active_customers': latest['active_customers'],
        'customer_change': customer_change,
        'arr_per_customer': latest['arr_per_customer']
    }

def create_compact_waterfall(arr_rollforward_df):
    """Create compact, clear waterfall chart"""
    latest = arr_rollforward_df.iloc[-1]
    
    fig = go.Figure()
    
    # Create waterfall with clear labels
    categories = ['Starting<br>ARR', 'New<br>Customers', 'Expansions', 'Contractions', 'Churn', 'Ending<br>ARR']
    values = [
        latest['starting_arr'],
        latest['new_arr'],
        latest['expansion_arr'],
        latest['contraction_arr'],
        latest['churned_arr'],
        latest['ending_arr']
    ]
    
    measures = ["absolute", "relative", "relative", "relative", "relative", "total"]
    
    fig.add_trace(go.Waterfall(
        name="",
        orientation="v",
        measure=measures,
        x=categories,
        y=values,
        text=[f"${v:,.0f}" for v in values],
        textposition="outside",
        connector={"line":{"color":"#6b7280", "width": 2}},
        increasing={"marker":{"color":"#10b981"}},  # Clean green
        decreasing={"marker":{"color":"#ef4444"}},  # Clean red
        totals={"marker":{"color":"#3b82f6"}}       # Clean blue
    ))
    
    fig.update_layout(
        title=f"ARR Bridge - {latest['month']}",
        title_font_size=16,
        title_font_color="#374151",
        height=300,
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=11, color="#374151")
    )
    
    return fig

def create_compact_trend(arr_summary_df):
    """Create clean ARR trend chart"""
    # Last 12 months only
    recent_data = arr_summary_df.tail(12)
    
    fig = go.Figure()
    
    # ARR line with markers
    fig.add_trace(go.Scatter(
        x=recent_data['month_date'],
        y=recent_data['current_arr'],
        mode='lines+markers',
        name='ARR',
        line=dict(color='#3b82f6', width=3),
        marker=dict(size=6, color='#3b82f6'),
        fill='tonexty',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))
    
    fig.update_layout(
        title="12-Month ARR Trend",
        title_font_size=16,
        title_font_color="#374151",
        height=300,
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(showgrid=True, gridcolor='#f3f4f6'),
        yaxis=dict(showgrid=True, gridcolor='#f3f4f6', tickformat='$,.0f'),
        font=dict(size=11, color="#374151")
    )
    
    return fig

def create_customer_distribution(subscriptions_df):
    """Create simple customer segment chart"""
    active_subs = subscriptions_df[subscriptions_df['is_active'] == True]
    segment_data = active_subs.groupby('customer_segment').agg({
        'arr_amount': 'sum',
        'customer_id': 'count'
    }).reset_index()
    
    fig = px.bar(
        segment_data,
        x='customer_segment',
        y='arr_amount',
        title="ARR by Customer Segment",
        color='customer_segment',
        color_discrete_map={
            'SMB': '#93c5fd',
            'Mid-Market': '#3b82f6', 
            'Enterprise': '#1e40af',
            'Strategic': '#1e3a8a'
        }
    )
    
    # Add value labels on bars
    for i, row in segment_data.iterrows():
        fig.add_annotation(
            x=row['customer_segment'],
            y=row['arr_amount'],
            text=f"${row['arr_amount']:,.0f}",
            showarrow=False,
            yshift=10,
            font=dict(color="white", size=12, weight="bold")
        )
    
    fig.update_layout(
        height=300,
        margin=dict(l=50, r=50, t=50, b=50),
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_title="Customer Segment",
        yaxis_title="ARR ($)",
        yaxis=dict(tickformat='$,.0f'),
        title_font_size=16,
        title_font_color="#374151",
        font=dict(size=11, color="#374151")
    )
    
    return fig

def main():
    """Main executive dashboard - single page design"""
    
    # Load data
    arr_summary_df, arr_rollforward_df, subscriptions_df = load_data()
    
    if arr_summary_df is None:
        st.error("Please ensure your data files are available")
        st.stop()
    
    # Dashboard header
    st.markdown("""
    <div class="dashboard-header">
        <h1 class="header-title">📊 ARR Executive Dashboard</h1>
        <p class="header-subtitle">Monthly Recurring Revenue Performance & Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Get current metrics
    metrics = create_executive_metrics(arr_summary_df)
    
    # TOP ROW: Key Metrics (Executive Summary)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        change_color = "positive" if metrics['arr_change'] > 0 else "negative"
        change_symbol = "▲" if metrics['arr_change'] > 0 else "▼"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Current ARR</div>
            <div class="metric-value">${metrics['current_arr']:,.0f}</div>
            <div class="metric-change {change_color}">{change_symbol} ${abs(metrics['arr_change']):,.0f}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        cust_color = "positive" if metrics['customer_change'] >= 0 else "negative"
        cust_symbol = "▲" if metrics['customer_change'] >= 0 else "▼"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Customers</div>
            <div class="metric-value">{metrics['active_customers']:,}</div>
            <div class="metric-change {cust_color}">{cust_symbol} {abs(metrics['customer_change'])}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">ARR per Customer</div>
            <div class="metric-value">${metrics['arr_per_customer']:,.0f}</div>
            <div class="metric-change">Average</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        growth_color = "positive" if metrics['arr_growth_rate'] > 0 else "negative"
        growth_symbol = "▲" if metrics['arr_growth_rate'] > 0 else "▼"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Monthly Growth</div>
            <div class="metric-value">{metrics['arr_growth_rate']:.1f}%</div>
            <div class="metric-change {growth_color}">{growth_symbol} Growth Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    # MIDDLE ROW: Core Analysis Charts
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1.5, 1.5, 1])
    
    with col1:
        # ARR Waterfall
        waterfall_fig = create_compact_waterfall(arr_rollforward_df)
        st.plotly_chart(waterfall_fig, use_container_width=True, config={'displayModeBar': False})
    
    with col2:
        # ARR Trend
        trend_fig = create_compact_trend(arr_summary_df)
        st.plotly_chart(trend_fig, use_container_width=True, config={'displayModeBar': False})
    
    with col3:
        # Customer segments
        segment_fig = create_customer_distribution(subscriptions_df)
        st.plotly_chart(segment_fig, use_container_width=True, config={'displayModeBar': False})
    
    # BOTTOM ROW: Quick Insights Table
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Executive summary table - last 6 months only
    recent_summary = arr_summary_df.tail(6).copy()
    recent_summary['Month'] = recent_summary['month_date'].dt.strftime('%b %Y')
    
    summary_table = recent_summary[['Month', 'current_arr', 'arr_growth_rate', 'active_customers']].copy()
    summary_table['current_arr'] = summary_table['current_arr'].apply(lambda x: f"${x:,.0f}")
    summary_table['arr_growth_rate'] = summary_table['arr_growth_rate'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
    summary_table.columns = ['Month', 'ARR', 'Growth %', 'Customers']
    
    # Display table with better formatting
    st.markdown("#### 📅 Recent Performance Summary")
    st.dataframe(
        summary_table,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Month": st.column_config.TextColumn("Month", width="small"),
            "ARR": st.column_config.TextColumn("ARR", width="medium"),
            "Growth %": st.column_config.TextColumn("Growth %", width="small"),
            "Customers": st.column_config.NumberColumn("Customers", width="small")
        }
    )
    
    # Footer with key takeaways
    latest_month = arr_summary_df.iloc[-1]
    
    # Generate executive insights
    if latest_month['arr_growth_rate'] > 5:
        trend_message = "🟢 **Strong Growth**: ARR is accelerating"
    elif latest_month['arr_growth_rate'] > 0:
        trend_message = "🟡 **Steady Growth**: ARR trending upward"
    else:
        trend_message = "🔴 **Growth Challenge**: ARR declining"
    
    # Bottom insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Key Takeaways")
        st.markdown(f"• {trend_message}")
        st.markdown(f"• **Current ARR**: ${latest_month['current_arr']:,.0f} ({latest_month['active_customers']:,} customers)")
        st.markdown(f"• **Average per Customer**: ${latest_month['arr_per_customer']:,.0f}")
    
    with col2:
        st.markdown("#### 📊 Action Items")
        if latest_month['arr_growth_rate'] < 2:
            st.markdown("• **Focus on churn reduction**")
            st.markdown("• **Increase expansion revenue**")
        else:
            st.markdown("• **Maintain growth momentum**")
            st.markdown("• **Scale customer acquisition**")
        st.markdown("• **Monitor customer segments**")

# Additional functions for enhanced charts
def create_arr_kpi_summary(arr_summary_df):
    """Create a comprehensive KPI summary"""
    latest = arr_summary_df.iloc[-1]
    
    # Last 12 months metrics
    last_12_months = arr_summary_df.tail(12)
    avg_growth = last_12_months['arr_growth_rate'].mean()
    
    return {
        'current_arr': latest['current_arr'],
        'monthly_growth': latest['arr_growth_rate'], 
        'avg_12m_growth': avg_growth,
        'customers': latest['active_customers'],
        'arr_per_customer': latest['arr_per_customer']
    }

if __name__ == "__main__":
    main()
