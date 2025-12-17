# Diagnostic Suite - Quick Test Guide

**Goal**: Verify all 5 diagnostic features work correctly

---

## 🚀 Start Application

```bash
streamlit run app.py
```

---

## ✅ Test Checklist (10 minutes)

### 1. Multi-Column Context Selector (2 minutes)

**Location**: Sidebar → Settings → Context Labels

**Test**:
- [ ] Field shows "Label Source Columns (Range)"
- [ ] Default value is "A:D"
- [ ] Change to "B:C" and upload file
- [ ] Verify labels in risk list use columns B-C only

**Expected**: Labels concatenate with " > " separator (e.g., "SGA > Personnel > Salary")

---

### 2. Logic Translator (2 minutes)

**Location**: Driver X-Ray tab → Click any risk card

**Test**:
- [ ] Upload file with formulas
- [ ] Navigate to "Driver X-Ray" tab
- [ ] Click on a risk card
- [ ] Look for "Translated:" line below "Formula:"

**Expected**:
```
Formula: =F12*F13
Translated: =[Unit Price] * [Quantity]
💡 Formula with semantic labels - makes logic errors obvious
```

---

### 3. Row Consistency Scanner (2 minutes)

**Location**: Risk list (All Risks tab)

**Test**:
- [ ] Upload file with formulas in rows
- [ ] Look for "Inconsistent Formula" risk type
- [ ] Check severity is "High"
- [ ] Verify description mentions pattern difference

**Expected**:
```
Risk Type: Inconsistent Formula
Severity: High
Description: Formula pattern differs from 10 other cells in this row
```

**To trigger**: Create a row where 10 cells have =B5*C5 pattern but 1 cell has =B5+C5

---

### 4. Value Consistency Guard (2 minutes)

**Location**: Risk list (All Risks tab)

**Test**:
- [ ] Upload file with hardcoded values
- [ ] Look for "Conflicting Value" risk type
- [ ] Check severity is "High"
- [ ] Verify description mentions dominant value

**Expected**:
```
Risk Type: Conflicting Value
Severity: High
Description: Value 0.30 differs from 9 other cells with label 'Tax Rate' (expected 0.35)
```

**To trigger**: Create a row labeled "Tax Rate" with 10 cells having 0.35 and 1 cell having 0.30

---

### 5. Phantom Link Detector (2 minutes)

**Location**: Risk list (All Risks tab)

**Test**:
- [ ] Upload file with external references
- [ ] Look for "External Link" risk type
- [ ] Check severity is "Medium"
- [ ] Verify description shows external file name

**Expected**:
```
Risk Type: External Link
Severity: Medium
Description: Formula references external file: Budget2024.xlsx
```

**To trigger**: Create formula like `='[Budget2024.xlsx]Sheet1'!A5`

---

## 🐛 Common Issues

### Issue: No new risk types appearing
**Fix**: Ensure file has the specific patterns (see "To trigger" above)

### Issue: Translated formula not showing
**Fix**: Ensure cell has a formula (not just a value)

### Issue: Multi-column selector not working
**Fix**: Refresh browser (Ctrl+F5) and re-upload file

---

## 📊 Test Files

### Create Test File 1: Row Inconsistency

```
Row 5:
A5: 100
B5: 200
C5: =A5*B5
D5: =A5*B5
E5: =A5*B5
F5: =A5+B5  <- Different pattern!
```

**Expected**: "Inconsistent Formula" risk at F5

---

### Create Test File 2: Value Conflict

```
Row 10 (Label: "Tax Rate"):
A10: Tax Rate
B10: 0.35
C10: 0.35
D10: 0.35
E10: 0.30  <- Different value!
```

**Expected**: "Conflicting Value" risk at E10

---

### Create Test File 3: External Link

```
A1: ='[OtherFile.xlsx]Sheet1'!A1
```

**Expected**: "External Link" risk at A1

---

## ✅ Success Criteria

All checkboxes above should be checked (✓)

**If all pass**: ✅ Diagnostic Suite working correctly  
**If any fail**: ⚠️ Review error logs and retry

---

## 📸 Screenshot Checklist

For documentation, capture:
1. Multi-column selector in sidebar
2. Translated formula in X-Ray
3. Inconsistent Formula risk in list
4. Conflicting Value risk in list
5. External Link risk in list

---

## 🎯 Next Steps

1. **If successful**: Test with Vietnam Plan
2. **If issues found**: Document and fix
3. **After testing**: Update README with new features
4. **Final step**: Deploy to production

---

**Time Required**: 10 minutes  
**Prerequisites**: Excel file with test patterns  
**Command**: `streamlit run app.py`
