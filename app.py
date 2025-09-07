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

# Custom CSS for enhanced styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(90deg, #1f77b4, #17a2b8);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 1rem;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .metric-card.revenue {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
    }
    
    .metric-card.expense {
        background: linear-gradient(135deg, #fc466b 0%, #3f5efb 100%);
    }
    
    .metric-card.profit {
        background: linear-gradient(135deg, #fdbb2d 0%, #22c1c3 100%);
    }
    
    .metric-card.margin {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        color: #333;
    }
    
    .metric-title {
        font-size: 0.9rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        opacity: 0.9;
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        margin-bottom: 0.3rem;
    }
    
    .metric-change {
        font-size: 0.8rem;
        opacity: 0.8;
    }
    
    .upload-section {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(240, 147, 251, 0.3);
    }
    
    .info-card {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(79, 172, 254, 0.3);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: #333;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(250, 112, 154, 0.3);
    }
    
    .success-card {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: #333;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(168, 237, 234, 0.3);
    }
    
    .sidebar-section {
        background: rgba(255, 255, 255, 0.05);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .data-summary-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin-bottom: 1rem;
    }
    
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def load_data_from_upload(uploaded_file):
    """Load and process the uploaded Excel data"""
    try:
        # Read the uploaded Excel file
        df_raw = pd.read_excel(uploaded_file, sheet_name=0, header=None)
        
        # Process the data to extract financial information
        financial_data = []
        
        for idx, row in df_raw.iterrows():
            if len(row) > 5 and pd.notna(row.iloc[0]) and pd.notna(row.iloc[5]):
                description = str(row.iloc[0]).strip()
                try:
                    value = float(row.iloc[5])
                    # Filter out header rows and invalid descriptions
                    if (description and 
                        description not in ['DESCRIPTION', 'UNITECH - TOSL KSA', 'INCOME STATEMENT_AS OF JULY 2025'] and
                        not description.isdigit() and
                        len(description) > 2):
                        
                        financial_data.append({
                            'Description': description,
                            'Value': value,
                            'Category': classify_line_item(description),
                            'Abs_Value': abs(value)
                        })
                except (ValueError, TypeError):
                    continue
        
        if financial_data:
            return pd.DataFrame(financial_data)
        else:
            return None
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None

def classify_line_item(description):
    """Classify financial line items into categories"""
    description_lower = description.lower()
    
    if any(word in description_lower for word in ['revenue', 'income', 'sales', 'turnover']):
        return 'Revenue'
    elif any(word in description_lower for word in ['cost', 'expense', 'expenditure', 'operating', 'admin', 'selling']):
        return 'Expenses'
    elif any(word in description_lower for word in ['profit', 'loss', 'net', 'ebitda', 'ebit']):
        return 'Profit/Loss'
    elif any(word in description_lower for word in ['tax', 'interest', 'finance']):
        return 'Tax & Interest'
    elif any(word in description_lower for word in ['depreciation', 'amortization']):
        return 'Depreciation'
    else:
        return 'Other'

def create_sample_data():
    """Create sample financial data for demonstration"""
    return pd.DataFrame({
        'Description': [
            'Total Revenue', 'Revenue (Other Income)', 'Cost of Goods Sold',
            'Operating Expenses', 'Administrative Expenses', 'Depreciation', 
            'Interest Expense', 'Tax Expense', 'Net Income'
        ],
        'Value': [175595668.23, -91082.5, -162826952.23, -8500000, -2300000,
                 -1200000, -800000, -1500000, 2250000],
        'Category': ['Revenue', 'Revenue', 'Expenses', 'Expenses', 'Expenses',
                    'Depreciation', 'Tax & Interest', 'Tax & Interest', 'Profit/Loss'],
        'Abs_Value': [175595668.23, 91082.5, 162826952.23, 8500000, 2300000,
                     1200000, 800000, 1500000, 2250000]
    })

def create_metric_card(title, value, prefix="SAR", card_type="default"):
    """Create a custom metric card"""
    formatted_value = f"{prefix} {value:,.0f}" if prefix else f"{value:.1f}%"
    
    card_html = f"""
    <div class="metric-card {card_type}">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{formatted_value}</div>
    </div>
    """
    return card_html

def create_enhanced_waterfall_chart(df):
    """Create an enhanced waterfall chart"""
    revenue_items = df[df['Category'] == 'Revenue']['Value'].sum()
    expense_items = abs(df[df['Category'] == 'Expenses']['Value'].sum())
    depreciation = abs(df[df['Category'] == 'Depreciation']['Value'].sum())
    tax_interest = abs(df[df['Category'] == 'Tax & Interest']['Value'].sum())
    net_result = revenue_items - expense_items - depreciation - tax_interest
    
    fig = go.Figure(go.Waterfall(
        name="Financial Flow",
        orientation="v",
        measure=["relative", "relative", "relative", "relative", "total"],
        x=["Revenue", "Operating Expenses", "Depreciation", "Tax & Interest", "Net Result"],
        textposition="outside",
        text=[f"SAR {revenue_items:,.0f}", f"-SAR {expense_items:,.0f}", 
              f"-SAR {depreciation:,.0f}", f"-SAR {tax_interest:,.0f}", 
              f"SAR {net_result:,.0f}"],
        y=[revenue_items, -expense_items, -depreciation, -tax_interest, 0],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#ff6b6b"}},
        increasing={"marker": {"color": "#51cf66"}},
        totals={"marker": {"color": "#339af0"}}
    ))
    
    fig.update_layout(
        title="💰 Income Statement Waterfall Analysis",
        showlegend=False,
        height=500,
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_enhanced_pie_chart(df):
    """Create an enhanced category breakdown pie chart"""
    category_totals = df.groupby('Category')['Abs_Value'].sum()
    
    colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd']
    
    fig = px.pie(
        values=category_totals.values,
        names=category_totals.index,
        title="📊 Financial Categories Distribution",
        color_discrete_sequence=colors,
        hole=0.4
    )
    
    fig.update_traces(
        textposition='inside', 
        textinfo='percent+label',
        textfont_size=12,
        marker=dict(line=dict(color='#FFFFFF', width=2))
    )
    
    fig.update_layout(
        height=400,
        font=dict(size=12),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_enhanced_bar_chart(df):
    """Create an enhanced horizontal bar chart"""
    df_sorted = df.copy().sort_values('Abs_Value', ascending=True)
    
    # Color mapping
    color_map = {
        'Revenue': '#51cf66',
        'Expenses': '#ff6b6b',
        'Profit/Loss': '#339af0',
        'Tax & Interest': '#ffa726',
        'Depreciation': '#ab47bc',
        'Other': '#78909c'
    }
    
    colors = [color_map.get(cat, '#78909c') for cat in df_sorted['Category']]
    
    fig = go.Figure(data=[
        go.Bar(
            y=df_sorted['Description'],
            x=df_sorted['Value'],
            orientation='h',
            marker_color=colors,
            text=[f'SAR {val:,.0f}' for val in df_sorted['Value']],
            textposition='auto',
            marker=dict(
                line=dict(color='rgba(255,255,255,0.8)', width=1)
            )
        )
    ])
    
    fig.update_layout(
        title="📈 Detailed Financial Line Items",
        xaxis_title="Amount (SAR)",
        yaxis_title="Financial Items",
        height=max(400, len(df) * 35),
        showlegend=False,
        font=dict(size=11),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def create_kpi_chart(df):
    """Create a KPI gauge chart"""
    total_revenue = df[df['Category'] == 'Revenue']['Value'].sum()
    total_expenses = abs(df[df['Category'] == 'Expenses']['Value'].sum())
    net_income = total_revenue - total_expenses
    profit_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
    
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = profit_margin,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Profit Margin %"},
        delta = {'reference': 15, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "#339af0"},
            'steps': [
                {'range': [0, 10], 'color': "#ffcccb"},
                {'range': [10, 25], 'color': "#ffffcc"},
                {'range': [25, 100], 'color': "#ccffcc"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        font={'color': "darkblue", 'family': "Arial"},
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig

def main():
    # Header
    st.markdown('<div class="main-header">📊 Financial Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">UNITECH - TOSL KSA Income Statement Analysis</div>', unsafe_allow_html=True)
    
    # File Upload Section
    st.markdown("""
    <div class="upload-section">
        <h2>📁 Upload Your Financial Data</h2>
        <p>Upload your Excel file containing the Income Statement data to get started</p>
    </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "",
        type=['xlsx', 'xls'],
        help="Upload your Income Statement Excel file (Format: Column A = Descriptions, Column F = Values)",
        label_visibility="collapsed"
    )
    
    # Initialize session state for data
    if 'df_data' not in st.session_state:
        st.session_state.df_data = None
    
    # Process uploaded file
    if uploaded_file is not None:
        with st.spinner('🔄 Processing your file...'):
            df = load_data_from_upload(uploaded_file)
            if df is not None and not df.empty:
                st.session_state.df_data = df
                st.markdown("""
                <div class="success-card">
                    <h3>✅ File Processed Successfully!</h3>
                    <p>Your financial data has been loaded and is ready for analysis.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="warning-card">
                    <h3>⚠️ No Valid Data Found</h3>
                    <p>Please check your Excel file structure. Expected format:</p>
                    <ul>
                        <li>Column A: Financial item descriptions</li>
                        <li>Column F: Corresponding numerical values</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                st.session_state.df_data = create_sample_data()
    
    # Show demo data if no file uploaded
    elif st.session_state.df_data is None:
        st.markdown("""
        <div class="info-card">
            <h3>📈 Demo Mode</h3>
            <p>Upload your Excel file above to analyze your data, or explore the demo below!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Load Demo Data", type="primary"):
            st.session_state.df_data = create_sample_data()
            st.rerun()
    
    # Main dashboard (only show if data is available)
    if st.session_state.df_data is not None and not st.session_state.df_data.empty:
        df = st.session_state.df_data
        
        # Sidebar Controls
        with st.sidebar:
            st.markdown("### 🎛️ Dashboard Controls")
            
            # Data summary card
            st.markdown(f"""
            <div class="data-summary-card">
                <h4>📊 Data Summary</h4>
                <p><strong>Total Items:</strong> {len(df)}</p>
                <p><strong>Categories:</strong> {len(df['Category'].unique())}</p>
                <p><strong>File Status:</strong> {'Uploaded' if uploaded_file else 'Demo'}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Filter options
            categories = ['All'] + list(df['Category'].unique())
            selected_category = st.selectbox("🔍 Filter by Category", categories)
            
            if selected_category != 'All':
                df_filtered = df[df['Category'] == selected_category]
            else:
                df_filtered = df
            
            # Chart visibility controls
            st.markdown("### 📊 Chart Controls")
            show_waterfall = st.checkbox("💰 Waterfall Chart", value=True)
            show_pie = st.checkbox("📊 Category Breakdown", value=True)
            show_bar = st.checkbox("📈 Detailed Analysis", value=True)
            show_kpi = st.checkbox("🎯 KPI Gauge", value=True)
            
            # Reset button
            if st.button("🔄 Reset Dashboard"):
                st.session_state.df_data = None
                st.rerun()
        
        # Calculate key metrics
        total_revenue = df[df['Category'] == 'Revenue']['Value'].sum()
        total_expenses = abs(df[df['Category'] == 'Expenses']['Value'].sum())
        net_income = total_revenue - total_expenses
        profit_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
        
        # Key Metrics Cards
        st.markdown("### 💼 Key Financial Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(create_metric_card("Total Revenue", total_revenue, "SAR", "revenue"), unsafe_allow_html=True)
        
        with col2:
            st.markdown(create_metric_card("Total Expenses", total_expenses, "SAR", "expense"), unsafe_allow_html=True)
        
        with col3:
            st.markdown(create_metric_card("Net Income", net_income, "SAR", "profit"), unsafe_allow_html=True)
        
        with col4:
            st.markdown(create_metric_card("Profit Margin", profit_margin, "", "margin"), unsafe_allow_html=True)
        
        # Charts Section
        st.markdown("### 📊 Financial Analysis Charts")
        
        # First row of charts
        if show_waterfall:
            with st.container():
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(create_enhanced_waterfall_chart(df), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Second row of charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            if show_pie:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(create_enhanced_pie_chart(df_filtered), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        with chart_col2:
            if show_kpi:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(create_kpi_chart(df), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Third row - detailed analysis
        if show_bar:
            with st.container():
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                st.plotly_chart(create_enhanced_bar_chart(df_filtered), use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Data Table Section
        st.markdown("### 📋 Financial Data Table")
        
        # Format the dataframe for display
        display_df = df_filtered.copy()
        display_df['Formatted_Value'] = display_df['Value'].apply(lambda x: f"SAR {x:,.2f}")
        display_df = display_df[['Description', 'Category', 'Formatted_Value']].rename(columns={
            'Description': 'Financial Item',
            'Category': 'Category',
            'Formatted_Value': 'Amount'
        })
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
        
        # Export Section
        st.markdown("### 📥 Export & Download")
        col1, col2 = st.columns(2)
        
        with col1:
            csv = df.to_csv(index=False)
            st.download_button(
                label="📊 Download CSV",
                data=csv,
                file_name='financial_analysis.csv',
                mime='text/csv',
                type="primary"
            )
        
        with col2:
            # Summary report
            summary_text = f"""
Financial Summary Report
========================
Company: UNITECH - TOSL KSA
Date: {pd.Timestamp.now().strftime('%Y-%m-%d')}

Key Metrics:
- Total Revenue: SAR {total_revenue:,.2f}
- Total Expenses: SAR {total_expenses:,.2f}
- Net Income: SAR {net_income:,.2f}
- Profit Margin: {profit_margin:.1f}%

Total Line Items: {len(df)}
Categories: {', '.join(df['Category'].unique())}
            """
            
            st.download_button(
                label="📄 Download Report",
                data=summary_text,
                file_name='financial_summary.txt',
                mime='text/plain'
            )

if __name__ == "__main__":
    main()
