# Dominance Bug - CONFIRMED

## Your Example Proves the Bug ✅

```
Sheet: プロジェクションVDN
H19: ='プロジェクション円'!H19*201.26  ← Hardcoded 201.26
H20: =H19*0.4                          ← Depends on H19
H23: =H19+H9-H8-...                    ← Depends on H19
```

**Expected:** Dominance of H19 = 2 (H20, H23)
**Actual:** System shows 1

## Root Cause

The aggregation logic in `app.py` IS calculating dominance correctly:

```python
for risk in risk_group:
    cell_address = risk.get_location()
    impacts = model.get_dependents(cell_address)  # Gets H20, H23
    all_impacts.update(impacts)  # Adds to set

total_dominance = len(all_impacts)  # Should be 2!
```

This SHOULD work! But it's showing 1, which means either:

1. **Parser issue**: H19 → H20, H23 edges not being created
2. **Sheet name issue**: Cross-sheet references not tracked correctly
3. **Aggregation issue**: Only counting one cell's dependents

## Most Likely: Cross-Sheet Reference Bug

Your formula: `='プロジェクション円'!H19*201.26`

This references a DIFFERENT sheet. The parser might be:
- Not creating the edge correctly for cross-sheet refs
- Using wrong sheet name format in graph keys
- Skipping cross-sheet dependencies

## Diagnostic Needed

We need to check if the dependency graph contains:
```
プロジェクションVDN!H19 → プロジェクションVDN!H20
プロジェクションVDN!H19 → プロジェクションVDN!H23
```

If these edges exist, dominance should be 2.
If they don't exist, the parser has a bug.

## Immediate Fix

Since we can't easily debug the parser right now, we should:

1. **Remove the "測定不可" logic** - it's wrong if there ARE connections
2. **Show the actual dominance value** - even if it's low
3. **Add note**: "影響セル数は最小値です。実際の影響はより大きい可能性があります"

This is more honest than saying "unmeasurable" when we DO have some measurement.

## Code Fix Required

In `app.py`, remove this logic:

```python
# REMOVE THIS:
if diffusion > 10 and dominance < 5:
    st.metric("影響セル数", "測定不可")
    st.warning("...")
```

Replace with:

```python
# ALWAYS show the value:
st.metric("影響セル数", f"{dominance}")

# Add caveat if suspiciously low:
if diffusion > 10 and dominance < diffusion * 0.1:
    st.caption("⚠️ 注意: 影響セル数が予想より少ない可能性があります。クロスシート参照が正しく追跡されていない可能性があります。")
```

## Long-Term Fix

Need to investigate parser to ensure:
1. Cross-sheet references create correct edges
2. Sheet names are normalized consistently
3. All formula types are parsed correctly

## Summary

You're 100% correct - the file HAS connections, and dominance SHOULD be higher than 1. The current "測定不可" message is wrong and misleading. We need to show the actual value (even if incomplete) and add a caveat that it might be underestimated.
