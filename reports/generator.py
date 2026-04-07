import pandas as pd
import logging
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import RISK_FREE_RATE, TRADING_DAYS_PER_YEAR

logger = logging.getLogger(__name__)

def generate_markdown_report(perf_df: pd.DataFrame, turnover_df: pd.DataFrame, sector_df: pd.DataFrame, output_path: str = "indexforge_report.md"):
    """
    Generates a professional Markdown report summarizing index performance, turnover, and sector drift.
    """
    logger.info(f"Generating executive summary report at {output_path}...")
    
    with open(output_path, "w") as f:
        f.write("# IndexForge Rebalancing & Performance Summary\n\n")
        
        # 1. Performance Overview
        if not perf_df.empty:
            start_date = perf_df['date'].iloc[0]
            end_date = perf_df['date'].iloc[-1]
            
            # Simple Total Return
            index_total_ret = (perf_df['index_value'].iloc[-1] / perf_df['index_value'].iloc[0] - 1) * 100
            bench_total_ret = (perf_df['bench_rebased'].iloc[-1] / perf_df['bench_rebased'].iloc[0] - 1) * 100
            
            # Annualized Metrics
            years = len(perf_df) / TRADING_DAYS_PER_YEAR
            index_cagr = ((perf_df['index_value'].iloc[-1] / perf_df['index_value'].iloc[0]) ** (1/years) - 1) * 100
            bench_cagr = ((perf_df['bench_rebased'].iloc[-1] / perf_df['bench_rebased'].iloc[0]) ** (1/years) - 1) * 100
            
            # Volatility & Sharpe
            idx_vol = perf_df['index_return'].std() * (TRADING_DAYS_PER_YEAR ** 0.5) * 100
            idx_sharpe = (index_cagr/100 - RISK_FREE_RATE) / (idx_vol/100) if idx_vol != 0 else 0
            
            f.write("## 1. Portfolio-Level Performance Attribution\n")
            f.write(f"**Period**: {start_date} to {end_date}\n\n")
            f.write("| Metric | IndexForge Custom | Benchmark (SPY) | Relative |\n")
            f.write("| --- | --- | --- | --- |\n")
            f.write(f"| **Total Return** | {index_total_ret:.2f}% | {bench_total_ret:.2f}% | {index_total_ret - bench_total_ret:.2f}% |\n")
            f.write(f"| **Annualized Return (CAGR)** | {index_cagr:.2f}% | {bench_cagr:.2f}% | {index_cagr - bench_cagr:.2f}% |\n")
            f.write(f"| **Annualized Volatility** | {idx_vol:.2f}% | - | - |\n")
            f.write(f"| **Sharpe Ratio (Rf={RISK_FREE_RATE*100}%)** | {idx_sharpe:.2f} | - | - |\n\n")
        
        # 2. Rebalancing Turnover
        if not turnover_df.empty:
            f.write("## 2. Rebalancing Turnover\n")
            f.write("Turnover logic respects MSCI buffer thresholds, maintaining consistency and preventing unnecessary churn.\n\n")
            f.write(turnover_df.to_markdown(index=False) + "\n\n")
            
        # 3. Sector Drift
        if not sector_df.empty:
            f.write("## 3. Sector Displacement (Drift)\n")
            f.write("Tracks how sector weights migrate organically due to market-cap shifts between rebalances.\n\n")
            f.write(sector_df.round(2).to_markdown() + "\n\n")

    logger.info("Report generation successful.")
