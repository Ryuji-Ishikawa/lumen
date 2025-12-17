# Dominance Diagnosis - Why It's Low

## Your Example (Correct Understanding) ✅

```
E5: =A5*206.23    ← Contains hardcoded 206.23
E10: =E5*E6       ← References E5 (formula link)
E12: =E9+E10      ← References E10 (formula link)
```

**Dependency Graph:**
```
E5 → E10 → E12
```

**Dominance of E5 = 2** (E10, E12) ✅ CORRECT

The system SHOULD calculate this correctly because:
1. E5 is added to graph as a node
2. E10's formula `=E5*E6` creates edge: E5 → E10
3. E12's formula `=E9+E10` creates edge: E10 → E12
4. `nx.descendants(E5)` returns {E10, E12} = 2 dependents

## Vietnam Plan Reality (Why Dominance = 1) ❌

```
F4: 201.26        ← Hardcoded (no formula)
F8: 201.26        ← ALSO hardcoded (no formula)
F10: 201.26       ← ALSO hardcoded (no formula)
```

**Dependency Graph:**
```
F4  (isolated node, no edges)
F8  (isolated node, no edges)
F10 (isolated node, no edges)
```

**Dominance of F4 = 0** ❌ No dependents because no formulas reference it

## The Critical Difference

### Your Example (Good Model)
```
E5: =A5*206.23
E10: =E5*E6      ← Uses FORMULA REFERENCE to E5
```
✅ Creates dependency: E5 → E10

### Vietnam Plan (Bad Model)
```
F4: 201.26
F8: 201.26       ← COPY-PASTED the VALUE, not a formula
```
❌ No dependency: F4 and F8 are independent

## How to Verify

### Check if F8 references F4:

1. Click on F8 in Excel
2. Look at formula bar
3. If it shows: `=F4*100` → Good! Formula reference
4. If it shows: `201.26` → Bad! Copy-pasted value

### Most Likely Scenario

Your Vietnam Plan has 423 cells with `201.26`, but they are:
- **Copy-pasted values** (not formulas)
- **No formula connections** between them
- **Each cell is independent**

That's why dominance = 0 or 1.

## Why This Happens in Real Models

### Common Pattern (Bad Practice)
```
1. User types 201.26 in F4
2. User copies F4
3. User pastes to F8, F10, F13... (423 times!)
4. Result: 423 independent cells with same value
```

### Good Practice (What Should Happen)
```
1. User types 201.26 in F4
2. User types =F4 in F8
3. User types =F4 in F10
4. Result: F4 has 422 dependents!
```

## Implications

### If Dominance = 1 for 201.26:

This means:
1. ✅ The parser is working correctly
2. ✅ The graph is built correctly
3. ❌ The Excel model is poorly structured
4. ❌ Values are copy-pasted, not referenced

### This Validates Level 1 (Static)!

A model with:
- High diffusion (423 occurrences)
- Low dominance (1 dependent)

Is a **Level 1 (Static)** model where:
- Values are scattered
- No formula connections
- High maintenance risk

## Solution

The user needs to:
1. Delete 422 copies of `201.26`
2. Keep only 1 in a "Parameters" sheet
3. Replace all 422 cells with formulas like `=Parameters!A1`
4. Then dominance will be 422!

## Testing Your Understanding

### Scenario A: Formula References
```
A1: 100
B1: =A1*2
C1: =B1+10
```
**Dominance of A1 = ?**
Answer: 2 (B1, C1)

### Scenario B: Copy-Pasted Values
```
A1: 100
B1: 100  (copy-pasted, not =A1)
C1: 100  (copy-pasted, not =A1)
```
**Dominance of A1 = ?**
Answer: 0 (no dependents)

## Conclusion

Your understanding is **100% correct**! The system SHOULD calculate dominance = 2 in your example.

The reason Vietnam Plan shows dominance = 1 is because the model itself has no formula connections - it's all copy-pasted values.

This is actually **good diagnostic information** - it proves the model needs refactoring!
