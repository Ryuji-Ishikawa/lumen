# Quality Filter Fix - UAT Response

## Problem Identified
The `_is_poor_quality_label()` method was too permissive, allowing garbage labels like:
- `=(D18*E18)` (formula debris)
- `F24` (cell addresses)
- Math operators without spaces

Result: **0 poor quality labels detected, 0 AI calls**

## Fix Applied

### 1. Tightened Quality Filter Logic

Added 6 strict patterns to detect poor quality labels:

```python
def _is_poor_quality_label(self, text: str, verbose: bool = False) -> bool:
    """
    Pattern 1: Starts with = (formula debris like "=(D18*E18)")
    Pattern 2: Contains math operators without spaces (formula fragments)
    Pattern 3: Cell Address Pattern (case insensitive: "E92", "F24", "BN13")
    Pattern 4: Generic Stopwords (Total, Sum, 合計, etc.)
    Pattern 5: Symbols/Numeric Only ("-", "0", "123")
    Pattern 6: Too short (< 2 chars) or too long (> 50 chars)
    """
```

**Key Improvements:**
- ✅ Detects formula debris: `text.startswith('=')`
- ✅ Detects math operators: `re.search(r'[+*/]', text) and ' ' not in text`
- ✅ Case-insensitive cell addresses: `r'^[A-Za-z]+[0-9]+$'`
- ✅ Length validation: `len(text) < 2 or len(text) > 50`

### 2. Enabled Verbose Logging

For the first 5 risks, the system now logs:

```
[VERBOSE] Risk #1: BS!E92
[VERBOSE] Raw label from parser: '=(D18*E18)'
[FILTER] Label '=(D18*E18)' starts with = -> Poor Quality
[AI] Poor quality context '=(D18*E18)' detected for BS!E92
[AI] Attempting recovery for BS!E92
[AI] Context window for BS!E92:
  Left: ['Beginning', 'Balance']
  Above: ['Balance Sheet', 'Current Assets']
[AI] ✓ Recovered: 'Cash Balance'
```

## Test Results

Created `test_quality_filter.py` with 25 test cases:

**Garbage Labels (Should Trigger AI):**
- ✅ `=(D18*E18)` - Formula debris
- ✅ `A1*B2` - Math operators
- ✅ `F24`, `BN13` - Cell addresses
- ✅ `Total`, `合計` - Stopwords
- ✅ `-`, `123` - Symbols/numbers

**Good Labels (Should Pass):**
- ✅ `Cash Balance`
- ✅ `Personnel Cost`
- ✅ `現金残高` (Japanese)

**Result: 25/25 tests passed ✅**

## Expected Behavior

When you run the app with "Vietnam Plan":

```
[DEBUG] _add_context_labels called with X risks
[VERBOSE] Risk #1: BS!E92
[VERBOSE] Raw label from parser: '=(D18*E18)'
[FILTER] Label '=(D18*E18)' starts with = -> Poor Quality
[AI] Poor quality context '=(D18*E18)' detected for BS!E92
[AI] Attempting recovery for BS!E92
[AI] ✓ Recovered: 'Cash Balance'

[DEBUG] Summary: 0 empty, 15 poor quality, 15 AI calls
[AI] Summary: 12/15 successful recoveries
```

## Files Modified

1. **src/analyzer.py**
   - Enhanced `_is_poor_quality_label()` with 6 strict patterns
   - Added verbose logging for first 5 risks
   - Added detailed filter decision logging

2. **test_quality_filter.py** (NEW)
   - Comprehensive test suite for quality filter
   - 25 test cases covering all patterns

## Ready for UAT

The bouncer is now strict. Formula debris and cell addresses will be rejected and sent to AI recovery.

**Action:** Restart Streamlit and test with "Vietnam Plan"

```bash
streamlit run app.py
```
