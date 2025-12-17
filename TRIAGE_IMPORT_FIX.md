# Import Error Fix - RiskTriageEngine

## Error Message
```
ImportError: cannot import name 'RiskTriageEngine' from 'src.analyzer'
```

## Root Cause
Streamlit cached the old version of `src/analyzer.py` before the new code was added. The autoformatter reformatted the files, but Streamlit's cache wasn't cleared.

## Solution

### Option 1: Clear Python Cache (Recommended)
```bash
# Clear all Python cache files
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Restart Streamlit
streamlit run app.py
```

### Option 2: Force Streamlit Cache Clear
In the Streamlit UI:
1. Press `C` to clear cache
2. Or click the hamburger menu (☰) → "Clear cache"
3. Refresh the page

### Option 3: Restart Streamlit
```bash
# Kill the Streamlit process
pkill -f streamlit

# Start fresh
streamlit run app.py
```

## Verification

The code is working correctly - verified with:
```bash
python -c "from src.analyzer import RiskTriageEngine; print('✓ Import works')"
# Output: ✓ Import works
```

The issue is purely a caching problem, not a code problem.

## What Was Added

The following were successfully added to `src/analyzer.py`:
1. `classify_risk()` function - Classifies risks by business impact
2. `check_hardcode_consistency()` function - Checks if hardcodes are consistent
3. `RiskTriageEngine` class - Organizes risks into 3 tiers

All imports are working in fresh Python sessions.

## Quick Test
```bash
# This should work without errors:
python test_triage_system.py
```

Expected output:
```
✓ Circular reference → Fatal Error
✓ Phantom link → Fatal Error
✓ Inconsistent formula → Integrity Risk
...
✅ All tests passed!
```

---

**Status**: Code is correct, just needs cache clear + Streamlit restart
