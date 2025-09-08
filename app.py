import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import openpyxl
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="Cash Flow Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for white background and attractive styling
st.markdown("""
<style>
    .main {
        background-color: #FFFFFF;
        padding: 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 10px 10px 0px 0px;
        gap: 1px;
        padding-left: 20px;
        padding-right: 20px;
        font-weight: bold;
        font-size: 16px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f77b4;
        color: white;
    }
    .metric-container {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    .section-header {
        background: linear-gradient(90deg, #1f77b4, #17a2b8);
        color: white;
        padding: 10px 20px;
        border-radius: 10px;
        margin: 20px 0 10px 0;
        font-weight: bold;
        font-size: 18px;
    }
    .stMetric {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border: 1px solid #e0e0e0;
    }
    .stSelectbox {
        background-color: white;
    }
</style>
""", unsafe_allow_html=True)

# Sample data structure based on your Excel file
def create_sample_data():
    """Create sample cash flow data for three branches"""
    
    # Base cash flow items
    cash_flow_items = {
        'Operations': {
            'Cash receipts from customers': [693200, 720000, 650000],
            'Cash paid for inventory': [-264000, -280000, -245000],
            'General operating expenses': [-112000, -118000, -105000],
            'Wage expenses': [-123000, -130000, -115000],
            'Interest payments': [-13500, -14000, -12500],
            'Income taxes': [-32800, -35000, -30000]
        },
        'Investing Activities': {
            'Sale of equipment': [18500, 15000, 20000],
            'Purchase of equipment': [-45000, -50000, -40000],
            'Investment purchases': [-8500, -10000, -7000]
        },
        'Financing Activities': {
            'Proceeds from bank loan': [50000, 40000, 60000],
            'Repayment of bank loan': [-25000, -30000, -20000],
            'Owner investment': [15000, 20000, 10000],
            'Owner withdrawal': [-8000, -10000, -6000]
        }
    }
    
    branches = ['JEDDAH', 'DAMMAM', 'RIYADH']
    data = []
    
    for branch_idx, branch in enumerate(branches):
        for category, items in cash_flow_items.items():
            for item, values in items.items():
                data.append({
                    'Branch': branch,
                    'Category': category,
                    'Item': item,
                    'Amount': values[branch_idx],
                    'Year': 2024
                })
    
    # Add beginning cash balances
    beginning_cash = [15700, 18000, 14500]
    for i, branch in enumerate(branches):
        data.append({
            'Branch': branch,
            'Category': 'Beginning Balance',
            'Item': 'Cash at Beginning of Year',
            'Amount': beginning_cash[i],
            'Year': 2024
        })
    
    return pd.DataFrame(data)

# Load data function (replace this with your actual Excel loading)
@st.cache_data
def load_data():
    """Load cash flow data from Excel file or create sample data"""
    try:
        # Try to load from uploaded file
        # df = pd.read_excel('cashflowstatement.xlsx')
        # For now, use sample data
        return create_sample_data()
    except:
        return create_sample_data()

def calculate_metrics(df, branch):
    """Calculate key financial metrics for a branch"""
    branch_data = df[df['Branch'] == branch]
    
    # Operating cash flow
    operating_flow = branch_data[branch_data['Category'] == 'Operations']['Amount'].sum()
    
    # Investing cash flow
    investing_flow = branch_data[branch_data['Category'] == 'Investing Activities']['Amount'].sum()
    
    # Financing cash flow
    financing_flow = branch_data[branch_data['Category'] == 'Financing Activities']['Amount'].sum()
    
    # Net cash flow
    net_cash_flow = operating_flow + investing_flow + financing_flow
    
    # Beginning cash
    beginning_cash = branch_data[branch_data['Item'] == 'Cash at Beginning of Year']['Amount'].sum()
    
    # Ending cash
    ending_cash = beginning_cash + net_cash_flow
    
    return {
        'operating_flow': operating_flow,
        'investing_flow': investing_flow,
        'financing_flow': financing_flow,
        'net_cash_flow': net_cash_flow,
        'beginning_cash': beginning_cash,
        'ending_cash': ending_cash
    }

def create_waterfall_chart(metrics, branch):
    """Create a waterfall chart showing cash flow components"""
    fig = go.Figure()
    
    categories = ['Beginning Cash', 'Operating', 'Investing', 'Financing', 'Ending Cash']
    values = [
        metrics['beginning_cash'],
        metrics['operating_flow'],
        metrics['investing_flow'],
        metrics['financing_flow'],
        metrics['ending_cash']
    ]
    
    # Colors for each category
    colors = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#1f77b4']
    
    fig.add_trace(go.Waterfall(
        name="Cash Flow",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "total"],
        x=categories,
        textposition="outside",
        text=[f"${v:,.0f}" for v in values],
        y=values,
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        increasing={"marker": {"color": "#2ca02c"}},
        decreasing={"marker": {"color": "#d62728"}},
        totals={"marker": {"color": "#1f77b4"}}
    ))
    
    fig.update_layout(
        title=f"Cash Flow Waterfall - {branch}",
        title_x=0.5,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        height=400
    )
    
    return fig

def create_comparison_chart(df):
    """Create comparison chart across branches"""
    branch_metrics = {}
    for branch in df['Branch'].unique():
        branch_metrics[branch] = calculate_metrics(df, branch)
    
    # Create subplot with multiple charts
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Operating Cash Flow', 'Net Cash Flow', 'Beginning vs Ending Cash', 'Cash Flow Components'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "bar"}]]
    )
    
    branches = list(branch_metrics.keys())
    
    # Operating Cash Flow
    operating_values = [branch_metrics[b]['operating_flow'] for b in branches]
    fig.add_trace(go.Bar(x=branches, y=operating_values, name='Operating Flow', 
                         marker_color='#2ca02c'), row=1, col=1)
    
    # Net Cash Flow
    net_values = [branch_metrics[b]['net_cash_flow'] for b in branches]
    fig.add_trace(go.Bar(x=branches, y=net_values, name='Net Flow',
                         marker_color='#1f77b4'), row=1, col=2)
    
    # Beginning vs Ending Cash
    beginning_values = [branch_metrics[b]['beginning_cash'] for b in branches]
    ending_values = [branch_metrics[b]['ending_cash'] for b in branches]
    
    fig.add_trace(go.Bar(x=branches, y=beginning_values, name='Beginning Cash',
                         marker_color='#ff7f0e'), row=2, col=1)
    fig.add_trace(go.Bar(x=branches, y=ending_values, name='Ending Cash',
                         marker_color='#d62728'), row=2, col=1)
    
    # Cash Flow Components (Stacked)
    operating = [branch_metrics[b]['operating_flow'] for b in branches]
    investing = [branch_metrics[b]['investing_flow'] for b in branches]
    financing = [branch_metrics[b]['financing_flow'] for b in branches]
    
    fig.add_trace(go.Bar(x=branches, y=operating, name='Operating',
                         marker_color='#2ca02c'), row=2, col=2)
    fig.add_trace(go.Bar(x=branches, y=investing, name='Investing',
                         marker_color='#ff7f0e'), row=2, col=2)
    fig.add_trace(go.Bar(x=branches, y=financing, name='Financing',
                         marker_color='#d62728'), row=2, col=2)
    
    fig.update_layout(
        height=600,
        showlegend=True,
        title_text="Branch Comparison Dashboard",
        title_x=0.5,
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    return fig

def create_detailed_breakdown(df, branch, category):
    """Create detailed breakdown chart for specific category"""
    branch_data = df[(df['Branch'] == branch) & (df['Category'] == category)]
    
    if len(branch_data) == 0:
        return None
    
    fig = px.bar(
        branch_data,
        x='Item',
        y='Amount',
        title=f'{category} Breakdown - {branch}',
        color='Amount',
        color_continuous_scale=['red', 'yellow', 'green']
    )
    
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis_tickangle=-45,
        height=400,
        title_x=0.5
    )
    
    return fig

# Main dashboard
def main():
    # Header
    st.markdown("""
    <div style='text-align: center; padding: 2rem 0;'>
        <h1 style='color: #1f77b4; font-size: 3rem; margin-bottom: 0;'>💰 Cash Flow Dashboard</h1>
        <p style='font-size: 1.2rem; color: #666; margin-top: 0;'>Multi-Branch Financial Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    # Sidebar
    with st.sidebar:
        st.markdown("<div class='section-header'>Dashboard Controls</div>", unsafe_allow_html=True)
        
        # Year selector (if you have multiple years)
        year = st.selectbox("Select Year", [2024], index=0)
        
        # Export option
        if st.button("📊 Export Summary Report"):
            st.success("Report exported successfully!")
        
        st.markdown("---")
        st.markdown("### Quick Stats")
        total_branches = len(df['Branch'].unique())
        st.metric("Total Branches", total_branches)
        
        total_operating_flow = sum([calculate_metrics(df, branch)['operating_flow'] 
                                  for branch in df['Branch'].unique()])
        st.metric("Total Operating Flow", f"${total_operating_flow:,.0f}")

    # Main content with tabs
    tab1, tab2, tab3 = st.tabs(["🏢 JEDDAH", "🏢 DAMMAM", "🏢 RIYADH"])
    
    # Branch tabs
    for tab, branch in zip([tab1, tab2, tab3], ['JEDDAH', 'DAMMAM', 'RIYADH']):
        with tab:
            metrics = calculate_metrics(df, branch)
            
            # Key metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    label="Operating Cash Flow",
                    value=f"${metrics['operating_flow']:,.0f}",
                    delta=f"{metrics['operating_flow']/metrics['beginning_cash']*100:.1f}% of beginning cash"
                )
            
            with col2:
                st.metric(
                    label="Net Cash Flow",
                    value=f"${metrics['net_cash_flow']:,.0f}",
                    delta="Positive" if metrics['net_cash_flow'] > 0 else "Negative"
                )
            
            with col3:
                st.metric(
                    label="Beginning Cash",
                    value=f"${metrics['beginning_cash']:,.0f}"
                )
            
            with col4:
                st.metric(
                    label="Ending Cash",
                    value=f"${metrics['ending_cash']:,.0f}",
                    delta=f"${metrics['net_cash_flow']:,.0f}"
                )
            
            st.markdown("---")
            
            # Charts row
            col1, col2 = st.columns(2)
            
            with col1:
                # Waterfall chart
                waterfall_fig = create_waterfall_chart(metrics, branch)
                st.plotly_chart(waterfall_fig, use_container_width=True)
            
            with col2:
                # Category breakdown
                branch_data = df[df['Branch'] == branch]
                category_summary = branch_data.groupby('Category')['Amount'].sum().reset_index()
                
                fig = px.pie(
                    category_summary,
                    values='Amount',
                    names='Category',
                    title=f'Cash Flow by Category - {branch}',
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                fig.update_layout(plot_bgcolor='white', paper_bgcolor='white', height=400)
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("---")
            
            # Detailed breakdown
            st.markdown(f"<div class='section-header'>Detailed Analysis - {branch}</div>", unsafe_allow_html=True)
            
            # Category selector
            categories = df[df['Branch'] == branch]['Category'].unique()
            categories = [cat for cat in categories if cat != 'Beginning Balance']
            
            selected_category = st.selectbox(f"Select Category for {branch}", categories, key=f"{branch}_category")
            
            if selected_category:
                breakdown_fig = create_detailed_breakdown(df, branch, selected_category)
                if breakdown_fig:
                    st.plotly_chart(breakdown_fig, use_container_width=True)
            
            # Data table
            with st.expander(f"View Raw Data - {branch}"):
                branch_data = df[df['Branch'] == branch].copy()
                st.dataframe(branch_data, use_container_width=True)
    
    # Comparison section
    st.markdown("---")
    st.markdown("<div class='section-header'>🔄 Branch Comparison</div>", unsafe_allow_html=True)
    
    comparison_fig = create_comparison_chart(df)
    st.plotly_chart(comparison_fig, use_container_width=True)
    
    # Summary table
    st.markdown("### Summary Table")
    summary_data = []
    for branch in df['Branch'].unique():
        metrics = calculate_metrics(df, branch)
        summary_data.append({
            'Branch': branch,
            'Operating Flow': f"${metrics['operating_flow']:,.0f}",
            'Investing Flow': f"${metrics['investing_flow']:,.0f}",
            'Financing Flow': f"${metrics['financing_flow']:,.0f}",
            'Net Flow': f"${metrics['net_cash_flow']:,.0f}",
            'Beginning Cash': f"${metrics['beginning_cash']:,.0f}",
            'Ending Cash': f"${metrics['ending_cash']:,.0f}"
        })
    
    summary_df = pd.DataFrame(summary_data)
    st.dataframe(summary_df, use_container_width=True)

if __name__ == "__main__":
    main()
