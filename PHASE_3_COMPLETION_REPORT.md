# Phase 3 Completion Report: Monthly Guardian (Composite Key Matching)

## Executive Summary

**Status:** ✅ COMPLETE - The Retention Engine is operational

**Business Impact:** Users can now intelligently track monthly changes in their Excel models, even when rows are inserted, deleted, or reordered. This is our competitive moat for monthly board meeting preparation.

**Test Results:** 16/16 tests passing (100% pass rate)

---

## What We Built

### 1. Composite Key Matching Engine
**The Core Technology**

Users can select key columns (e.g., "Account Name" / 勘定科目) to match rows across monthly versions:

```
Example: Monthly P&L Comparison
Old File (April):          New File (May):
Row 2: 売上高              Row 2: 売上高        ✓ Matched
Row 3: 売上原価            Row 3: 新規項目      ➕ Added
Row 4: 販売費              Row 4: 売上原価      ✓ Matched (moved from row 3)
Row 5: 営業利益            Row 5: 販売費        ✓ Matched (moved from row 4)
                          Row 6: 営業利益      ✓ Matched (moved from row 5)
```

**Result:** All rows matched correctly by content, not by row number.

### 2. Key Uniqueness Validator (Smart UX)
**The Safety Net**

Before running the diff, the system validates that selected key columns are unique enough:

**Scenario A: Non-Unique Keys (Bad)**
```
Column A only: 40% unique ⚠️
Duplicates found: ['売上高', '売上高', '売上高']

Warning: "These columns are not unique (40% unique). 
Please add another column like 'Department' to ensure accurate matching."
```

**Scenario B: Unique Keys (Good)**
```
Column A + B: 100% unique ✅
No duplicates found

Success: "Keys are unique (100% unique). 
These columns provide good matching accuracy."
```

### 3. Preview Matches Feature
**The Confidence Builder**

Users can preview how rows will be matched before running the full diff:

```
Preview Row Matches:
┌─────────────┬─────────┬─────────┬──────────┐
│ Key         │ Old Row │ New Row │ Status   │
├─────────────┼─────────┼─────────┼──────────┤
│ 売上高      │    2    │    2    │ ✓ Matched│
│ 売上原価    │    3    │    4    │ ✓ Matched│
│ 販売費      │    4    │    5    │ ✓ Matched│
│ 営業利益    │    5    │    6    │ ✓ Matched│
└─────────────┴─────────┴─────────┴──────────┘
```

### 4. Change Detection
**The Intelligence Layer**

The system distinguishes between:
- **Logic Changes** (Critical): Formula modified → Alert the user
- **Input Updates** (Normal): Value changed → Expected monthly update
- **Risk Changes**: Risks improved or degraded
- **Structural Changes**: Sheets added/removed

---

## Technical Implementation

### Files Modified

1. **src/diff.py**
   - Added `build_composite_keys_with_duplicates()` method
   - Updated `validate_key_uniqueness()` to detect duplicates
   - Enhanced row matching algorithm

2. **app.py**
   - Added Composite Key Matching UI section
   - Sheet selector for comparison
   - Key column input with validation
   - Real-time uniqueness feedback
   - Preview Matches button

3. **tests/test_composite_key_matching.py**
   - Added duplicate detection test
   - Validates 40% → 100% uniqueness improvement
   - Tests multi-column key combinations

### Test Coverage

**Phase 1 (Robust Parser):** 11 tests ✅
- Heavy merged cells
- Complex grid layouts
- Japanese text
- Circular references
- Cross-sheet complexity
- Edge cases
- Hanko boxes (approval stamps)

**Phase 3 (Composite Key Matching):** 5 tests ✅
- Composite key generation
- Row matching with insertion
- Uniqueness validation
- Logic change detection
- Duplicate key detection

**Total:** 16/16 tests passing (100% pass rate)

---

## User Experience Flow

### Step 1: Upload Files
```
Sidebar:
├── Upload Reference File (Old) → April_PL.xlsx
└── Upload Target File (New)    → May_PL.xlsx
```

### Step 2: Configure Matching
```
🔑 Composite Key Matching
Select Sheet to Compare: [PL ▼]
Key Columns: [A    ] (e.g., A or A,B)

Key Uniqueness Validation:
✅ Keys are unique (100% unique)
These columns provide good matching accuracy.

[🔍 Preview Row Matches]
```

### Step 3: Review Changes
```
📊 Comparison Summary
🎉 Model Health Improved! Score: 75 → 82 (+7)

📋 Changes Detected
├── Improved (3 risks fixed)
├── Degraded (1 new risk)
└── Structural (1 row added)
```

---

## Why This Matters (Business Value)

### The Problem We Solved
**Before:** Global tools match rows by row number
- Insert a row → All subsequent rows mismatch
- Reorder rows → Complete chaos
- Delete a row → False "changes" everywhere

**After:** Lumen matches rows by content (Account Name)
- Insert a row → Correctly identified as "added"
- Reorder rows → All rows still match correctly
- Delete a row → Correctly identified as "deleted"

### The Competitive Moat
This is **not** a feature that can be easily copied:
1. Requires deep understanding of Japanese Excel patterns
2. Requires intelligent key selection UX
3. Requires duplicate detection and validation
4. Requires preview functionality for user confidence

**Result:** Users trust the system and keep coming back monthly.

---

## Next Steps

### Recommended: Test with Real Data
Before proceeding to Phase 4, validate the competitive moat:
1. Upload a real monthly P&L (April vs May)
2. Test with row insertions/deletions
3. Verify matching accuracy
4. Gather user feedback

### Phase 4: Driver X-Ray (Next Priority)
Once Phase 3 is validated, proceed to:
- Trace hardcodes to their impact on drivers
- Show "This hardcode affects 15 cells including Revenue"
- Interactive dependency navigation

### Phase 5: AI Model Architect
- AI-powered formula explanations
- Breakdown suggestions for complex drivers
- PII/numeric masking for enterprise security

---

## Conclusion

**Phase 3 Status:** ✅ COMPLETE

**The "Hanko Box" gets them in the door.**
**The "Diff Engine" keeps them paying every month.**

The retention engine is now operational. Time to validate with real monthly P&L files and prepare for Phase 4.

---

**Prepared by:** Kiro AI
**Date:** December 2, 2025
**Test Results:** 16/16 passing (100%)
