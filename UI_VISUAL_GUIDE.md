# Project Lumen - Visual UI Guide

**Quick Reference**: What Users Will See

---

## 1. Enhanced Maturity Header

```
═══════════════════════════════════════════════════════════════
                    DASHBOARD HEADER
───────────────────────────────────────────────────────────────

┌──────────────┬────────────────────────────────┬──────────────┐
│              │                                │              │
│ 🟢 Health    │  ╔═══════════════════════╗    │ 📈 Progress  │
│   Score      │  ║                       ║    │              │
│              │  ║        🏥             ║    │  [████░░░░]  │
│   75/100     │  ║  Level 1: Static      ║    │              │
│              │  ║       Model           ║    │  45% → L2    │
│              │  ║                       ║    │              │
│              │  ╚═══════════════════════╝    │              │
│              │   (Gold Border + Gradient)    │              │
└──────────────┴────────────────────────────────┴──────────────┘

═══════════════════════════════════════════════════════════════
```

**Key Features**:
- Large emoji (🏥, 🩹, or 🏆)
- Gold border (3px)
- Gradient background (purple → violet)
- Progress bar with percentage
- Prominent center placement

---

## 2. Teasing Lock Buttons

```
═══════════════════════════════════════════════════════════════
                    PREMIUM FEATURES
───────────────────────────────────────────────────────────────

🔒 Premium Features

┌─────────────────────────────┬─────────────────────────────┐
│                             │                             │
│  🔒 🎯 Goal Seek            │  🔒 📊 Scenario Planning    │
│  (Strategy Mode)            │                             │
│                             │                             │
│  [Gold Gradient Button]     │  [Gold Gradient Button]     │
│  Hover: Scales up 2%        │  Hover: Scales up 2%        │
│                             │                             │
└─────────────────────────────┴─────────────────────────────┘

═══════════════════════════════════════════════════════════════
```

**When Clicked**:
```
⚠️ Unlock Strategy Mode

Current Level: 🏥 Level 1: Static Model

To unlock these features, you need to:
• Fix 3 more hardcoded values
• Resolve 1 circular reference

Progress: [████████░░░░░░░░] 45% → Level 2

💡 Tip: Click the ✨ Suggest Improvement button next to any
        hardcode to get AI-powered guidance.
```

---

## 3. Risk Heatmap Tab

```
═══════════════════════════════════════════════════════════════
                    RISK HEATMAP TAB
───────────────────────────────────────────────────────────────

🗺️ Risk Heatmap - Bird's Eye View

ℹ️ Visual Impact Map: See where risks are concentrated
   🟥 Red: High-risk hardcodes (Unknown values)
   🟨 Yellow: Medium-risk (Common constants)
   🟩 Green: No risks detected

Select Sheet: [Vietnam Plan ▼]

───────────────────────────────────────────────────────────────

Row 5 (3 risks)
┌─────────┬─────────┬─────────┐
│  🟥 A5  │  🟨 B5  │  🟥 C5  │
│ 2 risks │ 1 risk  │ 3 risks │
└─────────┴─────────┴─────────┘

Row 8 (5 risks)
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│  🟥 D8  │  🟥 E8  │  🟨 F8  │  🟨 G8  │  🟩 H8  │
│ 3 risks │ 2 risks │ 1 risk  │ 1 risk  │ 0 risks │
└─────────┴─────────┴─────────┴─────────┴─────────┘
+ 3 more cells in this row

Row 12 (2 risks)
┌─────────┬─────────┐
│  🟧 A12 │  🟨 B12 │
│ 2 risks │ 1 risk  │
└─────────┴─────────┘

Showing first 50 rows. Total rows with risks: 87

═══════════════════════════════════════════════════════════════
```

---

## Complete Dashboard Layout

```
╔═══════════════════════════════════════════════════════════════╗
║                    PROJECT LUMEN                              ║
║                 Excel Model Guardian 🛡️                       ║
╚═══════════════════════════════════════════════════════════════╝

┌───────────────────────────────────────────────────────────────┐
│                     MATURITY HEADER                           │
│  ┌──────────┬──────────────────────┬──────────┐              │
│  │ Health   │   🏥 Level 1         │ Progress │              │
│  │ 75/100   │   [Gold Badge]       │ 45% → L2 │              │
│  └──────────┴──────────────────────┴──────────┘              │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                   LOCKED FEATURES                             │
│  ┌──────────────────┬──────────────────┐                     │
│  │ 🔒 Goal Seek     │ 🔒 Scenario Plan │                     │
│  └──────────────────┴──────────────────┘                     │
│                                                               │
│  ⚠️ Unlock Requirements:                                     │
│  • Fix 3 more hardcodes                                      │
│  • Resolve 1 circular reference                              │
│  Progress: [████████░░░░░░░░] 45%                           │
└───────────────────────────────────────────────────────────────┘

┌───────────────────────────────────────────────────────────────┐
│                      RISK ANALYSIS                            │
│                                                               │
│  📋 Detected Risks                                           │
│                                                               │
│  [All Risks] [By Severity] [Driver X-Ray] [Risk Heatmap] [Debug]
│                                                               │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                                                         │ │
│  │  [Tab Content - Risk List, Heatmap, etc.]              │ │
│  │                                                         │ │
│  └─────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────┘
```

---

## Color Palette

### Maturity Badge
- **Background**: Linear gradient #667eea → #764ba2 (Purple → Violet)
- **Border**: Gold (#ffd700)
- **Text**: White (#ffffff)

### Locked Buttons
- **Background**: Same gradient as badge
- **Border**: Gold (2px solid)
- **Hover**: Scale 1.02, enhanced shadow

### Risk Heatmap
- **Critical**: 🟥 Red (#ff4444)
- **High**: 🟧 Orange (#ff8800)
- **Medium**: 🟨 Yellow (#ffdd00)
- **Low/None**: 🟩 Green (#88dd88)

---

## Responsive Behavior

### Desktop (> 1280px)
- Full 3-column maturity header
- Side-by-side locked buttons
- Heatmap shows up to 10 cells per row

### Tablet (768px - 1280px)
- Stacked maturity header
- Side-by-side locked buttons
- Heatmap shows up to 5 cells per row

### Mobile (< 768px)
- Fully stacked layout
- Stacked locked buttons
- Heatmap shows 2-3 cells per row

---

## Animation & Interactions

### Hover Effects
- **Locked Buttons**: Scale up 2%, enhanced shadow
- **Heatmap Cells**: Slight brightness increase (future)

### Click Effects
- **Locked Buttons**: Show unlock popup immediately
- **Heatmap Cells**: Show risk details (future)

### Progress Updates
- **Real-time**: Progress bar updates as risks are fixed
- **Smooth**: Animated transitions (Streamlit default)

---

## Accessibility

### Color Contrast
- ✅ Gold on purple: WCAG AA compliant
- ✅ White text on colored backgrounds: High contrast
- ✅ Emoji + text labels: Redundant encoding

### Screen Readers
- ✅ Semantic HTML structure
- ✅ Alt text for visual elements
- ✅ Clear button labels

### Keyboard Navigation
- ✅ Tab through buttons
- ✅ Enter to activate
- ✅ Escape to close popups

---

## User Journey

### First-Time User
1. **Upload file** → See maturity badge (Level 1)
2. **See locked features** → Curiosity triggered
3. **Click locked button** → See clear unlock path
4. **View heatmap** → Understand problem scope
5. **Click AI suggestion** → Get guidance
6. **Fix issues** → See progress increase
7. **Level up** → Features unlock, celebration

### Returning User
1. **Upload new file** → Compare to previous level
2. **See progress** → Motivated to continue
3. **Use unlocked features** → Reward for effort
4. **Share success** → Social proof

---

## Success Metrics

### Engagement
- Time spent on heatmap tab
- Clicks on locked buttons
- AI suggestion usage rate

### Progression
- Average time to Level 2
- Average time to Level 3
- Percentage reaching Level 3

### Retention
- Return visits per week
- Files analyzed per user
- Feature usage patterns

---

**Status**: ✅ READY FOR TESTING  
**Next**: End-to-End UAT with Vietnam Plan
