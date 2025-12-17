# Spaghetti Excel Test Suite

This directory contains test Excel files with various Japanese Excel patterns that are known to break global tools.

## Test Files

### 1. heavy_merged_cells.xlsx
**Pattern**: Headers with 5+ merged columns
**Challenge**: Multiple levels of merged headers (company name, period, categories)
**Expected Behavior**: 
- Parser should identify all merged ranges
- Virtual Fill should propagate values to all coordinates
- Formulas with hardcoded values (1000000, 1.1) should be detected
- Dependency graph should include all virtual cells

### 2. complex_grid_layout.xlsx
**Pattern**: Mixed merged rows and columns
**Challenge**: Vertical merges for categories + horizontal merges for sub-categories
**Expected Behavior**:
- Parser should handle both vertical and horizontal merges
- Formulas referencing merged ranges should resolve correctly
- No cells should be lost or duplicated

### 3. japanese_text_mixed.xlsx
**Pattern**: Mixed Japanese/English text
**Challenge**: Japanese characters in cell values and formulas
**Expected Behavior**:
- Parser should handle UTF-8 Japanese text correctly
- Context labels should display Japanese characters
- No encoding errors

### 4. circular_references.xlsx
**Pattern**: Intentional circular references
**Challenge**: A → B → C → A cycle
**Expected Behavior**:
- Parser should not hang or crash
- Circular reference detector should identify all cycles
- Critical severity alerts should be created

### 5. cross_sheet_complex.xlsx
**Pattern**: 10+ sheets with cross-references
**Challenge**: Complex cross-sheet dependencies
**Expected Behavior**:
- Parser should handle all sheets
- Cross-sheet references should be extracted correctly
- Dependency graph should span multiple sheets
- Cross-sheet spaghetti detector should flag formulas with >2 external sheets

### 6. edge_cases.xlsx
**Pattern**: Extreme merge scenarios
**Challenge**: Single cell merge, entire row merge, entire column merge, large rectangular merge
**Expected Behavior**:
- Parser should handle all edge cases without crashing
- Virtual Fill should work for all merge types
- No performance degradation

### 7. hanko_boxes.xlsx
**Pattern**: Japanese approval stamp grid
**Challenge**: 3x3 grid of merged cells (very common in Japanese business Excel)
**Expected Behavior**:
- Parser should handle hanko box grid correctly
- Merged cells in top-right corner should not interfere with data area
- All formulas should be extracted correctly

## Success Criteria

For the parser to pass this test suite:
1. **No Crashes**: All files must parse without exceptions
2. **Specific Errors**: If parsing fails, error messages must be specific and actionable
3. **Partial Success**: If some cells fail, parser should continue and return partial results
4. **Virtual Fill**: All merged cells must have propagated values
5. **Dependency Graph**: All cells (including virtual) must be in the graph
6. **Performance**: Parsing should complete within 60 seconds per file

## Running Tests

```bash
pytest tests/test_parser_robustness.py -v
```

## Adding New Test Files

When adding new spaghetti patterns:
1. Create the Excel file in this directory
2. Document the pattern and expected behavior in this README
3. Add test case to test_parser_robustness.py
