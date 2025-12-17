# Dominance Issue - Root Cause Analysis

## Problem

Value `201.26` appears 423 times but shows "影響セル数: 1" (1 dependent cell).

## Root Cause: Hardcoded Values Don't Create Dependencies

### How Dependency Graphs Work

Excel dependency graphs track **cell references**, not **values**:

```
Cell A1: =B1+C1    → Dependencies: B1, C1
Cell B1: 100       → Dependencies: NONE (hardcoded value)
Cell C1: =D1*2     → Dependencies: D1
```

### The Problem with Hardcoded Values

When `201.26` is hardcoded in a cell:

```
Cell F4: 201.26    → No dependencies tracked
Cell F8: 201.26    → No dependencies tracked
Cell F10: 201.26   → No dependencies tracked
```

**Result:** `get_dependents()` returns 0 or 1 because these cells don't reference each other.

### Why This Happens

1. **Parser only tracks formula references**
   - `=F4` creates a dependency
   - `201.26` does NOT create a dependency

2. **Hardcoded values are invisible to the graph**
   - They're just static values
   - No cell-to-cell relationships

3. **Dominance calculation fails**
   ```python
   dominance = len(model.get_dependents(cell_address))
   # Returns 0 or 1 because hardcoded cells have no dependents
   ```

## Why Diffusion Works But Dominance Doesn't

- **Diffusion**: Counts text occurrences of "201.26" ✅ Works
- **Dominance**: Counts graph descendants ❌ Fails for hardcoded values

## Solutions

### Option 1: Show Warning for Hardcoded Values (RECOMMENDED)

```python
if diffusion > 10 and dominance < 5:
    # Suspicious: high diffusion but low dominance
    # This indicates hardcoded values (not formulas)
    st.warning("""
    ⚠️ 影響セル数が測定できません
    
    この値はベタ打ちされているため、依存関係が追跡できません。
    
    **推奨**: この値を前提条件シートに移動し、数式で参照してください。
    そうすることで、正確な影響範囲が計算できます。
    """)
```

### Option 2: Estimate Dominance from Diffusion

```python
if dominance < 5 and diffusion > 10:
    # Estimate: assume each occurrence affects at least 1 other cell
    estimated_dominance = diffusion * 0.5  # Conservative estimate
    st.caption(f"推定影響: 約{int(estimated_dominance)}セル")
```

### Option 3: Change Terminology

Instead of "影響セル数" (dependent cells), use:
- "リスク箇所数" (risk locations) = diffusion
- "潜在的影響" (potential impact) = estimated

## Recommended Fix

Update `app.py` to detect this situation and show appropriate message:

```python
# After calculating dominance
if diffusion > 10 and dominance < 5:
    # Hardcoded value detected
    display_dominance = f"測定不可 ({diffusion}箇所に分散)"
    show_warning = True
else:
    display_dominance = f"{dominance}"
    show_warning = False

# In UI
st.metric("影響セル数", display_dominance)

if show_warning:
    st.warning("""
    ⚠️ この値はベタ打ちのため、正確な影響範囲を計算できません。
    
    **対策**: 前提条件シートに移動し、数式で参照することで、
    依存関係が追跡可能になります。
    """)
```

## For AI Prompt

Update the AI prompt to handle this case:

```python
if diffusion > 10 and dominance < 5:
    prompt += f"""
⚠️ **重要**: この値は{diffusion}箇所でベタ打ちされています。
現在の依存関係は追跡できていません（{dominance}個のみ検出）。

一元管理することで:
1. 依存関係が明確になる
2. 影響範囲が正確に計算できる
3. 変更時のリスクが可視化される
"""
```

## Why This Is Actually Good News

The low dominance **proves the problem**:
- High diffusion (423) = value is scattered
- Low dominance (1) = no formula connections
- **This confirms the model is "Static" (Level 1)**

This validates the maturity model! The user needs to:
1. Centralize hardcoded values
2. Convert to formula references
3. Then dominance will be measurable

## Implementation Priority

1. **Immediate**: Add warning message for low dominance + high diffusion
2. **Short-term**: Update AI prompt to explain the situation
3. **Long-term**: Consider value-based dependency tracking (complex)

## Code Location

File: `app.py`
Lines to update: ~790-800 (metric display section)

Add this logic:
```python
# Detect hardcoded value situation
is_hardcoded_scattered = (diffusion > 10 and dominance < 5)

if is_hardcoded_scattered:
    st.warning("⚠️ ベタ打ち値のため影響範囲を測定できません")
    st.caption(f"この値を一元管理すると、{diffusion}箇所の依存関係が追跡可能になります")
```
