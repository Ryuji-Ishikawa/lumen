# Implementation Plan - Project Lumen V0.4

## Overview

This implementation plan focuses on building our competitive moat: **Virtual Fill** and **Composite Key Matching**. Priority 1 is the Robust Parser that can handle messy Japanese Excel files that break global tools.

## Phase 1: Foundation - Robust Parser (PRIORITY 1)

### Task 1: Create Spaghetti Excel Test Suite

**Purpose**: Validate our assumptions about Japanese Excel patterns before building the parser.

- [x] 1.1 Create test Excel files with Japanese patterns
  - Create `tests/fixtures/spaghetti_excel/` directory
  - Build test file: `heavy_merged_cells.xlsx` (headers with 5+ merged columns)
  - Build test file: `complex_grid_layout.xlsx` (mixed merged rows and columns)
  - Build test file: `japanese_text_mixed.xlsx` (Japanese + English in formulas)
  - Build test file: `circular_references.xlsx` (intentional circular refs)
  - Build test file: `cross_sheet_complex.xlsx` (10+ sheets with cross-references)
  - Build test file: `edge_cases.xlsx` (single cell merge, entire row merge, overlapping ranges)
  - Document expected behavior for each test file
  - _Requirements: 1.1, 1.5, 2.1, 2.2, 17.1, 17.5_

- [x] 1.2 Create parser validation framework
  - Write `tests/test_parser_robustness.py`
  - Implement test harness that loads each spaghetti file
  - Assert: Parser never crashes (all exceptions caught)
  - Assert: Parser returns ModelAnalysis object (even if partial)
  - Assert: Error messages are specific and actionable
  - _Requirements: 1.5, 17.1, 17.4_

### Task 2: Update Data Models for V0.4

- [x] 2.1 Enhance CellInfo dataclass
  - Add `row_number: int` field
  - Add `col_number: int` field  
  - Add `is_merged: bool` field (already exists, verify)
  - Add `merged_range: Optional[str]` field (already exists, verify)
  - Update `__post_init__` to extract row/col from address
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

- [x] 2.2 Create CompositeKey dataclass
  - Create new dataclass in `models.py`
  - Fields: `key_columns`, `key_value`, `normalized_key`, `sheet`, `row_number`
  - Add normalization method: lowercase, strip whitespace
  - Add hash method for efficient lookups
  - _Requirements: 10.2_

- [x] 2.3 Create RowMapping dataclass
  - Create new dataclass in `models.py`
  - Fields: `old_row`, `new_row`, `composite_key`, `match_confidence`
  - Add method to check if row is matched/added/deleted
  - _Requirements: 10.1, 10.2_

- [x] 2.4 Create ChangeCategory dataclass
  - Create new dataclass in `models.py`
  - Fields: `change_type`, `severity`, `old_value`, `new_value`, `description`
  - Add enum for change_type: logic_change, input_update, risk_improved, risk_degraded
  - _Requirements: 10.3, 10.4_

- [x] 2.5 Update DiffResult dataclass
  - Add `logic_changes: List[ChangeCategory]` field
  - Add `input_updates: List[ChangeCategory]` field
  - Add `row_mapping: Dict[int, int]` field
  - Update existing fields to match new design
  - _Requirements: 10.1, 10.2, 10.3, 10.4_

### Task 3: Implement Virtual Fill Algorithm (CRITICAL - Our Moat)

- [x] 3.1 Implement merged cell identification
  - Update `_identify_merged_ranges()` in `parser.py`
  - Use `worksheet.merged_cells.ranges` from openpyxl
  - Extract bounds: `min_col, min_row, max_col, max_row`
  - Return List of range strings: ["A1:C1", "D5:D10"]
  - Add error handling for malformed merged ranges
  - _Requirements: 2.1, 17.5_

- [x] 3.2 Implement Virtual Fill propagation
  - Create `_apply_virtual_fill()` method in `parser.py`
  - For each merged range, get top-left cell data
  - Iterate through all coordinates in range
  - Create CellInfo for each coordinate with:
    - Same value as top-left
    - Same formula as top-left (if exists)
    - `is_merged=True`
    - `merged_range` set to range string
  - Add to cells dictionary with key "Sheet!Address"
  - _Requirements: 2.2, 2.3, 2.4_

- [x] 3.3 Test Virtual Fill with spaghetti files
  - Run parser on all test files from Task 1.1
  - Verify: All merged cells have propagated values
  - Verify: Dependency extraction works with virtual cells
  - Verify: No cells are lost or duplicated
  - Fix any issues discovered
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 17.1_

- [ ]* 3.4 Write property tests for Virtual Fill
  - **Property**: All cells in merged range have same value
  - **Property**: Dependency graph includes all virtual cells
  - **Property**: No cell is lost during Virtual Fill
  - Use hypothesis library to generate random merged ranges
  - _Requirements: 2.1, 2.2, 2.3, 2.4_

### Task 4: Enhance Dependency Extraction

- [x] 4.1 Update dependency extraction for Virtual Fill
  - Modify `_extract_dependencies()` in `parser.py`
  - When formula references merged range, resolve to virtual cells
  - Ensure all virtual cells are included in dependency list
  - Handle edge case: formula references middle of merged range
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 4.2 Build dependency graph with virtual cells
  - Update `_build_dependency_graph()` in `parser.py`
  - Add all cells (including virtual) as nodes
  - Add edges for all dependencies
  - Add node attributes: `is_merged`, `risk_level`
  - Verify graph is valid (no orphaned nodes)
  - _Requirements: 3.5, 11.2_

- [x] 4.3 Test dependency graph with merged cells
  - Create test: formula references merged range
  - Verify: All virtual cells appear in precedents
  - Verify: Dependency navigation works correctly
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

### Task 5: Implement Graceful Error Handling

- [x] 5.1 Add file upload error handling
  - Wrap `openpyxl.load_workbook()` in try-except
  - Catch `InvalidFileException` → check for password/corruption
  - Display Japanese error messages
  - Never show Python stack traces
  - _Requirements: 1.2, 1.3, 17.1_

- [x] 5.2 Add cell parsing error handling
  - Wrap cell value extraction in try-except
  - Log failed cells but continue parsing
  - Track parse success rate (e.g., "98% of cells parsed")
  - Display warning if success rate < 90%
  - _Requirements: 17.1, 17.4, 17.5_

- [x] 5.3 Add timeout handling
  - Implement 60-second timeout for parsing
  - Use signal.alarm() on Unix, threading.Timer on Windows
  - Display helpful message: "File too complex, try smaller file"
  - _Requirements: 17.2_

- [x] 5.4 Add memory error handling
  - Catch MemoryError during parsing
  - Display message: "File too large (max 50MB recommended)"
  - Suggest: "Try analyzing one sheet at a time"
  - _Requirements: 17.3_

- [x] 5.5 Test error handling with spaghetti files
  - Verify all test files parse without crashes
  - Verify error messages are specific and actionable
  - Verify partial results are displayed when possible
  - _Requirements: 17.1, 17.2, 17.3, 17.4, 17.5_

## Phase 2: Risk Detection & Context

### Task 6: Implement Risk Detection

- [x] 6.1 Implement hidden hardcode detection
  - Update `_detect_hidden_hardcodes()` in `analyzer.py`
  - Use openpyxl tokenizer to find NUMBER tokens
  - Exclude user-configured allowed constants
  - Create High severity alerts
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [x] 6.2 Implement circular reference detection
  - Implement `_detect_circular_references()` in `analyzer.py`
  - Use `networkx.simple_cycles()` on dependency graph
  - Limit to first 100 cycles
  - Create Critical severity alerts
  - _Requirements: 5.1, 5.2, 5.3_

- [x] 6.3 Implement merged cell risk detection
  - Implement `_detect_merged_cell_risks()` in `analyzer.py`
  - Check if formula ranges overlap with merged ranges
  - Create Medium severity alerts
  - _Requirements: 6.1, 6.2, 6.3_

- [x] 6.4 Implement cross-sheet spaghetti detection
  - Implement `_detect_cross_sheet_spaghetti()` in `analyzer.py`
  - Count distinct external sheets per formula
  - Alert if > 2 external sheets
  - Create Low severity alerts
  - _Requirements: 7.1, 7.2, 7.3_

- [x] 6.5 Implement health score calculation
  - Implement `_calculate_health_score()` in `analyzer.py`
  - Formula: 100 - (Critical×10) - (High×5) - (Medium×2)
  - Add color coding: Green ≥80, Yellow ≥60, Red <60
  - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

### Task 7: Implement Context Labeling

- [x] 7.1 Implement row label extraction
  - Create `_get_row_label()` method in `analyzer.py`
  - Scan columns A-D in same row
  - Return first non-empty string
  - Handle Japanese characters correctly
  - _Requirements: 4.4, 15.1_

- [x] 7.2 Implement column label extraction
  - Create `_get_column_label()` method in `analyzer.py`
  - Scan rows 1-20 in same column
  - Match date patterns: MM-YYYY, Q1, FY2024, etc.
  - Return first matching label
  - _Requirements: 4.4, 8.1, 15.1_

- [x] 7.3 Add context labels to all risks
  - Update `_add_context_labels()` in `analyzer.py`
  - Call for each risk alert
  - Set `row_label` and `col_label` fields
  - Format context as "Row Label @ Col Label"
  - _Requirements: 4.4, 15.1_

### Task 7A: Implement AI Smart Context with Quality Filtering

- [ ] 7A.1 Implement context quality validator
  - Create `_is_poor_quality_label()` method in `analyzer.py`
  - Pattern 1: Cell address pattern (regex `^[A-Z]+[0-9]+$`)
  - Pattern 2: Generic stopwords (Total, Sum, Subtotal, Check, Val, 合計, 小計, 計, チェック, 検証)
  - Pattern 3: Symbols/numeric only (regex `^[-0-9\s]+$`)
  - Return True if poor quality, False if acceptable
  - _Requirements: 12A.1, 12A.2, 12A.3, 12A.4_

- [ ] 7A.2 Integrate quality filter with context labeling
  - Update `_add_context_labels()` in `analyzer.py`
  - After getting initial context, validate quality
  - If poor quality OR empty, trigger AI recovery
  - Log: "[AI] Poor quality context 'X' detected for Sheet!Cell"
  - Call `smart_context.recover_context()` if enabled
  - Log: "[AI] ✓ Recovered: 'Y'" or "[AI] ✗ Recovery failed"
  - _Requirements: 12A.5, 12A.6_

- [ ] 7A.3 Implement context window extraction
  - Create `_extract_context_window()` method in `smart_context.py`
  - Extract 3 cells left, 5 cells above, 3 cells right, 3 cells below
  - Return dict with "left", "above", "right", "below" lists
  - Handle edge cases (cells at sheet boundaries)
  - Log: "[AI] Context window sent: ['Assets', 'Current', ...]"
  - _Requirements: 12A.5_

- [ ] 7A.4 Implement AI context recovery in SmartContext
  - Update `recover_context()` method in `smart_context.py`
  - Call `_extract_context_window()` to get surrounding cells
  - Build prompt with sheet, cell, and context window
  - Prompt: "Cell has poor quality label. Surrounding cells: [context]. Provide meaningful label."
  - Call AI API (GPT-4o or Gemini)
  - Parse response and return label (max 50 chars)
  - Return None if AI fails
  - _Requirements: 12A.5, 12A.6, 12A.7_

- [ ] 7A.5 Test quality filter with real examples
  - Test with cell address labels ("E92", "AA1")
  - Test with generic stopwords ("Total", "合計")
  - Test with symbols ("-", "0", "---")
  - Verify: AI recovery triggered for all poor quality labels
  - Verify: Context window extracted and logged
  - Verify: Meaningful labels recovered
  - _Requirements: 12A.1, 12A.2, 12A.3, 12A.4, 12A.5_

- [ ] 7A.6 Fix Streamlit deprecation warning
  - Global search for `use_container_width=True`
  - Replace with `width="stretch"` or appropriate value
  - Test UI to ensure layout unchanged
  - _Requirements: UX_

## Phase 3: Monthly Guardian - Composite Key Matching (CRITICAL - Our Moat)

### Task 8: Implement Composite Key Matching

- [x] 8.1 Implement composite key generation
  - Create `_build_composite_key()` method in `diff.py`
  - Accept user-selected key columns (e.g., ["Account Name"])
  - Extract values from key columns
  - Concatenate with "|" delimiter
  - Normalize: lowercase, strip whitespace
  - Return normalized key string
  - _Requirements: 10.2_

- [x] 8.2 Build composite key mappings
  - Create `_build_composite_keys()` method in `diff.py`
  - For each row in model, generate composite key
  - Store mapping: composite_key → row_number
  - Return Dict[str, int]
  - _Requirements: 10.2_

- [x] 8.3 Implement row matching algorithm
  - Create `_match_rows_by_composite_key()` method in `diff.py`
  - Compare old_keys and new_keys
  - Create row mapping: old_row → new_row
  - Handle unmatched rows (added/deleted)
  - Return Dict[int, int] and confidence scores
  - _Requirements: 10.1, 10.2_

- [x] 8.4 Test composite key matching
  - Create test files: old.xlsx and new.xlsx
  - Insert row in new file (test row insertion handling)
  - Delete row in new file (test row deletion handling)
  - Reorder rows in new file (test reordering handling)
  - Verify: Rows matched correctly by key, not by row number
  - _Requirements: 10.1, 10.2_

- [x] 8.5 Implement Key Uniqueness Validator UI (SMART UX)
  - Calculate uniqueness rate for selected key columns
  - Formula: unique_values / total_rows
  - Display uniqueness percentage in UI
  - If < 95% unique: Show warning with red badge
  - Warning text: "⚠️ These columns are not unique (X% unique). Please add another column like 'Department' to ensure accurate matching."
  - If ≥ 95% unique: Show success with green checkmark
  - Add "Preview Matches" button to show sample row mappings
  - Test with duplicate keys to verify warning appears
  - _Requirements: 10.2, UX_

### Task 9: Implement Change Detection

- [x] 9.1 Implement logic change detection
  - Create `_detect_logic_changes()` method in `diff.py`
  - Compare formulas between matched rows
  - If formula changed → "logic_change" (Critical)
  - Store old and new formulas
  - _Requirements: 10.3_

- [x] 9.2 Implement input update detection
  - Create `_detect_input_changes()` method in `diff.py`
  - Compare values between matched rows
  - If value changed but formula same → "input_update" (Normal)
  - Store old and new values
  - _Requirements: 10.4_

- [x] 9.3 Implement risk change detection
  - Update `_compare_risks()` method in `diff.py`
  - Use row mapping to match risks across versions
  - Categorize: improved (risk removed), degraded (risk added)
  - _Requirements: 10.5, 10.6, 10.8_

- [x] 9.4 Implement structural change detection
  - Update `_detect_structural_changes()` method in `diff.py`
  - Detect sheets added/removed
  - Detect rows added/removed (from row mapping)
  - _Requirements: 10.7_

- [x] 9.5 Test change detection
  - Create test file pairs with various changes
  - Verify: Logic changes detected correctly
  - Verify: Input updates detected correctly
  - Verify: Risk changes categorized correctly
  - _Requirements: 10.3, 10.4, 10.5, 10.6_

## Phase 4: Driver X-Ray & Dependency Navigation

### Task 10: Implement Driver X-Ray

- [x] 10.1 Add precedent/dependent navigation
  - Create `get_precedents()` method in `ModelAnalysis`
  - Use dependency graph to find cells this cell depends on
  - Create `get_dependents()` method
  - Use dependency graph to find cells that depend on this cell
  - _Requirements: 11.1, 11.3_

- [x] 10.2 Implement trace to drivers
  - Create `trace_to_drivers()` method in `analyzer.py`
  - For hardcoded cell, traverse dependency graph
  - Find all ultimate dependents (cells with no outgoing edges)
  - Return list of driver cells
  - _Requirements: 4.5, 11.1_

- [x] 10.3 Add risk-level coloring to graph
  - Update dependency graph node attributes
  - Add `risk_level` attribute: "critical", "high", "medium", "none"
  - Update visualization to color-code nodes
  - Red = Critical, Yellow = High, Blue = Normal
  - _Requirements: 11.5_

- [x] 10.4 Implement graph filtering
  - Add filter by sheet
  - Add filter by risk level
  - Add limit on displayed nodes (max 500)
  - Update UI to show filters
  - _Requirements: 11.4_

### Task 11: Implement Interactive Dependency Visualization

- [x] 11.1 Create dependency tree tab
  - Add "Dependency Tree" tab to UI
  - Display graph statistics (nodes, edges)
  - Add performance safeguard (skip if > 2,000 nodes)
  - _Requirements: 11.2, 11.4_

- [x] 11.2 Integrate streamlit-agraph
  - Convert NetworkX graph to agraph format
  - Create Node objects with labels and colors
  - Create Edge objects with directions
  - Configure interactive settings
  - _Requirements: 11.2_

- [x] 11.3 Add click interactions
  - When user clicks node, show precedents/dependents
  - Display cell details in sidebar
  - Add "Trace to Drivers" button
  - _Requirements: 11.3_

## Phase 5: AI Model Architect

### Task 12: Implement AI Integration

- [x] 12.1 Create AI provider abstraction
  - Create `ai_explainer.py` module
  - Create `AIProvider` base class
  - Implement `OpenAIProvider` (GPT-4o)
  - Implement `GoogleProvider` (Gemini-1.5-flash)
  - _Requirements: 12.1, 12.2_

- [x] 12.2 Implement API key management
  - Add API key input in sidebar (type="password")
  - Store in session_state only (never persist)
  - Add provider selector (OpenAI / Google)
  - Disable AI features if no key provided
  - _Requirements: 12.1_

- [x] 12.3 Implement driver breakdown suggestions
  - Create `suggest_breakdown()` method
  - Build prompt with cell context
  - Call AI API with prompt
  - Parse and display suggestion in Japanese
  - _Requirements: 12.2, 12.3, 12.4, 12.7_

- [x] 12.4 Add AI error handling
  - Wrap all AI calls in try-except
  - Display warning on failure (don't crash)
  - Keep core features functional without AI
  - _Requirements: 12.5_

- [x] 12.5 Add "Suggest Breakdown" button to UI
  - Add button next to hardcode risks
  - Show loading spinner during AI call
  - Display suggestion in expandable section
  - Format suggestion nicely in Japanese
  - _Requirements: 12.3, 12.4_

- [x] 12.6 Implement PII/Numeric Masking for AI Prompts (ENTERPRISE SECURITY)
  - Add "Data Masking" toggle in sidebar settings
  - Default: ON (for enterprise security)
  - When enabled: Replace numeric values with tokens (<NUM_1>, <NUM_2>)
  - Only send: Formula structure, labels, cell references
  - Never send: Actual values, sensitive data
  - Add warning: "Masking enabled - AI sees structure only"
  - Test: Verify no actual values in API requests
  - _Requirements: 12.1, Security_

## Phase 6: UI/UX Enhancements

### Task 13: Implement Heatmap Visualization

- [x] 13.1 Create heatmap data structure
  - Convert cells to grid format
  - Assign risk level to each cell
  - Handle sparse grids efficiently
  - _Requirements: 13.1_

- [x] 13.2 Implement heatmap rendering
  - Use Streamlit to render grid
  - Color-code cells: Red (Critical), Yellow (High/Medium), Green (None)
  - Add tooltips with risk descriptions
  - Handle large sheets (zoom/sample)
  - _Requirements: 13.2, 13.3, 13.4_

- [x] 13.3 Add heatmap tab to UI
  - Create "Risk Heatmap" tab
  - Display sheet selector
  - Render heatmap for selected sheet
  - _Requirements: 13.1, 13.2_

### Task 14: Implement Version Timeline

- [x] 14.1 Store file upload history
  - Store metadata in session_state
  - Fields: filename, timestamp, health_score
  - Persist across page refreshes (session only)
  - _Requirements: 14.1_

- [x] 14.2 Create timeline visualization
  - Render visual timeline (not just list)
  - Show upload dates and health scores
  - Use Streamlit columns for layout
  - _Requirements: 14.2_

- [x] 14.3 Add version selection
  - Make timeline entries clickable
  - Allow selection of two versions for comparison
  - Auto-trigger diff analysis
  - _Requirements: 14.3, 14.4_

### Task 15: Polish Guardian Persona

- [x] 15.1 Update all UI text to Japanese
  - Translate error messages
  - Translate risk descriptions
  - Use Guardian tone: protective, helpful
  - Use "リスク" not "エラー"
  - _Requirements: 15.1, 15.2, 15.3_

- [x] 15.2 Add encouraging messages
  - Show "🎉 改善されました！" for improvements
  - Show positive feedback for high health scores
  - Use emojis appropriately
  - _Requirements: 15.3_

- [x] 15.3 Verify wide layout
  - Ensure 1280px minimum width
  - Test on different screen sizes
  - Adjust sidebar width
  - _Requirements: 15.4, 15.5_

## Phase 7: Testing & Validation

### Task 16: Comprehensive Testing

- [x] 16.1 Run full spaghetti test suite
  - Test all files from Task 1.1
  - Verify: No crashes
  - Verify: Specific error messages
  - Verify: Partial results when possible
  - _Requirements: 1.5, 17.1, 17.4_

- [x] 16.2 Test composite key matching
  - Test with various key column combinations
  - Test with Japanese characters
  - Test with special characters
  - Test with missing keys
  - _Requirements: 10.1, 10.2_

- [x] 16.3 Test Virtual Fill edge cases
  - Single cell merge (A1:A1)
  - Entire row merge (A1:XFD1)
  - Entire column merge (A1:A1048576)
  - Overlapping ranges (should error gracefully)
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 17.5_

- [x] 16.4 Performance testing
  - Test with 10,000 cell file
  - Test with 50,000 cell file
  - Test with 100,000 cell file
  - Verify: Parsing completes within 60s
  - Verify: Memory usage reasonable
  - _Requirements: 16.1, 16.2, 16.3, 17.2, 17.3_

- [ ]* 16.5 Write property-based tests
  - Virtual Fill invariants
  - Composite key invariants
  - Dependency graph invariants
  - Use hypothesis library
  - _Requirements: All_

## Phase 7: Excel Rehab Maturity Model (Gamification)

### Task 18: Implement Maturity Scoring Engine

- [x] 18.1 Create MaturityLevel enum and data models
  - Create `MaturityLevel` enum in `models.py`
  - Values: LEVEL_1, LEVEL_2, LEVEL_3
  - Add `display_name` property with emoji badges
  - Add `locked_features` property listing locked features per level
  - Create `MaturityScore` dataclass with level, counts, progress
  - Create `UnlockRequirement` dataclass for feature unlock logic
  - _Requirements: 19.1, 19.2, 19.3, 19.4_

- [x] 18.2 Implement heuristic scoring algorithm (3-second target)
  - Create `calculate_maturity_level_heuristic()` in `analyzer.py`
  - Count Critical and High severity risks from quick scan
  - Heuristic 1: Critical risks present → Level 1 or 2
  - Heuristic 2: Hardcode count > 5 → Level 1
  - Heuristic 3: High risks > 3 → Level 2
  - Heuristic 4: Clean model → Level 3
  - Target: Complete within 3 seconds
  - Log execution time for monitoring
  - _Requirements: 19.1, 19.2, 19.3, 19.4_

- [x] 18.3 Implement deep scoring algorithm (accurate)
  - Create `calculate_maturity_level_deep()` in `analyzer.py`
  - Identify critical rows (KPI-related, high impact)
  - Count hardcodes specifically in critical rows
  - Level 1: > 5 hardcodes in critical rows
  - Level 2: Circular refs OR > 3 high-severity risks
  - Level 3: No Critical risks AND < 3 High risks
  - _Requirements: 19.1, 19.2, 19.3, 19.4_

- [x] 18.4 Implement two-phase progressive scoring
  - Create `analyze_with_progressive_scoring()` in `app.py`
  - Phase 1: Quick parse → heuristic scoring → display immediately
  - Phase 2: Full parse → deep scoring → update if changed
  - Display spinner during Phase 2: "Running deep analysis..."
  - Show info message if level changes after deep analysis
  - _Requirements: 19.1, 19.12_

- [x] 18.5 Implement unlock requirement calculator
  - Create `calculate_unlock_requirements()` in `analyzer.py`
  - For current level, determine issues blocking next level
  - Count remaining hardcodes, circular refs, high-severity risks
  - Generate actionable steps list
  - Return `UnlockRequirement` object
  - _Requirements: 19.5, 19.6, 19.7_

- [ ]* 18.6 Write property test for maturity monotonicity
  - **Property 1: Maturity level monotonicity**
  - **Validates: Requirements 19.1, 19.12**
  - Generate random models with varying risk counts
  - Fix issues (reduce risk count)
  - Assert: Maturity level never decreases
  - _Requirements: 19.1, 19.12_

### Task 19: Implement "Teasing Lock" UX (Psychology-Driven)

- [x] 19.1 Create premium locked button styling
  - Add custom CSS for locked premium buttons
  - Gradient background: #667eea to #764ba2
  - Gold border (2px solid gold)
  - Hover effect: scale(1.02), opacity increase
  - Make button look attractive, not disabled
  - _Requirements: 19.5, 19.6, 19.7_

- [x] 19.2 Implement Goal Seek button with teasing lock
  - Create `render_goal_seek_button()` in `app.py`
  - If Level 3: Show unlocked button with full functionality
  - If Level 1/2: Show locked premium button
  - On click (locked): Trigger popup with unlock requirements
  - Popup shows: Current level, remaining issues, progress bar
  - Include actionable tip: "Click ✨ Suggest Improvement"
  - _Requirements: 19.5, 19.6, 19.7_

- [x] 19.3 Implement unlock requirement popup
  - Create popup with st.warning() or custom modal
  - Display current maturity level with emoji
  - Show explicit unlock requirements (e.g., "Fix 3 more hardcodes")
  - Display progress bar with percentage
  - Include actionable guidance linking to AI Suggestion
  - Test with different maturity levels
  - _Requirements: 19.7_

- [x] 19.4 Add Scenario Planning locked feature
  - Create "Scenario Planning" button (locked for Level 1/2)
  - Use same teasing lock UX pattern
  - Display unlock requirements on click
  - _Requirements: 19.5, 19.6_

- [x] 19.5 Implement progress visualization
  - Create `calculate_progress_percentage()` in `analyzer.py`
  - Formula: (issues_fixed / total_issues_to_next_level) × 100
  - Display progress bar in unlock popup
  - Display progress badge in dashboard header
  - Update progress in real-time as issues are fixed
  - _Requirements: 19.11_

### Task 20: Implement AI Persona Adjustment

- [x] 20.1 Create persona prompt templates
  - Create `LEVEL_1_SYSTEM_PROMPT` in `ai_explainer.py`
  - Persona: "Coach" focused on decomposition
  - Tone: Encouraging, motivational, "resurrect the model"
  - Create `LEVEL_2_SYSTEM_PROMPT`
  - Persona: "Mechanic" focused on stability
  - Tone: Technical, precise, "fix what's broken"
  - Create `LEVEL_3_SYSTEM_PROMPT`
  - Persona: "Strategist" focused on optimization
  - Tone: Strategic, forward-looking, "what's possible now"
  - _Requirements: 19.8, 19.9, 19.10_

- [x] 20.2 Integrate persona selection with AI suggestions
  - Update `suggest_breakdown()` in `ai_explainer.py`
  - Accept `maturity_level` parameter
  - Select appropriate system prompt based on level
  - Level 1: Use Coach persona (decomposition focus)
  - Level 2: Use Mechanic persona (stability focus)
  - Level 3: Use Strategist persona (optimization focus)
  - _Requirements: 19.8, 19.9, 19.10_

- [x] 20.3 Test persona consistency
  - Generate AI suggestions for each maturity level
  - Verify Level 1 suggestions focus on variable creation
  - Verify Level 2 suggestions focus on error fixes
  - Verify Level 3 suggestions focus on strategic planning
  - Verify tone matches persona definition
  - _Requirements: 19.8, 19.9, 19.10_

- [ ]* 20.4 Write property test for AI persona consistency
  - **Property 4: AI persona consistency**
  - **Validates: Requirements 19.8, 19.9, 19.10**
  - Generate random cells with hardcodes
  - For each maturity level, generate AI suggestion
  - Assert: Suggestion uses correct persona keywords
  - _Requirements: 19.8, 19.9, 19.10_

### Task 21: Implement Dashboard Maturity Display

- [x] 21.1 Create maturity badge component
  - Create `display_maturity_badge()` in `app.py`
  - Display emoji and level name (e.g., "🏥 Level 1: Static Model")
  - Use color coding: Red (Level 1), Yellow (Level 2), Green (Level 3)
  - Display in prominent position (dashboard header)
  - Add tooltip with level description
  - _Requirements: 19.2, 19.3, 19.4_

- [x] 21.2 Add progress bar to dashboard header
  - Display progress toward next level
  - Show percentage and visual bar
  - Update in real-time as issues are fixed
  - Include motivational text (e.g., "75% to Level 3!")
  - _Requirements: 19.11_

- [x] 21.3 Add level-up notification
  - Detect when maturity level increases
  - Display celebration message with st.balloons()
  - Show "🎉 Level Up! You reached Level X!"
  - Highlight newly unlocked features
  - _Requirements: 19.12_

- [x] 21.4 Integrate maturity display with file upload
  - Display maturity badge immediately after heuristic scoring
  - Update badge after deep scoring completes
  - Show transition animation if level changes
  - _Requirements: 19.1, 19.12_

### Task 22: Optimization for 3-Second Target

- [ ] 22.1 Implement quick parse for heuristic scoring
  - Create `quick_parse()` in `parser.py`
  - Parse only first 1,000 cells (configurable limit)
  - Skip Virtual Fill in quick parse
  - Skip dependency graph construction
  - Return minimal ModelAnalysis object
  - _Requirements: 19.1_

- [ ] 22.2 Implement quick risk scan
  - Create `quick_risk_scan()` in `analyzer.py`
  - Detect only obvious risks: hardcodes, circular refs
  - Skip merged cell risk detection
  - Skip cross-sheet spaghetti detection
  - Return risk list with counts by severity
  - _Requirements: 19.1_

- [ ] 22.3 Add performance monitoring
  - Log execution time for heuristic scoring
  - Log execution time for deep scoring
  - Display warning if heuristic > 5 seconds
  - Add performance metrics to debug panel
  - _Requirements: 19.1_

- [ ] 22.4 Test performance with large files
  - Test with 10,000 cell file
  - Test with 50,000 cell file
  - Verify heuristic scoring < 5 seconds
  - Verify deep scoring completes without timeout
  - Optimize if performance targets not met
  - _Requirements: 19.1_

- [ ]* 22.5 Write property test for heuristic scoring speed
  - **Property 5: Heuristic scoring speed**
  - **Validates: Requirements 19.1, Performance**
  - Generate random Excel files of varying sizes
  - Run heuristic scoring
  - Assert: Execution time < 5 seconds
  - _Requirements: 19.1_

### Task 23: Integration and Testing

- [ ] 23.1 Integrate maturity scoring with existing analysis
  - Update main analysis flow in `app.py`
  - Call progressive scoring on file upload
  - Pass maturity level to AI suggestions
  - Update UI to show locked/unlocked features
  - _Requirements: 19.1, 19.5, 19.6, 19.8_

- [ ] 23.2 Test maturity level transitions
  - Upload file with > 5 hardcodes (expect Level 1)
  - Fix hardcodes, re-upload (expect Level 2 or 3)
  - Verify level-up notification appears
  - Verify features unlock correctly
  - _Requirements: 19.12_

- [ ] 23.3 Test locked feature interactions
  - Click locked Goal Seek button
  - Verify popup appears with unlock requirements
  - Verify progress bar displays correctly
  - Verify actionable guidance is clear
  - _Requirements: 19.5, 19.6, 19.7_

- [ ] 23.4 Test AI persona adjustment
  - Generate suggestions at Level 1 (expect Coach persona)
  - Generate suggestions at Level 2 (expect Mechanic persona)
  - Generate suggestions at Level 3 (expect Strategist persona)
  - Verify tone and focus match persona definition
  - _Requirements: 19.8, 19.9, 19.10_

- [ ]* 23.5 Write integration tests for maturity system
  - Test full workflow: upload → score → fix → re-upload → level up
  - Test edge cases: exactly 5 hardcodes, exactly 3 high risks
  - Test unlock requirements calculation
  - Test progress percentage calculation
  - _Requirements: 19.1, 19.2, 19.3, 19.4, 19.5, 19.6, 19.7, 19.11, 19.12_

## Phase 8: 3-Tier Risk Triage System

### Task 24: Implement Risk Classification Engine

- [ ] 24.1 Create RiskCategory enum and classification logic
  - Add `RiskCategory` enum to `models.py` with three values
  - Add `category` field to `RiskAlert` dataclass
  - Create `classify_risk()` function in `analyzer.py`
  - Implement classification rules per design document
  - Test classification with sample risks
  - _Requirements: 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8, 20.9_

- [ ] 24.2 Implement hardcode consistency checker
  - Create `check_hardcode_consistency()` function in `analyzer.py`
  - Find all hardcodes with same row label
  - Compare values to determine consistency
  - Return True if consistent (Structural Debt), False if inconsistent (Integrity Risk)
  - Test with consistent and inconsistent hardcode examples
  - _Requirements: 20.6, 20.8_

- [ ] 24.3 Create RiskTriageEngine class
  - Create `RiskTriageEngine` class in `analyzer.py`
  - Implement `classify_all()` method to sort risks into three lists
  - Implement `get_tab_counts()` method for tab labels
  - Add properties for accessing each category
  - Test with mixed risk types
  - _Requirements: 20.1, 20.13_

- [ ] 24.4 Update risk detection to include consistency metadata
  - Update `_detect_hidden_hardcodes()` to check consistency
  - Add `is_consistent` flag to risk metadata
  - Ensure all risks have necessary metadata for classification
  - _Requirements: 20.6, 20.8_

- [ ]* 24.5 Write property test for classification consistency
  - **Property 7: Risk classification consistency**
  - **Validates: Requirements 20.1-20.9**
  - Generate random risks of various types
  - Assert: Each risk classified into exactly one category
  - Assert: Classification is deterministic (same input → same output)
  - _Requirements: 20.1-20.9_

### Task 25: Implement 3-Tier Tabbed UI

- [ ] 25.1 Create tab rendering function
  - Create `render_risk_triage_tabs()` function in `app.py`
  - Use `st.tabs()` to create three tabs
  - Add risk counts to tab labels (e.g., "Fatal Errors (3)")
  - Add icons and color coding per design
  - _Requirements: 20.10, 20.11, 20.12, 20.13_

- [ ] 25.2 Implement Fatal Errors tab (Tab 1)
  - Add red color theme (#DC2626)
  - Add 🔴 icon and "Calculation Breakage" description
  - Render risk table with fatal errors
  - Add critical severity indicators
  - _Requirements: 20.2, 20.3, 20.4, 20.10_

- [ ] 25.3 Implement Integrity Risks tab (Tab 2) - MAKE PROMINENT
  - Add orange/yellow color theme (#F59E0B)
  - Add ⚠️ icon and "Hidden Bugs" description
  - Add visual prominence: larger font, warning badge
  - Add "🔍 Review Priority" badge
  - Render risk table with integrity risks
  - _Requirements: 20.5, 20.6, 20.7, 20.11_

- [ ] 25.4 Implement Structural Debt tab (Tab 3)
  - Add blue/gray color theme (#3B82F6)
  - Add 🔧 icon and "Maintenance Issues" description
  - Render risk table with structural debt
  - Use subdued styling to indicate lower priority
  - _Requirements: 20.8, 20.9, 20.12_

- [ ] 25.5 Create risk table component
  - Create `render_risk_table()` function
  - Columns: Cell, Sheet, Context, Description, Actions
  - Make cell addresses clickable
  - Add context-specific action buttons
  - Format table with appropriate styling per category
  - _Requirements: 20.14_

- [ ] 25.6 Add custom CSS for visual prominence
  - Add CSS for Tab 2 prominence (pulsing border, larger font)
  - Add CSS for color-coded tabs
  - Add CSS for risk severity badges
  - Test visual hierarchy across all tabs
  - _Requirements: 20.11_

### Task 26: Integration and Migration

- [ ] 26.1 Replace existing risk display with triage tabs
  - Locate current "Detected Risks" display in `app.py`
  - Replace with `render_risk_triage_tabs()` call
  - Remove old single-list display code
  - Ensure all risk types are handled
  - _Requirements: 20.1_

- [ ] 26.2 Update risk analysis flow
  - Update `analyze()` method to classify risks
  - Create `RiskTriageEngine` instance after risk detection
  - Pass triage engine to UI rendering
  - Ensure backward compatibility with existing code
  - _Requirements: 20.1, 20.13_

- [ ] 26.3 Test with real Excel files
  - Test with file containing circular references (expect Tab 1)
  - Test with file containing inconsistent formulas (expect Tab 2)
  - Test with file containing merged cells (expect Tab 3)
  - Test with file containing mixed risk types
  - Verify tab counts are accurate
  - _Requirements: 20.1-20.14_

- [ ] 26.4 Test hardcode consistency detection
  - Create test file with consistent hardcodes (same label, same value)
  - Verify: Classified as Structural Debt (Tab 3)
  - Create test file with inconsistent hardcodes (same label, different values)
  - Verify: Classified as Integrity Risk (Tab 2)
  - _Requirements: 20.6, 20.8_

- [ ]* 26.5 Write property test for tab count accuracy
  - **Property 8: Tab count accuracy**
  - **Validates: Requirements 20.13**
  - Generate random risk lists
  - Classify into tabs
  - Assert: Sum of tab counts equals total risk count
  - Assert: No risks lost or duplicated
  - _Requirements: 20.13_

### Task 27: Polish and Documentation

- [ ] 27.1 Add tooltips and help text
  - Add tooltip to each tab explaining the category
  - Add help text for "Integrity Risks" explaining why it's priority
  - Add guidance on how to prioritize fixes
  - _Requirements: 20.10, 20.11, 20.12_

- [ ] 27.2 Update user documentation
  - Document the 3-tier triage system in user guide
  - Explain business impact vs technical severity
  - Provide examples of each category
  - Add screenshots of new UI
  - _Requirements: 20.1-20.14_

- [ ] 27.3 Add analytics/logging
  - Log risk distribution across tabs
  - Track which tab users interact with most
  - Monitor classification accuracy
  - _Requirements: 20.1_

- [ ] 27.4 Final visual polish
  - Verify color scheme is consistent
  - Verify Tab 2 stands out appropriately
  - Test responsive layout on different screen sizes
  - Get user feedback on visual hierarchy
  - _Requirements: 20.10, 20.11, 20.12_

## Phase 9: Professional Minimalism & Master-Detail Layout ("The Cockpit")

### Task 28: Implement Master-Detail Split View

- [ ] 28.1 Create split-view layout structure
  - Replace existing long-scroll layout with `st.columns([0.6, 0.4])`
  - Left column (60%): Master panel with risk table
  - Right column (40%): Detail panel with inspection view
  - Add session state for selected risk tracking
  - Test responsive behavior on different screen sizes
  - _Requirements: 21.1_

- [ ] 28.2 Implement master panel risk table
  - Create `render_master_risk_table()` function in `app.py`
  - Use `st.dataframe()` with `selection_mode="single-row"`
  - Configure columns: Location (Sheet!Cell), Context, Risk Type, Value
  - Set compact row height and minimal padding
  - Enable row selection and store selected index in session state
  - _Requirements: 21.2, 21.3, 21.12_

- [ ] 28.3 Remove emojis and decorative elements from data
  - Strip all emojis from risk type labels (e.g., "🔴 Fatal Error" → "Fatal Error")
  - Remove icons from context labels
  - Remove decorative separators and borders
  - Keep data cells clean with text only
  - _Requirements: 21.4_

- [ ] 28.4 Implement severity-based color coding
  - Add conditional formatting to dataframe
  - Critical/High severity: Bold red text (#DC2626) or light red background (#FEE2E2)
  - Medium/Low severity: Default black/gray text (#374151)
  - Apply color only to severity column or entire row
  - Test color contrast for readability
  - _Requirements: 21.5, 21.6_

- [ ] 28.5 Implement intelligent sorting
  - Create `sort_risks_by_priority()` function in `analyzer.py`
  - Primary sort: Severity (Critical → High → Medium → Low)
  - Secondary sort: Impact count (descending)
  - Ensure most dangerous risk always appears at top
  - Apply sorting before rendering table
  - _Requirements: 21.7_

### Task 29: Implement Detail Panel (Inspection View)

- [ ] 29.1 Create detail panel rendering function
  - Create `render_detail_panel()` function in `app.py`
  - Check if risk is selected from session state
  - If no selection: Display instructions ("Select a risk to inspect")
  - If selected: Render detailed inspection view
  - _Requirements: 21.8, 21.11_

- [ ] 29.2 Implement Section A: Logic X-Ray
  - Create `render_logic_xray()` function in `app.py`
  - Display section header: "Logic X-Ray"
  - Show dependency trace in simple text format
  - Format: "F4 (201.26) ➔ F24 (Cost Calculation)"
  - Use monospace font for cell references
  - Add collapsible section for long traces
  - _Requirements: 21.9_

- [ ] 29.3 Implement Section B: The Cure (AI Suggestion)
  - Create `render_ai_cure()` function in `app.py`
  - Display section header: "The Cure"
  - Show AI suggestion button if API key configured
  - Display refactoring recipe in clear, actionable format
  - Use numbered steps for multi-step suggestions
  - Add copy-to-clipboard button for suggestions
  - _Requirements: 21.10_

- [ ] 29.4 Add detail panel polish
  - Use clean typography with appropriate font sizes
  - Add subtle section dividers (1px gray line)
  - Ensure proper spacing between sections
  - Add loading spinner for AI suggestions
  - Test with various risk types
  - _Requirements: 21.9, 21.10, 21.13_

### Task 30: Professional Minimalism Styling

- [ ] 30.1 Create custom CSS for financial statement aesthetic
  - Create `inject_professional_css()` function in `app.py`
  - Define clean typography: Sans-serif font, appropriate sizes
  - Remove rounded corners and shadows
  - Use sharp, clean lines and borders
  - Define color palette: Black, gray, red for danger only
  - _Requirements: 21.13_

- [ ] 30.2 Optimize data density
  - Reduce row height in dataframe (use `height` parameter)
  - Minimize padding and margins throughout
  - Increase visible rows "above the fold" (target: 15-20 rows)
  - Remove unnecessary whitespace
  - Test on 1920x1080 and 1280x720 resolutions
  - _Requirements: 21.12_

- [ ] 30.3 Remove all decorative UI elements
  - Remove emoji badges from headers
  - Remove progress bars from main view (move to settings)
  - Remove celebration animations (st.balloons)
  - Remove gradient backgrounds
  - Keep UI strictly functional
  - _Requirements: 21.4, 21.13_

- [ ] 30.4 Implement compact header
  - Reduce header size and padding
  - Display only essential information: File name, Health score
  - Move secondary information to sidebar
  - Use single-line layout for header
  - _Requirements: 21.12, 21.13_

### Task 31: Integration and Migration

- [ ] 31.1 Refactor main app.py layout
  - Locate existing risk display code
  - Replace with master-detail split view
  - Migrate risk table rendering to new format
  - Ensure all risk types are handled
  - Test with existing features (AI suggestions, export)
  - _Requirements: 21.1, 21.2_

- [ ] 31.2 Update risk selection handling
  - Implement row selection event handler
  - Store selected risk in session state
  - Update detail panel when selection changes
  - Handle deselection (clicking same row)
  - Test selection persistence across interactions
  - _Requirements: 21.8_

- [ ] 31.3 Migrate AI suggestion to detail panel
  - Move AI suggestion button from risk table to detail panel
  - Update AI suggestion display to fit detail panel layout
  - Ensure AI context includes selected risk details
  - Test AI suggestion flow with new UI
  - _Requirements: 21.10_

- [ ] 31.4 Update CSV export for new layout
  - Ensure CSV export still works with new table format
  - Verify all columns are included in export
  - Test export with sorted and filtered data
  - _Requirements: 21.3_

### Task 32: Testing and Polish

- [ ] 32.1 Test with real Excel files
  - Upload file with 50+ risks
  - Verify table displays compactly with 15-20 visible rows
  - Test row selection and detail panel updates
  - Verify sorting places most dangerous risks at top
  - Test color coding for different severity levels
  - _Requirements: 21.7, 21.12_

- [ ] 32.2 Test detail panel functionality
  - Select various risk types
  - Verify Logic X-Ray displays correctly
  - Test AI suggestion generation
  - Verify instructions display when no selection
  - Test with risks that have no dependencies
  - _Requirements: 21.9, 21.10, 21.11_

- [ ] 32.3 Test professional aesthetic
  - Verify no emojis in data cells
  - Verify color used only for danger signals
  - Verify clean typography and spacing
  - Compare to Bloomberg Terminal aesthetic
  - Get feedback from finance professionals
  - _Requirements: 21.4, 21.5, 21.6, 21.13_

- [ ] 32.4 Performance testing
  - Test with 100+ risks in table
  - Verify scrolling performance
  - Verify selection responsiveness
  - Test detail panel rendering speed
  - Optimize if performance issues detected
  - _Requirements: 21.2, 21.8_

- [ ] 32.5 Write property test for sorting consistency
  - **Property 9: Risk sorting consistency**
  - **Validates: Requirements 21.7**
  - Generate random risk lists with varying severities
  - Apply sorting algorithm
  - Assert: Critical risks always before High risks
  - Assert: Within same severity, higher impact count comes first
  - _Requirements: 21.7_

### Task 33: Documentation and User Guide

- [ ] 33.1 Update user documentation
  - Document master-detail layout concept
  - Explain how to select and inspect risks
  - Document Logic X-Ray feature
  - Document AI Cure feature
  - Add screenshots of new UI
  - _Requirements: 21.1-21.13_

- [ ] 33.2 Create quick reference guide
  - One-page guide for finance professionals
  - Explain "The Cockpit" metaphor
  - Show keyboard shortcuts (if any)
  - Explain color coding system
  - _Requirements: 21.5, 21.6, 21.13_

- [ ] 33.3 Add tooltips and help text
  - Add tooltip to master panel explaining selection
  - Add tooltip to detail panel sections
  - Add help icon with layout explanation
  - Keep help text minimal and professional
  - _Requirements: 21.11_

## Phase 10: Deployment Preparation

### Task 17: Final Polish

- [ ] 17.1 Update README with V0.4 features
  - Document Virtual Fill capability
  - Document Composite Key Matching
  - Document AI Model Architect
  - Add screenshots
  - _Requirements: All_

- [ ] 17.2 Create user guide
  - How to upload files
  - How to select key columns
  - How to use AI suggestions
  - How to interpret heatmap
  - _Requirements: All_

- [ ] 17.3 Add logging
  - Log all errors with context
  - Log parse success rates
  - Log AI API usage
  - Never log sensitive data
  - _Requirements: 17.4_

- [ ] 17.4 Optimize caching
  - Verify Streamlit cache working
  - Add cache for AI responses
  - Clear old cache entries
  - _Requirements: 16.1, 16.2, 16.3_

- [ ] 17.5 Final checkpoint
  - Run all tests
  - Verify all features working
  - Test with real Japanese Excel files
  - Get user feedback
  - _Requirements: All_

---

## Phase 11: Risk Review System (Session-Based Tracking)

### Task 34: Implement Risk Review State Management

- [ ] 34.1 Create RiskReviewState data models
  - Create `RiskReviewState` dataclass in `models.py`
  - Fields: `risk_id`, `is_reviewed`, `reviewed_at`
  - Create `ReviewProgress` dataclass
  - Fields: `total_risks`, `reviewed_count`, `unreviewed_count`, `percentage`, `initial_score`, `current_score`, `improvement_delta`
  - Add `display_text` property to ReviewProgress
  - _Requirements: 22.2, 22.4, 22.5_

- [ ] 34.2 Implement RiskReviewStateManager
  - Create `RiskReviewStateManager` class in new file `src/risk_review.py`
  - Implement `get_risk_id()` method to generate unique identifier
  - Implement `is_reviewed()` method to check review state
  - Implement `set_reviewed()` method to update state
  - Implement `get_reviewed_count()` method
  - Implement `get_unreviewed_risks()` method
  - Implement `clear_all()` method
  - Store state in `st.session_state.risk_review_states` dictionary
  - _Requirements: 22.1, 22.2, 22.10_

- [ ] 34.3 Implement DynamicScoreCalculator
  - Create `DynamicScoreCalculator` class in `src/risk_review.py`
  - Implement `calculate_initial_score()` method (all risks)
  - Formula: 100 - (Critical×10) - (High×5) - (Medium×2)
  - Implement `calculate_current_score()` method (unreviewed risks only)
  - Implement `calculate_progress()` method returning ReviewProgress
  - Calculate improvement delta: current_score - initial_score
  - _Requirements: 22.4, 22.5, 22.11, 22.12_

- [ ]* 34.4 Write property test for score calculation
  - **Property 13: Review state consistency**
  - **Validates: Requirements 22.2, 22.4, 22.11**
  - Generate random risk lists with varying severities
  - Mark random subset as reviewed
  - Assert: Reviewed risks don't contribute to current score
  - _Requirements: 22.2, 22.4, 22.11_

- [ ]* 34.5 Write property test for progress calculation
  - **Property 14: Progress calculation accuracy**
  - **Validates: Requirements 22.5**
  - Generate random risk lists
  - Mark random subset as reviewed
  - Assert: percentage = (reviewed_count / total_count) × 100
  - _Requirements: 22.5_

### Task 35: Implement Risk Table with Checkboxes

- [ ] 35.1 Add checkbox column to risk table
  - Update `render_risk_table_with_checkboxes()` in `src/master_detail_ui.py`
  - Add "確認" column as leftmost column
  - Use `st.data_editor()` with CheckboxColumn config
  - Disable editing for all columns except checkbox
  - _Requirements: 22.1_

- [ ] 35.2 Implement visual feedback for reviewed risks
  - Apply styling function to gray out reviewed risks
  - Set opacity to 0.6 for reviewed rows
  - Use color #9CA3AF for text
  - Keep unreviewed risks with normal styling
  - _Requirements: 22.3_

- [ ] 35.3 Implement checkbox state synchronization
  - Capture checkbox changes from st.data_editor
  - Update RiskReviewStateManager on each change
  - Trigger re-render to show updated state
  - Ensure immediate UI feedback (<100ms)
  - _Requirements: 22.2_

- [ ] 35.4 Test checkbox interaction
  - Test checking/unchecking updates state correctly
  - Test visual feedback applies immediately
  - Test state persists during session
  - Test state clears on new session
  - _Requirements: 22.1, 22.2, 22.3, 22.10_

### Task 36: Implement Progress Display

- [ ] 36.1 Create progress display component
  - Create `render_progress_display()` function in `src/risk_review.py`
  - Display 4 metrics: Initial Score, Current Score, Reviewed Count, Unreviewed Count
  - Use `st.metric()` with delta for improvement
  - Show green delta for positive improvement
  - _Requirements: 22.4, 22.5, 22.12_

- [ ] 36.2 Add progress bar visualization
  - Add `st.progress()` bar showing percentage complete
  - Update progress bar in real-time as risks are reviewed
  - Show percentage text: "確認済み: X/Y (Z%)"
  - _Requirements: 22.5_

- [ ] 36.3 Add encouraging messages
  - Show "🎉 すべてのリスクを確認しました！" when 100% complete
  - Show "💪 あとX個です！" when 50%+ complete
  - Show motivational message when improvement delta > 10
  - _Requirements: 22.12_

- [ ] 36.4 Test progress display updates
  - Test metrics update immediately on checkbox change
  - Test progress bar updates correctly
  - Test encouraging messages appear at right thresholds
  - Test color coding for improvement delta
  - _Requirements: 22.4, 22.5, 22.12_

### Task 37: Implement Filter System

- [ ] 37.1 Create filter controls
  - Create `render_filter_controls()` function in `src/risk_review.py`
  - Add radio buttons for: "すべて", "未確認のみ", "確認済みのみ"
  - Use horizontal layout for compact display
  - Store filter mode in session state
  - _Requirements: 22.7_

- [ ] 37.2 Implement filter logic
  - Update `render_risk_table_with_checkboxes()` to accept filter_mode
  - Filter "unreviewed": Show only unchecked risks
  - Filter "reviewed": Show only checked risks
  - Filter "all": Show all risks
  - _Requirements: 22.7, 22.8, 22.9_

- [ ] 37.3 Test filter functionality
  - Test "未確認のみ" shows only unreviewed risks
  - Test "確認済みのみ" shows only reviewed risks
  - Test "すべて" shows all risks
  - Test filter updates table immediately
  - _Requirements: 22.7, 22.8, 22.9_

- [ ]* 37.4 Write property test for filter correctness
  - **Property 15: Filter correctness**
  - **Validates: Requirements 22.7, 22.8, 22.9**
  - Generate random risk lists with random review states
  - Apply each filter mode
  - Assert: Displayed risks match filter criteria exactly
  - _Requirements: 22.7, 22.8, 22.9_

### Task 38: Implement CSV Export with Review State

- [ ] 38.1 Extend CSV export function
  - Update `export_risks_with_review_state()` in `src/risk_review.py`
  - Add "確認済み" column with TRUE/FALSE values
  - Add "エクスポート日時" column with timestamp
  - Format timestamp as "YYYY-MM-DD HH:MM:SS"
  - _Requirements: 22.6_

- [ ] 38.2 Update export button
  - Update download button in `app.py`
  - Label: "📥 CSVエクスポート（確認状態を含む）"
  - Generate filename with timestamp: `risk_review_YYYYMMDD_HHMMSS.csv`
  - Use UTF-8 encoding with BOM for Excel compatibility
  - _Requirements: 22.6_

- [ ] 38.3 Test CSV export
  - Test export includes all required columns
  - Test "確認済み" column has correct TRUE/FALSE values
  - Test timestamp column has correct format
  - Test Japanese characters display correctly in Excel
  - _Requirements: 22.6_

- [ ]* 38.4 Write property test for export completeness
  - **Property 16: CSV export completeness**
  - **Validates: Requirements 22.6**
  - Generate random risk lists with random review states
  - Export to CSV
  - Assert: All risks present in export
  - Assert: Review state matches for each risk
  - Assert: Timestamp column present
  - _Requirements: 22.6_

### Task 39: Integration and Testing

- [ ] 39.1 Integrate with master-detail layout
  - Add checkbox column to master panel risk table
  - Maintain single-row selection functionality
  - Update detail panel to show review state
  - Test interaction between checkbox and row selection
  - _Requirements: 22.1, 22.2_

- [ ] 39.2 Integrate with triage system
  - Apply review system to all three tabs (Fatal, Integrity, Structural)
  - Calculate separate progress for each tab
  - Allow filtering within each tab
  - Test review state persists across tab switches
  - _Requirements: 22.1, 22.2, 22.7_

- [ ] 39.3 Integrate with health score display
  - Replace static health score with dynamic score
  - Show both initial and current scores in header
  - Display improvement delta prominently
  - Update score in real-time as risks are reviewed
  - _Requirements: 22.4, 22.11, 22.12_

- [ ] 39.4 Performance testing
  - Test with 100 risks (target: <500ms render)
  - Test with 500 risks (target: <2s render)
  - Test checkbox interaction speed (target: <100ms)
  - Test score calculation speed (target: <100ms)
  - Optimize if performance targets not met
  - _Requirements: Performance_

- [ ] 39.5 End-to-end testing
  - Test complete workflow: upload → review → filter → export
  - Test session isolation (new session = fresh state)
  - Test all filter modes with various review states
  - Test CSV export with different review states
  - Test encouraging messages appear correctly
  - _Requirements: 22.1-22.12_

- [ ]* 39.6 Write property test for session isolation
  - **Property 17: Session isolation**
  - **Validates: Requirements 22.10**
  - Simulate multiple sessions
  - Assert: Review state empty at start of each session
  - Assert: No state leakage between sessions
  - _Requirements: 22.10_

- [ ]* 39.7 Write property test for score improvement monotonicity
  - **Property 18: Score improvement monotonicity**
  - **Validates: Requirements 22.11, 22.12**
  - Generate random risk lists
  - Mark risks as reviewed one by one
  - Assert: Current score never decreases
  - Assert: Improvement delta never negative
  - _Requirements: 22.11, 22.12_

### Task 40: Documentation and Polish

- [ ] 40.1 Update user documentation
  - Document risk review feature
  - Explain checkbox functionality
  - Explain dynamic score calculation
  - Explain filter system
  - Add screenshots of review workflow
  - _Requirements: 22.1-22.12_

- [ ] 40.2 Add tooltips and help text
  - Add tooltip to checkbox column explaining review
  - Add tooltip to progress display explaining scores
  - Add tooltip to filter controls
  - Keep help text minimal and clear
  - _Requirements: 22.1, 22.4, 22.7_

- [ ] 40.3 Add translation keys
  - Add Japanese translations to `src/i18n.py`
  - Keys: "review_checkbox", "initial_score", "current_score", "improvement"
  - Keys: "filter_all", "filter_unreviewed", "filter_reviewed"
  - Keys: "export_with_review_state"
  - Keys: "all_reviewed_message", "keep_going_message"
  - _Requirements: 22.1, 22.4, 22.5, 22.7, 22.12_

- [ ] 40.4 Final checkpoint
  - Run all tests for risk review system
  - Verify all features working correctly
  - Test with real risk data from sample files
  - Get user feedback on review workflow
  - _Requirements: 22.1-22.12_

## Priority Summary

**Phase 1 (CRITICAL)**: Robust Parser with Virtual Fill
- Task 1: Spaghetti Excel Test Suite
- Task 2: Data Models
- Task 3: Virtual Fill Algorithm
- Task 4: Dependency Extraction
- Task 5: Error Handling

**Phase 3 (CRITICAL)**: Composite Key Matching
- Task 8: Composite Key Implementation
- Task 9: Change Detection

**Phase 11 (NEW FEATURE)**: Risk Review System
- Task 34: State Management
- Task 35: Checkbox UI
- Task 36: Progress Display
- Task 37: Filter System
- Task 38: CSV Export
- Task 39: Integration
- Task 40: Documentation

**Other Phases**: Important but can be built incrementally after Phase 1 & 3 are solid.

## Notes

- Tasks marked with `*` are optional property-based tests
- Focus on Phase 1 first - this is our competitive moat
- Test early and often with real Japanese Excel files
- Never compromise on graceful error handling
- Phase 11 (Risk Review) can be implemented independently after core features are stable
