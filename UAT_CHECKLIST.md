# UAT Checklist - Debug Dashboard

## Pre-Flight Check

### Environment Setup
- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Streamlit working (`streamlit --version`)

### Start Application
```bash
streamlit run app.py
```

Expected: Browser opens to `http://localhost:8501`

---

## Core Functionality Tests

### 1. File Upload (Single File)
- [ ] Upload a small Excel file (< 1MB)
- [ ] Verify parse time is displayed
- [ ] Check Debug Log tab shows details
- [ ] Verify no errors

**Expected Output:**
```
✅ Successfully parsed [filename] in X.XXs
```

### 2. File Upload (Large File)
- [ ] Upload a large Excel file (10-50MB)
- [ ] Verify spinner shows during parsing
- [ ] Check parse time is reasonable (< 60s)
- [ ] Verify Debug Log shows file size

**Expected Output:**
```
ℹ️ File size: XX.XX MB
✅ Parsed [filename] in XX.XXs
```

### 3. Japanese Excel Files
- [ ] Upload file with Japanese text
- [ ] Verify Japanese characters display correctly
- [ ] Check merged cells are handled
- [ ] Verify no encoding errors

**Expected Output:**
- Japanese text renders properly
- No garbled characters
- Merged ranges detected

### 4. Error Handling
- [ ] Upload a password-protected file
- [ ] Verify app does NOT crash
- [ ] Check error message is displayed
- [ ] Verify Debug Log shows error details

**Expected Output:**
```
⚠️ Attention Required
[Error message]
💡 Tip: Make sure your file is a valid .xlsx format...
```

### 5. Debug Log Tab
- [ ] Navigate to "Debug Log" tab
- [ ] Verify parse time metric is shown
- [ ] Check log entries are displayed
- [ ] Expand log entries to see details

**Expected Output:**
```
Total Parse Time: X.XXs

X log entries

✅ [HH:MM:SS] Parsed [filename] in X.XXs
  {
    "sheets": X,
    "cells": X,
    "merged_ranges": X
  }
```

---

## Advanced Tests

### 6. Differential Analysis
- [ ] Upload two files (Reference + Target)
- [ ] Verify both files parse successfully
- [ ] Check Composite Key Matching UI appears
- [ ] Test uniqueness validation

**Expected Output:**
```
📊 Differential Analysis Mode - Comparing two files
✅ Successfully parsed both files in X.XXs
```

### 7. Risk Detection
- [ ] Upload file with hardcoded values
- [ ] Verify risks are detected
- [ ] Check health score is calculated
- [ ] Navigate through risk tabs

**Expected Output:**
```
🔴 Health Score: XX/100
Critical: X | High: X | Medium: X | Low: X
```

### 8. Dependency Graph
- [ ] Navigate to "Dependency Tree" tab
- [ ] Verify graph statistics are shown
- [ ] Test sheet filter
- [ ] Adjust node limit slider

**Expected Output:**
```
Graph Statistics: X cells, X dependencies
[Interactive graph visualization]
```

### 9. Performance Monitoring
- [ ] Upload multiple files in sequence
- [ ] Check parse times are consistent
- [ ] Verify Debug Log accumulates entries
- [ ] Test with files of varying sizes

**Expected Behavior:**
- Parse times scale with file size
- No memory leaks
- App remains responsive

---

## Edge Cases

### 10. Corrupted Files
- [ ] Upload a corrupted .xlsx file
- [ ] Verify graceful error handling
- [ ] Check Debug Log shows error type

### 11. Very Large Files (>50MB)
- [ ] Upload a file larger than 50MB
- [ ] Verify timeout handling
- [ ] Check error message is helpful

### 12. Complex Merged Cells
- [ ] Upload file with heavy merged cells
- [ ] Verify Virtual Fill works
- [ ] Check no cells are lost
- [ ] Verify dependency graph includes virtual cells

### 13. Circular References
- [ ] Upload file with circular references
- [ ] Verify detection works
- [ ] Check error is logged
- [ ] Verify app doesn't hang

---

## Debug Dashboard Specific Tests

### 14. Log Levels
- [ ] Verify INFO logs (blue ℹ️)
- [ ] Verify SUCCESS logs (green ✅)
- [ ] Verify WARNING logs (yellow ⚠️)
- [ ] Verify ERROR logs (red ❌)

### 15. Log Details
- [ ] Expand log entries
- [ ] Verify JSON details are shown
- [ ] Check timestamps are accurate
- [ ] Verify reverse chronological order

### 16. Performance Metrics
- [ ] Check parse time is displayed
- [ ] Verify file size is logged
- [ ] Check cell count is accurate
- [ ] Verify merged range count

---

## Real-World Scenarios

### 17. Confidential Business Files
- [ ] Upload actual business P&L
- [ ] Verify sensitive data is parsed correctly
- [ ] Check no data is leaked in logs
- [ ] Verify all Japanese patterns work

### 18. Monthly Comparison
- [ ] Upload April and May P&L files
- [ ] Test Composite Key Matching
- [ ] Verify row matching works with insertions
- [ ] Check logic changes are detected

### 19. Complex Financial Models
- [ ] Upload multi-sheet financial model
- [ ] Verify all sheets are parsed
- [ ] Check cross-sheet dependencies work
- [ ] Verify performance is acceptable

---

## Sign-Off

### Business Owner Approval

**Tested By:** ___________________

**Date:** ___________________

**Files Tested:**
1. ___________________
2. ___________________
3. ___________________

**Issues Found:**
- [ ] None - Ready for Phase 5
- [ ] Minor issues (list below)
- [ ] Major issues (list below)

**Issues:**
_______________________________________
_______________________________________
_______________________________________

**Decision:**
- [ ] ✅ APPROVED - Proceed to Phase 5 (AI Integration)
- [ ] ⚠️ CONDITIONAL - Fix issues then proceed
- [ ] ❌ BLOCKED - Major rework needed

**Notes:**
_______________________________________
_______________________________________
_______________________________________

---

## Success Criteria

**Must Have:**
- ✅ App starts without errors
- ✅ Files upload successfully
- ✅ Parse time is displayed
- ✅ Debug Log shows details
- ✅ Errors don't crash the app
- ✅ Japanese text works correctly

**Nice to Have:**
- ✅ Parse time < 30s for typical files
- ✅ Error messages are actionable
- ✅ Debug Log is easy to read
- ✅ Performance is consistent

**Blockers:**
- ❌ App crashes on file upload
- ❌ Japanese text is garbled
- ❌ Parse time > 60s for small files
- ❌ Errors are not caught

---

**Ready for UAT!** 🚀

*"I don't need it to look pretty yet. I need it to reveal the truth about my data."*
