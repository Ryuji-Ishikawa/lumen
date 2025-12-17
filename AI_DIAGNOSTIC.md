# AI Context Recovery - Diagnostic

**Status:** DEBUGGING  
**Date:** December 2, 2025

---

## Added Debug Logging

I've added comprehensive debug logging to understand what's happening:

### What You'll See in Console

```
[DEBUG] _add_context_labels called with 9 risks
[DEBUG] smart_context configured: True
[DEBUG] smart_context enabled: True
[DEBUG] Empty context for BS!E92
[DEBUG] Empty context for BS!E169
[DEBUG] Summary: 2 empty contexts, 2 AI calls
[AI] Attempting recovery for BS!E92
[AI] ✓ Recovered: 'Beginning Balance'
[AI] Summary: 1/2 successful recoveries
```

---

## Possible Scenarios

### Scenario 1: No Empty Contexts
```
[DEBUG] _add_context_labels called with 9 risks
[DEBUG] smart_context configured: True
[DEBUG] smart_context enabled: True
[DEBUG] Summary: 0 empty contexts, 0 AI calls
```

**Meaning:** Rule-based found labels for ALL risks  
**Action:** AI not needed (rule-based is working)

### Scenario 2: AI Not Configured
```
[DEBUG] _add_context_labels called with 9 risks
[DEBUG] smart_context configured: False
```

**Meaning:** API key not passed to analyzer  
**Action:** Check app.py integration

### Scenario 3: AI Disabled
```
[DEBUG] _add_context_labels called with 9 risks
[DEBUG] smart_context configured: True
[DEBUG] smart_context enabled: False
```

**Meaning:** API key is None or invalid  
**Action:** Check API key in sidebar

---

## Next Steps

1. **Restart Streamlit** (if not already done)
2. **Upload file**
3. **Check console** for `[DEBUG]` messages
4. **Report back** what you see

---

## What to Look For

**Question 1:** Do you see `[DEBUG] _add_context_labels called`?
- YES → Function is being called
- NO → Function not being called (integration issue)

**Question 2:** What does `smart_context configured` show?
- True → API key was passed
- False → API key not passed (app.py issue)

**Question 3:** How many empty contexts?
- 0 → Rule-based found everything (AI not needed)
- >0 → AI should be called

**Question 4:** Do you see `[AI] Attempting recovery`?
- YES → AI is being called
- NO → Check enabled status

---

**Status:** Waiting for console output to diagnose further
