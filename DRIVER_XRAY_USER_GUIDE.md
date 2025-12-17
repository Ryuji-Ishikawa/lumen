# Driver X-Ray User Guide 🔍

## What is Driver X-Ray?

Driver X-Ray helps you **trace dependencies** in your Excel model. When you see a risk (like a hardcoded value), you can instantly see:
- **⬆️ What drives it** (precedents/inputs)
- **⬇️ What it impacts** (dependents/outputs)

## How to Use

### Step 1: Upload Your File
Upload your Excel file in the sidebar.

### Step 2: Navigate to Driver X-Ray
Click on the **"Driver X-Ray"** tab (3rd tab in the risk analysis section).

### Step 3: Select a Cell
Choose a cell from the dropdown. The dropdown shows cells that have risks detected.

Example:
```
Select a cell to trace: プロジェクション円!F24
```

### Step 4: Review the Trace

You'll see three sections:

#### 📍 Selected Cell Information
```
Selected Cell: プロジェクション円!F24
Context: 資金投入(百万VDN)
Risk: Hidden Hardcode (High)
Formula: =F4*1000
Current Value: 201260
```

#### ⬆️ DRIVERS (What feeds into this cell)
```
Cells that プロジェクション円!F24 depends on:
- F4: Exchange Rate = 201.26
```

#### ⬇️ IMPACTS (What depends on this cell)
```
Cells that depend on プロジェクション円!F24:
- F30: Net Income = 201,260
- F35: Cash Flow = 201,260
- F40: NPV = 150,000
```

### Step 5: Read the Insights

At the bottom, you'll see actionable insights:

```
💡 Insights

⚠️ Root Cause Alert: This cell has a formula but no drivers. 
It may contain hardcoded values.

⚠️ High Impact: Changes to this cell will affect 3 other cells.
```

## Real-World Example

### Scenario
You're reviewing your financial model and see:
- **Risk:** Hidden Hardcode at F24
- **Description:** Formula contains hardcoded value: 1000

### Using Driver X-Ray

1. **Select F24** from the dropdown
2. **See the trace:**
   - Driver: F4 (Exchange Rate = 201.26)
   - Impacts: F30 (Net Income), F35 (Cash Flow), F40 (NPV)
3. **Understand the problem:**
   - F24 multiplies F4 by a hardcoded 1000
   - This affects 3 critical financial metrics
4. **Take action:**
   - Create a new driver cell for the multiplier (e.g., F3 = 1000)
   - Update F24 formula to =F4*F3
   - Now the multiplier is visible and adjustable

## Tips

### Finding Root Causes
- Look for cells with **no drivers** but have formulas
- These often contain hardcoded values that should be drivers

### Assessing Impact
- Cells with **many impacts** (5+) are critical
- Changes to these cells cascade through your model
- Fix these risks first for maximum benefit

### Tracing Chains
- Start with a high-impact cell
- Trace back to its drivers
- Continue tracing until you find the root driver
- This reveals the full dependency chain

## Common Patterns

### Pattern 1: Hidden Driver
```
Cell: F24 (Calculation)
Drivers: None
Formula: =201.26*1000
Insight: Root Cause Alert
Action: Extract 201.26 to a driver cell
```

### Pattern 2: Cascade Effect
```
Cell: F10 (Revenue)
Impacts: F20 (Gross Profit), F30 (Net Income), F40 (Cash Flow)
Insight: High Impact (3 cells)
Action: Ensure F10 is accurate - it affects multiple outputs
```

### Pattern 3: Simple Chain
```
Cell: F24
Drivers: F4 (Exchange Rate)
Impacts: F30 (Net Income)
Insight: Simple Dependency
Action: Easy to trace and fix
```

## Keyboard Shortcuts

- **Tab**: Navigate between sections
- **Arrow Keys**: Navigate dropdown options
- **Enter**: Select cell from dropdown

## Performance Notes

- Shows up to 20 drivers/impacts per cell
- If more exist, you'll see: "Showing 20 of 45 drivers"
- This keeps the UI fast and readable

## Troubleshooting

### "No drivers found"
- This is normal for input cells (like exchange rates)
- These are root drivers - they don't depend on other cells

### "No impacts found"
- This cell isn't used by any other cells
- Consider if this cell is necessary in your model

### Cell not in dropdown
- Only cells with detected risks appear in the dropdown
- To trace any cell, use the "Dependency Tree" tab instead

## Next Feature: AI Suggestions

Coming soon: Click a button to get AI-powered suggestions for fixing hardcoded values!

Example:
```
✨ AI Suggestion for F24:
"Consider creating a driver cell for the multiplier (1000). 
Formula suggestion: =F4*F3 where F3 = 1000"
```

---

**Questions?** The Driver X-Ray is designed to be intuitive. Just select a cell and explore!
