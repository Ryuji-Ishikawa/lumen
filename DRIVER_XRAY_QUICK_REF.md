# Driver X-Ray - Quick Reference Card

## 🎯 Purpose
Trace dependencies to find root causes and assess impact.

## 🚀 Quick Start
1. Upload Excel file
2. Click "Driver X-Ray" tab
3. Select cell from dropdown
4. Review trace

## 📊 What You See

### ⬆️ DRIVERS (Precedents)
**What feeds into this cell**
- Shows cells this cell depends on
- Displays: Address, Label, Value
- Limit: 20 drivers max

### ⬇️ IMPACTS (Dependents)
**What depends on this cell**
- Shows cells that use this cell
- Displays: Address, Label, Value
- Limit: 20 impacts max

### 💡 INSIGHTS
**Actionable warnings**
- Root Cause Alert: No drivers + has formula
- Simple Dependency: Only 1 driver
- Complex Calculation: 10+ drivers
- High Impact: 5+ impacts

## 🔍 Common Patterns

### Root Driver
```
⬆️ DRIVERS: None
⬇️ IMPACTS: Multiple cells
💡 This is an input cell
```

### Calculation Cell
```
⬆️ DRIVERS: 1-5 cells
⬇️ IMPACTS: 1-5 cells
💡 Middle of dependency chain
```

### Output Cell
```
⬆️ DRIVERS: Multiple cells
⬇️ IMPACTS: None
💡 Final result cell
```

### Hardcoded Value
```
⬆️ DRIVERS: None
⬇️ IMPACTS: Multiple cells
💡 Root Cause Alert
```

## ⚡ Quick Actions

### Find Root Cause
1. Select cell with risk
2. Check DRIVERS
3. If empty → hardcoded value
4. Extract to driver cell

### Assess Impact
1. Select cell
2. Check IMPACTS count
3. If 5+ → high priority
4. Fix carefully

### Trace Chain
1. Start with output cell
2. Check its drivers
3. Select a driver
4. Repeat until root

## 🎨 Visual Guide

```
F4 (Exchange Rate)          ← Root Driver (no drivers)
  ↓
F10 (Unit Price)            ← Calculation (1 driver, 1 impact)
  ↓
F20 (Revenue)               ← Calculation (1 driver, 1 impact)
  ↓
F30 (Net Income)            ← Output (1 driver, no impacts)
```

## 💡 Pro Tips

1. **Start with high-severity risks**
2. **Check impact before fixing**
3. **Trace back to root drivers**
4. **Fix high-impact cells first**
5. **Use insights to prioritize**

## 🐛 Troubleshooting

**"No drivers found"**
→ Normal for input cells

**"No impacts found"**
→ Cell might be unused

**"Showing 20 of X"**
→ More exist, limited for performance

**Cell not in dropdown**
→ Only cells with risks shown

## 📱 Keyboard Shortcuts

- **Tab**: Navigate sections
- **↑↓**: Navigate dropdown
- **Enter**: Select cell

## 🎯 Success Criteria

✅ Can trace root cause  
✅ Can assess impact  
✅ Can prioritize fixes  
✅ Insights are actionable

## 📞 Support

Questions? Check:
- `DRIVER_XRAY_USER_GUIDE.md` (detailed guide)
- `demo_driver_xray.py` (interactive demo)
- `PHASE_6_EXECUTIVE_SUMMARY.md` (business value)

---

**Remember:** Data is useless if it doesn't lead to a decision. Driver X-Ray makes your data actionable.
