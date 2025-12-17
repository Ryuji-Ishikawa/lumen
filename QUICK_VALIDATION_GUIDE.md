# Quick Validation Guide - 4 Bug Fixes

**For Business Owner - 5 Minute Validation**

---

## ✅ Bug 1A: Dirty Labels

**What to Check:** Context column in CSV export

**PASS if:**
- Context shows: `うち利益剰余金` ✅
- Context shows: `Revenue` ✅

**FAIL if:**
- Context shows: `(うち利益剰余金) @ =J9+K19-12076` ❌
- Context shows: `=J9+K19` ❌

---

## ✅ Bug 1B: Short Sight

**What to Check:** Cells far from Column A have context

**PASS if:**
- Cell G26 has Context: `Revenue` ✅
- Cell H30 has Context: `Sales` ✅

**FAIL if:**
- Cell G26 has Context: (empty) ❌
- Cell H30 has Context: None ❌

---

## ✅ Bug 2: Lazy Detection

**What to Check:** Formulas with multiple hardcodes

**PASS if:**
- Formula `=100630*0.02*5/12`
- Shows: `Hardcoded values: 100630, 0.02, 5` ✅

**FAIL if:**
- Formula `=100630*0.02*5/12`
- Shows: `Hardcoded value: 100630` ❌ (missing 0.02, 5)

---

## ✅ Bug 3: Bounding Box Trap

**What to Check:** Risk grouping for scattered cells

**PASS if:**
- F4 has 201.26 → Shows: `F4` ✅
- F8 has 201.26 → Shows: `F8` ✅
- (Two separate risks)

**FAIL if:**
- F4 and F8 have 201.26 → Shows: `F4...BN13` ❌
- (Grouped together, includes innocent cells)

---

## ✅ Bug 4: Black Void

**What to Check:** Dependency Tree visualization

**PASS if:**
- White background ✅
- Black text visible ✅
- Labels show: "F24: 純資産" ✅

**FAIL if:**
- Black background ❌
- Invisible nodes ❌
- No labels ❌

---

## Quick Test Procedure

1. **Upload** Vietnam Plan file
2. **Go to** "All Risks" tab
3. **Check** Context column (Bugs 1A, 1B, 2)
4. **Check** Cell locations (Bug 3)
5. **Go to** "Dependency Tree" tab
6. **Check** Background color (Bug 4)

**Total Time:** 5 minutes

---

## Pass/Fail Checklist

- [ ] Bug 1A: Context is clean (no formulas)
- [ ] Bug 1B: Context found for distant cells
- [ ] Bug 2: All hardcodes detected
- [ ] Bug 3: Scattered cells not grouped
- [ ] Bug 4: Graph has white background

**If all checked:** ✅ APPROVE  
**If any unchecked:** ❌ REJECT

---

**Date:** December 2, 2025  
**Developer:** Kiro AI Agent
