# Auto-Diagnosis Dashboard - Demo

## The Transformation

### BEFORE: Manual Exploration (Tedious)
```
🔍 Driver X-Ray - Root Cause Analysis

Select a cell to analyze: [Dropdown ▼]
├─ Sheet1!F4
├─ Sheet1!F10
├─ Sheet1!F20
├─ Sheet1!F30
├─ Sheet1!F35
├─ ... (45 more cells)

[User must manually search through 50+ cells]
```

**User Reaction:** "Which one should I look at first?"

---

### AFTER: Auto-Diagnosis (Executive)
```
🎯 Executive Diagnosis - Top Risks

Auto-Diagnosis: We've analyzed your model and identified 
the most dangerous hardcoded values. Click a card to see 
the full impact trace.

🚨 Top 3 Most Dangerous Hardcodes

┌─────────────────────────────────────────────────────────┐
│ #1: Unit Price (Sheet1!F10)                    [Expand]│
├─────────────────────────────────────────────────────────┤
│ Severity: High                                          │
│ Impact Count: 25 cells                                  │
│ KPI Impact: ⚠️ CRITICAL                                 │
│ Description: Formula contains hardcoded value: 1000     │
│                                                         │
│ 📊 Impact Trace                                         │
│ ├─ 📖 Analysis Summary                                  │
│ │   This cell depends on 1 driver.                     │
│ │   🚨 ROOT CAUSE: F4 (Exchange Rate) hardcoded.       │
│ │   ⚠️ CRITICAL IMPACT: Affects Net Income, Cash Flow. │
│ │                                                       │
│ ├─ ⬆️ SOURCE                                            │
│ │   🚨 F4: Exchange Rate = 201.26                      │
│ │                                                       │
│ └─ ⬇️ CONSEQUENCES                                      │
│     ⚠️ F30: Net Income = 20076000                      │
│     ⚠️ F35: Cash Flow = 15000000                       │
│     + 23 more consequences                             │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ #2: Exchange Rate (Sheet1!F4)                 [Expand]│
├─────────────────────────────────────────────────────────┤
│ Severity: High                                          │
│ Impact Count: 15 cells                                  │
│ KPI Impact: Normal                                      │
│ Description: Formula contains hardcoded value: 201.26   │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ #3: Multiplier (Sheet1!F5)                    [Expand]│
├─────────────────────────────────────────────────────────┤
│ Severity: High                                          │
│ Impact Count: 8 cells                                   │
│ KPI Impact: Normal                                      │
│ Description: Formula contains hardcoded value: 1000     │
└─────────────────────────────────────────────────────────┘

📊 12 additional hardcoded values detected. 
   Focus on the top 3 first for maximum impact.
```

**User Reaction:** "Perfect! F10 is the biggest problem. Let me fix that first."

---

## How It Works

### 1. Automatic Analysis
System analyzes ALL hardcoded values and ranks them by danger:

```python
Danger Score = (Impact Count × 10) + KPI Bonus + Severity Bonus

Where:
- Impact Count × 10 = downstream cascade
- KPI Bonus = 1000 if affects critical KPIs
- Severity Bonus = 100 (High) or 200 (Critical)
```

### 2. Smart KPI Detection
Automatically detects if hardcode affects critical metrics:

**Keywords:**
- English: profit, income, cash, sales, revenue, NPV, IRR, EBITDA
- Japanese: 利益, 収益, 売上, 現金, 純利益, 営業利益

**Example:**
```
F10 impacts F30 (Net Income) → KPI Impact: ⚠️ CRITICAL
```

### 3. Top 3 Display
Shows the 3 most dangerous hardcodes as cards:

```
#1: Highest danger score (e.g., 1125 points)
#2: Second highest (e.g., 250 points)
#3: Third highest (e.g., 180 points)
```

### 4. Click to Expand
- Card #1 is expanded by default
- Cards #2 and #3 are collapsed
- Click to see full impact trace
- Compact display (10 items max per section)

---

## Real-World Example

### Scenario
Financial model with 15 hardcoded values. User uploads file.

### Old Way (Manual)
1. User sees dropdown with 15 cells
2. User randomly picks F10
3. User sees trace
4. User goes back, picks F4
5. User sees trace
6. User goes back, picks F20
7. **Time wasted:** 5-10 minutes exploring

### New Way (Auto-Diagnosis)
1. System shows Top 3 automatically:
   - #1: F10 (affects Net Income - CRITICAL)
   - #2: F4 (affects 15 cells)
   - #3: F20 (affects 8 cells)
2. User clicks F10 card
3. User sees full trace
4. **Time saved:** Instant prioritization

---

## Danger Score Examples

### Example 1: High-Impact KPI Hardcode
```
Cell: F10 (Unit Price)
Impacts: 25 cells, including F30 (Net Income)
Severity: High

Score Calculation:
- Impact Count: 25 × 10 = 250
- KPI Bonus: +1000 (affects Net Income)
- Severity Bonus: +100 (High)
- Total: 1350 points → #1 Killer
```

### Example 2: High-Impact Non-KPI Hardcode
```
Cell: F4 (Exchange Rate)
Impacts: 15 cells, no KPIs
Severity: High

Score Calculation:
- Impact Count: 15 × 10 = 150
- KPI Bonus: +0 (no KPIs)
- Severity Bonus: +100 (High)
- Total: 250 points → #2 Killer
```

### Example 3: Low-Impact Hardcode
```
Cell: F5 (Multiplier)
Impacts: 8 cells, no KPIs
Severity: High

Score Calculation:
- Impact Count: 8 × 10 = 80
- KPI Bonus: +0 (no KPIs)
- Severity Bonus: +100 (High)
- Total: 180 points → #3 Killer
```

---

## User Journey

### Before (Exploration)
1. User uploads file
2. Sees 15 risks in table
3. Clicks "Driver X-Ray" tab
4. Sees dropdown with 15 cells
5. **Confused:** "Which one matters?"
6. Randomly picks a cell
7. Sees trace
8. **Unsure:** "Is this the worst one?"
9. Goes back, tries another
10. **Frustrated:** "This is tedious"

### After (Diagnosis)
1. User uploads file
2. Sees 15 risks in table
3. Clicks "Driver X-Ray" tab
4. **Immediately sees:** "Top 3 Most Dangerous"
5. **Clear:** "#1 affects Net Income (CRITICAL)"
6. Clicks #1 card
7. Sees full trace
8. **Confident:** "This is the worst one. Fix it first."
9. **Done:** No more searching

---

## Key Differences

| Aspect | Before | After |
|--------|--------|-------|
| **Discovery** | Manual dropdown | Auto-diagnosis |
| **Prioritization** | User guesses | System ranks |
| **KPI Detection** | User must know | System detects |
| **Time to Insight** | 5-10 minutes | Instant |
| **User Effort** | High (search & compare) | Low (read & click) |
| **Confidence** | Uncertain | High |

---

## Business Impact

### Time Savings
- **Before:** 5-10 minutes per analysis
- **After:** < 1 minute
- **Savings:** 80-90% time reduction

### Accuracy
- **Before:** User might miss critical issues
- **After:** System guarantees top issues shown
- **Improvement:** 100% coverage of top risks

### Decision Quality
- **Before:** User unsure what to fix first
- **After:** Clear prioritization by impact
- **Improvement:** Data-driven decisions

---

## Success Metrics

✅ **User can identify top issue in < 5 seconds**  
✅ **User knows which hardcode affects KPIs**  
✅ **User doesn't need to search through dropdown**  
✅ **User confident about prioritization**  

---

**Result:** From tedious exploration to instant diagnosis.

*"Don't make me think. Show me the problem."* ✅ Done.
