# Quick Test Guide - 5 Minute Validation

**Goal**: Verify all 3 UI components work correctly

---

## 🚀 Start Application

```bash
streamlit run app.py
```

**Expected**: Browser opens to http://localhost:8501

---

## ✅ Test Checklist (5 minutes)

### 1. Maturity Header (1 minute)

**Action**: Upload any Excel file with risks

**Verify**:
- [ ] Large maturity badge displays at top
- [ ] Badge has gold border
- [ ] Badge has purple gradient background
- [ ] Progress bar shows percentage
- [ ] Health score displays on left

**Expected Visual**:
```
┌──────────┬──────────────────┬──────────┐
│ Health   │   🏥 Level 1     │ Progress │
│ 75/100   │   [Gold Badge]   │ 45% → L2 │
└──────────┴──────────────────┴──────────┘
```

---

### 2. Locked Buttons (2 minutes)

**Action**: Scroll down to "Premium Features" section

**Verify**:
- [ ] Two buttons visible: "Goal Seek" and "Scenario Planning"
- [ ] Buttons have gold border
- [ ] Buttons have gradient background
- [ ] Hover effect: buttons scale up slightly

**Action**: Click "🔒 Goal Seek" button

**Verify**:
- [ ] Popup appears with unlock requirements
- [ ] Shows current maturity level
- [ ] Lists specific actions needed (e.g., "Fix 3 hardcodes")
- [ ] Progress bar displays
- [ ] Tip mentions "✨ Suggest Improvement"

**Expected Popup**:
```
⚠️ Unlock Strategy Mode

Current Level: 🏥 Level 1: Static Model

To unlock these features, you need to:
• Fix 3 more hardcoded values
• Resolve 1 circular reference

Progress: [████████░░░░░░░░] 45% → Level 2
```

---

### 3. Risk Heatmap (2 minutes)

**Action**: Navigate to "Risk Heatmap" tab (4th tab)

**Verify**:
- [ ] Tab exists and is clickable
- [ ] Sheet selector dropdown appears
- [ ] Info box explains color coding
- [ ] Grid of colored boxes displays

**Action**: Select a sheet from dropdown

**Verify**:
- [ ] Risks grouped by row
- [ ] Each cell shows:
  - [ ] Colored box (red/orange/yellow/green)
  - [ ] Cell address (e.g., "A5")
  - [ ] Risk count (e.g., "2 risks")
- [ ] Colors match severity:
  - [ ] 🟥 Red = Critical/High
  - [ ] 🟨 Yellow = Medium
  - [ ] 🟩 Green = Low/None

**Expected Visual**:
```
Row 5 (3 risks)
┌─────────┬─────────┬─────────┐
│  🟥 A5  │  🟨 B5  │  🟥 C5  │
│ 2 risks │ 1 risk  │ 3 risks │
└─────────┴─────────┴─────────┘
```

---

## 🐛 Common Issues

### Issue: Maturity badge not showing
**Fix**: Ensure file has risks detected

### Issue: Locked buttons not styled
**Fix**: Refresh browser (Ctrl+F5)

### Issue: Heatmap tab missing
**Fix**: Check that file has risks

### Issue: Colors not displaying
**Fix**: Verify browser supports CSS gradients

---

## ✅ Success Criteria

All checkboxes above should be checked (✓)

**If all pass**: ✅ UI implementation successful  
**If any fail**: ⚠️ Review error logs and retry

---

## 📸 Screenshot Checklist

For documentation, capture:
1. Maturity header (full width)
2. Locked buttons (both buttons visible)
3. Unlock popup (when button clicked)
4. Risk heatmap (showing colored grid)

---

## 🎯 Next Steps After Testing

1. **If successful**: Proceed to Vietnam Plan UAT
2. **If issues found**: Document and fix
3. **After UAT**: Update README with screenshots
4. **Final step**: Deploy to production

---

**Time Required**: 5 minutes  
**Prerequisites**: Excel file with risks  
**Command**: `streamlit run app.py`
