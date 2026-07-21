import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from datetime import datetime
import duckdb

# ============================================================================
# PAGE CONFIG & THEMING
# ============================================================================
st.set_page_config(
    page_title="Bioinformatics Profiler",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    * {
        margin: 0;
        padding: 0;
    }
    
    body {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Header Styling */
    .header-container {
        background: linear-gradient(90deg, #06b6d4 0%, #0891b2 100%);
        padding: 1.5rem 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        font-size: 2.5rem;
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
        margin-bottom: 1rem;
    }
    
    /* Navigation Tabs */
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
    
    /* Metric Cards */
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
    
    /* Filter Panel */
    .filter-panel {
        background: rgba(15, 23, 42, 0.5);
        border: 1px solid rgba(6, 182, 212, 0.15);
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 20px;
    }
    
    .filter-title {
        color: #06b6d4;
        font-weight: 700;
        font-size: 0.95rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 12px;
    }
    
    /* Chart Container */
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
    
    /* Data Table */
    .dataframe {
        background: rgba(15, 23, 42, 0.3) !important;
        border-radius: 8px !important;
    }
    
    /* Button Styling */
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
    
    /* Success Badge */
    .success-badge {
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 6px;
        padding: 8px 12px;
        color: #10b981;
        font-size: 0.85rem;
        font-weight: 600;
        display: inline-block;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 23, 42, 0.3);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(6, 182, 212, 0.4);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(6, 182, 212, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

@st.cache_data
def load_sample_data():
    """Generate sample bioinformatics dataset"""
    np.random.seed(42)
    
    # Sample tissues/cell lines
    tissues = ['Kidney', 'Heart', 'Brain', 'Liver', 'Lung']
    cell_lines = [
        'Normal-K1', 'Normal-K2', 'Normal-K3',
        'Cancer-C1', 'Cancer-C2', 'Cancer-C3',
        'Disease-D1', 'Disease-D2'
    ]
    
    # Generate genes
    genes = [f"GENE_{i:04d}" for i in range(1, 151)]
    
    data = []
    for gene in genes:
        for tissue in tissues:
            for cell_line in cell_lines:
                data.append({
                    'Gene': gene,
                    'Tissue': tissue,
                    'Cell_Line': cell_line,
                    'Expression': np.random.exponential(scale=2.5),
                    'p_value': np.random.uniform(0.0001, 0.95),
                    'log2FC': np.random.normal(0, 2),
                    'Sample_Size': np.random.randint(50, 500),
                })
    
    return pd.DataFrame(data)

@st.cache_data
def filter_data(df, tissues, cell_lines, min_expression=0):
    """Filter dataframe based on selections"""
    filtered = df[
        (df['Tissue'].isin(tissues)) &
        (df['Cell_Line'].isin(cell_lines)) &
        (df['Expression'] >= min_expression)
    ]
    return filtered

def create_metric_card(label, value, subtext=""):
    """Create styled metric card"""
    col = st.container()
    col.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value:,.0f}</div>
        <div style="font-size: 0.8rem; color: #64748b;">{subtext}</div>
    </div>
    """, unsafe_allow_html=True)

def create_expression_dist_chart(data):
    """Expression distribution histogram"""
    fig = go.Figure()
    
    for tissue in data['Tissue'].unique():
        tissue_data = data[data['Tissue'] == tissue]['Expression']
        fig.add_trace(go.Histogram(
            x=tissue_data,
            name=tissue,
            opacity=0.7,
            nbinsx=30,
        ))
    
    fig.update_layout(
        title="Expression Distribution by Tissue",
        xaxis_title="Expression Level",
        yaxis_title="Frequency",
        barmode='overlay',
        hovermode='x unified',
        template='plotly_dark',
        height=400,
        font=dict(family="Segoe UI", size=12, color="#e2e8f0"),
        plot_bgcolor='rgba(15, 23, 42, 0.3)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='rgba(148, 163, 184, 0.1)'),
    )
    
    return fig

def create_heatmap_chart(data, top_n=20):
    """Gene expression heatmap"""
    pivot_data = data.groupby(['Gene', 'Tissue'])['Expression'].mean().reset_index()
    heatmap_pivot = pivot_data.pivot(index='Gene', columns='Tissue', values='Expression')
    
    # Get top genes by variance
    top_genes = heatmap_pivot.var(axis=1).nlargest(top_n).index
    heatmap_data = heatmap_pivot.loc[top_genes]
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data.values,
        x=heatmap_data.columns,
        y=heatmap_data.index,
        colorscale='Viridis',
        hovertemplate='<b>%{y}</b><br>%{x}: %{z:.2f}<extra></extra>',
    ))
    
    fig.update_layout(
        title=f"Top {top_n} Genes - Expression Heatmap",
        xaxis_title="Tissue Type",
        yaxis_title="Gene",
        height=500,
        template='plotly_dark',
        font=dict(family="Segoe UI", size=11, color="#e2e8f0"),
        plot_bgcolor='rgba(15, 23, 42, 0.3)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
    )
    
    return fig

def create_volcano_plot(data):
    """Volcano plot: log2FC vs -log10(p_value)"""
    data['neg_log_p'] = -np.log10(data['p_value'] + 1e-300)
    
    # Color points based on significance
    conditions = [
        (data['log2FC'] > 1) & (data['neg_log_p'] > 2),
        (data['log2FC'] < -1) & (data['neg_log_p'] > 2),
    ]
    colors = ['#f43f5e' if c[0] else '#0ea5e9' if c[1] else '#94a3b8' 
              for c in zip(*conditions)]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=data['log2FC'],
        y=data['neg_log_p'],
        mode='markers',
        marker=dict(
            color=colors,
            size=6,
            opacity=0.6,
            line=dict(width=0.5, color='rgba(255, 255, 255, 0.1)')
        ),
        text=data['Gene'],
        hovertemplate='<b>%{text}</b><br>log2FC: %{x:.2f}<br>-log10(p): %{y:.2f}<extra></extra>',
    ))
    
    # Add threshold lines
    fig.add_hline(y=2, line_dash="dash", line_color="rgba(148, 163, 184, 0.3)", 
                  annotation_text="p=0.01", annotation_position="right")
    fig.add_vline(x=1, line_dash="dash", line_color="rgba(148, 163, 184, 0.3)", 
                  annotation_text="log2FC=1", annotation_position="top")
    fig.add_vline(x=-1, line_dash="dash", line_color="rgba(148, 163, 184, 0.3)", 
                  annotation_text="log2FC=-1", annotation_position="top")
    
    fig.update_layout(
        title="Volcano Plot - Differential Expression",
        xaxis_title="log2(Fold Change)",
        yaxis_title="-log10(p-value)",
        height=450,
        template='plotly_dark',
        font=dict(family="Segoe UI", size=12, color="#e2e8f0"),
        plot_bgcolor='rgba(15, 23, 42, 0.3)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        xaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='rgba(148, 163, 184, 0.1)', zeroline=True),
        yaxis=dict(showgrid=True, gridwidth=0.5, gridcolor='rgba(148, 163, 184, 0.1)'),
        hovermode='closest',
    )
    
    return fig

def create_pca_plot(data):
    """PCA-style scatter plot"""
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import StandardScaler
    
    # Prepare data for PCA
    pivot_expr = data.pivot_table(index='Cell_Line', columns='Gene', values='Expression', fill_value=0)
    
    if pivot_expr.shape[1] > 1:
        scaler = StandardScaler()
        scaled = scaler.fit_transform(pivot_expr)
        
        pca = PCA(n_components=2)
        pca_result = pca.fit_transform(scaled)
        
        tissue_mapping = data[['Cell_Line', 'Tissue']].drop_duplicates().set_index('Cell_Line')['Tissue'].to_dict()
        tissues = [tissue_mapping.get(cl, 'Unknown') for cl in pivot_expr.index]
        
        color_map = {t: c for t, c in zip(data['Tissue'].unique(), 
                                          ['#06b6d4', '#f43f5e', '#10b981', '#f59e0b', '#8b5cf6'])}
        
        fig = go.Figure()
        
        for tissue in data['Tissue'].unique():
            mask = np.array(tissues) == tissue
            fig.add_trace(go.Scatter(
                x=pca_result[mask, 0],
                y=pca_result[mask, 1],
                mode='markers',
                name=tissue,
                marker=dict(size=10, color=color_map[tissue], opacity=0.7),
            ))
        
        fig.update_layout(
            title=f"PCA Plot (Explained Variance: PC1={pca.explained_variance_ratio_[0]:.1%}, PC2={pca.explained_variance_ratio_[1]:.1%})",
            xaxis_title=f"PC1 ({pca.explained_variance_ratio_[0]:.1%})",
            yaxis_title=f"PC2 ({pca.explained_variance_ratio_[1]:.1%})",
            height=450,
            template='plotly_dark',
            font=dict(family="Segoe UI", size=12, color="#e2e8f0"),
            plot_bgcolor='rgba(15, 23, 42, 0.3)',
            paper_bgcolor='rgba(0, 0, 0, 0)',
            hovermode='closest',
        )
        
        return fig
    
    return None

def create_tissue_comparison(data):
    """Box plot: Gene expression by tissue"""
    fig = go.Figure()
    
    for tissue in sorted(data['Tissue'].unique()):
        tissue_data = data[data['Tissue'] == tissue]
        fig.add_trace(go.Box(
            y=tissue_data['Expression'],
            name=tissue,
            boxmean='sd',
            marker_color=['#06b6d4', '#f43f5e', '#10b981', '#f59e0b', '#8b5cf6'][
                list(data['Tissue'].unique()).index(tissue)
            ],
        ))
    
    fig.update_layout(
        title="Expression Distribution by Tissue Type",
        yaxis_title="Expression Level",
        height=450,
        template='plotly_dark',
        font=dict(family="Segoe UI", size=12, color="#e2e8f0"),
        plot_bgcolor='rgba(15, 23, 42, 0.3)',
        paper_bgcolor='rgba(0, 0, 0, 0)',
        showlegend=True,
    )
    
    return fig

# ============================================================================
# MAIN APP
# ============================================================================

# Header
st.markdown("""
<div class="header-container">
    <div class="header-title">🧬 Bioinformatics Profiler</div>
    <div class="header-subtitle">Multi-Tissue Gene Expression Analysis & Exploration</div>
</div>
""", unsafe_allow_html=True)

# Load data
data = load_sample_data()

# ============================================================================
# FILTER PANEL (Collapsible, Top)
# ============================================================================
with st.expander("🔍 **Filters & Options**", expanded=True):
    filter_cols = st.columns(4)
    
    with filter_cols[0]:
        selected_tissues = st.multiselect(
            "📊 Select Tissues",
            options=sorted(data['Tissue'].unique()),
            default=sorted(data['Tissue'].unique())[:2],
            key="tissue_filter"
        )
    
    with filter_cols[1]:
        selected_cell_lines = st.multiselect(
            "🧫 Select Cell Lines",
            options=sorted(data['Cell_Line'].unique()),
            default=sorted(data['Cell_Line'].unique())[:3],
            key="cell_line_filter"
        )
    
    with filter_cols[2]:
        min_expression = st.slider(
            "📈 Min Expression Level",
            0.0, 10.0, 0.0, 0.5
        )
    
    with filter_cols[3]:
        p_value_threshold = st.slider(
            "📌 p-value Threshold",
            0.0, 1.0, 0.05, 0.01
        )

# Apply filters
filtered_data = filter_data(data, selected_tissues, selected_cell_lines, min_expression)
filtered_data = filtered_data[filtered_data['p_value'] <= p_value_threshold]

# ============================================================================
# TABS: OVERVIEW | ANALYSIS | DATA
# ============================================================================
tab1, tab2, tab3 = st.tabs(["📊 Overview", "🔬 Analysis", "📋 Data"])

# ======================= TAB 1: OVERVIEW =======================
with tab1:
    # Metrics Row
    st.markdown("### Key Metrics")
    metric_cols = st.columns(4)
    
    with metric_cols[0]:
        create_metric_card("Total Genes", len(filtered_data['Gene'].unique()), "in dataset")
    
    with metric_cols[1]:
        create_metric_card("Cell Lines", len(filtered_data['Cell_Line'].unique()), "analyzed")
    
    with metric_cols[2]:
        create_metric_card("Tissues", len(filtered_data['Tissue'].unique()), "included")
    
    with metric_cols[3]:
        create_metric_card(
            "Mean Expression",
            filtered_data['Expression'].mean(),
            f"±{filtered_data['Expression'].std():.2f}"
        )
    
    # Charts Row 1
    st.markdown("### Expression Patterns")
    chart_cols = st.columns(2)
    
    with chart_cols[0]:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(create_expression_dist_chart(filtered_data), use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    with chart_cols[1]:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        st.plotly_chart(create_tissue_comparison(filtered_data), use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Charts Row 2
    st.markdown("### Gene Expression Heatmap")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(create_heatmap_chart(filtered_data, top_n=15), use_container_width=True, config={'displayModeBar': False})
    st.markdown('</div>', unsafe_allow_html=True)

# ======================= TAB 2: ANALYSIS =======================
with tab2:
    st.markdown("### Advanced Analysis")
    
    analysis_cols = st.columns(2)
    
    with analysis_cols[0]:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        volcano = create_volcano_plot(filtered_data)
        if volcano:
            st.plotly_chart(volcano, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
    
    with analysis_cols[1]:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        pca = create_pca_plot(filtered_data)
        if pca:
            st.plotly_chart(pca, use_container_width=True, config={'displayModeBar': False})
        else:
            st.info("PCA plot requires more data samples.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Summary statistics
    st.markdown("### Statistical Summary")
    summary_data = filtered_data.groupby('Tissue').agg({
        'Expression': ['count', 'mean', 'std', 'min', 'max'],
        'p_value': 'mean',
    }).round(3)
    
    st.dataframe(summary_data, use_container_width=True)

# ======================= TAB 3: DATA =======================
with tab3:
    st.markdown("### Filtered Dataset")
    
    col1, col2 = st.columns(2)
    
    with col1:
        sort_by = st.selectbox("Sort by:", ['Gene', 'Tissue', 'Expression', 'p_value'])
    
    with col2:
        ascending = st.checkbox("Ascending order", value=True)
    
    display_data = filtered_data.sort_values(sort_by, ascending=ascending)
    
    st.dataframe(
        display_data[['Gene', 'Tissue', 'Cell_Line', 'Expression', 'p_value', 'log2FC']],
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
            "gene_expression_data.csv",
            "text/csv"
        )
    
    with col2:
        excel_buffer = display_data.to_excel(index=False)
        st.download_button(
            "📊 Download as Excel",
            excel_buffer,
            "gene_expression_data.xlsx",
            "application/vnd.ms-excel"
        )
    
    with col3:
        st.metric("Total Records", len(display_data))

# Footer
st.markdown("""
<div style='text-align: center; color: #64748b; margin-top: 3rem; padding-top: 2rem; border-top: 1px solid rgba(6, 182, 212, 0.1);'>
    <small>🧬 Bioinformatics Profiler v1.0 | Built with Streamlit, Plotly & DuckDB</small>
</div>
""", unsafe_allow_html=True)
