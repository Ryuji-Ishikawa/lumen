# Risk Aggregation Fix - Phase 7.4

## Problem Statement

When the same hardcoded value (e.g., 201.26) appears in multiple locations, the system was showing **duplicate risks** in the Top 3:

**Before Fix:**
- #1: 全体開発費（百万VDN）※7年償却 - Value '201.26' (1 instance)
- #2: バイク製造費（百万VDN） - Value '201.26' (60 instances)
- #3: 車台販売収益（百万VDN） - Value '201.26' (60 instances)

This is confusing because:
1. **Same root cause**: All three risks are the same value (201.26)
2. **Redundant information**: User sees the same issue 3 times
3. **Misleading metrics**: Each risk shows partial impact, not total impact
4. **Wasted attention**: User must read 3 cards to understand 1 problem

## Solution: Aggregate Risks by Hardcoded Value

### Key Insight

**One hardcoded value = One risk**, regardless of how many locations it appears in.

### Implementation

**File: `app.py` (lines ~690-850)**

#### Step 1: Group Risks by Hardcoded Value

```python
from collections import defaultdict

# Group all risks with the same hardcoded value
risks_by_value = defaultdict(list)
for risk in hardcode_risks:
    hardcoded_value = risk.details.get('hardcoded_value', '')
    risks_by_value[hardcoded_value].append(risk)
```

#### Step 2: Aggregate Metrics Across All Locations

For each unique hardcoded value, calculate:

1. **Total Diffusion**: Sum of all instances across all locations
   ```python
   total_diffusion = sum(r.details.get('instance_count', 1) for r in risk_group)
   ```

2. **Total Dominance**: Union of all dependent cells
   ```python
   all_impacts = set()
   for risk in risk_group:
       impacts = model.get_dependents(risk.get_location())
       all_impacts.update(impacts)
   total_dominance = len(all_impacts)
   ```

3. **KPI Impact**: True if ANY location impacts a KPI
   ```python
   kpi_impact = any(check_kpi_impact(risk) for risk in risk_group)
   ```

#### Step 3: Create Aggregated Risk Object

```python
risk_scores.append({
    'primary_risk': risk_group[0],  # Representative risk
    'hardcoded_value': hardcoded_value,
    'all_locations': [r.get_location() for r in risk_group],
    'diffusion': total_diffusion,  # AGGREGATED
    'dominance': total_dominance,  # AGGREGATED
    'kpi_impact': kpi_impact,
    'score': calculated_score,
    'risk_count': len(risk_group)  # How many locations
})
```

### UI Changes

#### New Card Title Format

**Before:**
```
#1: 全体開発費（百万VDN）※7年償却 (プロジェクションVDN!F4)
```

**After:**
```
#1: Value '201.26' (8 locations affected)
```

#### New Metrics Display

```
┌─────────────┬─────────────┬──────────┬────────────┐
│ Diffusion   │ Dominance   │ Severity │ KPI Impact │
│ 423x        │ 150         │ High     │ ⚠️ YES     │
└─────────────┴─────────────┴──────────┴────────────┘
```

- **Diffusion**: Total occurrences across ALL locations
- **Dominance**: Total dependent cells across ALL locations
- **Severity**: From primary risk
- **KPI Impact**: True if ANY location impacts KPI

#### Location List

Added expandable section showing all affected locations:

```
📍 Show all locations
  - プロジェクションVDN!F4
  - プロジェクションVDN!F8...BM8
  - プロジェクションVDN!G9...BN9
  ... and 5 more locations
```

### AI Suggestion Updates

#### Updated Context Passed to AI

```python
cell_labels['diffusion'] = diffusion  # Aggregated total
cell_labels['dominance'] = dominance  # Aggregated total
cell_labels['affected_locations'] = risk_count  # NEW
```

#### Updated AI Prompt

**Before:**
```
- 出現回数: 423箇所
```

**After:**
```
- 出現回数: 423箇所 (ワークブック全体で8つの異なる場所に分散)

【重要】この値は8つの異なる場所で使用されています。
一元管理することで、すべての場所を同時に更新できます。
```

This helps the AI understand:
1. The value is scattered across multiple locations
2. Centralization will fix ALL locations at once
3. The total impact is much larger than any single location

## Expected Results

### Before Fix (Redundant)

```
Top 3 Most Dangerous Hardcodes:
#1: Value '201.26' at F4 (1 instance, 5 dependents)
#2: Value '201.26' at F8...BM8 (60 instances, 10 dependents)
#3: Value '201.26' at G9...BN9 (60 instances, 8 dependents)
```

User thinks: "Why am I seeing the same value 3 times?"

### After Fix (Aggregated)

```
Top 3 Most Dangerous Hardcodes:
#1: Value '201.26' (8 locations affected)
    Diffusion: 423x | Dominance: 150 | KPI Impact: YES
    
#2: Value '1000000' (9 locations affected)
    Diffusion: 269x | Dominance: 80 | KPI Impact: NO
    
#3: Value '0.4' (2 locations affected)
    Diffusion: 35x | Dominance: 120 | KPI Impact: YES
```

User thinks: "I have 3 different values to fix, each with clear total impact."

## Benefits

1. **No Duplicates**: Each unique value appears once
2. **Complete Picture**: Shows total impact across all locations
3. **Better Prioritization**: Ranks by total impact, not per-location
4. **Clearer Action**: Fix one value → fixes all locations
5. **AI Accuracy**: AI sees the full scope and suggests appropriate refactoring

## Testing

1. Upload Excel file with 201.26 appearing in 8 locations
2. Check Top 3 Most Dangerous Hardcodes
3. Verify:
   - Only ONE card for 201.26
   - Diffusion shows 423 (total)
   - Dominance shows aggregated dependents
   - Location list shows all 8 locations
   - AI suggestion mentions "8つの異なる場所"

## Technical Notes

### Why Aggregate by Value, Not by Location?

**Location-based** (old approach):
- F4 has 201.26 → Risk #1
- F8 has 201.26 → Risk #2
- G9 has 201.26 → Risk #3

Problem: Same root cause, different symptoms.

**Value-based** (new approach):
- 201.26 appears in 8 locations → ONE Risk

Solution: One root cause, one fix.

### Prescription Mode Selection

With aggregated metrics, prescription mode is more accurate:

```python
if volatility == "High":
    prescription_mode = "Scenario Planning"
elif dominance > 50:  # Uses TOTAL dominance
    prescription_mode = "Driver Decomposition"
elif diffusion > 3:  # Uses TOTAL diffusion
    prescription_mode = "Centralization"
else:
    prescription_mode = "Basic Refactoring"
```

For 201.26:
- Diffusion: 423 → Triggers "Centralization"
- Dominance: 150 → Also suggests "Driver Decomposition"
- Result: AI recommends creating a single driver cell

## Code Quality

- No breaking changes to existing APIs
- Backward compatible with single-location risks
- Clean separation of concerns (aggregation → scoring → display)
- Maintains all existing functionality

## Future Enhancements

1. **Visual Heatmap**: Show which sheets have the most occurrences
2. **Impact Timeline**: Show when each location was added
3. **Batch Fix**: "Fix all 8 locations" button
4. **Dependency Graph**: Visualize how locations are connected
