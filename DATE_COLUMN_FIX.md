# Date-Only Column Filter Fix

## Problem
The CSV export was showing redundant @ symbols with date-only column labels:
- `必要な年数の中間値 @ 2022-09` 
- `IRR（年 @ 2022-08`
- `NPV ② @ 2022-08`
- `バイク製造費（百万VDN） @ 2022-08`

The date information doesn't add meaningful context when the row label is already descriptive.

## Solution
Updated the `get_context()` method in `src/models.py` to filter out date-only column labels.

### Changes Made

**File:** `src/models.py`

Added **Rule B: Date-Only Columns** to the `get_context()` method:

```python
# Rule B: Date-Only Columns
# If column label is just a date/time period, it usually doesn't add value
# Date patterns: "2022-08", "2022-09", "2023-01", "FY2024", "Q1", etc.
import re
date_only_patterns = [
    r'^\d{4}-\d{2}$',  # 2022-08, 2023-01
    r'^\d{2}-\d{4}$',  # 08-2022, 01-2023
    r'^FY\s*\d{4}$',   # FY2024, FY 2024
    r'^Q\d$',          # Q1, Q2, Q3, Q4
    r'^[A-Z][a-z]{2}\s+\d{4}$',  # Jan 2024, Feb 2024
]

is_date_only = any(re.match(pattern, self.col_label.strip()) for pattern in date_only_patterns)

if is_date_only:
    # Date-only column label doesn't add value - just use row label
    return self.row_label
```

## Results

### Before Fix
```
必要な年数の中間値 @ 2022-09
IRR（年 @ 2022-08
NPV ② @ 2022-08
バイク製造費（百万VDN） @ 2022-08
全体開発費（百万VDN）※7年償却 @ 2022-08
```

### After Fix
```
必要な年数の中間値
IRR（年
NPV ②
バイク製造費（百万VDN）
全体開発費（百万VDN）※7年償却
```

## Testing

Created comprehensive tests to verify the fix:

1. **test_date_column_filter.py** - Tests basic date filtering logic
2. **test_japanese_date_filter.py** - Tests with actual examples from user's CSV

All tests pass ✅

## How to Regenerate Your CSV

To regenerate your CSV with the fix applied:

1. Make sure you have your original Excel file (the one with Japanese content)
2. Run the analysis using the Streamlit app or the regenerate script:

```bash
# Option 1: Using the regenerate script
python regenerate_csv.py

# Option 2: Using the Streamlit app
streamlit run app.py
# Then upload your file and export the results
```

The fix is now permanent in the codebase, so all future CSV exports will have clean context labels without redundant date information.

## Design Philosophy

The fix follows these principles:

1. **Show their data, not our formatting logic** - Users care about what the data represents, not when it was recorded
2. **Reduce noise** - Date-only columns rarely add meaningful context when the row label is descriptive
3. **Keep non-date columns** - Columns like "Scenario A", "Budget", "Forecast" are still shown with @ symbol because they add value

## Edge Cases Handled

- ✅ YYYY-MM format (2022-08, 2023-01)
- ✅ MM-YYYY format (08-2022, 01-2023)  
- ✅ Fiscal year format (FY2024, FY 2024)
- ✅ Quarter format (Q1, Q2, Q3, Q4)
- ✅ Month-year format (Jan 2024, Feb 2024)
- ✅ Long row labels (>30 chars) still drop column labels
- ✅ Non-date columns still show with @ symbol
- ✅ Redundancy check still works (if column text is in row text)
