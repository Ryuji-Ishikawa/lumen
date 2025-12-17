# AI Context Recovery - Troubleshooting Guide

**Issue:** AI not being called / Same output with/without API key

---

## Why AI Might Not Be Called

### Reason 1: Rule-Based Found Something ✅
**Symptom:** Fast response, no API calls  
**Cause:** Rule-based method found a label (even if wrong)  
**Solution:** AI only triggers when rule-based returns EMPTY

**Current Logic:**
```python
if not row_label and self.smart_context:
    # Call AI
```

**This means:** AI is only called when context is completely empty, not when it's wrong.

---

### Reason 2: API Key Not Configured ❌
**Symptom:** No "AI-Powered Context Recovery: ENABLED" message  
**Cause:** API key not entered or invalid  
**Solution:** Enter valid API key in sidebar

**Check:**
1. Look for blue info box: "🤖 AI-Powered Context Recovery: ENABLED"
2. If not present, API key is not configured

---

### Reason 3: OpenAI API Version Mismatch ❌
**Symptom:** Error in console about `openai.ChatCompletion`  
**Cause:** Using old OpenAI API syntax with new library  
**Solution:** Updated to use new OpenAI client (v1.0+)

**Fixed in:** `src/smart_context.py`

---

## How to Verify AI is Working

### Step 1: Check Console Output
When AI is called, you'll see:
```
[AI] Attempting recovery for Sheet1!E92
[AI] Recovered: 'Revenue'
```

### Step 2: Check Debug Log
Go to "Debug Log" tab and look for:
- "Smart Context Recovery enabled (OpenAI)"
- AI recovery attempts

### Step 3: Test with Known Empty Context
1. Find a cell with empty context in your file
2. Note the cell address (e.g., E92)
3. Re-run analysis with API key
4. Check if that cell now has context

---

## Current Limitation

**AI only triggers when rule-based returns EMPTY**

This means:
- ✅ Empty context → AI called
- ❌ Wrong context (formula) → AI NOT called

**Why:** Rule-based method finds *something* (even if it's a formula), so AI doesn't trigger.

---

## Solution Options

### Option A: More Aggressive AI (Recommended)
Call AI for ALL cells, not just empty ones.

**Pros:** Higher accuracy  
**Cons:** Higher API costs

**Implementation:**
```python
# Always try AI if available
if self.smart_context:
    ai_label = self.smart_context.recover_context(...)
    if ai_label:
        row_label = ai_label  # Override rule-based
```

### Option B: Validate Rule-Based Results
Check if rule-based result looks suspicious (contains `=`, numbers, etc.)

**Pros:** Lower API costs  
**Cons:** More complex logic

**Implementation:**
```python
# Check if rule-based result is suspicious
if row_label and (row_label.startswith('=') or row_label.isdigit()):
    # Try AI
    if self.smart_context:
        ai_label = self.smart_context.recover_context(...)
        if ai_label:
            row_label = ai_label
```

### Option C: Current (Conservative)
Only call AI when rule-based returns empty.

**Pros:** Lowest API costs  
**Cons:** Misses cases where rule-based is wrong

---

## Recommended Next Step

**For Business Owner:**

1. Check console output for `[AI]` messages
2. If you see them → AI is working
3. If you don't → Rule-based is finding labels (even if wrong)

**Decision:**
- If accuracy is good enough → Keep current approach
- If accuracy is poor → Switch to Option A (more aggressive AI)

---

## Quick Test

Run this to test AI:
```bash
python test_ai_context.py
```

Expected output:
- Test 1: None (no API key)
- Test 2: Attempts API call (may fail with invalid key)
- Test 3: Shows grid extraction with masking

---

**Date:** December 2, 2025  
**Status:** Troubleshooting guide for AI Context Recovery
