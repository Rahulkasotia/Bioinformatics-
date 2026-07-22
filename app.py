import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from pathlib import Path
import os
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PAGE CONFIG & HIGH-CONTRAST MONOCHROME THEME
# ============================================================================
st.set_page_config(
    page_title="HPA Gene Expression Explorer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for crisp Black/White UI with glowing interactive elements
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #080808;
        color: #ffffff;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Styling */
    .header-container {
        background: #000000;
        border: 1px solid #333333;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.05);
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .header-container:hover {
        border-color: #ffffff;
        transform: translateY(-2px);
    }
    .header-title {
        font-size: 2.3rem;
        font-weight: 900;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin-bottom: 0.4rem;
    }
    .header-subtitle {
        font-size: 0.95rem;
        color: #a1a1aa;
    }
    
    /* Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: #111111;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid #222222;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #888888;
        font-weight: 600;
        padding: 10px 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .stTabs [aria-selected="true"] [data-baseweb="tab"] {
        background: #ffffff !important;
        color: #000000 !important;
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.4);
        font-weight: 800;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #0d0d0d;
        border: 1px solid #262626;
        border-radius: 12px;
        padding: 22px;
        text-align: center;
        transition: all 0.3s ease;
    }
    .metric-card:hover {
        border-color: #ffffff;
        transform: translateY(-4px);
        box-shadow: 0 8px 25px rgba(255, 255, 255, 0.1);
    }
    .metric-value {
        font-size: 2.4rem;
        font-weight: 900;
        color: #ffffff;
        margin: 8px 0;
    }
    .metric-label {
        font-size: 0.8rem;
        color: #a1a1aa;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 700;
    }
    
    /* Chart Containers */
    .chart-container {
        background: #0d0d0d;
        border: 1px solid #222222;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s ease;
    }
    .chart-container:hover {
        border-color: #444444;
        box-shadow: 0 4px 20px rgba(255, 255, 255, 0.03);
    }
    .chart-title {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 15px;
    }
    
    /* Filter Controls Styling */
    .stExpander {
        background: #0a0a0a !important;
        border: 1px solid #262626 !important;
        border-radius: 12px !important;
    }
    
    .stButton > button {
        background: #ffffff;
        color: #000000;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        padding: 10px 24px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background: #e6e6e6;
        transform: scale(1.02);
        box-shadow: 0 0 15px rgba(255, 255, 255, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# DATA LOADING
# ============================================================================

@st.cache_data
def load_hpa_data():
    """Dynamically find and load any Excel file in the working directory"""
    try:
        search_dirs = [Path("."), Path("/mount/src")]
        excel_files = []
        
        for search_dir in search_dirs:
            if search_dir.exists():
                excel_files.extend(list(search_dir.rglob("*.xlsx")))
        
        if not excel_files:
            return None, "No .xlsx files found in the repository root directory."
        
        target_file = excel_files[0]
        
        # Parse Excel with openpyxl engine
        data = pd.read_excel(target_file, engine='openpyxl')
        
        if data.empty:
            return None, f"File '{target_file.name}' was found, but it contains 0 rows/data."
        
        # Standardize column names
        data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')
        
        return data, target_file.name
    
    except Exception as e:
        return None, str(e)

# Load data at startup
data, status_msg = load_hpa_data()

if data is None:
    st.error(f"❌ Error loading dataset: {status_msg}")
    st.info(f"📁 Files detected in current directory: {os.listdir('.')}")
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
        <div style="font-size: 0.8rem; color: #71717a;">{subtext}</div>
    </div>
    """, unsafe_allow_html=True)

# ============================================================================
# MAIN HEADER
# ============================================================================

st.markdown("""
<div class="header-container">
    <div class="header-title">🧬 Human Protein Atlas (HPA) Gene Expression Explorer</div>
    <div class="header-subtitle">Compare gene expression across normal tissues and cancer cell lines | Interactive transcriptomic profiling</div>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# FILTER PANEL
# ============================================================================
with st.expander("🔍 **Filter & Search Controls**", expanded=True):
    filter_cols = st.columns(4)
    
    genes_list = sorted(data.iloc[:, 0].unique().astype(str))[:100] if len(data) > 0 else []
    
    with filter_cols[0]:
        selected_genes = st.multiselect(
            "🧬 Select Genes",
            options=genes_list,
            default=genes_list[:2] if len(genes_list) > 1 else genes_list,
            key="gene_filter"
        )
    
    with filter_cols[1]:
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
            "📈 Min Expression Threshold",
            0.0, 20.0, 0.0, 0.5
        )
    
    with filter_cols[3]:
        st.success(f"✅ Active Dataset: {status_msg}")

# ============================================================================
# CUSTOM TABS (RENAMED)
# ============================================================================
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Summary & Stats", 
    "🔍 Gene Expression Lookup", 
    "🧫 Sample Profiler", 
    "🔄 Cross-Gene Analysis",
    "📁 Data Repository"
])

# ======================= TAB 1: SUMMARY & STATS =======================
with tab1:
    st.markdown("### 📊 Dataset Overview")
    
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
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Expression Distribution Spectrum</div>', unsafe_allow_html=True)
        
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            fig = px.histogram(
                data[numeric_cols[0]],
                nbins=30,
                color_discrete_sequence=['#FF007F'],
                labels={'value': 'Expression Level', 'count': 'Frequency'}
            )
            fig.update_layout(
                template='plotly_dark',
                height=350,
                font=dict(color="#ffffff"),
                plot_bgcolor='rgba(0, 0, 0, 0)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                showlegend=False,
                transition_duration=500
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Data Summary Metrics</div>', unsafe_allow_html=True)
        
        numeric_data = data.select_dtypes(include=[np.number])
        if len(numeric_data) > 0:
            summary_stats = numeric_data.describe().T.round(2)
            st.dataframe(summary_stats, use_container_width=True, height=300)
        
        st.markdown('</div>', unsafe_allow_html=True)

# ======================= TAB 2: GENE EXPRESSION LOOKUP =======================
with tab2:
    st.markdown("### 🔍 Target Gene Lookup & Profiling")
    st.write("Examine individual gene profiles and expression variation across samples.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        gene_search = st.text_input("🔍 Search for a gene symbol:", placeholder="e.g. TP53, BRCA1")
    
    with col2:
        search_type = st.radio("Search Type:", ["Exact Match", "Contains"], horizontal=True)
    
    if gene_search:
        if search_type == "Exact Match":
            matches = data[data.iloc[:, 0].astype(str) == gene_search]
        else:
            matches = data[data.iloc[:, 0].astype(str).str.contains(gene_search, case=False, na=False)]
        
        if len(matches) > 0:
            st.success(f"✅ Found {len(matches)} gene(s) matching '{gene_search}'")
            
            st.markdown("#### Expression Intensity Profile")
            
            numeric_cols = matches.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                fig = px.bar(
                    x=numeric_cols,
                    y=matches.iloc[0][numeric_cols].values,
                    title=f"Expression Intensity: {gene_search}",
                    labels={'x': 'Sample', 'y': 'Expression (nTPM)'},
                    color=matches.iloc[0][numeric_cols].values,
                    color_continuous_scale='Turbo'
                )
                
                fig.update_layout(
                    template='plotly_dark',
                    height=420,
                    font=dict(color="#ffffff"),
                    plot_bgcolor='rgba(0, 0, 0, 0)',
                    paper_bgcolor='rgba(0, 0, 0, 0)',
                    xaxis_tickangle=-45,
                    transition_duration=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Tabular Expression Data")
            st.dataframe(matches, use_container_width=True)
        else:
            st.warning(f"❌ No genes found matching '{gene_search}'")

# ======================= TAB 3: SAMPLE PROFILER =======================
with tab3:
    st.markdown("### 🧫 Sample & Cell Line Exploration")
    st.write("Analyze characterization and top gene expression levels for specific tissue profiles.")
    
    cell_line_col = None
    for col in data.columns:
        if 'cell' in col.lower() or 'cancer' in col.lower() or 'sample' in col.lower():
            cell_line_col = col
            break
    
    if cell_line_col:
        unique_cell_lines = sorted(data[cell_line_col].unique().astype(str))
        
        selected_cell_line = st.selectbox(
            "🧫 Select a Cell Line / Sample:",
            options=unique_cell_lines[:50]
        )
        
        if selected_cell_line:
            cell_line_data = data[data[cell_line_col] == selected_cell_line]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("Genes in Dataset", len(data))
            
            with col2:
                st.metric("Expression Samples", len(cell_line_data))
            
            st.markdown(f"#### Top Expressed Genes in {selected_cell_line}")
            
            numeric_data = data.select_dtypes(include=[np.number])
            if not numeric_data.empty:
                cell_line_expr = numeric_data.mean(axis=1)
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
                    color_continuous_scale='Plasma'
                )
                
                fig.update_layout(
                    template='plotly_dark',
                    height=420,
                    font=dict(color="#ffffff"),
                    plot_bgcolor='rgba(0, 0, 0, 0)',
                    paper_bgcolor='rgba(0, 0, 0, 0)',
                    xaxis_tickangle=-45,
                    transition_duration=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
    else:
        numeric_data = data.select_dtypes(include=[np.number])
        if not numeric_data.empty:
            st.markdown("#### Top Expressed Genes Across Dataset")
            cell_line_expr = numeric_data.mean(axis=1)
            top_genes = pd.DataFrame({
                'Gene': data.iloc[:, 0],
                'Expression': cell_line_expr
            }).nlargest(20, 'Expression')
            
            fig = px.bar(
                top_genes,
                x='Gene',
                y='Expression',
                title="Top 20 Expressed Genes Overall",
                color='Expression',
                color_continuous_scale='Plasma'
            )
            
            fig.update_layout(
                template='plotly_dark',
                height=420,
                font=dict(color="#ffffff"),
                plot_bgcolor='rgba(0, 0, 0, 0)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                xaxis_tickangle=-45,
                transition_duration=500
            )
            
            st.plotly_chart(fig, use_container_width=True)

# ======================= TAB 4: CROSS-GENE ANALYSIS =======================
with tab4:
    st.markdown("### 🔄 Multi-Gene Comparative Profiling")
    st.write("Compare expression trajectories of selected genes across normal tissue vs cancer samples.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        genes_to_compare = st.multiselect(
            "Select genes to compare:",
            options=genes_list[:50],
            default=genes_list[:2] if len(genes_list) > 1 else genes_list,
        )
    
    with col2:
        st.info("💡 Tip: Select 2-5 genes for optimal visual contrast")
    
    if genes_to_compare:
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) > 0:
            fig = go.Figure()
            
            colors = ['#00E5FF', '#FF007F', '#00FF66', '#FFB300', '#9D00FF']
            
            for idx, gene in enumerate(genes_to_compare):
                gene_data = data[data.iloc[:, 0].astype(str) == gene]
                if len(gene_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=numeric_cols,
                        y=gene_data.iloc[0][numeric_cols].values,
                        mode='lines+markers',
                        name=gene,
                        marker=dict(size=9, symbol='circle'),
                        line=dict(width=3, color=colors[idx % len(colors)])
                    ))
            
            fig.update_layout(
                title="Gene Expression Dynamics Across Samples",
                xaxis_title="Sample",
                yaxis_title="Expression (nTPM)",
                template='plotly_dark',
                height=520,
                font=dict(color="#ffffff"),
                plot_bgcolor='rgba(0, 0, 0, 0)',
                paper_bgcolor='rgba(0, 0, 0, 0)',
                hovermode='x unified',
                transition_duration=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Comparative Expression Statistics")
            
            comparison_stats = []
            for gene in genes_to_compare:
                gene_data = data[data.iloc[:, 0].astype(str) == gene]
                if len(gene_data) > 0:
                    numeric_vals = gene_data.iloc[0][numeric_cols].values
                    comparison_stats.append({
                        'Gene': gene,
                        'Mean Expression': f"{numeric_vals.mean():.2f}",
                        'Std Dev': f"{numeric_vals.std():.2f}",
                        'Min Value': f"{numeric_vals.min():.2f}",
                        'Max Value': f"{numeric_vals.max():.2f}"
                    })
            
            if comparison_stats:
                st.dataframe(pd.DataFrame(comparison_stats), use_container_width=True)

# ======================= TAB 5: DATA REPOSITORY =======================
with tab5:
    st.markdown("### 📁 Dataset Explorer & Export")
    st.write("Browse complete raw dataset records, sort features, and export results.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sort_by = st.selectbox("Sort records by:", list(data.columns)[:5])
    
    with col2:
        ascending = st.checkbox("Ascending order", value=True)
    
    display_data = data.sort_values(by=sort_by, ascending=ascending) if sort_by in data.columns else data
    
    st.dataframe(
        display_data,
        use_container_width=True,
        height=500
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        csv = display_data.to_csv(index=False)
        st.download_button(
            "📥 Export to CSV",
            csv,
            "hpa_expression_data.csv",
            "text/csv"
        )
    
    with col2:
        st.metric("Total Records", len(display_data))
    
    with col3:
        st.metric("Total Features", display_data.shape[1])

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<div style='text-align: center; color: #71717a; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #222222;'>
    <small>🧬 Human Protein Atlas (HPA) Gene Expression Explorer | Built with Streamlit & Plotly</small>
</div>
""", unsafe_allow_html=True)
