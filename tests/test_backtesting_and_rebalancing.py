import datetime as dt

import pandas as pd

from backtesting import attribution, performance, visualizer
from index_math import rebalancing


def test_get_mock_free_float_is_stable_and_bounded():
    first = rebalancing.get_mock_free_float("AAPL")
    second = rebalancing.get_mock_free_float("AAPL")
    assert first == second
    assert 0.70 <= first <= 1.0


def test_compare_vs_benchmark_uses_synthetic_when_download_fails(monkeypatch):
    index_df = pd.DataFrame(
        {
            "date": [dt.date(2024, 1, 2), dt.date(2024, 1, 3), dt.date(2024, 1, 4)],
            "index_value": [1000.0, 1010.0, 1020.0],
        }
    )

    monkeypatch.setattr(performance.yf, "download", lambda *args, **kwargs: pd.DataFrame())
    monkeypatch.setattr(performance.pd, "read_sql", lambda *args, **kwargs: index_df.copy())

    result = performance.compare_vs_benchmark(dt.date(2024, 1, 2), dt.date(2024, 1, 4), "SPY")

    assert not result.empty
    assert "bench_rebased" in result.columns
    assert result["bench_rebased"].iloc[0] == 1000.0
    assert "index_return" in result.columns
    assert "bench_return" in result.columns


def test_compare_vs_benchmark_returns_empty_when_no_index_points(monkeypatch):
    monkeypatch.setattr(performance.yf, "download", lambda *args, **kwargs: pd.DataFrame())
    monkeypatch.setattr(performance.pd, "read_sql", lambda *args, **kwargs: pd.DataFrame())

    result = performance.compare_vs_benchmark(dt.date(2024, 1, 2), dt.date(2024, 1, 4), "SPY")
    assert result.empty


def test_calculate_turnover(monkeypatch):
    source_df = pd.DataFrame(
        {
            "rebalance_date": [dt.date(2024, 5, 31), dt.date(2024, 5, 31), dt.date(2024, 11, 30), dt.date(2024, 11, 30)],
            "ticker": ["AAA", "BBB", "AAA", "CCC"],
            "weight": [0.6, 0.4, 0.5, 0.5],
        }
    )
    monkeypatch.setattr(attribution.pd, "read_sql", lambda *args, **kwargs: source_df.copy())

    result = attribution.calculate_turnover()

    assert len(result) == 1
    assert result["rebalance_date"].iloc[0] == dt.date(2024, 11, 30)
    assert result["turnover_pct"].iloc[0] == 50.0


def test_calculate_sector_drift_pivots_to_percentages(monkeypatch):
    source_df = pd.DataFrame(
        {
            "rebalance_date": [dt.date(2024, 5, 31), dt.date(2024, 5, 31)],
            "sector": ["Tech", "Health"],
            "sector_weight": [0.7, 0.3],
        }
    )
    monkeypatch.setattr(attribution.pd, "read_sql", lambda *args, **kwargs: source_df.copy())

    result = attribution.calculate_sector_drift()

    assert result.loc[dt.date(2024, 5, 31), "Tech"] == 70.0
    assert result.loc[dt.date(2024, 5, 31), "Health"] == 30.0


def test_plot_performance_creates_image(tmp_path):
    output = tmp_path / "index_performance.png"
    perf_df = pd.DataFrame(
        {
            "date": [dt.date(2024, 1, 2), dt.date(2024, 1, 3)],
            "index_value": [1000.0, 1015.0],
            "bench_rebased": [1000.0, 1008.0],
        }
    )

    visualizer.plot_performance(perf_df, str(output))

    assert output.exists()
