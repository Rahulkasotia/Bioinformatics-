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
# PAGE CONFIG & MONOCHROME BLACK & WHITE THEME
# ============================================================================
st.set_page_config(
    page_title="HPA Gene Expression Explorer",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Pure Black/White UI & Clean Multi-select Styling
st.markdown("""
<style>
    /* Main Background */
    .stApp {
        background-color: #000000;
        color: #f8fafc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Change red borders/focus rings in multi-selects to clean white/gray */
    div[data-baseweb="select"] > div {
        border-color: #3f3f46 !important;
    }
    div[data-baseweb="select"] div:focus, div[data-baseweb="select"] div:active {
        border-color: #ffffff !important;
        box-shadow: 0 0 0 1px #ffffff !important;
    }
    
    /* Header Card */
    .header-container {
        background: #0a0a0a;
        border: 1px solid #262626;
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.8);
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
        color: #a1a1aa;
    }
    
    /* Expander / Filter Panel Fixes */
    div[data-testid="stExpander"] {
        background: #0a0a0a !important;
        border: 1px solid #262626 !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6) !important;
    }
    div[data-testid="stExpander"] summary {
        color: #ffffff !important;
        font-weight: 700 !important;
    }
    
    /* Custom Styling for Select Chips */
    span[data-baseweb="tag"] {
        background-color: #27272a !important;
        color: #ffffff !important;
        border: 1px solid #3f3f46 !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
    }
    
    /* Navigation Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #0a0a0a;
        padding: 6px;
        border-radius: 12px;
        border: 1px solid #262626;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 8px;
        color: #a1a1aa;
        font-weight: 600;
        padding: 10px 22px;
        border: none !important;
        transition: all 0.2s ease;
    }
    .stTabs [aria-selected="true"] [data-baseweb="tab"] {
        background: #ffffff !important;
        color: #000000 !important;
        font-weight: 800;
        box-shadow: 0 0 20px rgba(255, 255, 255, 0.3);
    }
    
    /* Metric Cards */
    .metric-card {
        background: #0a0a0a;
        border: 1px solid #262626;
        border-radius: 14px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
        transition: all 0.2s ease;
    }
    .metric-card:hover {
        border-color: #ffffff;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(255, 255, 255, 0.1);
    }
    .metric-value {
        font-size: 2.3rem;
        font-weight: 900;
        color: #ffffff;
        margin: 6px 0;
    }
    .metric-label {
        font-size: 0.78rem;
        color: #a1a1aa;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        font-weight: 700;
    }
    
    /* Chart Containers */
    .chart-container {
        background: #0a0a0a;
        border: 1px solid #262626;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.5);
    }
    .chart-title {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 12px;
    }
    
    /* Primary Buttons */
    .stButton > button {
        background: #ffffff;
        color: #000000;
        border: none;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.75rem;
        padding: 4px 8px;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        background: #e4e4e7;
        box-shadow: 0 0 10px rgba(255, 255, 255, 0.4);
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
        <div style="font-size: 0.8rem; color: #a1a1aa;">{subtext}</div>
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
# INTERACTIVE GLOBAL FILTER PANEL WITH FIXED BUTTON LOGIC
# ============================================================================
all_genes = sorted(raw_data.iloc[:, 0].unique().astype(str)) if len(raw_data) > 0 else []
numeric_cols_all = raw_data.select_dtypes(include=[np.number]).columns.tolist()

# Initialize safe session state tracking
if 'selected_genes_val' not in st.session_state:
    st.session_state.selected_genes_val = all_genes[:5] if len(all_genes) >= 5 else all_genes
if 'selected_samples_val' not in st.session_state:
    st.session_state.selected_samples_val = numeric_cols_all[:10] if len(numeric_cols_all) >= 10 else numeric_cols_all

with st.expander("🔍 **Global Filter Controls & Reset**", expanded=True):
    filter_cols = st.columns(4)
    
    with filter_cols[0]:
        st.markdown("**🧬 Filter Genes**")
        selected_genes = st.multiselect(
            "Select specific genes:",
            options=all_genes,
            default=st.session_state.selected_genes_val,
            key="gene_widget",
            label_visibility="collapsed"
        )
        st.session_state.selected_genes_val = selected_genes
        
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            if st.button("Select All", key="all_genes_btn", use_container_width=True):
                st.session_state.selected_genes_val = all_genes
                st.rerun()
        with col_g2:
            if st.button("Clear All", key="clear_genes_btn", use_container_width=True):
                st.session_state.selected_genes_val = []
                st.rerun()
    
    with filter_cols[1]:
        st.markdown("**🧫 Filter Samples**")
        selected_samples = st.multiselect(
            "Select specific samples:",
            options=numeric_cols_all,
            default=st.session_state.selected_samples_val,
            key="sample_widget",
            label_visibility="collapsed"
        )
        st.session_state.selected_samples_val = selected_samples
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("Select All", key="all_samples_btn", use_container_width=True):
                st.session_state.selected_samples_val = numeric_cols_all
                st.rerun()
        with col_s2:
            if st.button("Clear All", key="clear_samples_btn", use_container_width=True):
                st.session_state.selected_samples_val = []
                st.rerun()
    
    with filter_cols[2]:
        st.markdown("**📈 Min Expression**")
        min_expression = st.slider(
            "Min Expression Value",
            float(0.0), 
            float(raw_data[numeric_cols_all].max().max() if numeric_cols_all else 100.0), 
            float(0.0), 
            0.5,
            label_visibility="collapsed"
        )
    
    with filter_cols[3]:
        st.markdown("**⚡ Quick Actions**")
        st.write("") 
        if st.button("🔄 Reset All Filters", key="reset_all_btn", use_container_width=True):
            st.session_state.selected_genes_val = all_genes
            st.session_state.selected_samples_val = numeric_cols_all
            st.rerun()

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
            flat_vals = data[numeric_cols].values.flatten()
            
            fig = px.histogram(
                x=flat_vals,
                nbins=25,
                labels={'x': 'Expression Level', 'y': 'Frequency'}
            )
            fig.update_traces(marker_color=flat_vals, marker_colorscale='Turbo', showlegend=False)
            
            fig.update_layout(
                template='plotly_dark',
                height=350,
                font=dict(color="#f8fafc", family="Inter"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
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
            matches = raw_data[raw_data.iloc[:, 0].astype(str) == gene_search]
        else:
            matches = raw_data[raw_data.iloc[:, 0].astype(str).str.contains(gene_search, case=False, na=False)]
        
        if len(matches) > 0:
            st.success(f"✅ Found {len(matches)} gene(s) matching '{gene_search}'")
            
            st.markdown("#### Expression Intensity Profile")
            
            if len(numeric_cols_all) > 0:
                fig = px.bar(
                    x=numeric_cols_all,
                    y=matches.iloc[0][numeric_cols_all].values,
                    title=f"Expression Intensity: {gene_search}",
                    labels={'x': 'Sample', 'y': 'Expression (nTPM)'},
                    color=matches.iloc[0][numeric_cols_all].values,
                    color_continuous_scale='Turbo'
                )
                
                fig.update_layout(
                    template='plotly_dark',
                    height=420,
                    font=dict(color="#f8fafc", family="Inter"),
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)',
                    xaxis_tickangle=-45
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Tabular Expression Data")
            st.dataframe(matches, use_container_width=True)
        else:
            st.warning(f"❌ No genes found matching '{gene_search}' in dataset")

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
            font=dict(color="#f8fafc", family="Inter"),
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
    
    if len(raw_data) > 0 and len(numeric_cols_all) > 0:
        available_genes = raw_data.iloc[:, 0].unique().tolist()
        genes_to_compare = st.multiselect(
            "Select genes to compare from active dataset:",
            options=available_genes,
            default=available_genes[:3] if len(available_genes) >= 3 else available_genes,
            key="comp_genes"
        )
        
        if genes_to_compare:
            fig = go.Figure()
            
            colors = ['#00ffcc', '#ff007f', '#ffe600', '#00bfff', '#ff5500', '#bf00ff']
            
            for idx, gene in enumerate(genes_to_compare):
                gene_data = raw_data[raw_data.iloc[:, 0].astype(str) == gene]
                if len(gene_data) > 0:
                    fig.add_trace(go.Scatter(
                        x=numeric_cols_all,
                        y=gene_data.iloc[0][numeric_cols_all].values,
                        mode='lines+markers',
                        name=gene,
                        marker=dict(size=8),
                        line=dict(width=3, color=colors[idx % len(colors)])
                    ))
            
            fig.update_layout(
                title="Gene Expression Analysis Overview",
                xaxis_title="Sample",
                yaxis_title="Expression (nTPM)",
                template='plotly_dark',
                height=480,
                font=dict(color="#f8fafc", family="Inter"),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                hovermode='x unified'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("#### Comparative Expression Statistics")
            
            comparison_stats = []
            for gene in genes_to_compare:
                gene_data = raw_data[raw_data.iloc[:, 0].astype(str) == gene]
                if len(gene_data) > 0:
                    numeric_vals = gene_data.iloc[0][numeric_cols_all].values
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
<div style='text-align: center; color: #71717a; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid #262626;'>
    <small>🧬 Human Protein Atlas (HPA) Gene Expression Explorer | Built with Streamlit & Plotly</small>
</div>
""", unsafe_allow_html=True)
