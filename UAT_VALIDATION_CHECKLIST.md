# UAT Validation Checklist

**Business Owner:** Please complete this checklist to validate the fixes.

---

## Pre-Test Setup

- [ ] Application is running (`streamlit run app.py`)
- [ ] Vietnam Plan Excel file is ready
- [ ] Browser is open to the application

---

## Test 1: Context Extraction (CRITICAL)

### Steps:
1. Upload Vietnam Plan file
2. Wait for analysis to complete
3. Go to "All Risks" tab
4. Look at the "Context" column

### Validation:

**✅ PASS if Context shows:**
- [ ] Text labels (e.g., "売上高", "純資産", "Exchange Rate")
- [ ] Empty strings (acceptable if no text found)
- [ ] Years (e.g., "2025") if applicable

**❌ FAIL if Context shows:**
- [ ] Formulas starting with `=` (e.g., "=(D18*E18)")
- [ ] Formula patterns (e.g., "=-D24+D25")
- [ ] Numbers (e.g., "100", "201.26")

### Result:
- [ ] PASS - Context shows text labels only
- [ ] FAIL - Context shows formulas or numbers

---

## Test 2: CSV Export (CRITICAL)

### Steps:
1. Copy the risk table from "All Risks" tab
2. Paste into Excel or Google Sheets
3. Look at the "Context" column

### Validation:

**✅ PASS if:**
- [ ] Context column contains text labels
- [ ] NO formulas visible (no cells starting with `=`)
- [ ] NO numbers visible (except years)

**❌ FAIL if:**
- [ ] Any cell in Context column starts with `=`
- [ ] Any cell in Context column is a number (except years)

### Result:
- [ ] PASS - CSV Context is clean
- [ ] FAIL - CSV Context has formulas/numbers

---

## Test 3: Graph Visualization

### Steps:
1. Go to "Dependency Tree" tab
2. Look at the graph nodes (blue dots)

### Validation:

**✅ PASS if:**
- [ ] Labels are visible on nodes
- [ ] Labels show format: "Address: Context" (e.g., "F24: 純資産")
- [ ] Labels are readable (not too small)

**❌ FAIL if:**
- [ ] No labels visible (just blue dots)
- [ ] Labels are too small to read
- [ ] Labels are cut off or truncated incorrectly

### Result:
- [ ] PASS - Graph labels are visible and readable
- [ ] FAIL - Graph labels are missing or unreadable

---

## Test 4: Regression Testing

### Steps:
1. Test other features to ensure nothing broke
2. Try uploading different Excel files
3. Check health score calculation

### Validation:

**✅ PASS if:**
- [ ] Health score displays correctly
- [ ] Risk detection works
- [ ] File parsing works
- [ ] No errors or crashes

**❌ FAIL if:**
- [ ] Application crashes
- [ ] Features don't work
- [ ] Errors appear

### Result:
- [ ] PASS - No regressions detected
- [ ] FAIL - Something broke

---

## Overall Result

### Summary:
- Test 1 (Context Extraction): [ ] PASS / [ ] FAIL
- Test 2 (CSV Export): [ ] PASS / [ ] FAIL
- Test 3 (Graph Visualization): [ ] PASS / [ ] FAIL
- Test 4 (Regression Testing): [ ] PASS / [ ] FAIL

### Decision:
- [ ] **APPROVE** - All tests passed, ready for production
- [ ] **REJECT** - Some tests failed, needs more work

### Notes:
```
[Add any observations, issues, or feedback here]




```

---

## Sign-Off

**Business Owner Name:** ___________________________

**Date:** ___________________________

**Signature:** ___________________________

---

## If Tests Fail

**Please provide:**
1. Which test failed?
2. What did you see? (screenshot if possible)
3. What did you expect to see?
4. Which file were you testing with?

**Contact:** Developer (Kiro AI Agent)

---

**Version:** 1.0  
**Date:** December 2, 2025
