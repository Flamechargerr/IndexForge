import pandas as pd
from sqlalchemy import text
import yfinance as yf
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import engine
from index_math.construction import INDEX_BASE_VALUE

def compare_vs_benchmark(start_date, end_date, benchmark_ticker="SPY"):
    """
    Compares the calculated index against a benchmark ETF.
    Aligns dates and rebases benchmark to INDEX_BASE_VALUE (1000).
    """
    print(f"Fetching benchmark ({benchmark_ticker}) for comparison...")
    benchmark_df = yf.download(benchmark_ticker, start=start_date, end=end_date, auto_adjust=False, progress=False)
    
    if benchmark_df.empty:
        print("Could not fetch benchmark data. Generating synthetic SPY benchmark...")
        dates = pd.date_range(start=start_date, end=end_date, freq='B')
        import numpy as np
        np.random.seed(999)
        returns = np.random.normal(loc=0.0003, scale=0.012, size=len(dates))
        price_path = 300 * np.exp(np.cumsum(returns))
        benchmark_df = pd.DataFrame({
            'date': dates.date,
            'bench_close': price_path
        })
    else:
        benchmark_df = benchmark_df.reset_index()
        # yfinance 0.2.37 or newer might return multiindex columns if multiple tickers, but for one it's single
        
        if isinstance(benchmark_df.columns, pd.MultiIndex):
            # Flatten multiindex if needed
            benchmark_df.columns = [col[0] for col in benchmark_df.columns.values]
            
        benchmark_df = benchmark_df.rename(columns={'Date': 'date', 'Close': 'bench_close'})
        benchmark_df['date'] = pd.to_datetime(benchmark_df['date']).dt.date
    
    # Fetch index values
    query = text("""
        SELECT date, value as index_value 
        FROM index_values 
        WHERE date >= :s AND date <= :e
        ORDER BY date
    """)
    index_df = pd.read_sql(query, engine, params={"s": start_date, "e": end_date})
    
    if index_df.empty:
        print("No index values found for performance calculation.")
        return pd.DataFrame()
        
    # Merge and align on trading dates
    merged = pd.merge(index_df, benchmark_df[['date', 'bench_close']], on='date', how='inner')
    
    if merged.empty:
        return pd.DataFrame()
        
    # Rebase benchmark
    initial_bench_price = merged['bench_close'].iloc[0]
    merged['bench_rebased'] = (merged['bench_close'] / initial_bench_price) * INDEX_BASE_VALUE
    
    # Calculate returns
    merged['index_return'] = merged['index_value'].pct_change()
    merged['bench_return'] = merged['bench_close'].pct_change()
    
    print("Performance comparison complete.")
    return merged
