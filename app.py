import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# Set page config
st.set_page_config(
    page_title="Financial Dashboard - UNITECH TOSL KSA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
    }
    .sidebar-header {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and process the Excel data"""
    try:
        # Read the Excel file
        df = pd.read_excel('IS.xlsx', sheet_name='IS 2020_As of Feb ')
        
        # The data structure shows financial line items in column A and values in column F
        # Let's extract the relevant data
        financial_data = []
        
        # Read the file more carefully
        df_raw = pd.read_excel('IS.xlsx', sheet_name='IS 2020_As of Feb ', header=None)
        
        for idx, row in df_raw.iterrows():
            if pd.notna(row.iloc[0]) and pd.notna(row.iloc[5]):  # Column A has description, Column F has value
                description = str(row.iloc[0]).strip()
                try:
                    value = float(row.iloc[5])
                    if description and value != 0:  # Skip empty descriptions and zero values
                        financial_data.append({
                            'Description': description,
                            'Value': value,
                            'Category': classify_line_item(description)
                        })
                except (ValueError, TypeError):
                    continue
        
        return pd.DataFrame(financial_data)
    
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Return sample data for demonstration
        return create_sample_data()

def classify_line_item(description):
    """Classify financial line items into categories"""
    description_lower = description.lower()
    
    if any(word in description_lower for word in ['revenue', 'income', 'sales']):
        return 'Revenue'
    elif any(word in description_lower for word in ['cost', 'expense', 'expenditure']):
        return 'Expenses'
    elif any(word in description_lower for word in ['profit', 'loss', 'net']):
        return 'Profit/Loss'
    elif any(word in description_lower for word in ['tax', 'interest']):
        return 'Tax & Interest'
    else:
        return 'Other'

def create_sample_data():
    """Create sample financial data for demonstration"""
    return pd.DataFrame({
        'Description': [
            'Revenue', 'Revenue (Other Income)', 'Cost of Goods Sold',
            'Operating Expenses', 'Depreciation', 'Interest Expense',
            'Tax Expense', 'Net Income'
        ],
        'Value': [175595668.23, -91082.5, 162826952.23, 8500000, 1200000, 
                 800000, 1500000, 750000],
        'Category': ['Revenue', 'Revenue', 'Expenses', 'Expenses', 'Expenses',
                    'Tax & Interest', 'Tax & Interest', 'Profit/Loss']
    })

def create_waterfall_chart(df):
    """Create a waterfall chart showing the income statement flow"""
    # Prepare data for waterfall chart
    revenue_items = df[df['Category'] == 'Revenue']['Value'].sum()
    expense_items = df[df['Category'] == 'Expenses']['Value'].sum()
    tax_interest = df[df['Category'] == 'Tax & Interest']['Value'].sum()
    
    fig = go.Figure(go.Waterfall(
        name="Income Statement Flow",
        orientation="v",
        measure=["relative", "relative", "relative", "total"],
        x=["Total Revenue", "Total Expenses", "Tax & Interest", "Net Result"],
        textposition="outside",
        text=[f"{revenue_items:,.0f}", f"-{expense_items:,.0f}", 
              f"-{tax_interest:,.0f}", f"{revenue_items - expense_items - tax_interest:,.0f}"],
        y=[revenue_items, -expense_items, -tax_interest, 0],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
    ))
    
    fig.update_layout(
        title="Income Statement Waterfall Analysis",
        showlegend=False,
        height=500
    )
    
    return fig

def create_category_breakdown(df):
    """Create a pie chart showing breakdown by category"""
    category_totals = df.groupby('Category')['Value'].sum().abs()  # Use absolute values for pie chart
    
    fig = px.pie(
        values=category_totals.values,
        names=category_totals.index,
        title="Financial Categories Breakdown",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(height=400)
    
    return fig

def create_bar_chart(df):
    """Create a horizontal bar chart of all line items"""
    # Sort by absolute value for better visualization
    df_sorted = df.copy()
    df_sorted['abs_value'] = df_sorted['Value'].abs()
    df_sorted = df_sorted.sort_values('abs_value', ascending=True)
    
    # Color code by category
    color_map = {
        'Revenue': '#2E8B57',
        'Expenses': '#DC143C',
        'Profit/Loss': '#4169E1',
        'Tax & Interest': '#FF8C00',
        'Other': '#9932CC'
    }
    
    colors = [color_map.get(cat, '#9932CC') for cat in df_sorted['Category']]
    
    fig = go.Figure(data=[
        go.Bar(
            y=df_sorted['Description'],
            x=df_sorted['Value'],
            orientation='h',
            marker_color=colors,
            text=[f'{val:,.0f}' for val in df_sorted['Value']],
            textposition='auto',
        )
    ])
    
    fig.update_layout(
        title="Detailed Line Items Analysis",
        xaxis_title="Amount (SAR)",
        yaxis_title="Description",
        height=max(400, len(df) * 30),
        showlegend=False
    )
    
    return fig

def main():
    # Header
    st.markdown('<div class="main-header">📊 UNITECH - TOSL KSA Financial Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #666; margin-bottom: 2rem;">Income Statement Analysis - As of July 2025</div>', unsafe_allow_html=True)
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.error("No data found. Please check your Excel file.")
        return
    
    # Sidebar
    st.sidebar.markdown('<div class="sidebar-header">📈 Dashboard Controls</div>', unsafe_allow_html=True)
    
    # Filter options
    categories = ['All'] + list(df['Category'].unique())
    selected_category = st.sidebar.selectbox("Filter by Category", categories)
    
    if selected_category != 'All':
        df_filtered = df[df['Category'] == selected_category]
    else:
        df_filtered = df
    
    # Show/hide charts
    st.sidebar.markdown("### Chart Options")
    show_waterfall = st.sidebar.checkbox("Waterfall Chart", value=True)
    show_pie = st.sidebar.checkbox("Category Breakdown", value=True)
    show_bar = st.sidebar.checkbox("Detailed Analysis", value=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_revenue = df[df['Category'] == 'Revenue']['Value'].sum()
    total_expenses = df[df['Category'] == 'Expenses']['Value'].sum()
    net_income = df[df['Category'] == 'Profit/Loss']['Value'].sum()
    
    with col1:
        st.metric("Total Revenue", f"SAR {total_revenue:,.0f}")
    
    with col2:
        st.metric("Total Expenses", f"SAR {total_expenses:,.0f}")
    
    with col3:
        st.metric("Net Income", f"SAR {net_income:,.0f}")
    
    with col4:
        profit_margin = (net_income / total_revenue * 100) if total_revenue != 0 else 0
        st.metric("Profit Margin", f"{profit_margin:.1f}%")
    
    # Charts
    if show_waterfall:
        st.plotly_chart(create_waterfall_chart(df), use_container_width=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if show_pie:
            st.plotly_chart(create_category_breakdown(df_filtered), use_container_width=True)
    
    with col2:
        if show_bar and not df_filtered.empty:
            st.plotly_chart(create_bar_chart(df_filtered), use_container_width=True)
    
    # Data Table
    st.markdown("### 📊 Financial Data Summary")
    
    # Format the dataframe for display
    display_df = df_filtered.copy()
    display_df['Value'] = display_df['Value'].apply(lambda x: f"SAR {x:,.2f}")
    
    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True
    )
    
    # Export functionality
    st.markdown("### 📥 Export Data")
    csv = df.to_csv(index=False)
    st.download_button(
        label="Download data as CSV",
        data=csv,
        file_name='financial_data.csv',
        mime='text/csv'
    )

if __name__ == "__main__":
    main()