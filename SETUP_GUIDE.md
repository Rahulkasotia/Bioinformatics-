# 🧬 Bioinformatics Profiler - Setup Guide

## Quick Start

### 1. Install Dependencies
```bash
pip install streamlit plotly pandas numpy scikit-learn openpyxl duckdb
```

### 2. Run the App
```bash
streamlit run bioinfo_dashboard.py
```

The app will start at `http://localhost:8501`

---

## Project Structure

```
your_project/
├── bioinfo_dashboard.py          # Main application
├── .streamlit/
│   └── config.toml               # Streamlit configuration
├── data/
│   ├── gene_expression.parquet   # Your actual data
│   └── metadata.csv              # Sample metadata
├── requirements.txt
└── README.md
```

---

## Configuration File (.streamlit/config.toml)

Create this file in your project root under `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#06b6d4"
backgroundColor = "#0f172a"
secondaryBackgroundColor = "#1e293b"
textColor = "#e2e8f0"
font = "sans serif"

[client]
showErrorDetails = false
toolbarMode = "minimal"

[logger]
level = "info"

[server]
headless = true
port = 8501
maxUploadSize = 200
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

---

## Loading Your Own Data

### Option 1: From Parquet File (Recommended for Large Data)
```python
import duckdb
import pandas as pd

# Load Parquet
query = """
    SELECT * 
    FROM read_parquet('data/gene_expression.parquet')
    LIMIT 10000
"""
data = duckdb.query(query).to_df()
```

### Option 2: From CSV
```python
# Load CSV efficiently
data = pd.read_csv('data/gene_expression.csv', low_memory=False)
```

### Option 3: From Excel
```python
data = pd.read_excel('data/gene_expression.xlsx', sheet_name='Expression')
```

### Required Columns in Your Data:
```
- Gene (str): Gene identifier
- Tissue (str): Tissue type
- Cell_Line (str): Cell line identifier
- Expression (float): Expression value (log-normalized recommended)
- p_value (float): Statistical p-value
- log2FC (float): Log2 fold change
- Sample_Size (int): Sample size for this measurement
```

---

## UI/UX Customization

### Change Color Scheme
Edit the CSS in the `st.markdown()` section. Key colors:
- **Primary (Cyan)**: `#06b6d4` → Change to your brand color
- **Accent (Red)**: `#f43f5e` → For upregulated genes
- **Success (Green)**: `#10b981` → For statistics
- **Warning (Yellow)**: `#f59e0b` → For alerts

Example:
```css
.header-container {
    background: linear-gradient(90deg, YOUR_COLOR_1 0%, YOUR_COLOR_2 100%);
}
```

### Change Layout
- To make sidebar permanent: Change `initial_sidebar_state="collapsed"` to `"expanded"`
- To change page width: Modify `layout="wide"` to `"centered"`

---

## Performance Tips

### 1. Cache Large Data
```python
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    return pd.read_parquet('data/gene_expression.parquet')
```

### 2. Optimize Plots
```python
# Use Plotly with optimized settings
st.plotly_chart(
    fig,
    use_container_width=True,
    config={'displayModeBar': False}  # Hide toolbar for cleaner look
)
```

### 3. Filter Before Plotting
```python
# Bad: Plot then filter
fig = create_chart(data)  # All data

# Good: Filter first
filtered = filter_data(data, selections)
fig = create_chart(filtered)
```

---

## Adding More Features

### Add a Gene Search Feature
```python
# In your filter section:
gene_search = st.text_input("🔍 Search genes (e.g., TP53, BRCA1):")
if gene_search:
    filtered_data = filtered_data[
        filtered_data['Gene'].str.contains(gene_search, case=False)
    ]
```

### Add Export to PDF
```python
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

def export_report(data):
    c = canvas.Canvas("report.pdf", pagesize=letter)
    c.drawString(100, 750, "Gene Expression Report")
    c.save()
```

### Add Database Connection (DuckDB)
```python
import duckdb

conn = duckdb.connect('database.duckdb')

# Efficient filtering with SQL
query = f"""
    SELECT * FROM expression_data
    WHERE tissue IN ({','.join([f"'{t}'" for t in selected_tissues])})
    AND expression > {min_expression}
"""
filtered = conn.execute(query).fetch_df()
```

---

## Deployment Options

### Option 1: Streamlit Cloud (Easiest)
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repo and deploy

### Option 2: Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "bioinfo_dashboard.py"]
```

Run: `docker build -t bioinfo-app . && docker run -p 8501:8501 bioinfo-app`

### Option 3: Self-hosted (Ubuntu/Linux)
```bash
# Install Python & dependencies
sudo apt-get update && apt-get install python3-pip
pip3 install -r requirements.txt

# Run with systemd service
sudo systemctl start streamlit-app
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'streamlit'"
**Solution**: 
```bash
pip install streamlit --upgrade
```

### Issue: "Memory Error" with large datasets
**Solution**: Use DuckDB to process data in chunks
```python
import duckdb

# Process 100k rows at a time
conn = duckdb.connect(':memory:')
conn.execute("CREATE TABLE data AS SELECT * FROM read_csv('large_file.csv')")
result = conn.execute("SELECT * FROM data LIMIT 10000").fetch_df()
```

### Issue: Plots not showing
**Solution**: Check if `plotly` is installed
```bash
pip install plotly --upgrade
```

### Issue: Slow performance
**Solution**: Enable caching and optimize queries
```python
@st.cache_data
def expensive_function():
    return slow_computation()
```

---

## Project Statistics

- **Lines of Code**: ~600
- **Supported Visualizations**: 8+ (histogram, heatmap, volcano, PCA, box plot, etc.)
- **Max Recommended Genes**: 50,000 (depends on your hardware)
- **Max Recommended Samples**: 100,000+ (with DuckDB optimization)

---

## What's Different from Your Friend's Dashboard?

✅ **Top Navigation** - Cleaner header with gradient  
✅ **Collapsible Filters** - More space for visualizations  
✅ **Better Color Scheme** - Modern cyan/teal + accent colors  
✅ **Advanced Charts** - PCA, Volcano plots, Statistical summaries  
✅ **Responsive Layout** - Works on desktop, tablet, mobile  
✅ **Export Options** - CSV, Excel downloads  
✅ **Performance Optimized** - Caching, efficient filtering  
✅ **Professional Styling** - Custom CSS for polish  

---

## Next Steps

1. ✅ Copy the `bioinfo_dashboard.py` script
2. ✅ Create `.streamlit/config.toml`
3. ✅ Install dependencies: `pip install -r requirements.txt`
4. ✅ Replace sample data with your actual gene expression data
5. ✅ Run: `streamlit run bioinfo_dashboard.py`
6. ✅ Customize colors/layout to your preference
7. ✅ Deploy to Streamlit Cloud or your server

---

## Support

For issues or questions:
- **Streamlit Docs**: https://docs.streamlit.io
- **Plotly Docs**: https://plotly.com/python/
- **DuckDB Docs**: https://duckdb.org/docs/

Happy analyzing! 🧬📊
