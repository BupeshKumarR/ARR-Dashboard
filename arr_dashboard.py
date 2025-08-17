"""
Professional SaaS ARR Dashboard
Streamlit application for interactive ARR analysis and communication

Installation:
pip install streamlit plotly pandas openpyxl

Usage:
streamlit run arr_dashboard.py

This creates a shareable web dashboard perfect for presentations and analysis.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os

# Page configuration
st.set_page_config(
    page_title="SaaS ARR Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional, readable styling
st.markdown("""
<style>
    /* Light, professional background */
    .main {
        background-color: #f8fafc;
    }
    
    /* Clean header styling */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e293b;
        text-align: center;
        margin-bottom: 1.5rem;
        padding: 1rem;
        background: linear-gradient(135deg, #1e40af, #3b82f6);
        color: white;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Metric cards with light background and clear borders */
    .metric-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        border: 2px solid #e2e8f0;
        margin-bottom: 1rem;
        transition: all 0.2s ease;
    }
    
    .metric-container:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border-color: #3b82f6;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #1e293b;
        line-height: 1;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.875rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    
    .metric-change {
        font-size: 0.875rem;
        font-weight: 600;
        padding: 0.25rem 0.5rem;
        border-radius: 6px;
        display: inline-block;
    }
    
    .positive-change {
        background-color: #dcfce7;
        color: #166534;
        border: 1px solid #bbf7d0;
    }
    
    .negative-change {
        background-color: #fef2f2;
        color: #dc2626;
        border: 1px solid #fecaca;
    }
    
    .neutral-change {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
    }
    
    /* Section headers with clear visual separation */
    .section-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e293b;
        margin: 2rem 0 1rem 0;
        padding: 1rem 0;
        border-bottom: 3px solid #3b82f6;
        position: relative;
    }
    
    .section-header::after {
        content: '';
        position: absolute;
        bottom: -3px;
        left: 0;
        width: 60px;
        height: 3px;
        background: #1e40af;
    }
    
    /* Chart containers with light backgrounds */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
        margin-bottom: 1.5rem;
    }
    
    /* Data table styling */
    .data-table {
        background: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    
    /* Insight boxes */
    .insight-box {
        background: linear-gradient(135deg, #f8fafc, #e2e8f0);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    
    .insight-title {
        font-weight: 600;
        color: #1e293b;
        margin-bottom: 0.5rem;
    }
    
    .insight-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_arr_data():
    """Load the processed ARR data"""
    try:
        # Load all sheets from the Excel file
        excel_file = 'cleaned_arr_data/saas_arr_complete.xlsx'
        
        customers_df = pd.read_excel(excel_file, sheet_name='Customers')
        subscriptions_df = pd.read_excel(excel_file, sheet_name='Subscriptions')
        transactions_df = pd.read_excel(excel_file, sheet_name='Transactions')
        arr_summary_df = pd.read_excel(excel_file, sheet_name='ARR_Monthly_Summary')
        arr_rollforward_df = pd.read_excel(excel_file, sheet_name='ARR_Rollforward')
        
        # Convert date columns
        arr_summary_df['month_date'] = pd.to_datetime(arr_summary_df['month_date'])
        customers_df['signup_date'] = pd.to_datetime(customers_df['signup_date'])
        subscriptions_df['start_date'] = pd.to_datetime(subscriptions_df['start_date'])
        subscriptions_df['end_date'] = pd.to_datetime(subscriptions_df['end_date'])
        transactions_df['transaction_date'] = pd.to_datetime(transactions_df['transaction_date'])
        
        return customers_df, subscriptions_df, transactions_df, arr_summary_df, arr_rollforward_df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Make sure 'cleaned_arr_data/saas_arr_complete.xlsx' exists in your directory")
        return None, None, None, None, None

def create_metric_card(title, value, change=None, format_type="currency", change_label=""):
    """Create a professional, readable metric card"""
    if format_type == "currency":
        formatted_value = f"${value:,.0f}" if value else "$0"
    elif format_type == "number":
        formatted_value = f"{value:,.0f}" if value else "0"
    elif format_type == "percentage":
        formatted_value = f"{value:.1f}%" if value else "0.0%"
    else:
        formatted_value = str(value)
    
    change_html = ""
    if change is not None:
        if change > 0:
            change_class = "positive-change"
            change_symbol = "▲"
        elif change < 0:
            change_class = "negative-change"
            change_symbol = "▼"
        else:
            change_class = "neutral-change"
            change_symbol = "●"
        
        if format_type == "currency":
            change_text = f"{change_symbol} ${abs(change):,.0f}"
        elif format_type == "percentage":
            change_text = f"{change_symbol} {abs(change):.1f}%"
        else:
            change_text = f"{change_symbol} {abs(change):,.0f}"
        
        if change_label:
            change_text += f" {change_label}"
        
        change_html = f'<div class="metric-change {change_class}">{change_text}</div>'
    
    card_html = f"""
    <div class="metric-container">
        <div class="metric-label">{title}</div>
        <div class="metric-value">{formatted_value}</div>
        {change_html}
    </div>
    """
    return card_html

def create_arr_waterfall_chart(arr_rollforward_df):
    """Create ARR waterfall chart - one question: How did ARR change this month?"""
    latest_month = arr_rollforward_df.iloc[-1]
    
    fig = go.Figure(go.Waterfall(
        name="ARR Changes",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "total"],
        x=["Starting ARR", "New ARR", "Expansion", "Contraction", "Churn", "Ending ARR"],
        y=[
            latest_month['starting_arr'],
            latest_month['new_arr'],
            latest_month['expansion_arr'], 
            latest_month['contraction_arr'],
            latest_month['churned_arr'],
            latest_month['ending_arr']
        ],
        text=[
            f"${latest_month['starting_arr']:,.0f}",
            f"${latest_month['new_arr']:,.0f}",
            f"${latest_month['expansion_arr']:,.0f}",
            f"${abs(latest_month['contraction_arr']):,.0f}",
            f"${abs(latest_month['churned_arr']):,.0f}",
            f"${latest_month['ending_arr']:,.0f}"
        ],
        textposition="outside",
        connector={"line":{"color":"#64748b", "width":2}},
        increasing={"marker":{"color":"#059669"}},
        decreasing={"marker":{"color":"#dc2626"}},
        totals={"marker":{"color":"#3b82f6"}}
    ))
    
    fig.update_layout(
        title=f"ARR Rollforward - {latest_month['month']}",
        title_font_size=18,
        title_font_color="#1e293b",
        height=450,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12, color="#374151"),
        xaxis=dict(
            showgrid=False,
            zeroline=False,
            tickfont=dict(size=11)
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='#e2e8f0',
            zeroline=False,
            tickfont=dict(size=11)
        )
    )
    
    return fig

def create_arr_trend_chart(arr_summary_df):
    """Create ARR growth trend chart - one question: How is ARR growing over time?"""
    fig = go.Figure()
    
    # ARR trend line with area fill
    fig.add_trace(go.Scatter(
        x=arr_summary_df['month_date'],
        y=arr_summary_df['current_arr'],
        mode='lines+markers',
        name='ARR',
        line=dict(color='#3b82f6', width=4),
        marker=dict(size=6, color='#3b82f6'),
        fill='tonexty',
        fillcolor='rgba(59, 130, 246, 0.1)'
    ))
    
    fig.update_layout(
        title="ARR Growth Trajectory",
        title_font_size=18,
        title_font_color="#1e293b",
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12, color="#374151"),
        xaxis=dict(
            title="Month",
            showgrid=True,
            gridcolor='#e2e8f0',
            zeroline=False
        ),
        yaxis=dict(
            title="ARR ($)",
            showgrid=True,
            gridcolor='#e2e8f0',
            zeroline=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_growth_rate_chart(arr_summary_df):
    """Create growth rate chart - one question: What's our monthly growth rate?"""
    fig = go.Figure()
    
    # Growth rate bars
    colors = ['#059669' if x > 0 else '#dc2626' for x in arr_summary_df['arr_growth_rate']]
    
    fig.add_trace(go.Bar(
        x=arr_summary_df['month_date'],
        y=arr_summary_df['arr_growth_rate'],
        name='Growth Rate',
        marker_color=colors,
        opacity=0.8
    ))
    
    # Add zero line
    fig.add_hline(y=0, line_dash="dash", line_color="#64748b", line_width=1)
    
    fig.update_layout(
        title="Monthly ARR Growth Rate",
        title_font_size=18,
        title_font_color="#1e293b",
        height=350,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12, color="#374151"),
        xaxis=dict(
            title="Month",
            showgrid=True,
            gridcolor='#e2e8f0',
            zeroline=False
        ),
        yaxis=dict(
            title="Growth Rate (%)",
            showgrid=True,
            gridcolor='#e2e8f0',
            zeroline=False
        ),
        showlegend=False
    )
    
    return fig

def create_customer_segmentation_chart(subscriptions_df):
    """Create customer segmentation chart - one question: How is ARR distributed across segments?"""
    # Calculate ARR by segment
    segment_data = subscriptions_df[subscriptions_df['is_active'] == True].groupby('customer_segment').agg({
        'arr_amount': 'sum',
        'customer_id': 'count'
    }).reset_index()
    
    segment_data.columns = ['Segment', 'ARR', 'Customers']
    
    # Create horizontal bar chart for better readability
    fig = go.Figure(go.Bar(
        x=segment_data['ARR'],
        y=segment_data['Segment'],
        orientation='h',
        marker_color=['#3b82f6', '#059669', '#f59e0b', '#dc2626'],
        text=[f"${x:,.0f}" for x in segment_data['ARR']],
        textposition='auto',
        textfont=dict(size=11, color='white')
    ))
    
    fig.update_layout(
        title="ARR by Customer Segment",
        title_font_size=18,
        title_font_color="#1e293b",
        height=300,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12, color="#374151"),
        xaxis=dict(
            title="ARR ($)",
            showgrid=True,
            gridcolor='#e2e8f0',
            zeroline=False
        ),
        yaxis=dict(
            showgrid=False,
            zeroline=False
        ),
        showlegend=False
    )
    
    return fig

def create_arr_components_chart(arr_summary_df):
    """Create ARR components chart - one question: What drives our ARR changes?"""
    # Get last 12 months
    recent_data = arr_summary_df.tail(12).copy()
    
    fig = go.Figure()
    
    # Stacked area chart for ARR components
    fig.add_trace(go.Scatter(
        x=recent_data['month_date'],
        y=recent_data['new_arr'],
        mode='lines',
        name='New ARR',
        stackgroup='one',
        fill='tonexty',
        line=dict(color='#059669', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=recent_data['month_date'],
        y=recent_data['expansion_arr'],
        mode='lines',
        name='Expansion ARR',
        stackgroup='one',
        fill='tonexty',
        line=dict(color='#3b82f6', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=recent_data['month_date'],
        y=recent_data['contraction_arr'],
        mode='lines',
        name='Contraction ARR',
        stackgroup='one',
        fill='tonexty',
        line=dict(color='#f59e0b', width=2)
    ))
    
    fig.add_trace(go.Scatter(
        x=recent_data['month_date'],
        y=recent_data['churned_arr'],
        mode='lines',
        name='Churned ARR',
        stackgroup='one',
        fill='tonexty',
        line=dict(color='#dc2626', width=2)
    ))
    
    fig.update_layout(
        title="ARR Components Over Time",
        title_font_size=18,
        title_font_color="#1e293b",
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12, color="#374151"),
        xaxis=dict(
            title="Month",
            showgrid=True,
            gridcolor='#e2e8f0',
            zeroline=False
        ),
        yaxis=dict(
            title="ARR ($)",
            showgrid=True,
            gridcolor='#e2e8f0',
            zeroline=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def main():
    """Main dashboard application following best practices"""
    
    # Load data
    customers_df, subscriptions_df, transactions_df, arr_summary_df, arr_rollforward_df = load_arr_data()
    
    if customers_df is None:
        st.stop()
    
    # Dashboard header
    st.markdown('<h1 class="main-header">📊 SaaS ARR Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #64748b; font-size: 1.1rem; margin-bottom: 2rem;">Executive Summary & Financial Performance Analysis</p>', unsafe_allow_html=True)
    
    # Get latest metrics
    latest_month = arr_summary_df.iloc[-1]
    previous_month = arr_summary_df.iloc[-2] if len(arr_summary_df) > 1 else latest_month
    
    # Calculate changes
    arr_change = latest_month['current_arr'] - previous_month['current_arr']
    customer_change = latest_month['active_customers'] - previous_month['active_customers']
    
    # Key Metrics Row (Hero Section) - Following research: single values at top
    st.markdown('<div class="section-header">📈 Executive Summary</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
    
    with col1:
        st.markdown(create_metric_card(
            "Current ARR", 
            latest_month['current_arr'], 
            arr_change, 
            "currency",
            "vs last month"
        ), unsafe_allow_html=True)
    
    with col2:
        st.markdown(create_metric_card(
            "Active Customers", 
            latest_month['active_customers'], 
            customer_change, 
            "number",
            "vs last month"
        ), unsafe_allow_html=True)
    
    with col3:
        st.markdown(create_metric_card(
            "ARR per Customer", 
            latest_month['arr_per_customer'], 
            None, 
            "currency"
        ), unsafe_allow_html=True)
    
    with col4:
        st.markdown(create_metric_card(
            "Monthly Growth", 
            latest_month['arr_growth_rate'], 
            None, 
            "percentage"
        ), unsafe_allow_html=True)
    
    # ARR Growth Analysis - Progressive disclosure pattern
    st.markdown('<div class="section-header">📊 ARR Growth Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        trend_fig = create_arr_trend_chart(arr_summary_df)
        st.plotly_chart(trend_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        seg_fig = create_customer_segmentation_chart(subscriptions_df)
        st.plotly_chart(seg_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ARR Rollforward Analysis - Waterfall chart for executive view
    st.markdown('<div class="section-header">🔄 ARR Rollforward Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        waterfall_fig = create_arr_waterfall_chart(arr_rollforward_df)
        st.plotly_chart(waterfall_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Key insights box
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.subheader("📊 Key Insights")
        
        latest_rollforward = arr_rollforward_df.iloc[-1]
        net_change = latest_rollforward['net_change']
        
        st.markdown(f'<div class="insight-title">Net ARR Change</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-value">${net_change:,.0f}</div>', unsafe_allow_html=True)
        
        if net_change > 0:
            st.success("🚀 Positive ARR growth this month")
        else:
            st.warning("⚠️ ARR declined this month")
        
        st.markdown("---")
        
        # ARR components summary
        components = [
            ("New ARR", latest_rollforward['new_arr'], "#059669"),
            ("Expansion", latest_rollforward['expansion_arr'], "#3b82f6"),
            ("Contraction", abs(latest_rollforward['contraction_arr']), "#f59e0b"),
            ("Churn", abs(latest_rollforward['churned_arr']), "#dc2626")
        ]
        
        for name, value, color in components:
            st.markdown(f'<div style="color: {color}; font-weight: 600;">{name}: ${value:,.0f}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Growth Rate Analysis - Separate chart for focused analysis
    st.markdown('<div class="section-header">📈 Growth Rate Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        growth_fig = create_growth_rate_chart(arr_summary_df)
        st.plotly_chart(growth_fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        # Growth insights
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.subheader("📊 Growth Insights")
        
        avg_growth = arr_summary_df['arr_growth_rate'].mean()
        recent_growth = arr_summary_df.tail(6)['arr_growth_rate'].mean()
        
        st.markdown(f'<div class="insight-title">Average Growth (All Time)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-value">{avg_growth:.1f}%</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="insight-title">Recent Growth (6 months)</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-value">{recent_growth:.1f}%</div>', unsafe_allow_html=True)
        
        if recent_growth > avg_growth:
            st.success("📈 Growth accelerating")
        elif recent_growth < avg_growth:
            st.warning("📉 Growth slowing")
        else:
            st.info("➡️ Growth stable")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ARR Components Over Time - Detailed analysis
    st.markdown('<div class="section-header">🔍 ARR Components Analysis</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    components_fig = create_arr_components_chart(arr_summary_df)
    st.plotly_chart(components_fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Monthly Performance Table - Detail on demand
    st.markdown('<div class="section-header">📅 Monthly Performance Details</div>', unsafe_allow_html=True)
    
    # Show last 12 months with expandable view
    with st.expander("📊 View Last 12 Months Performance", expanded=False):
        recent_data = arr_summary_df.tail(12).copy()
        recent_data['month_display'] = recent_data['month_date'].dt.strftime('%Y-%m')
        
        display_data = recent_data[[
            'month_display', 'current_arr', 'new_arr', 'expansion_arr', 
            'contraction_arr', 'churned_arr', 'arr_growth_rate', 'active_customers'
        ]].copy()
        
        # Format columns
        currency_cols = ['current_arr', 'new_arr', 'expansion_arr', 'contraction_arr', 'churned_arr']
        for col in currency_cols:
            display_data[col] = display_data[col].apply(lambda x: f"${x:,.0f}")
        
        display_data['arr_growth_rate'] = display_data['arr_growth_rate'].apply(lambda x: f"{x:.1f}%")
        
        # Rename columns for display
        display_data.columns = [
            'Month', 'Current ARR', 'New ARR', 'Expansion', 'Contraction', 
            'Churn', 'Growth Rate', 'Customers'
        ]
        
        st.markdown('<div class="data-table">', unsafe_allow_html=True)
        st.dataframe(display_data, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Interactive Analysis Section - Progressive disclosure
    st.markdown('<div class="section-header">🔍 Interactive Analysis</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Date range selector
        date_range = st.selectbox(
            "Select Analysis Period:",
            ["Last 6 months", "Last 12 months", "Last 24 months", "All time"],
            index=1
        )
        
        # Filter data based on selection
        if date_range == "Last 6 months":
            filtered_data = arr_summary_df.tail(6)
        elif date_range == "Last 12 months":
            filtered_data = arr_summary_df.tail(12)
        elif date_range == "Last 24 months":
            filtered_data = arr_summary_df.tail(24)
        else:
            filtered_data = arr_summary_df
    
    with col2:
        # Key insights
        st.markdown('<div class="insight-box">', unsafe_allow_html=True)
        st.subheader("📊 Period Analysis")
        
        avg_growth = filtered_data['arr_growth_rate'].mean()
        total_customers = latest_month['active_customers']
        arr_trend = "Growing" if avg_growth > 0 else "Declining"
        
        st.markdown(f'<div class="insight-title">ARR Trend</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-value">{arr_trend} at {avg_growth:.1f}% avg</div>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="insight-title">Customer Base</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="insight-value">{total_customers:,} active</div>', unsafe_allow_html=True)
        
        if latest_month['arr_growth_rate'] > 5:
            st.success("🚀 Strong growth momentum!")
        elif latest_month['arr_growth_rate'] > 0:
            st.info("📈 Steady growth trajectory")
        else:
            st.warning("⚠️ Growth challenges detected")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Export Options
    st.markdown('<div class="section-header">💾 Export & Share</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Export ARR Summary", type="primary"):
            # Create export CSV
            export_data = arr_summary_df.tail(12)
            csv = export_data.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"arr_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("📈 Generate Executive Report"):
            st.info("Report generation feature - connect to email service for automated reports")
    
    with col3:
        st.write("**Share this dashboard:**")
        st.code("streamlit run arr_dashboard.py", language="bash")
    
    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #64748b; font-size: 0.875rem;">'
        f'Data last updated: {arr_summary_df["month_date"].max().strftime("%B %d, %Y")} • '
        f'Dashboard powered by Streamlit + Plotly</p>',
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
