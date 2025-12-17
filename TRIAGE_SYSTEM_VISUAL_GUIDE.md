# 3-Tier Risk Triage System - Visual Guide

## Before: Technical Severity (Overwhelming)

```
📋 Detected Risks

[All Risks] [By Severity] [Driver X-Ray] [Risk Heatmap] [Debug Log]

All Risks:
┌─────────────────┬──────────┬──────────┬─────────────────────────────────┐
│ Risk Type       │ Severity │ Location │ Description                     │
├─────────────────┼──────────┼──────────┼─────────────────────────────────┤
│ Hidden Hardcode │ High     │ Sheet1!A1│ Hardcoded value detected        │
│ Hidden Hardcode │ High     │ Sheet1!A2│ Hardcoded value detected        │
│ Hidden Hardcode │ High     │ Sheet1!A3│ Hardcoded value detected        │
│ Circular Ref    │ Critical │ Sheet1!B1│ Circular reference detected     │
│ Merged Cell     │ Medium   │ Sheet1!C1│ Merged cell detected            │
│ Hidden Hardcode │ High     │ Sheet1!D1│ Hardcoded value detected        │
│ Hidden Hardcode │ High     │ Sheet1!D2│ Hardcoded value detected        │
└─────────────────┴──────────┴──────────┴─────────────────────────────────┘

❌ Problem: User sees 7 risks, all look similar, unclear what to fix first
```

## After: Business Impact (Actionable)

```
📋 Detected Risks

[🔴 Fatal Errors (1)] [⚠️ Integrity Risks (2)] [🔧 Structural Debt (4)] [🎯 Driver X-Ray] [📊 Risk Heatmap]

Tab 1: 🔴 Fatal Errors
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The model is broken or uncomputable
🚨 Priority: CRITICAL - Must fix immediately

┌──────┬────────┬─────────┬──────────────────────────────────────────┐
│ Cell │ Sheet  │ Context │ Description                              │
├──────┼────────┼─────────┼──────────────────────────────────────────┤
│ B1   │ Sheet1 │ Revenue │ Circular reference detected              │
└──────┴────────┴─────────┴──────────────────────────────────────────┘

✅ Clear: 1 critical issue that breaks calculations


Tab 2: ⚠️ Integrity Risks
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The model runs, but logic/values seem wrong
🔍 Review Priority: Hidden bugs live here

┌──────┬────────┬─────────┬──────────────────────────────────────────┐
│ Cell │ Sheet  │ Context │ Description                              │
├──────┼────────┼─────────┼──────────────────────────────────────────┤
│ D1   │ Sheet1 │ Cost    │ Hardcoded value: 50 (inconsistent)       │
│ D2   │ Sheet1 │ Cost    │ Hardcoded value: 75 (inconsistent)       │
└──────┴────────┴─────────┴──────────────────────────────────────────┘

⚠️ Alert: Same label "Cost" has different values → Update omission!


Tab 3: 🔧 Structural Debt
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Works correctly now, but hard to maintain
ℹ️ Priority: MEDIUM - Technical debt to address over time

┌──────┬────────┬─────────┬──────────────────────────────────────────┐
│ Cell │ Sheet  │ Context │ Description                              │
├──────┼────────┼─────────┼──────────────────────────────────────────┤
│ A1   │ Sheet1 │ Revenue │ Hardcoded value: 100 (consistent)        │
│ A2   │ Sheet1 │ Revenue │ Hardcoded value: 100 (consistent)        │
│ A3   │ Sheet1 │ Revenue │ Hardcoded value: 100 (consistent)        │
│ C1   │ Sheet1 │ Header  │ Merged cell detected                     │
└──────┴────────┴─────────┴──────────────────────────────────────────┘

✅ OK: These work correctly but should be improved when you have time
```

## Key Improvements

### 1. Clear Prioritization
- **Before**: "7 risks, all High/Critical severity"
- **After**: "1 MUST FIX NOW, 2 REVIEW CAREFULLY, 4 FIX LATER"

### 2. Business Context
- **Before**: "Hidden Hardcode" (technical term)
- **After**: "Inconsistent values → Update omission" (business problem)

### 3. Visual Hierarchy
- **Tab 1 (Red)**: Calculation breakage - immediate action required
- **Tab 2 (Orange)**: Hidden bugs - careful review needed
- **Tab 3 (Blue)**: Maintenance issues - address over time

### 4. Smart Classification
- **Consistent hardcodes** (same label, same value) → Structural Debt
- **Inconsistent hardcodes** (same label, different values) → Integrity Risk
- Rationale: Inconsistent values indicate someone forgot to update all instances

## User Workflow

### Old Workflow (Overwhelming)
1. See 7 risks in one list
2. All look similar (mostly "High" severity)
3. Unclear where to start
4. Analysis paralysis

### New Workflow (Actionable)
1. Check Tab 1 (Fatal Errors) - Fix immediately
2. Review Tab 2 (Integrity Risks) - Investigate carefully
3. Note Tab 3 (Structural Debt) - Plan for later
4. Clear action plan

## Color Coding

```
🔴 Red (Fatal Errors)
   #DC2626
   "The model is broken"
   
⚠️ Orange (Integrity Risks)
   #F59E0B
   "The model seems wrong"
   
🔧 Blue (Structural Debt)
   #3B82F6
   "The model is hard to maintain"
```

## Tab Counts

Tab labels show risk counts for quick assessment:
- `🔴 Fatal Errors (1)` - 1 critical issue
- `⚠️ Integrity Risks (2)` - 2 suspicious issues
- `🔧 Structural Debt (4)` - 4 maintenance issues

Total: 7 risks, but now organized by business impact

---

**Result**: Users can now focus on what matters most instead of being overwhelmed by a long list of technical issues.
