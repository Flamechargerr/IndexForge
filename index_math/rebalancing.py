import pandas as pd
from sqlalchemy import text
from datetime import date
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db.connection import engine
import numpy as np

# Mock free-float factor generator for demonstration (real MSCI uses proprietary research)
def get_mock_free_float(ticker):
    np.random.seed(hash(ticker) % (2**32))
    return np.random.uniform(0.70, 1.0)

def calculate_rebalance(rebalance_date: date, target_constituents=50, buffer_zone=5):
    """
    Applies rules to select index constituents for a given date.
    Returns a dataframe of selected constituents and their weights.
    """
    print(f"Executing rebalance for {rebalance_date}...")
    
    # 1. Fetch universe state as of rebalance_date
    query = text("""
        SELECT e.ticker, e.shares_outstanding, p.close_price, p.adtv_20d
        FROM equities e
        JOIN daily_prices p ON e.ticker = p.ticker
        WHERE p.date = :r_date
    """)
    df = pd.read_sql(query, engine, params={"r_date": rebalance_date})
    
    if df.empty:
        print(f"No pricing data found for {rebalance_date}. Skipping rebalance.")
        return pd.DataFrame()
        
    # 2. Liquidity Screen (e.g., ADTV > 500,000)
    df = df[df['adtv_20d'] > 500000].copy()
    
    # 3. Calculate free-float adjusted market cap
    df['free_float_factor'] = df['ticker'].apply(get_mock_free_float)
    df['market_cap'] = df['shares_outstanding'] * df['close_price']
    df['ff_market_cap'] = df['market_cap'] * df['free_float_factor']
    
    # 4. Rank by ff_market_cap
    df['rank'] = df['ff_market_cap'].rank(ascending=False)
    
    # 5. Buffer rules (keep current constituents if they drop slightly below threshold)
    # Fetch current constituents (most recent rebalance prior to this date)
    curr_query = text("""
        SELECT ticker FROM index_constituents 
        WHERE rebalance_date = (SELECT MAX(rebalance_date) FROM index_constituents WHERE rebalance_date < :r_date)
    """)
    curr_constituents_df = pd.read_sql(curr_query, engine, params={"r_date": rebalance_date})
    current_tickers = set(curr_constituents_df['ticker']) if not curr_constituents_df.empty else set()
    
    selected_tickers = set()
    
    # Rule 1: Choose top (target - buffer_zone) unconditionally
    top_tier = set(df[df['rank'] <= (target_constituents - buffer_zone)]['ticker'])
    selected_tickers.update(top_tier)
    
    # Rule 2: Current constituents in buffer zone (target - buffer, target + buffer) are kept
    buffer_tier = df[(df['rank'] > (target_constituents - buffer_zone)) & (df['rank'] <= (target_constituents + buffer_zone))]
    kept_constituents = set(buffer_tier['ticker']).intersection(current_tickers)
    selected_tickers.update(kept_constituents)
    
    # Rule 3: Fill the rest from the highest ranked remaining
    remaining_needed = target_constituents - len(selected_tickers)
    if remaining_needed > 0:
        remaining_candidates = df[~df['ticker'].isin(selected_tickers)].sort_values(by='rank')
        fillers = set(remaining_candidates.head(remaining_needed)['ticker'])
        selected_tickers.update(fillers)
        
    # Final Selection
    index_df = df[df['ticker'].isin(selected_tickers)].copy()
    
    # Calculate Weights (Cap-weighted)
    total_ff_mcap = index_df['ff_market_cap'].sum()
    index_df['weight'] = index_df['ff_market_cap'] / total_ff_mcap
    index_df['shares_in_index'] = index_df['shares_outstanding'] * index_df['free_float_factor']
    index_df['rebalance_date'] = rebalance_date
    
    return index_df[['ticker', 'rebalance_date', 'weight', 'shares_in_index', 'free_float_factor']]

def apply_rebalance(rebalance_date: date):
    index_df = calculate_rebalance(rebalance_date)
    if index_df.empty:
        return
        
    print(f"Applying {len(index_df)} constituents to database...")
    index_df.to_sql('index_constituents', engine, if_exists='append', index=False)
