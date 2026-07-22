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
# PAGE CONFIG & SLEEK BLACK THEME
# ============================================================================
st.set_page_config(
    page_title="HPA Gene Expression Explorer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Sleek Dark/Black UI with polished panels & tags
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #090a0f;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Header Card */
    .header-container {
        background: #12151e;
        border: 1px solid #1e2638;
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .header-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin-bottom: 0.3rem;
    }
    .header-subtitle {
        font-size: 0.95rem;
        color: #94a3b8;
    }
    
    /* Expander / Filter Panel Fixes */
    div[data-testid="stExpander"] {
        background: #12151e !important;
        border: 1px solid #1e2638 !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3) !important;
    }
    div[data-testid="stExpander"] summary {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Custom Styling for Select Chips */
    span[data-baseweb="tag"] {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
        border: 1px solid #334155 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    
    /* Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #12151e;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #1e2638;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #94a3b8;
        font-weight: 600;
        padding: 10px 22px;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] [data-baseweb="tab"] {
        background: #0284c7 !important;
        color: #ffffff !important;
        font-weight: 700;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);
    }
    
    /* Metric Cards */
    .metric-card {
        background: #12151e;
        border: 1px solid #1e2638;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
        transition: all 0.2s ease;
    }
    .metric-card:hover {
        border-color: #0284c7;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(2, 132, 199, 0.15);
    }
    .metric-value {
        font-size: 2.3rem;
        font-weight: 800;
        color: #38bdf8;
        margin: 6px 0;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 700;
    }
    
    /* Chart Containers */
    .chart-container {
        background: #12151e;
        border: 1px solid #1e2638;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    }
    .chart-title {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 12px;
    }
    
    /* Primary Buttons */
    .stButton > button {
        background: #0284c7;
        color: #ffffff;
        border: none;
        border-radius: 8px;
        font-weight: 700;
        padding: 10px 24px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: #0369a1;
        box-shadow: 0 4px 15px rgba(2, 132, 199, 0.4);
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
        data = pd.read_excel(target_file, engine='openpyxl')
        
        if data.empty:
            return None, f"File '{target_file.name}' was found, but it contains 0 rows/data."
        
        data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_')
        return data, target_file.name
    
    except Exception as e:
        return None, str(e)

raw_data, status_msg = load_hpa_data()

if raw_data is None:
    st.error(f"❌ Error loading dataset: {status_msg}")
    st.info(f"📁 Files detected in current directory: {os.listdir('.')}")
    st.stop()

def create_metric_card(label, value, subtext=""):
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value:,.0f}</div>
        <div style="font-size: 0.8rem; color: #94a3b8;">{subtext}</div>
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
# INTERACTIVE GLOBAL FILTER PANEL
# ============================================================================
with st.expander("🔍 **Global Filter Controls**", expanded=True):
    filter_cols = st.columns(4)
    
    all_genes = sorted(raw_data.iloc[:, 0].unique().astype(str)) if len(raw_data) > 0 else []
    numeric_cols_all = raw_data.select_dtypes(include=[np.number]).columns.tolist()
    
    with filter_cols[0]:
        selected_genes = st.multiselect(
            "🧬 Filter Genes",
            options=all_genes,
            default=all_genes[:5] if len(all_genes) >= 5 else all_genes,
            key="gene_filter"
        )
    
    with filter_cols[1]:
        selected_samples = st.multiselect(
            "🧫 Filter Samples / Columns",
            options=numeric_cols_all,
            default=numeric_cols_all[:10] if len(numeric_cols_all) >= 10 else numeric_cols_all,
            key="sample_filter"
        )
    
    with filter_cols[2]:
        min_expression = st.slider(
            "📈 Min Expression Value",
            float(0.0), 
            float(raw_data[numeric_cols_all].max().max() if numeric_cols_all else 100.0), 
            float(0.0), 
            0.5
        )
    
    with filter_cols[3]:
        st.success(f"✅ Active File: {status_msg}")

# ============================================================================
# APPLY FILTERS DYNAMICALLY TO DATASET
# ============================================================================
data = raw_data.copy()

if selected_genes:
    data = data[data.iloc[:, 0].astype(str).isin(selected_genes)]

gene_col = [data.columns[0]]
if selected_samples:
    keep_cols = gene_col + [c for c in selected_samples if c in data.columns]
    data = data[keep_cols]

numeric_cols = data.select_dtypes(include=[np.number]).columns
if len(numeric_cols) > 0 and min_expression > 0:
    data = data[(data[numeric_cols] >= min_expression).any(axis=1)]

# ============================================================================
# CUSTOM TABS
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
        create_metric_card("Active Genes", len(data), "filtered genes")
    
    with metric_cols[1]:
        create_metric_card("Active Samples", len(numeric_cols), "selected columns")
    
    with metric_cols[2]:
        create_metric_card("Total Rows", len(data), "matching rows")
    
    with metric_cols[3]:
        if len(numeric_cols) > 0 and len(data) > 0:
            avg_val = data[numeric_cols].values.flatten().mean()
            std_val = data[numeric_cols].values.flatten().std()
            create_metric_card("Mean Expression", avg_val, f"±{std_val:.2f}")
        else:
            create_metric_card("Mean Expression", 0, "No data")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Expression Distribution Spectrum</div>', unsafe_allow_html=True)
        
        if len(numeric_cols) > 0 and len(data) > 0:
            fig = px.histogram(
                data[numeric_cols].values.flatten(),
                nbins=25,
                color_discrete_sequence=['#38bdf8'],
                labels={'value': 'Expression Level', 'count': 'Frequency'}
            )
            fig.update_layout(
                template='plotly_dark',
                height=350,
                font=dict(color="#f1f5f9", family="Inter"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                showlegend=False,
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
        else:
            st.warning("No data available with current filter settings.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.markdown('<div class="chart-title">Data Summary Metrics</div>', unsafe_allow_html=True)
        
        if len(numeric_cols) > 0 and len(data) > 0:
            summary_stats = data[numeric_cols].describe().T.round(2)
            st.dataframe(summary_stats, use_container_width=True, height=350)
        else:
            st.warning("No data available.")
            
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
                    font=dict(color="#f1f5f9", family="Inter"),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Tabular Expression Data")
            st.dataframe(matches, use_container_width=True)
        else:
            st.warning(f"❌ No genes found matching '{gene_search}' in filtered dataset")

# ======================= TAB 3: SAMPLE PROFILER =======================
with tab3:
    st.markdown("### 🧫 Sample & Cell Line Exploration")
    st.write("Analyze characterization and top gene expression levels for specific tissue profiles.")
    
    if len(numeric_cols) > 0 and len(data) > 0:
        st.markdown("#### Top Expressed Genes Across Filtered Dataset")
        
        gene_means = data.set_index(data.columns[0])[numeric_cols].mean(axis=1).reset_index()
        gene_means.columns = ['Gene', 'Expression']
        top_genes = gene_means.nlargest(20, 'Expression')
        
        fig = px.bar(
            top_genes,
            x='Gene',
            y='Expression',
            title="Top Expressed Genes",
            color='Expression',
            color_continuous_scale='Plasma'
        )
        
        fig.update_layout(
            template='plotly_dark',
            height=420,
            font=dict(color="#f1f5f9", family="Inter"),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis_tickangle=-45
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No samples/data available under current filter settings.")

# ======================= TAB 4: CROSS-GENE ANALYSIS =======================
with tab4:
    st.markdown("### 🔄 Multi-Gene Comparative Profiling")
    st.write("Compare expression trajectories of selected genes across normal tissue vs cancer samples.")
    
    if len(data) > 0 and len(numeric_cols) > 0:
        available_genes = data.iloc[:, 0].unique().tolist()
        genes_to_compare = st.multiselect(
            "Select genes to compare from active dataset:",
            options=available_genes,
            default=available_genes[:3] if len(available_genes) >= 3 else available_genes
        )
        
        if genes_to_compare:
            fig = go.Figure()
            
            colors = ['#38bdf8', '#f43f5e', '#34d399', '#fbbf24', '#c084fc']
            
            for idx, gene in enumerate(genes_to_compare):
                gene_data = data[data.iloc[:, 0].astype(str) == gene]
                if len(gene_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=numeric_cols,
                        y=gene_data.iloc[0][numeric_cols].values,
                        mode='lines+markers',
                        name=gene,
                        marker=dict(size=8),
                        line=dict(width=2.5, color=colors[idx % len(colors)])
                    ))
            
            fig.update_layout(
                title="Gene Expression Dynamics Across Samples",
                xaxis_title="Sample",
                yaxis_title="Expression (nTPM)",
                template='plotly_dark',
                height=480,
                font=dict(color="#f1f5f9", family="Inter"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                hovermode='x unified'
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
    else:
        st.warning("No data available to compare under current filters.")

# ======================= TAB 5: DATA REPOSITORY =======================
with tab5:
    st.markdown("### 📁 Dataset Explorer & Export")
    st.write("Browse complete raw dataset records, sort features, and export results.")
    
    if len(data) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            sort_by = st.selectbox("Sort records by:", list(data.columns))
        
        with col2:
            ascending = st.checkbox("Ascending order", value=True)
        
        display_data = data.sort_values(by=sort_by, ascending=ascending)
        
        st.dataframe(
            display_data,
            use_container_width=True,
            height=500
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv = display_data.to_csv(index=False)
            st.download_button(
                "📥 Export Active Filtered Data (CSV)",
                csv,
                "hpa_filtered_expression_data.csv",
                "text/csv"
            )
        
        with col2:
            st.metric("Total Rows", len(display_data))
        
        with col3:
            st.metric("Total Columns", display_data.shape[1])
    else:
        st.warning("No dataset rows match current filters.")

# ============================================================================
# FOOTER
# ============================================================================
st.markdown("""
<div style='text-align: center; color: #64748b; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #1e2638;'>
    <small>🧬 Human Protein Atlas (HPA) Gene Expression Explorer | Built with Streamlit & Plotly</small>
</div>
""", unsafe_allow_html=True)
