"""
Data Loader Module for Bioinformatics Dashboard
Supports: CSV, Excel, Parquet, DuckDB
"""

import pandas as pd
import numpy as np
import duckdb
from pathlib import Path
import streamlit as st

class BioinfoDataLoader:
    """Load and validate bioinformatics data from various sources"""
    
    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self.data = None
        self.required_columns = [
            'Gene', 'Tissue', 'Cell_Line', 'Expression', 'p_value', 'log2FC'
        ]
    
    def load_csv(self) -> pd.DataFrame:
        """Load from CSV file"""
        try:
            data = pd.read_csv(self.filepath, low_memory=False)
            print(f"✅ Loaded CSV: {data.shape[0]:,} rows, {data.shape[1]} columns")
            return data
        except Exception as e:
            print(f"❌ Error loading CSV: {e}")
            return None
    
    def load_excel(self, sheet_name=0) -> pd.DataFrame:
        """Load from Excel file"""
        try:
            data = pd.read_excel(self.filepath, sheet_name=sheet_name)
            print(f"✅ Loaded Excel: {data.shape[0]:,} rows, {data.shape[1]} columns")
            return data
        except Exception as e:
            print(f"❌ Error loading Excel: {e}")
            return None
    
    def load_parquet(self) -> pd.DataFrame:
        """Load from Parquet file (optimized for large data)"""
        try:
            data = pd.read_parquet(self.filepath)
            print(f"✅ Loaded Parquet: {data.shape[0]:,} rows, {data.shape[1]} columns")
            return data
        except Exception as e:
            print(f"❌ Error loading Parquet: {e}")
            return None
    
    def load_duckdb(self, table_name: str) -> pd.DataFrame:
        """Load from DuckDB database"""
        try:
            conn = duckdb.connect(str(self.filepath))
            data = conn.execute(f"SELECT * FROM {table_name}").fetch_df()
            print(f"✅ Loaded DuckDB: {data.shape[0]:,} rows, {data.shape[1]} columns")
            conn.close()
            return data
        except Exception as e:
            print(f"❌ Error loading DuckDB: {e}")
            return None
    
    def load(self, format_type='auto') -> pd.DataFrame:
        """Auto-detect and load based on file extension"""
        if format_type == 'auto':
            suffix = self.filepath.suffix.lower()
            format_type = suffix.lstrip('.')
        
        format_map = {
            'csv': self.load_csv,
            'xlsx': self.load_excel,
            'xls': self.load_excel,
            'parquet': self.load_parquet,
            'pq': self.load_parquet,
        }
        
        loader = format_map.get(format_type)
        if not loader:
            print(f"❌ Unsupported format: {format_type}")
            return None
        
        self.data = loader()
        return self.data
    
    def validate(self) -> bool:
        """Check if data has required columns"""
        if self.data is None:
            print("❌ No data loaded")
            return False
        
        missing = [col for col in self.required_columns if col not in self.data.columns]
        
        if missing:
            print(f"❌ Missing columns: {missing}")
            print(f"Available columns: {list(self.data.columns)}")
            return False
        
        print(f"✅ All required columns present: {self.required_columns}")
        return True
    
    def preprocess(self) -> pd.DataFrame:
        """Clean and prepare data"""
        if self.data is None:
            return None
        
        df = self.data.copy()
        
        # Convert to appropriate types
        df['Gene'] = df['Gene'].astype(str)
        df['Tissue'] = df['Tissue'].astype(str)
        df['Cell_Line'] = df['Cell_Line'].astype(str)
        df['Expression'] = pd.to_numeric(df['Expression'], errors='coerce')
        df['p_value'] = pd.to_numeric(df['p_value'], errors='coerce')
        df['log2FC'] = pd.to_numeric(df['log2FC'], errors='coerce')
        
        # Handle missing values
        initial_rows = len(df)
        df = df.dropna(subset=['Expression', 'p_value', 'log2FC'])
        removed_rows = initial_rows - len(df)
        
        if removed_rows > 0:
            print(f"⚠️  Removed {removed_rows:,} rows with missing values")
        
        # Remove duplicates (optional, keep first occurrence)
        df = df.drop_duplicates(subset=['Gene', 'Tissue', 'Cell_Line'], keep='first')
        
        print(f"✅ Preprocessed: {len(df):,} rows remaining")
        return df
    
    def add_calculated_columns(self) -> pd.DataFrame:
        """Add derived columns for analysis"""
        if self.data is None:
            return None
        
        df = self.data.copy()
        
        # Add -log10(p-value) for volcano plots
        df['neg_log_p'] = -np.log10(df['p_value'].replace(0, 1e-300))
        
        # Add significance flags
        df['is_significant'] = (
            (df['log2FC'].abs() > 1) & 
            (df['p_value'] < 0.05)
        )
        
        # Add expression category
        def categorize_expression(val):
            if val < np.percentile(df['Expression'], 25):
                return 'Low'
            elif val < np.percentile(df['Expression'], 75):
                return 'Medium'
            else:
                return 'High'
        
        df['Expression_Category'] = df['Expression'].apply(categorize_expression)
        
        print("✅ Added calculated columns: neg_log_p, is_significant, Expression_Category")
        return df
    
    def get_summary_stats(self) -> dict:
        """Get summary statistics"""
        if self.data is None:
            return {}
        
        df = self.data
        
        stats = {
            'Total Genes': df['Gene'].nunique(),
            'Total Tissues': df['Tissue'].nunique(),
            'Total Cell Lines': df['Cell_Line'].nunique(),
            'Total Records': len(df),
            'Mean Expression': f"{df['Expression'].mean():.2f}",
            'Std Expression': f"{df['Expression'].std():.2f}",
            'Min Expression': f"{df['Expression'].min():.2f}",
            'Max Expression': f"{df['Expression'].max():.2f}",
        }
        
        return stats


# Example Usage
def main():
    # Example 1: Load CSV
    loader = BioinfoDataLoader('data/gene_expression.csv')
    data = loader.load('csv')
    
    if loader.validate():
        data = loader.preprocess()
        data = loader.add_calculated_columns()
        
        stats = loader.get_summary_stats()
        print("\n📊 Summary Statistics:")
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        # Save preprocessed data
        data.to_parquet('data/gene_expression_processed.parquet', compression='snappy')
        print("\n✅ Saved preprocessed data to gene_expression_processed.parquet")
    
    # Example 2: Load Parquet
    # loader = BioinfoDataLoader('data/gene_expression.parquet')
    # data = loader.load('parquet')
    # data = loader.preprocess()


# Streamlit Integration
def streamlit_data_uploader():
    """Upload and process data via Streamlit UI"""
    st.subheader("📤 Upload Gene Expression Data")
    
    uploaded_file = st.file_uploader(
        "Choose a file (CSV, Excel, or Parquet)",
        type=['csv', 'xlsx', 'xls', 'parquet', 'pq']
    )
    
    if uploaded_file is not None:
        # Save temporarily
        temp_path = f"temp_{uploaded_file.name}"
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        # Load and validate
        loader = BioinfoDataLoader(temp_path)
        data = loader.load()
        
        if data is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                if loader.validate():
                    st.success("✅ Data structure is valid!")
                else:
                    st.error("❌ Data validation failed. Check column names.")
                    st.info(f"Available columns: {list(data.columns)}")
            
            with col2:
                stats = loader.get_summary_stats()
                for key, value in stats.items():
                    st.metric(key, value)
            
            # Preview data
            st.subheader("Data Preview")
            st.dataframe(data.head(100), use_container_width=True)
            
            # Download preprocessed
            if st.button("🔧 Process & Download"):
                processed = loader.preprocess()
                processed = loader.add_calculated_columns()
                
                csv = processed.to_csv(index=False)
                st.download_button(
                    "📥 Download Processed Data (CSV)",
                    csv,
                    "gene_expression_processed.csv",
                    "text/csv"
                )


if __name__ == "__main__":
    main()
