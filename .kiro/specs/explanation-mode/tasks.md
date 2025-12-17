# Explanation Mode - Implementation Plan

**Project**: Lumen v1.1  
**Target Launch**: 2025-01-15 (29 days)  
**Priority**: P0 (Must-Have Features Only)

---

## Implementation Strategy

### Phased Approach

**Phase 1: Foundation** (Days 1-7)
- Data models
- Factor detection
- Period inference

**Phase 2: UI Core** (Days 8-14)
- Mode toggle
- Target selection
- Basic tree display

**Phase 3: Advanced UI** (Days 15-21)
- AgGrid tree with expansion
- Global date override
- Evidence memo

**Phase 4: Integration & Testing** (Days 22-29)
- Integration with existing code
- Bug fixes
- Manual testing with real Excel files

---

## Task List

### **Phase 1: Foundation (Data Models & Core Logic)**

- [x] 1. Extend Data Models
  - Create `src/explanation_models.py` with new classes
  - `Factor`: id, sheet, address, label, factor_type, **values, formatted_values**, period_attrs, is_fixed, evidence_memo
  - `CausalNode`: id, sheet, address, label, is_factor, formula, formula_readable, **values, formatted_values**, children, depth, is_expanded, is_untraceable
  - `PeriodAttribute`: column_index, column_label, period_type, confidence, inference_method, is_user_overridden
  - `EvidenceMemo`: factor_id, factor_label, memo_text, created_at, updated_at
  - Extend `ModelAnalysis` in `src/models.py` to include: factors, causal_trees, global_date_override, evidence_memos
  - **CRITICAL**: `values` stores numeric data (Dict[int, Any]), `formatted_values` stores Excel-formatted strings (Dict[int, str])
  - _Requirements: 2.1 Factor, 2.3 Node, 4.3 Period Attribute, 4.6 Evidence Memo, Data Model Correction #1_

- [ ] 2. Implement Factor Detector
  - [x] 2.1 Create `src/factor_detector.py`
    - Implement `detect_factors(model: ModelAnalysis) -> List[Factor]`
    - Condition 1: No formula OR simple reference (e.g., `=Sheet1!A10`)
    - Condition 2: Has Context Label OR is referenced by important calculations
    - Condition 3: Has downstream dependencies (out_degree > 0)
    - Rescue: If no label, use `[No Label] (Address)`
    - _Requirements: A1 Factor Detection Conditions_
  
  - [x] 2.2 Implement helper functions
    - `is_simple_reference(formula: str) -> bool`: Check if formula is just a cell reference
    - `is_referenced_by_important_calc(cell_key: str, model: ModelAnalysis) -> bool`: Check downstream impact
    - `detect_factor_type(cell_key: str, model: ModelAnalysis) -> str`: Determine "scalar" vs "series"
    - _Requirements: A1, A2 Series Factor_
  
  - [x] 2.3 Integrate with Context Labeling
    - Reuse existing `_get_context_labels()` from `src/analyzer.py`
    - Handle multi-context (semantic blocks) if already implemented
    - _Requirements: B1 Semantic Block_

- [ ] 3. Implement Period Inference Engine
  - [x] 3.1 Create `src/period_inference.py`
    - Implement `infer_period_attributes(model: ModelAnalysis) -> Dict[int, PeriodAttribute]`
    - Priority 1: Header Keywords (Act, Est, Plan, 実績, 予測) → HIGH confidence
    - Priority 2: Column Majority Vote (hardcode vs formula count) → MEDIUM confidence
    - Priority 3: Date Fallback (< Current - 3 months) → LOW confidence
    - Default: UNCERTAIN
    - _Requirements: 4.3 Period Attribute Logic, D2 Column Majority Vote_
  
  - [x] 3.2 Implement helper functions
    - `get_all_columns(model: ModelAnalysis) -> List[int]`: Extract all column indices with data
    - `get_column_header(col_idx: int, model: ModelAnalysis) -> str`: Get header label for column
    - `has_keyword(text: str, keywords: List[str]) -> bool`: Check for period keywords
    - `get_constituent_cells(col_idx: int, model: ModelAnalysis) -> List[CellInfo]`: Get all cells in column (excluding headers/totals)
    - `parse_date_from_header(header: str) -> Optional[datetime]`: Extract date from header string
    - _Requirements: D1, D2, D3 Period Inference Details_

- [ ] 4. Implement Causal Tree Builder
  - [x] 4.1 Create `src/causal_tree_builder.py`
    - Implement `build_causal_tree(target_id: str, model: ModelAnalysis, max_depth: int = 1) -> CausalNode`
    - Recursive tree construction from dependency graph
    - Initial depth: 1 (target + direct precedents)
    - Mark UNTRACEABLE nodes (formula error, hardcode, inconsistency, missing reference)
    - _Requirements: 4.2 Causal Tree, C1 Target Selection_
  
  - [x] 4.2 Integrate Logic Translator
    - Reuse `translate_formula_to_labels()` from `src/analyzer.py`
    - Set `formula_readable` field for each node
    - _Requirements: 4.2 Formula Representation_
  
  - [x] 4.3 Implement helper functions
    - `is_untraceable(cell: CellInfo, model: ModelAnalysis) -> bool`: Check if node cannot be decomposed
    - `get_untraceable_reason(cell: CellInfo, model: ModelAnalysis) -> str`: Explain why untraceable
    - `get_kpi_candidates(model: ModelAnalysis) -> List[Factor]`: Filter KPI candidates (must contain "売上" or "Revenue", top 10)
    - _Requirements: 5.1 Broken Excel Behavior, C1 Target Selection_

---

### **Phase 2: UI Core (Mode Toggle & Basic Display)**

- [ ] 5. Implement Mode Toggle UI
  - [x] 5.1 Update `app.py`
    - Add mode toggle at top level (before tabs)
    - Use `st.radio()` with horizontal layout: ["Risk Review", "Explanation Mode"]
    - Store mode in `st.session_state['app_mode']`
    - Route to appropriate rendering function based on mode
    - _Requirements: 4.1 UI Structure_
  
  - [x] 5.2 Create `src/explanation_mode.py`
    - Implement `render_explanation_mode(model: ModelAnalysis, lang: str)`
    - Main entry point for Explanation Mode UI
    - Layout: Left Sidebar (10%) + Main Area (90% split 60/40)
    - _Requirements: H Layout_

- [ ] 6. Implement Target Selection UI
  - [x] 6.1 Add target selection dropdown
    - Use `st.selectbox()` with KPI candidates
    - Filter: Must contain "売上" or "Revenue"
    - Limit: Top 10 candidates
    - Store selected target in `st.session_state['target_metric']`
    - _Requirements: C1 Target Selection_
  
  - [x] 6.2 Handle no candidates case
    - Show warning if no KPI candidates found
    - Provide fallback: Manual cell address input
    - _Requirements: 7. Error Handling_

- [ ] 7. Implement Basic Tree Display (Placeholder)
  - [ ] 7.1 Create simple tree view
    - Use `st.expander()` for each level (temporary, before AgGrid)
    - Display: Node label, formula (readable), value
    - Show only 1 level initially (target + direct precedents)
    - _Requirements: 4.2 Causal Tree Structure_
  
  - [ ] 7.2 Add UNTRACEABLE node handling
    - Display warning icon for untraceable nodes
    - Show reason in tooltip or caption
    - _Requirements: 5.1 Broken Excel Behavior_

---

### **Phase 3: Advanced UI (AgGrid, Global Override, Evidence Memo)**

- [ ] 8. Implement AgGrid Tree Display
  - [ ] 8.1 Install and configure streamlit-aggrid
    - Add `streamlit-aggrid` to `requirements.txt`
    - Test basic AgGrid rendering
    - _Requirements: H2 Visualization Library_
  
  - [ ] 8.2 Implement tree data mode
    - Create `flatten_tree(node: CausalNode) -> List[Dict]`: Convert tree to flat list with hierarchy paths
    - Configure AgGrid with `treeData=True` and `getDataPath`
    - Enable group/expand functionality
    - **Columns (SIMPLE)**: Structure (auto-group), Label, Formula, Representative Value
    - **NO monthly columns** - avoid horizontal scroll, maintain clarity
    - Implement `get_representative_value(node)`: Return latest ACTUAL, total, or most recent value
    - _Requirements: H2 AgGrid Tree Data Mode, UI Layout Strategy Clarification #2_
  
  - [ ] 8.3 Add expand/collapse functionality
    - Initial state: Only 1 level expanded
    - User click: Expand node to show children
    - Lazy loading: Build children on-demand (performance optimization)
    - _Requirements: P0 Causal Tree Expansion_

- [ ] 9. Implement Global Date Override UI
  - [ ] 9.1 Add date picker component
    - Position: Top of Explanation Mode (above tree)
    - Use `st.date_input()` with default value (e.g., 2024-09-30)
    - Add "Apply to All Uncertain Periods" button
    - _Requirements: 4.4 Global Date Override, E1 UI Placement_
  
  - [ ] 9.2 Implement override logic
    - Create `apply_global_override(model: ModelAnalysis, cutoff_date: datetime)`
    - For each Factor's period_attrs: If UNCERTAIN, set to ACTUAL (≤ cutoff) or FORECAST (> cutoff)
    - Mark as `is_user_overridden = True`
    - Update `model.global_date_override` field
    - _Requirements: E1 Global Date Override Logic_
  
  - [ ] 9.3 Update tree display
    - Refresh tree to show updated period classifications
    - Highlight overridden periods (visual indicator)
    - _Requirements: 4.4 Global Date Override Behavior_

- [ ] 10. Implement Evidence Memo Manager
  - [ ] 10.1 Create JSON persistence functions
    - Implement `save_evidence_memos(model: ModelAnalysis, excel_path: str)` in `src/evidence_memo.py`
    - Implement `load_evidence_memos(excel_path: str) -> List[EvidenceMemo]`
    - JSON structure: excel_file, analysis_date, global_date_override, memos[]
    - File naming: `[ExcelName].lumen.json` in same directory
    - _Requirements: 4.6 Evidence Memo Persistence, F1 JSON Structure_
  
  - [ ] 10.2 Add detail panel UI (Right Panel)
    - **Section 1: Time-Series View** (NEW - CRITICAL)
      - Display selected node's values over time (chart + table)
      - Use `node.values` and `node.formatted_values` from data model
      - Color-code by period type (ACTUAL=blue, FORECAST=orange, UNCERTAIN=gray)
      - Implement with Plotly line chart
      - Show detailed table with Period | Value | Type columns
    - **Section 2: Divergence Analysis** (NEW)
      - Calculate Actual trend (simple growth rate)
      - Compare Forecast values against projected trend
      - Highlight significant deviations (> 10% threshold)
    - **Section 3: Evidence Memo Editor** (Existing)
      - Use `st.text_area()` for memo input
      - Show existing memo if available
      - Add "Save Memo" button
    - _Requirements: 4.6 Evidence Memo Function, UI Layout Strategy Clarification #2_
  
  - [ ] 10.3 Integrate with tree selection
    - Detect node selection in AgGrid
    - Load corresponding memo from `model.evidence_memos`
    - Update memo on save
    - Persist to JSON file immediately
    - _Requirements: F2 Factor ID Uniqueness_

---

### **Phase 4: Integration & Polish**

- [ ] 11. Integrate with Existing Risk Review
  - [ ] 11.1 Ensure Risk Review remains unchanged
    - Test all existing tabs: File Info, Fatal Errors, Integrity Risks, Structural Debt
    - Verify no regression in risk detection
    - Confirm Health Score, Maturity Level still work
    - _Requirements: 3. MVP Scope Part A (As-Is)_
  
  - [ ] 11.2 Share data between modes
    - Use same `ModelAnalysis` object for both modes
    - Cache Factor detection results
    - Avoid re-parsing Excel when switching modes
    - _Requirements: 1. Core Principles (Incremental)_

- [ ] 12. Add Semantic Inconsistency Detection (Heuristic)
  - [ ] 12.1 Implement type inference
    - Create `infer_value_type(label: str) -> str` in `src/semantic_checker.py`
    - Types: RATIO ("率", "比", "%"), AMOUNT ("円", "額", "$"), COUNT ("人", "数", "個")
    - Priority: More specific keywords first
    - _Requirements: 4.7 Semantic Inconsistency, G1 Type Judgment_
  
  - [ ] 12.2 Implement inconsistency detection
    - Check formula operations: Warn if RATIO + AMOUNT or COUNT + RATIO (addition/subtraction only)
    - Ignore multiplication/division (e.g., AMOUNT × COUNT is OK)
    - Set `has_semantic_warning = True` on CausalNode
    - _Requirements: G2 Warning Conditions_
  
  - [ ] 12.3 Display warnings in tree
    - Add warning icon (⚠️) to nodes with semantic issues
    - Show tooltip with explanation
    - _Requirements: 4.7 Semantic Inconsistency UI_

- [ ] 13. Error Handling & Edge Cases
  - [ ] 13.1 Handle missing data gracefully
    - No KPI candidates: Show warning + manual selection
    - No column headers: Use column letters (A, B, C...)
    - No context labels: Use `[No Label] (Address)`
    - _Requirements: 7. Error Handling_
  
  - [ ] 13.2 Handle JSON save failures
    - Catch file write errors
    - Offer download as fallback
    - Keep memos in session state (temporary)
    - _Requirements: 7.3 JSON Save Failure_
  
  - [ ] 13.3 Performance limits
    - Max tree nodes: 1000 (prevent UI freeze)
    - Max memos: 1000 (reasonable limit)
    - Show warning if limits exceeded
    - _Requirements: 8. Performance Considerations_

- [ ] 14. Testing & Validation
  - [ ] 14.1 Unit tests
    - `test_factor_detector.py`: Test factor identification logic
    - `test_period_inference.py`: Test column majority vote
    - `test_causal_tree_builder.py`: Test tree construction
    - `test_evidence_memo.py`: Test JSON save/load
    - _Requirements: 9.1 Unit Tests_
  
  - [ ] 14.2 Integration tests
    - End-to-end: Upload Excel → Build tree → Save memo → Reload
    - Mode switching: Risk Review ↔ Explanation Mode (no data loss)
    - Global override: Apply date → Verify period changes
    - _Requirements: 9.2 Integration Tests_
  
  - [ ] 14.3 Manual testing with real files
    - Test with `Business_Plan.xlsx` (existing test file)
    - Verify KPI candidates are sensible
    - Check tree readability (formula translation)
    - Confirm JSON persistence across sessions
    - _Requirements: 9.3 Manual Testing_

- [ ] 15. Documentation & Cleanup
  - [ ] 15.1 Update README
    - Add Explanation Mode section
    - Document new features: Causal Tree, Period Analysis, Evidence Memo
    - Add screenshots (if possible)
    - _Requirements: Documentation_
  
  - [ ] 15.2 Code cleanup
    - Remove debug print statements
    - Add docstrings to all new functions
    - Format code with Black
    - Run linter (flake8 or pylint)
    - _Requirements: Code Quality_
  
  - [ ] 15.3 Create user guide
    - How to use Explanation Mode
    - How to interpret Causal Tree
    - How to use Global Date Override
    - How to add Evidence Memos
    - _Requirements: User Documentation_

---

## Checkpoint: Ensure All Tests Pass

- [ ] 16. Final Validation
  - Run all unit tests
  - Run all integration tests
  - Manual testing with multiple Excel files
  - Verify no regression in Risk Review mode
  - Confirm JSON persistence works correctly
  - Check performance with large Excel files (10,000+ cells)
  - _Requirements: 7. Acceptance Criteria_

---

## Dependencies

### Python Packages (Add to requirements.txt)
```
streamlit-aggrid>=0.3.4
plotly>=5.0.0
```

### Existing Dependencies (Already in requirements.txt)
```
streamlit
pandas
openpyxl
networkx
```

---

## Milestones

| Milestone | Target Date | Tasks |
|-----------|-------------|-------|
| **M1: Foundation Complete** | Day 7 (2025-12-24) | Tasks 1-4 |
| **M2: Basic UI Working** | Day 14 (2025-12-31) | Tasks 5-7 |
| **M3: Advanced UI Complete** | Day 21 (2026-01-07) | Tasks 8-10 |
| **M4: Integration & Testing** | Day 28 (2026-01-14) | Tasks 11-15 |
| **M5: Launch Ready** | Day 29 (2026-01-15) | Task 16 |

---

## Risk Mitigation

### High-Risk Items

1. **AgGrid Tree Performance**: Large trees (1000+ nodes) may cause UI lag
   - Mitigation: Lazy loading, virtual scrolling, depth limit
   
2. **Period Inference Accuracy**: Column Majority Vote may fail for complex layouts
   - Mitigation: Global Date Override as manual correction tool
   
3. **JSON File Conflicts**: Multiple users editing same Excel file
   - Mitigation: MVP is single-user; add file locking in future

### Contingency Plans

- If AgGrid is too complex: Fall back to `st.expander()` tree (simpler but less polished)
- If Period Inference is inaccurate: Make Global Date Override more prominent (required step)
- If JSON save fails: Offer in-memory storage + download button

---

## Success Criteria

✅ **Functional**:
- Mode toggle works without breaking Risk Review
- Causal Tree displays correctly with 1-level expansion
- User can expand nodes to see deeper levels
- Period inference classifies columns as ACTUAL/FORECAST/UNCERTAIN
- Global Date Override updates all UNCERTAIN periods
- Evidence Memos save to JSON and persist across sessions

✅ **Performance**:
- Tree renders in < 2 seconds for typical Excel files (< 5,000 cells)
- No UI freeze with trees up to 1,000 nodes
- JSON save/load completes in < 500ms

✅ **Quality**:
- No regression in existing Risk Review features
- All unit tests pass
- Manual testing with 3+ real Excel files successful
- Code is documented and maintainable

---

**End of Implementation Plan**
