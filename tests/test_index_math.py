import pytest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from index_math.construction import calculate_adjusted_divisor

def test_divisor_adjustment_continuity():
    """
    Test that the divisor adjustment formula correctly maintains index value 
    given a change in market capitalization.
    Index_Value = Market_Cap / Divisor
    """
    last_index_value = 1050.0
    new_mcap = 5000000000.0
    
    new_divisor = calculate_adjusted_divisor(new_mcap, last_index_value)
    
    # Recalculate index with new divisor
    calculated_index = new_mcap / new_divisor
    
    assert round(calculated_index, 6) == round(last_index_value, 6)

def test_divisor_adjustment_zero_division():
    """Verify that the function handles zero index value gracefully."""
    assert calculate_adjusted_divisor(1000, 0) == 0

def test_divisor_scaling():
    """Test that doubling the market cap results in a doubled divisor for the same index value."""
    last_index = 1000.0
    mcap1 = 1000000.0
    mcap2 = 2000000.0
    
    div1 = calculate_adjusted_divisor(mcap1, last_index)
    div2 = calculate_adjusted_divisor(mcap2, last_index)
    
    assert div2 == 2 * div1
