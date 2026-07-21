# 🎨 Customization & Comparison Guide

## Your Dashboard vs Your Friend's Dashboard

### Layout Differences

| Aspect | Your Friend's | Your New One | Advantage |
|--------|---------------|-------------|-----------|
| **Filter Position** | Left sidebar | Top collapsible | ✅ More space for charts, cleaner look |
| **Navigation** | Tabs at top | Tabs at top | Same approach (clean) |
| **Color Scheme** | Blue/Cyan | Cyan/Teal gradient | ✅ Modern, professional gradient |
| **Chart Layout** | Sequential | Grid-based columns | ✅ Better use of screen space |
| **Header** | Simple text | Gradient banner | ✅ More visually appealing |
| **Data Table** | Sortable | Sortable + Export | ✅ CSV/Excel download buttons |

---

## Color Palette Customization

### Current Colors (Your Dashboard)
```css
Primary:    #06b6d4 (Cyan)
Dark BG:    #0f172a (Navy)
Accent Red: #f43f5e (Rose)
Success:    #10b981 (Green)
Warning:    #f59e0b (Amber)
Purple:     #8b5cf6 (Violet)
```

### Preset Color Schemes You Can Use

#### Option 1: Deep Ocean (Cool & Professional)
```css
Primary:    #0ea5e9 (Sky Blue)
Dark BG:    #001f3f (Navy)
Accent:     #06b6d4 (Cyan)
Success:    #10b981 (Green)
```
Usage: Perfect for healthcare/biotech

#### Option 2: Sunset (Warm & Creative)
```css
Primary:    #f97316 (Orange)
Dark BG:    #1f1f2e (Charcoal)
Accent:     #ec4899 (Pink)
Success:    #22c55e (Lime)
```
Usage: Great for dynamic, creative projects

#### Option 3: Forest (Natural & Calm)
```css
Primary:    #10b981 (Emerald)
Dark BG:    #064e3b (Dark Green)
Accent:     #f59e0b (Amber)
Success:    #6366f1 (Indigo)
```
Usage: Environmental/ecological data

#### Option 4: Tech Purple (Modern & Sleek)
```css
Primary:    #8b5cf6 (Purple)
Dark BG:    #1e1b4b (Deep Purple)
Accent:     #ec4899 (Pink)
Success:    #06b6d4 (Cyan)
```
Usage: AI/ML, tech projects

### How to Apply a Color Scheme

Find this section in `bioinfo_dashboard.py`:

```python
st.markdown("""
<style>
    /* Change these values */
    .header-container {
        background: linear-gradient(90deg, #06b6d4 0%, #0891b2 100%);
    }
    
    .metric-value {
        color: #06b6d4;
    }
</style>
""", unsafe_allow_html=True)
```

Replace the hex colors with your chosen palette:

```python
st.markdown("""
<style>
    .header-container {
        background: linear-gradient(90deg, #0ea5e9 0%, #06b6d4 100%);  # Sky Blue gradient
    }
    
    .metric-value {
        color: #0ea5e9;  # Sky Blue
    }
    
    .stButton > button {
        background: linear-gradient(90deg, #0ea5e9 0%, #06b6d4 100%);
    }
</style>
""", unsafe_allow_html=True)
```

---

## Layout Customization

### Change Filter Position (Back to Sidebar)

Replace this:
```python
with st.expander("🔍 **Filters & Options**", expanded=True):
    filter_cols = st.columns(4)
```

With this:
```python
st.sidebar.markdown("### 🔍 Filters")
with st.sidebar:
    selected_tissues = st.multiselect("📊 Select Tissues", ...)
    selected_cell_lines = st.multiselect("🧫 Select Cell Lines", ...)
```

**Pros of sidebar**: Traditional, more familiar  
**Cons of sidebar**: Takes up horizontal space (what you have now is better)

### Add Sidebar Search Box

```python
st.sidebar.markdown("### 🔎 Quick Search")
search_term = st.sidebar.text_input("Search genes...", "")

if search_term:
    filtered_data = filtered_data[
        filtered_data['Gene'].str.contains(search_term, case=False, regex=False)
    ]
    st.sidebar.metric("Results", len(filtered_data))
```

### Change to 3-Column Layout for Metrics

Replace:
```python
metric_cols = st.columns(4)
```

With:
```python
metric_cols = st.columns(3)
```

This makes each card wider and more readable.

---

## Chart Customization

### Change Chart Colors

**For Expression Distribution Chart:**
```python
def create_expression_dist_chart(data):
    fig = go.Figure()
    
    colors = ['#06b6d4', '#f43f5e', '#10b981', '#f59e0b', '#8b5cf6']
    
    for i, tissue in enumerate(data['Tissue'].unique()):
        tissue_data = data[data['Tissue'] == tissue]['Expression']
        fig.add_trace(go.Histogram(
            x=tissue_data,
            name=tissue,
            marker_color=colors[i % len(colors)],  # Use custom colors
            opacity=0.7,
            nbinsx=30,
        ))
```

**For Heatmap:**
```python
fig = go.Figure(data=go.Heatmap(
    z=heatmap_data.values,
    x=heatmap_data.columns,
    y=heatmap_data.index,
    colorscale='Plasma',  # Options: Viridis, Plasma, Inferno, Magma, Cividis, Blues, Greens
))
```

### Add Custom Annotations to Charts

```python
# In volcano plot or any chart
fig.add_annotation(
    text="Significant genes (p<0.05)",
    x=1, y=2,
    showarrow=True,
    arrowhead=2,
    ax=40, ay=-40,
    font=dict(color="#06b6d4", size=12)
)
```

---

## Feature Additions

### 1. Add Search Functionality

```python
# Add to Overview tab
search_col1, search_col2 = st.columns(2)

with search_col1:
    gene_search = st.text_input("🔍 Search by gene name:")
    if gene_search:
        filtered_data = filtered_data[
            filtered_data['Gene'].str.contains(gene_search, case=False)
        ]
        st.success(f"Found {len(filtered_data)} records for '{gene_search}'")

with search_col2:
    cellline_search = st.text_input("🧫 Search by cell line:")
    if cellline_search:
        filtered_data = filtered_data[
            filtered_data['Cell_Line'].str.contains(cellline_search, case=False)
        ]
```

### 2. Add Gene Comparison Feature

```python
st.markdown("### 🔄 Compare Genes")

compare_col1, compare_col2 = st.columns(2)

with compare_col1:
    gene1 = st.selectbox("Select Gene 1", filtered_data['Gene'].unique())

with compare_col2:
    gene2 = st.selectbox("Select Gene 2", filtered_data['Gene'].unique())

if gene1 != gene2:
    comparison_data = filtered_data[filtered_data['Gene'].isin([gene1, gene2])]
    
    fig = px.bar(
        comparison_data,
        x='Tissue',
        y='Expression',
        color='Gene',
        barmode='group',
        title=f"Expression Comparison: {gene1} vs {gene2}"
    )
    st.plotly_chart(fig, use_container_width=True)
```

### 3. Add Statistical Tests (t-test, ANOVA)

```python
from scipy import stats

st.markdown("### 📊 Statistical Analysis")

tissue1 = st.selectbox("Tissue 1", filtered_data['Tissue'].unique())
tissue2 = st.selectbox("Tissue 2", filtered_data['Tissue'].unique())

expr1 = filtered_data[filtered_data['Tissue'] == tissue1]['Expression'].values
expr2 = filtered_data[filtered_data['Tissue'] == tissue2]['Expression'].values

t_stat, p_value = stats.ttest_ind(expr1, expr2)

col1, col2 = st.columns(2)
with col1:
    st.metric("t-statistic", f"{t_stat:.4f}")
with col2:
    st.metric("p-value", f"{p_value:.6f}")

if p_value < 0.05:
    st.success("✅ Significant difference detected!")
else:
    st.info("ℹ️ No significant difference")
```

### 4. Add Expression Profile Card

```python
# Get gene details
st.markdown("### 📋 Gene Profile")

selected_gene = st.selectbox("Select gene for details:", filtered_data['Gene'].unique())
gene_data = filtered_data[filtered_data['Gene'] == selected_gene]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Avg Expression", f"{gene_data['Expression'].mean():.2f}")

with col2:
    st.metric("Max Expression", f"{gene_data['Expression'].max():.2f}")

with col3:
    st.metric("Tissues", gene_data['Tissue'].nunique())

with col4:
    st.metric("Sig. Found", len(gene_data[gene_data['p_value'] < 0.05]))
```

---

## Performance Optimization

### Add Progress Bar for Large Datasets

```python
import time

progress_bar = st.progress(0)
status_text = st.empty()

for i, chunk in enumerate(chunks):
    # Process chunk
    process_chunk(chunk)
    
    # Update progress
    progress = (i + 1) / len(chunks)
    progress_bar.progress(progress)
    status_text.text(f"Processing chunk {i+1}/{len(chunks)}")
```

### Optimize Data Loading with DuckDB

```python
import duckdb

conn = duckdb.connect(':memory:')

# Load large dataset efficiently
query = """
    SELECT 
        gene,
        tissue,
        AVG(expression) as mean_expression,
        STDDEV(expression) as std_expression,
        COUNT(*) as n_samples
    FROM expression_data
    GROUP BY gene, tissue
    HAVING n_samples > 10
"""

summary = conn.execute(query).fetch_df()
```

---

## Styling Tips

### Make Cards More Prominent

```css
.metric-card {
    background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(8, 145, 178, 0.1));
    border: 2px solid rgba(6, 182, 212, 0.4);  /* Thicker, brighter border */
    box-shadow: 0 8px 16px rgba(6, 182, 212, 0.15);  /* Add shadow */
    transition: transform 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-4px);  /* Lift on hover */
    box-shadow: 0 12px 24px rgba(6, 182, 212, 0.25);
}
```

### Add Loading States

```python
# Show spinner while processing
with st.spinner('🔄 Generating charts...'):
    time.sleep(2)
    st.success('Done!')
```

### Add Info Boxes

```python
st.info("💡 Tip: Hover over charts to see exact values")
st.success("✅ All filters applied successfully")
st.warning("⚠️ Large dataset detected. Some features may be slow.")
st.error("❌ Missing required column: Expression")
```

---

## Responsive Design Tips

### Mobile-Friendly Layout

```python
# Use st.columns() responsively
if st.session_state.get('is_mobile', False):
    # Stack vertically on mobile
    for metric in metrics:
        st.metric(metric['label'], metric['value'])
else:
    # Use columns on desktop
    cols = st.columns(4)
    for i, metric in enumerate(metrics):
        with cols[i]:
            st.metric(metric['label'], metric['value'])
```

---

## What Makes Your Dashboard Better

| Feature | Your Dashboard | Advantage |
|---------|---|---|
| Collapsible Filters | ✅ | More screen real estate |
| Gradient Colors | ✅ | Modern, professional look |
| Custom CSS Styling | ✅ | Polished UI |
| Multiple Export Formats | ✅ CSV, Excel | More flexible |
| PCA Visualization | ✅ | Advanced analysis |
| Volcano Plot | ✅ | Statistical insight |
| Responsive Layout | ✅ | Works on all devices |
| Performance Caching | ✅ | Fast loading |
| Statistical Summary | ✅ | Better insights |

---

## Next Customization Steps

1. **Change colors** to match your institution/brand
2. **Add your own data** using `data_loader.py`
3. **Add search features** for better UX
4. **Optimize for your data size** (adjust caching, DuckDB)
5. **Add domain-specific charts** (pathway analysis, GO enrichment, etc.)
6. **Deploy to Streamlit Cloud** for easy sharing

Good luck with your project! 🧬
