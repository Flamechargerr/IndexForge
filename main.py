import argparse
import sys
import os
from datetime import date, timedelta
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.init_db import init_db
from data_ingestion.yfinance_client import get_universe_tickers, fetch_equity_metadata, fetch_historical_prices
from data_ingestion.db_loader import load_equities_to_db, load_prices_to_db, clear_database
from index_math.rebalancing import apply_rebalance
from index_math.construction import calculate_daily_index
from backtesting.performance import compare_vs_benchmark
from backtesting.attribution import calculate_turnover, calculate_sector_drift
from reports.generator import generate_markdown_report

def main():
    parser = argparse.ArgumentParser(description="IndexForge - Equity Index Construction Engine")
    parser.add_argument('--setup', action='store_true', help='Initialize database tables')
    parser.add_argument('--ingest', action='store_true', help='Download universe and pricing data')
    parser.add_argument('--run-engine', action='store_true', help='Run semi-annual rebalances and index calculations')
    parser.add_argument('--backtest', action='store_true', help='Generate attribution and performance reports')
    
    args = parser.parse_args()
    
    START_DATE = '2019-01-01'
    END_DATE = '2024-01-01'
    
    if args.setup:
        init_db()

    if args.ingest:
        print("Starting data ingestion loop...")
        clear_database()
        tickers = get_universe_tickers()
        # Cap at 50 for speed during testing, could be scaled back up to 100+ internally or up to 500 for a true MSCI proxy
        tickers = tickers[:50] 
        print(f"Tracking Universe of {len(tickers)} companies.")
        
        meta_df = fetch_equity_metadata(tickers)
        if not meta_df.empty:
            load_equities_to_db(meta_df)
            
        prices_df = fetch_historical_prices(tickers, start_date=START_DATE, end_date=END_DATE)
        if not prices_df.empty:
            load_prices_to_db(prices_df)

    if args.run_engine:
        # Define semi-annual rebalancing dates
        year_start = int(START_DATE[:4])
        year_end = int(END_DATE[:4])
        
        rebalance_dates = []
        for y in range(year_start, year_end + 1):
            # May and November rebalances (MSCI schedule)
            rebalance_dates.append(date(y, 5, 31))
            rebalance_dates.append(date(y, 11, 30))
            
        # Filter dates within range
        rebalance_dates = [d for d in rebalance_dates if pd.to_datetime(START_DATE).date() <= d <= pd.to_datetime(END_DATE).date()]
        
        for r_date in rebalance_dates:
            apply_rebalance(r_date)
            
        # Calculate daily index using chosen constituents
        calculate_daily_index(pd.to_datetime(START_DATE).date(), pd.to_datetime(END_DATE).date())
        
    if args.backtest:
        perf_df = compare_vs_benchmark(pd.to_datetime(START_DATE).date(), pd.to_datetime(END_DATE).date(), "SPY")
        turnover_df = calculate_turnover()
        sector_df = calculate_sector_drift()
        generate_markdown_report(perf_df, turnover_df, sector_df, "indexforge_report.md")
        print("Backtest complete. View indexforge_report.md")

if __name__ == "__main__":
    main()
