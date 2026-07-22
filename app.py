import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIG & THEMING
# ============================================================================
st.set_page_config(
    page_title="HPA Gene Expression Explorer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    body {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .header-container {
        background: linear-gradient(90deg, #06b6d4 0%, #0891b2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: white;
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 0.5rem;
    }
    
    .header-subtitle {
        font-size: 0.95rem;
        color: rgba(255, 255, 255, 0.85);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(15, 23, 42, 0.4);
        padding: 8px 12px;
        border-radius: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(148, 163, 184, 0.1);
        border-radius: 6px;
        color: #cbd5e1;
        font-weight: 600;
        padding: 10px 20px;
    }
    
    .stTabs [aria-selected="true"] [data-baseweb="tab"] {
        background: linear-gradient(90deg, #06b6d4 0%, #0891b2 100%);
        color: white;
    }
    
    .metric-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(6, 182, 212, 0.2);
        border-radius: 10px;
        padding: 20px;
        text-align: center;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #06b6d4;
        margin: 10px 0;
    }
    
    .metric-label {
        font-size: 0.85rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .chart-container {
        background: rgba(15, 23, 42, 0.4);
        border: 1px solid rgba(6, 182, 212, 0.1);
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .chart-title {
        color: #e2e8f0;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #06b6d4 0%, #0891b2 100%);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        box-shadow: 0 4px 12px rgba(6, 182, 212, 0.4);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_hpa_data():
    """Load HPA data from Excel file"""
    try:
        excel_file = 'Normal_Vs_Cancer_data.xlsx'
        
        # Try to load from multiple possible locations
        possible_paths = [
            excel_file,
            f'/mount/src/biocia/{excel_file}',
            f'./data/{excel_file}',
            Path(excel_file)
        ]
        
        data = None
        for path in possible_paths:
            try:
                if Path(path).exists():
                    data = pd.read_excel(path)
                    break
            except:
                continue
        
        if data is None:
            st.error("❌ Could not find Excel file. Please ensure 'Normal_Vs_Cancer_data.xlsx' is in the project directory.")
            return None
        
        # Standardize column names
        data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')
        
        print(f"✅ Loaded Excel: {data.shape[0]:,} rows, {data.shape[1]} columns")
        print(f"Columns: {list(data.columns)}")
        return data
    
    except Exception as e:
        st.error(f"❌ Error loading data: {str(e)}")
        print(f"Error details: {e}")
        return None

# Load data at startup
data = load_hpa_data()

if data is None:
    st.error("⚠️ Application cannot start without data. Please check the Excel file.")
    st.stop()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def create_metric_card(label, value, subtext=""):
    """Create styled metric card"""
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value:,.0f}</div>
        <div style="font-size: 0.8rem; color: #64748b;">{subtext}</div>
    </div>
    """, unsafe_allow_html=True)

def create_comparison_chart(gene_data, gene_name):
    """Create normal vs cancer comparison chart"""
    if len(gene_data) == 0:
        st.warning("No data available for this gene")
        return None
    
    fig = go.Figure()
    
    # Find normal vs cancer samples
    for tissue_type in gene_data['tissue_type'].unique() if 'tissue_type' in gene_data.columns else ['Normal', 'Cancer']:
        subset = gene_data[gene_data.get('tissue_type', 'Normal') == tissue_type] if 'tissue_type' in gene_data.columns else gene_data
        
        if len(subset) > 0:
            fig.add_trace(go.Bar(
                x=subset.get('cell_line', subset.get('sample', ['Sample'])),
                y=subset.iloc[:, -1],  # Last numeric column (expression)
                name=tissue_type,
                marker=dict(
                    color='#10b981' if tissue_type == 'Normal' else '#f43f5e',
                    opacity=0.8
                )
            ))
    
    fig.update_layout(
        title=f"Expression Levels: {gene_name}",
        xaxis_title="Sample",
        yaxis_title="Expression (nTPM)",
        barmode='group',
        template='plotly_dark',
        height=400,
        font=dict(color="#e2e8f0"),
        plot_bgcolor='rgba(15, 23, 42, 0.3)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        hovermode='x unified'
    )
    
    return fig

def create_tissue_comparison(data):
    """Compare expression across tissues"""
    try:
        # Group by tissue if possible
        if 'tissue' in data.columns:
            tissue_expr = data.groupby('tissue').iloc[:, -1].mean()
            
            fig = px.bar(
                x=tissue_expr.index,
                y=tissue_expr.values,
                title="Average Expression by Tissue Type",
                labels={'x': 'Tissue Type', 'y': 'Expression (nTPM)'},
                color=tissue_expr.values,
                color_continuous_scale='Viridis'
            )
            
            fig.update_layout(
                template='plotly_dark',
                height=400,
                font=dict(color="#e2e8f0"),
                plot_bgcolor='rgba(15, 23, 42, 0.3)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
            )
            
            return fig
    except Exception as e:
        print(f"Error creating tissue comparison: {e}")
    
    return None

# ============================================================================
# MAIN APP
# ============================================================================

# Header
st.markdown("""
<div class="header-container">
    <div class="header-title">🧬 Human Protein Atlas (HPA) Gene Expression Explorer</div>
    <div class="header-subtitle">Compare gene expression across normal tissues and cancer cell lines | Interactive visual exploration of transcriptomic data</div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# FILTER PANEL
# ============================================================================
with st.expander("🔍 **Filters & Options**", expanded=True):
    filter_cols = st.columns(4)
    
    # Get unique values from data
    genes_list = sorted(data.iloc[:, 0].unique().astype(str))[:100] if len(data) > 0 else []
    
    with filter_cols[0]:
        selected_genes = st.multiselect(
            "🧬 Select Genes",
            options=genes_list,
            default=genes_list[:2] if len(genes_list) > 1 else genes_list,
            key="gene_filter"
        )
    
    with filter_cols[1]:
        # Try to get cell lines from data
        cell_lines_list = []
        for col in data.columns:
            if 'cell' in col.lower() or 'cancer' in col.lower() or 'sample' in col.lower():
                cell_lines_list = sorted(data[col].unique().astype(str))
                break
        
        selected_cell_lines = st.multiselect(
            "🧫 Select Cell Lines/Samples",
            options=cell_lines_list[:20] if cell_lines_list else ['All'],
            default=cell_lines_list[:3] if len(cell_lines_list) > 2 else cell_lines_list,
            key="cell_line_filter"
        )
    
    with filter_cols[2]:
        min_expression = st.slider(
            "📈 Min Expression Level",
            0.0, 20.0, 0.0, 0.5
        )
    
    with filter_cols[3]:
        st.info("✅ Data Loaded Successfully")

# ============================================================================
# MAIN TABS
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview", 
    "🔬 Gene Search", 
    "🧫 Cell Line Search", 
    "🧪 Compare",
    "🗂️ Dataset Browser"
])

# ======================= TAB 1: OVERVIEW =======================
with tab1:
    st.markdown("### 📊 Dataset Overview")
    
    # Metrics
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        create_metric_card("Total Genes", len(data), "in dataset")
    
    with metric_cols[1]:
        create_metric_card("Total Samples", data.shape[1], "columns")
    
    with metric_cols[2]:
        create_metric_card("Total Records", len(data), "rows")
    
    with metric_cols[3]:
        numeric_data = data.select_dtypes(include=[np.number])
        if len(numeric_data) > 0:
            create_metric_card(
                "Mean Expression",
                numeric_data.values.flatten().mean(),
                f"±{numeric_data.values.flatten().std():.2f}"
            )
    
    st.markdown("---")
    
    # Chart Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Expression Distribution</div>', unsafe_allow_html=True)
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            fig = px.histogram(
                data[numeric_cols.iloc[0]],
                nbins=30,
                title="",
                labels={'value': 'Expression Level', 'count': 'Frequency'}
            )
            fig.update_layout(
                template='plotly_dark',
                height=350,
                font=dict(color="#e2e8f0"),
                plot_bgcolor='rgba(15, 23, 42, 0.3)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Data Summary Statistics</div>', unsafe_allow_html=True)
        
        numeric_data = data.select_dtypes(include=[np.number])
        if len(numeric_data) > 0:
            summary_stats = numeric_data.describe().T.round(2)
            st.dataframe(summary_stats, use_container_width=True, height=300)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ======================= TAB 2: GENE SEARCH =======================
with tab2:
    st.markdown("### 🔬 Gene Search & Expression Analysis")
    st.write("Look up individual genes and see their expression levels across tissues and cell lines.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        gene_search = st.text_input("🔍 Search for a gene:", placeholder="Enter gene name or symbol")
    
    with col2:
        search_type = st.radio("Search Type:", ["Exact Match", "Contains"], horizontal=True)
    
    if gene_search:
        # Search in first column (assumed to be gene names)
        if search_type == "Exact Match":
            matches = data[data.iloc[:, 0].astype(str) == gene_search]
        else:
            matches = data[data.iloc[:, 0].astype(str).str.contains(gene_search, case=False, na=False)]
        
        if len(matches) > 0:
            st.success(f"✅ Found {len(matches)} gene(s) matching '{gene_search}'")
            
            # Display gene details
            st.markdown("#### Gene Expression Details")
            
            # Create visualization
            numeric_cols = matches.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                fig = px.bar(
                    x=numeric_cols,
                    y=matches.iloc[0][numeric_cols].values,
                    title=f"Expression Profile: {gene_search}",
                    labels={'x': 'Sample', 'y': 'Expression (nTPM)'},
                    color=matches.iloc[0][numeric_cols].values,
                    color_continuous_scale='Viridis'
                )
                
                fig.update_layout(
                    template='plotly_dark',
                    height=400,
                    font=dict(color="#e2e8f0"),
                    plot_bgcolor='rgba(15, 23, 42, 0.3)',
                    paper_bgcolor='rgba(0, 0, 0, 0)',
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Show data table
            st.markdown("#### Full Expression Data")
            st.dataframe(matches, use_container_width=True)
        else:
            st.warning(f"❌ No genes found matching '{gene_search}'")

# ======================= TAB 3: CELL LINE SEARCH =======================
with tab3:
    st.markdown("### 🧫 Cell Line / Sample Search")
    st.write("Browse and analyze expression data for specific cell lines or tissue samples.")
    
    # Try to identify cell line column
    cell_line_col = None
    for col in data.columns:
        if 'cell' in col.lower() or 'cancer' in col.lower() or 'sample' in col.lower():
            cell_line_col = col
            break
    
    if cell_line_col:
        unique_cell_lines = sorted(data[cell_line_col].unique().astype(str))
        
        selected_cell_line = st.selectbox(
            "🧫 Select a Cell Line:",
            options=unique_cell_lines[:50]
        )
        
        if selected_cell_line:
            cell_line_data = data[data[cell_line_col] == selected_cell_line]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Genes in Dataset", len(data))
            
            with col2:
                st.metric("Expression Samples", len(cell_line_data))
            
            # Show top genes for this cell line
            st.markdown(f"#### Top Expressed Genes in {selected_cell_line}")
            
            numeric_cols = data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                cell_line_expr = data.iloc[:, 1:].mean(axis=1) if data.shape[1] > 1 else data.iloc[:, 0]
                top_genes = pd.DataFrame({
                    'Gene': data.iloc[:, 0],
                    'Expression': cell_line_expr
                }).nlargest(20, 'Expression')
                
                fig = px.bar(
                    top_genes,
                    x='Gene',
                    y='Expression',
                    title=f"Top 20 Expressed Genes",
                    color='Expression',
                    color_continuous_scale='Viridis'
                )
                
                fig.update_layout(
                    template='plotly_dark',
                    height=400,
                    font=dict(color="#e2e8f0"),
                    plot_bgcolor='rgba(15, 23, 42, 0.3)',
                    paper_bgcolor='rgba(0, 0, 0, 0)',
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("ℹ️ Cell line column not detected. Please check your data format.")

# ======================= TAB 4: COMPARE =======================
with tab4:
    st.markdown("### 🧪 Gene Expression Comparison")
    st.write("Compare expression of selected genes across normal tissue vs cancer cell lines.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        genes_to_compare = st.multiselect(
            "Select genes to compare:",
            options=genes_list[:50],
            default=genes_list[:2] if len(genes_list) > 1 else genes_list,
        )
    
    with col2:
        st.info("✅ Select 1-5 genes for best visualization")
    
    if genes_to_compare:
        # Create comparison visualization
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            fig = go.Figure()
            
            for gene in genes_to_compare:
                gene_data = data[data.iloc[:, 0].astype(str) == gene]
                if len(gene_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=numeric_cols,
                        y=gene_data.iloc[0][numeric_cols].values,
                        mode='lines+markers',
                        name=gene,
                        marker=dict(size=8),
                        line=dict(width=2)
                    ))
            
            fig.update_layout(
                title="Gene Expression Comparison Across Samples",
                xaxis_title="Sample",
                yaxis_title="Expression (nTPM)",
                template='plotly_dark',
                height=500,
                font=dict(color="#e2e8f0"),
                plot_bgcolor='rgba(15, 23, 42, 0.3)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Statistics table
            st.markdown("#### Comparison Statistics")
            
            comparison_stats = []
            for gene in genes_to_compare:
                gene_data = data[data.iloc[:, 0].astype(str) == gene]
                if len(gene_data) > 0:
                    numeric_vals = gene_data.iloc[0][numeric_cols].values
                    comparison_stats.append({
                        'Gene': gene,
                        'Mean': f"{numeric_vals.mean():.2f}",
                        'Std Dev': f"{numeric_vals.std():.2f}",
                        'Min': f"{numeric_vals.min():.2f}",
                        'Max': f"{numeric_vals.max():.2f}"
                    })
            
            if comparison_stats:
                st.dataframe(pd.DataFrame(comparison_stats), use_container_width=True)

# ======================= TAB 5: DATASET BROWSER =======================
with tab5:
    st.markdown("### 🗂️ Dataset Browser")
    st.write("Explore the complete dataset with sorting and filtering options.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sort_by = st.selectbox("Sort by:", list(data.columns)[:5])
    
    with col2:
        ascending = st.checkbox("Ascending order", value=True)
    
    # Display data
    display_data = data.sort_values(by=sort_by, ascending=ascending) if sort_by in data.columns else data
    
    st.dataframe(
        display_data,
        use_container_width=True,
        height=500
    )
    
    # Download options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = display_data.to_csv(index=False)
        st.download_button(
            "📥 Download as CSV",
            csv,
            "hpa_expression_data.csv",
            "text/csv"
        )
    
    with col2:
        st.metric("Total Records", len(display_data))
    
    with col3:
        st.metric("Total Columns", display_data.shape[1])

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<div style='text-align: center; color: #64748b; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid rgba(6, 182, 212, 0.1);'>
    <small>🧬 Human Protein Atlas (HPA) Gene Expression Explorer | Built with Streamlit & Plotly</small>
    <br>
    <small>Compare normal tissue vs cancer cell line expression | Interactive transcriptomic data visualization</small>
</div>
""", unsafe_allow_html=True)
