# Phase 5: Smart Context Recovery with AI

**Status:** IN PROGRESS  
**Date:** December 2, 2025  
**Strategy:** Hybrid AI - Use LLM when rule-based fails

---

## Strategic Decision

**Problem:** 2-column layouts and complex structures defeat rule-based parsing  
**Solution:** Accept 80% accuracy from rules, use AI for the remaining 20%

**Philosophy:** "Don't let the Perfect be the enemy of the Profitable"

---

## Implementation Plan

### Step 1: Identify Empty Context ✅
When `_get_context_labels()` returns `None` or empty string, flag for AI recovery.

### Step 2: Extract 5x5 Grid
Capture surrounding cells (2 cells in each direction) to provide context to LLM.

### Step 3: AI Query
Ask LLM: "Based on this layout, what is the semantic label for the center cell?"

### Step 4: Cache Results
Store AI-recovered labels to avoid repeated API calls.

---

## Code Structure

```python
class SmartContextRecovery:
    """
    AI-powered context recovery for complex layouts.
    
    Uses LLM to understand 2-column layouts, merged cells,
    and other patterns that defeat rule-based parsing.
    """
    
    def __init__(self, ai_provider, api_key):
        self.ai_provider = ai_provider
        self.api_key = api_key
        self.cache = {}
    
    def recover_context(self, sheet, cell_address, cells):
        """
        Use AI to recover context for a cell.
        
        Args:
            sheet: Sheet name
            cell_address: Cell address (e.g., "E92")
            cells: Dictionary of all cells
            
        Returns:
            Recovered context label or None
        """
        # Extract 5x5 grid
        grid = self._extract_grid(sheet, cell_address, cells)
        
        # Check cache
        cache_key = self._make_cache_key(grid)
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # Query LLM
        label = self._query_llm(grid)
        
        # Cache result
        self.cache[cache_key] = label
        
        return label
    
    def _extract_grid(self, sheet, cell_address, cells):
        """Extract 5x5 grid around target cell"""
        # Implementation
        pass
    
    def _query_llm(self, grid):
        """Query LLM for semantic label"""
        # Implementation with data masking
        pass
```

---

## Security: Data Masking

**CRITICAL:** Never send raw financial values to LLM.

**Masking Strategy:**
- Replace all numbers with `[NUM]`
- Keep text labels intact
- Keep cell structure intact

**Example:**
```
Before Masking:
A1: "Revenue"  B1: 1000000  C1: 2000000
A2: "EBITDA"   B2: 500000   C2: 800000

After Masking:
A1: "Revenue"  B1: [NUM]  C1: [NUM]
A2: "EBITDA"   B2: [NUM]  C2: [NUM]
```

---

## Integration Point

```python
def _get_context_labels(self, sheet, cell_address, cells):
    """Find row and column labels for a cell."""
    
    # Try rule-based first (80% accuracy)
    row_label, col_label = self._rule_based_context(sheet, cell_address, cells)
    
    # If empty, try AI recovery (20% fallback)
    if not row_label and hasattr(self, 'smart_context'):
        row_label = self.smart_context.recover_context(sheet, cell_address, cells)
    
    return row_label, col_label
```

---

## Next Steps

1. Implement `SmartContextRecovery` class
2. Add to `ModelAnalyzer` as optional component
3. Test with Vietnam Plan file
4. Measure accuracy improvement

---

**Target:** 95%+ context accuracy with hybrid approach
