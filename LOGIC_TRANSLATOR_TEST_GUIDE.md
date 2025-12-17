# Logic Translator - Quick Test Guide

## 🎯 What to Test

Logic Translator has been integrated into the Master-Detail UI. This guide helps you verify it works correctly.

---

## ✅ Quick Test Steps

### 1. Start the Application
```bash
streamlit run app.py
```

### 2. Upload Excel File
- Use any Excel file with risks (e.g., `Business_Plan_final_20211123.xlsx`)
- Wait for analysis to complete

### 3. Navigate to Risk Tabs
- Click on any risk tab: **Fatal Errors**, **Integrity Risks**, or **Structural Debt**
- You should see the Master-Detail layout (table on left, details on right)

### 4. Select a Risk with Formula
- Click on any risk in the table (especially **Inconsistent Formula** or **Hidden Hardcode**)
- Look at the right panel (詳細パネル)

### 5. Verify Logic Translator Section
You should see three sections in the detail panel:

```
#### ロジックX線
[Shows dependency trace]

---

#### 数式の意味
**元の数式:**
```
=F12*F13+G12*G13
```

**意味:**
```
=[Unit Price] * [Quantity] + [Tax Rate] * [Subtotal]
```

💡 この翻訳により、数式が何を参照しているか一目で分かります。

---

#### 修正案
[Shows suggestion if Hidden Hardcode]
```

---

## 🔍 What to Check

### ✅ Logic Translator Appears
- [ ] Section titled "数式の意味" (or "Formula Meaning" in English)
- [ ] Shows "元の数式" (Original Formula)
- [ ] Shows "意味" (Meaning)
- [ ] Shows helpful caption with 💡 icon

### ✅ Formula Translation Works
- [ ] Original formula displays correctly (e.g., `=F12*F13`)
- [ ] Translated formula shows labels (e.g., `=[Unit Price] * [Quantity]`)
- [ ] Cell references are replaced with meaningful names
- [ ] Falls back to cell address if no label available

### ✅ Works for Different Risk Types
- [ ] **Inconsistent Formula**: Shows formula translation
- [ ] **Hidden Hardcode**: Shows formula translation
- [ ] **External Link**: Shows formula translation (if formula exists)
- [ ] **Other risks**: Section hidden if no formula

### ✅ Handles Edge Cases
- [ ] Compressed risks (ranges like "F8:BM8"): Uses first cell
- [ ] Risks without formulas: Section not displayed
- [ ] AI OFF mode: Still works (no API required)

### ✅ Driver X-Ray Tab Hidden
- [ ] Only 3 tabs visible: **Fatal Errors**, **Integrity Risks**, **Structural Debt**
- [ ] No "Driver X-Ray" tab in the UI
- [ ] File Information tab still works

---

## 🐛 Common Issues

### Issue 1: Logic Translator Not Showing
**Symptom:** "数式の意味" section missing in detail panel

**Possible Causes:**
1. Selected risk has no formula (expected behavior)
2. Formula not in risk.details (check compressed risks)

**Solution:** Try selecting a different risk with a formula (e.g., Inconsistent Formula)

### Issue 2: Translation Shows Cell Addresses
**Symptom:** Translation shows `[F12]` instead of `[Unit Price]`

**Possible Causes:**
1. Context detection failed for that cell
2. Cell has no row/column labels

**Solution:** This is expected behavior (fallback). Try enabling AI for better context detection.

### Issue 3: Driver X-Ray Tab Still Visible
**Symptom:** 4 tabs instead of 3

**Possible Causes:**
1. Code not properly commented out in app.py

**Solution:** Check line 743 in app.py - should be commented with `#`

---

## 📊 Test Scenarios

### Scenario 1: Basic Formula Translation
1. Upload file with Inconsistent Formula risks
2. Select a risk
3. Verify translation shows semantic labels

**Expected Result:** Formula like `=F12*F13` becomes `=[Unit Price] * [Quantity]`

### Scenario 2: Hidden Hardcode with Formula
1. Upload file with Hidden Hardcode risks
2. Select a hardcode risk
3. Verify Logic Translator shows formula with hardcoded value

**Expected Result:** Formula like `=F12*1.02` becomes `=[Unit Price] * 1.02`

### Scenario 3: Compressed Risk (Range)
1. Upload file with range risks (e.g., "F8:BM8")
2. Select the range risk
3. Verify Logic Translator uses first cell (F8)

**Expected Result:** Translation based on F8's formula

### Scenario 4: AI OFF Mode
1. Remove API key from sidebar
2. Upload file
3. Select risk with formula
4. Verify Logic Translator still works

**Expected Result:** Translation works without AI (uses rule-based context)

---

## 🎓 Understanding the Output

### Good Translation Example
```
元の数式: =F12*F13+G12*G13
意味: =[Unit Price] * [Quantity] + [Tax Rate] * [Subtotal]
```
✅ Clear semantic meaning, easy to understand

### Fallback Translation Example
```
元の数式: =F12*F13
意味: =[F12] * [F13]
```
⚠️ No context labels found, falls back to cell addresses (still useful for structure)

### Complex Translation Example
```
元の数式: =SUM(F12:F24)*G5+H5
意味: =SUM([Revenue]:[Cost]) * [Tax Rate] + [Discount]
```
✅ Shows range references and multiple operations

---

## 📝 Feedback Checklist

After testing, please provide feedback on:

- [ ] **Usefulness**: Does the translation help you understand formulas?
- [ ] **Accuracy**: Are the semantic labels correct?
- [ ] **Performance**: Does it load instantly?
- [ ] **UI/UX**: Is the layout clear and readable?
- [ ] **Coverage**: Does it work for all risk types you tested?

---

## 🚀 Next Steps

### If Everything Works ✅
- Approve Phase 1 implementation
- Discuss Phase 2 (Error Detection) timeline
- Consider additional features

### If Issues Found ❌
- Document specific issues with screenshots
- Provide example Excel files that fail
- Describe expected vs actual behavior

---

## 💡 Tips

1. **Best Results**: Enable AI for better context detection
2. **Quick Test**: Use "Inconsistent Formula" risks (always have formulas)
3. **Edge Cases**: Test with compressed risks and ranges
4. **Comparison**: Compare with original Excel file to verify accuracy

---

## 📞 Support

If you encounter issues:
1. Check this guide for common solutions
2. Verify Python files compile: `python3 -m py_compile src/master_detail_ui.py`
3. Check browser console for JavaScript errors
4. Provide specific error messages and steps to reproduce

---

**Status:** Ready for Testing
**Estimated Test Time:** 5-10 minutes
**Required Files:** Any Excel file with formula-based risks
