import pandas as pd
import math

def generate_markdown_report(perf_df: pd.DataFrame, turnover_df: pd.DataFrame, sector_df: pd.DataFrame, output_path: str = "indexforge_summary.md"):
    """
    Generates a Markdown report summarizing index performance, turnover, and sector drift.
    """
    print(f"Generating performance report at {output_path}...")
    
    with open(output_path, "w") as f:
        f.write("# IndexForge Rebalancing & Performance Summary\n\n")
        
        # 1. Performance Overview
        if not perf_df.empty:
            start_date = perf_df['date'].iloc[0]
            end_date = perf_df['date'].iloc[-1]
            
            # Simple Total Return
            index_total_ret = (perf_df['index_value'].iloc[-1] / perf_df['index_value'].iloc[0] - 1) * 100
            bench_total_ret = (perf_df['bench_rebased'].iloc[-1] / perf_df['bench_rebased'].iloc[0] - 1) * 100
            
            # Annualization based on trading days approx (252)
            years = len(perf_df) / 252.0
            if years > 0:
                index_cagr = ((perf_df['index_value'].iloc[-1] / perf_df['index_value'].iloc[0]) ** (1/years) - 1) * 100
                bench_cagr = ((perf_df['bench_rebased'].iloc[-1] / perf_df['bench_rebased'].iloc[0]) ** (1/years) - 1) * 100
            else:
                index_cagr = 0
                bench_cagr = 0
            
            f.write("## 1. Portfolio-Level Performance Attribution\n")
            f.write(f"**Period**: {start_date} to {end_date}\n\n")
            f.write("| Metric | IndexForge Custom | Benchmark (SPY) | Relative |\n")
            f.write("| --- | --- | --- | --- |\n")
            f.write(f"| **Total Return** | {index_total_ret:.2f}% | {bench_total_ret:.2f}% | {index_total_ret - bench_total_ret:.2f}% |\n")
            f.write(f"| **CAGR** | {index_cagr:.2f}% | {bench_cagr:.2f}% | {index_cagr - bench_cagr:.2f}% |\n\n")
        
        # 2. Rebalancing Turnover
        if not turnover_df.empty:
            f.write("## 2. Rebalancing Turnover\n")
            f.write("Turnover logic respects MSCI buffer thresholds, retaining entities inside the buffer zone and preventing unnecessary weight reallocations.\n\n")
            f.write(turnover_df.to_markdown(index=False) + "\n\n")
            avg_turnover = turnover_df['turnover_pct'].mean()
            f.write(f"**Average Run Turnover**: {avg_turnover:.2f}%\n\n")
            
        # 3. Sector Drift
        if not sector_df.empty:
            f.write("## 3. Sector Drift Over Time (in %)\n")
            f.write("Shows how dynamic market-cap based weighting causes sectoral biases to shift inherently across structural rebalances.\n\n")
            # Round numeric columns for cleaner markdown
            formatted_sector = sector_df.round(2)
            f.write(formatted_sector.to_markdown() + "\n\n")

    print("Report generated successfully.")
