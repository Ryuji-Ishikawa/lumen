# System Design Document - Project Lumen V0.4

## Overview

Project Lumen V0.4 is an AI-Powered Strategic Guardian for FP&A professionals in Japan. The system is architected around two core competitive advantages:

1. **Virtual Fill Algorithm** - Enables parsing of complex Japanese Excel models with merged cells that break global tools
2. **Composite Key Matching** - Enables intelligent monthly variance analysis that handles row insertions/deletions

This design document focuses on the technical architecture required to deliver these capabilities robustly.

## Architecture

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Streamlit UI Layer                       │
│  (File Upload, Heatmap, Timeline, Dependency Viz, AI Chat)  │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                  Application Layer                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Parser     │  │   Analyzer   │  │  Diff Engine │     │
│  │  (Virtual    │  │  (Risk Det.) │  │  (Composite  │     │
│  │   Fill)      │  │              │  │   Key Match) │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                   Data Layer                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ ModelAnalysis│  │  NetworkX    │  │  AI Provider │     │
│  │   Object     │  │  Dep Graph   │  │  (GPT/Gemini)│     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

- **Frontend**: Streamlit (Python web framework)
- **Excel Parsing**: openpyxl (with custom Virtual Fill layer)
  - **Performance Contingency**: If parsing >60s in testing, swap read-engine to calamine (Rust-based, 10x faster)
- **Graph Analysis**: NetworkX (dependency graph, cycle detection)
- **Visualization**: streamlit-agraph (interactive dependency tree)
- **AI Integration**: OpenAI (GPT-4o) / Google (Gemini-1.5-flash)
- **Data Structures**: Python dataclasses, pandas DataFrames
- **Code Quality**: ruff (linting), pre-commit (hooks), pytest (testing)

## Components and Interfaces

### 1. ExcelParser (with Virtual Fill)

**Purpose**: Parse Japanese Excel files with complex merged cells and extract formulas, values, and dependencies.

**Key Methods**:
```python
class ExcelParser:
    def parse(file_obj: BytesIO, filename: str) -> ModelAnalysis
    def _identify_merged_ranges(worksheet: Worksheet) -> List[str]
    def _apply_virtual_fill(worksheet: Worksheet, merged_ranges: List[str]) -> Dict[str, CellInfo]
    def _extract_dependencies(formula: str, current_sheet: str) -> List[str]
    def _build_dependency_graph(cells: Dict[str, CellInfo]) -> nx.DiGraph
```

**Virtual Fill Data Flow** (CRITICAL - Our Moat):

```
Step 1: Identify Merged Ranges
┌─────────────────────────────────────────────────────────┐
│ Input: openpyxl Worksheet                                │
│ Process: worksheet.merged_cells.ranges                   │
│ Output: List["A1:C1", "D5:D10", ...]                    │
└─────────────────────────────────────────────────────────┘
                          ↓
Step 2: Extract Top-Left Cell Data
┌─────────────────────────────────────────────────────────┐
│ For each merged range "A1:C1":                           │
│   - Get top-left cell (A1)                               │
│   - Extract: value, formula, data_type                   │
│   - Store as "master" cell data                          │
└─────────────────────────────────────────────────────────┘
                          ↓
Step 3: Propagate to All Coordinates (Virtual Fill)
┌─────────────────────────────────────────────────────────┐
│ For each coordinate in range (A1, B1, C1):               │
│   - Create CellInfo object                               │
│   - Copy value/formula from top-left                     │
│   - Set is_merged=True                                   │
│   - Set merged_range="A1:C1"                             │
│   - Add to cells dict with key "Sheet!Address"          │
└─────────────────────────────────────────────────────────┘
                          ↓
Step 4: Dependency Extraction
┌─────────────────────────────────────────────────────────┐
│ For each cell with formula:                              │
│   - Tokenize formula with openpyxl.formula.tokenizer    │
│   - Extract RANGE tokens (cell references)              │
│   - Resolve merged cell references using Virtual Fill   │
│   - Build dependency list                                │
└─────────────────────────────────────────────────────────┘
                          ↓
Step 5: NetworkX Graph Construction
┌─────────────────────────────────────────────────────────┐
│ Create directed graph:                                   │
│   - Nodes: All cells (including virtual filled)         │
│   - Edges: Dependencies (A1 → B1 means B1 depends on A1)│
│   - Attributes: risk_level, is_hardcoded, etc.          │
└─────────────────────────────────────────────────────────┘
```

**Critical Implementation Details**:

1. **Merged Range Parsing**:
   ```python
   # openpyxl provides merged_cells.ranges
   for merged_range in worksheet.merged_cells.ranges:
       range_str = str(merged_range)  # "A1:C1"
       min_col, min_row, max_col, max_row = merged_range.bounds
       top_left_cell = worksheet.cell(min_row, min_col)
   ```

2. **Virtual Fill Propagation**:
   ```python
   # For each coordinate in the merged range
   for row in range(min_row, max_row + 1):
       for col in range(min_col, max_col + 1):
           cell_address = get_column_letter(col) + str(row)
           # Create virtual cell with top-left data
           virtual_cell = CellInfo(
               sheet=sheet_name,
               address=cell_address,
               value=top_left_cell.value,
               formula=top_left_cell.value if isinstance(top_left_cell.value, str) and top_left_cell.value.startswith('=') else None,
               is_merged=True,
               merged_range=range_str
           )
   ```

3. **Dependency Resolution with Virtual Fill**:
   ```python
   # When a formula references "A1:C1" and A1:C1 is merged
   # The dependency graph will have edges from all virtual cells
   # This ensures accurate precedent/dependent tracing
   ```

### 2. ModelAnalyzer (Risk Detection)

**Purpose**: Analyze parsed models to detect risks and calculate health scores.

**Key Methods**:
```python
class ModelAnalyzer:
    def analyze(model: ModelAnalysis, fiscal_start_month: int, allowed_constants: List[float]) -> ModelAnalysis
    def _detect_hidden_hardcodes(cells: Dict[str, CellInfo], allowed_constants: List[float]) -> List[RiskAlert]
    def _detect_circular_references(graph: nx.DiGraph) -> List[RiskAlert]
    def _detect_merged_cell_risks(cells: Dict[str, CellInfo], merged_ranges: Dict[str, List[str]]) -> List[RiskAlert]
    def _add_context_labels(risks: List[RiskAlert], cells: Dict[str, CellInfo]) -> List[RiskAlert]
    def _calculate_health_score(risks: List[RiskAlert]) -> int
```

**Risk Detection Pipeline**:
```
Input: ModelAnalysis with cells and dependency graph
  ↓
[Hidden Hardcode Detection]
  - Tokenize formulas
  - Identify NUMBER tokens
  - Exclude allowed constants
  - Create High severity alerts
  ↓
[Circular Reference Detection]
  - Use networkx.simple_cycles()
  - Identify all cycles
  - Create Critical severity alerts
  ↓
[Merged Cell Risk Detection]
  - Check formula ranges
  - Detect merged cell overlaps
  - Create Medium severity alerts
  ↓
[Context Labeling]
  - Scan columns A-D for row labels
  - Scan rows 1-20 for column labels
  - Add contextual information to alerts
  ↓
[AI Smart Context with Quality Filtering]
  - Validate context label quality
  - If poor quality detected, trigger AI recovery
  - Replace garbage labels with meaningful context
  ↓
[Health Score Calculation]
  - Start at 100
  - Subtract: Critical×10, High×5, Medium×2
  - Return final score
  ↓
Output: ModelAnalysis with risks and health score
```

### 3. DiffEngine (with Composite Key Matching)

**Purpose**: Compare two Excel models with intelligent row matching for monthly variance analysis.

**Key Methods**:
```python
class DiffEngine:
    def compare(old_model: ModelAnalysis, new_model: ModelAnalysis, key_columns: List[str]) -> DiffResult
    def _build_composite_keys(model: ModelAnalysis, key_columns: List[str]) -> Dict[str, str]
    def _match_rows_by_composite_key(old_keys: Dict, new_keys: Dict) -> Dict[str, str]
    def _detect_logic_changes(old_cell: CellInfo, new_cell: CellInfo) -> bool
    def _detect_input_changes(old_cell: CellInfo, new_cell: CellInfo) -> bool
    def _categorize_changes(old_model: ModelAnalysis, new_model: ModelAnalysis, row_mapping: Dict) -> DiffResult
```

**Composite Key Matching Data Flow** (CRITICAL - Our Moat):

```
Step 1: User Selects Key Columns
┌─────────────────────────────────────────────────────────┐
│ UI: User selects key columns (e.g., ["Account Name"])   │
│ Example: Column A contains account names                 │
└─────────────────────────────────────────────────────────┘
                          ↓
Step 2: Build Composite Keys for Old Model
┌─────────────────────────────────────────────────────────┐
│ For each row in old model:                               │
│   - Extract values from key columns                      │
│   - Concatenate: "Personnel Cost|Fixed"                  │
│   - Hash or normalize: hash("Personnel Cost|Fixed")      │
│   - Store mapping: composite_key → row_number           │
│                                                           │
│ Example:                                                  │
│   Row 5: "Personnel Cost" → key="Personnel Cost"        │
│   Row 6: "Marketing" → key="Marketing"                   │
└─────────────────────────────────────────────────────────┘
                          ↓
Step 3: Build Composite Keys for New Model
┌─────────────────────────────────────────────────────────┐
│ Same process for new model:                              │
│   Row 6: "Personnel Cost" → key="Personnel Cost"        │
│   Row 7: "Marketing" → key="Marketing"                   │
│   Row 8: "New Account" → key="New Account"              │
└─────────────────────────────────────────────────────────┘
                          ↓
Step 4: Match Rows by Composite Key
┌─────────────────────────────────────────────────────────┐
│ Create row mapping:                                      │
│   old_row_5 → new_row_6 (both have key="Personnel Cost")│
│   old_row_6 → new_row_7 (both have key="Marketing")     │
│   new_row_8 → NEW (key="New Account" not in old)        │
└─────────────────────────────────────────────────────────┘
                          ↓
Step 5: Categorize Changes
┌─────────────────────────────────────────────────────────┐
│ For each matched row pair:                               │
│   - Compare formulas → Logic Change (Critical)           │
│   - Compare values → Input Update (Normal)               │
│   - Compare risks → Improved/Degraded                    │
│                                                           │
│ For unmatched rows:                                      │
│   - Old only → Deleted row                               │
│   - New only → Added row                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
Output: DiffResult with categorized changes
```

**Composite Key Data Model**:

```python
@dataclass
class CompositeKey:
    """Represents a composite key for row matching"""
    key_columns: List[str]  # e.g., ["Account Name", "Category"]
    key_value: str          # e.g., "Personnel Cost|Fixed"
    normalized_key: str     # e.g., "personnelcost|fixed" (lowercase, no spaces)
    sheet: str
    row_number: int
    
@dataclass
class RowMapping:
    """Represents a mapping between old and new rows"""
    old_row: Optional[int]
    new_row: Optional[int]
    composite_key: str
    match_confidence: float  # 1.0 = exact match, 0.8 = fuzzy match
    
@dataclass
class ChangeCategory:
    """Categorizes a change between two cells"""
    change_type: str  # "logic_change", "input_update", "risk_improved", "risk_degraded"
    severity: str     # "critical", "normal", "positive"
    old_value: Any
    new_value: Any
    description: str
```

**Critical Implementation Details**:

1. **Composite Key Generation**:
   ```python
   def _build_composite_key(row_cells: List[CellInfo], key_columns: List[str]) -> str:
       # Extract values from key columns
       key_values = []
       for col in key_columns:
           cell = row_cells.get(col)
           if cell and cell.value:
               key_values.append(str(cell.value).strip())
       
       # Concatenate with delimiter
       composite_key = "|".join(key_values)
       
       # Normalize for matching (lowercase, remove extra spaces)
       normalized_key = composite_key.lower().replace("  ", " ")
       
       return normalized_key
   ```

2. **Row Matching Algorithm**:
   ```python
   def _match_rows(old_keys: Dict[str, int], new_keys: Dict[str, int]) -> Dict[int, int]:
       # Exact matching first
       row_mapping = {}
       for key, old_row in old_keys.items():
           if key in new_keys:
               new_row = new_keys[key]
               row_mapping[old_row] = new_row
       
       # Fuzzy matching for unmatched rows (optional, Phase 2)
       # Use difflib.SequenceMatcher for similarity scoring
       
       return row_mapping
   ```

3. **Change Detection**:
   ```python
   def _detect_change_type(old_cell: CellInfo, new_cell: CellInfo) -> str:
       # Logic change: formula modified
       if old_cell.formula != new_cell.formula:
           return "logic_change"  # Critical
       
       # Input update: value changed, formula same
       if old_cell.value != new_cell.value:
           return "input_update"  # Normal
       
       return "no_change"
   ```

### 4. AI Model Architect

**Purpose**: Provide AI-powered suggestions for breaking down hardcoded values into driver-based formulas.

**Key Methods**:
```python
class AIModelArchitect:
    def __init__(provider: str, api_key: str)
    def suggest_breakdown(cell: CellInfo, context: Dict) -> str
    def _build_prompt(cell: CellInfo, context: Dict) -> str
    def _call_ai_api(prompt: str) -> str
```

**AI Prompt Template** (with Data Sanitization):
```
Role: Expert FP&A Consultant specializing in driver-based financial modeling

Context:
- Cell: {sheet}!{address}
- Current Formula: {formula}
- Current Value: {masked_value}  # <NUM_1> if masking enabled, actual value if disabled
- Row Label: {row_label}
- Column Label: {col_label}

Task: This cell contains a hardcoded value. Suggest a driver-based breakdown that would make this assumption more transparent and maintainable.

Requirements:
- Provide suggestion in Japanese
- Focus on common FP&A drivers (headcount, unit price, volume, etc.)
- Be specific and actionable
- Format: "提案: [Driver 1] × [Driver 2]"

Example:
Current: "人件費 = <NUM_1>"  # Masked for enterprise security
Suggestion: "提案: 従業員数 × 平均給与"
```

**Data Sanitization (Enterprise Security)**:
- **Masking Mode Toggle**: User can enable/disable in settings
- **When Enabled**: Replace all numeric values with tokens (<NUM_1>, <NUM_2>, etc.)
- **What to Send**: Formula structure, row/column labels, cell references only
- **What NOT to Send**: Actual numeric values, cell values, sensitive data
- **Default**: Masking ON for enterprise clients

### 5. AI Smart Context with Quality Filtering

**Purpose**: Validate context label quality and use AI to recover meaningful labels when the parser finds garbage strings.

**Key Methods**:
```python
class SmartContext:
    def __init__(provider: str, api_key: str, enabled: bool)
    def recover_context(sheet: str, cell: str, cells: Dict[str, CellInfo]) -> Optional[str]
    def _is_poor_quality_label(text: str) -> bool
    def _build_context_prompt(sheet: str, cell: str, cells: Dict[str, CellInfo]) -> str
    def _call_ai_api(prompt: str) -> str
```

**Quality Filter Logic**:

The parser is "too easily satisfied" - it finds garbage strings and thinks the job is done. We need to be stricter and trigger AI recovery for poor quality labels.

```python
def _is_poor_quality_label(text: str) -> bool:
    """
    Validate if a context label is meaningful or garbage.
    
    Returns True if label is poor quality (triggers AI recovery).
    Returns False if label is acceptable.
    """
    if not text or not text.strip():
        return True
    
    text = text.strip()
    
    # Pattern 1: Cell Address Pattern (e.g., "E92", "AA1", "B123")
    if re.match(r'^[A-Z]+[0-9]+$', text):
        return True
    
    # Pattern 2: Generic Stopwords (English/Japanese)
    stopwords = {
        # English
        "Total", "Sum", "Subtotal", "Check", "Val", "Value",
        "Amount", "Number", "Item", "Row", "Column",
        # Japanese
        "合計", "小計", "計", "チェック", "検証", "値", "金額"
    }
    if text in stopwords:
        return True
    
    # Pattern 3: Symbols/Numeric Only (e.g., "-", "0", "123", "---")
    if re.match(r'^[-0-9\s]+$', text):
        return True
    
    return False
```

**Integration with Context Labeling**:

```python
def _add_context_labels(risks: List[RiskAlert], cells: Dict[str, CellInfo]) -> List[RiskAlert]:
    """Add context labels to risks with AI recovery for poor quality labels."""
    
    for risk in risks:
        # Get initial context from parser
        current_context = self._get_context_labels(risk.sheet, risk.cell, cells)
        
        # Check if context is missing OR poor quality
        if not current_context or self._is_poor_quality_label(current_context):
            if self.smart_context and self.smart_context.enabled:
                # Force AI Recovery
                print(f"[AI] Poor quality context '{current_context}' detected for {risk.sheet}!{risk.cell}")
                new_context = self.smart_context.recover_context(risk.sheet, risk.cell, cells)
                
                if new_context:
                    print(f"[AI] ✓ Recovered: '{new_context}'")
                    risk.row_label = new_context
                else:
                    print(f"[AI] ✗ Recovery failed, keeping original")
                    risk.row_label = current_context
            else:
                risk.row_label = current_context
        else:
            risk.row_label = current_context
    
    return risks
```

**AI Context Recovery Prompt**:

```
Role: Expert at understanding Japanese Excel financial models

Context:
- Sheet: {sheet}
- Cell: {cell}
- Context Window (surrounding cells):
  - Left (same row): {left_cells}
  - Above (same column): {above_cells}
  - Right (same row): {right_cells}
  - Below (same column): {below_cells}

Task: This cell has a poor quality context label (e.g., "E92", "Total"). 
Look at the surrounding cells and provide a meaningful, specific label that describes what this row/column represents.

Requirements:
- Return ONLY the label text, no explanation
- Be specific (e.g., "Cash Balance" not "Total")
- Use Japanese if the surrounding context is Japanese
- Maximum 50 characters

Example:
Poor: "E92"
Context: Above cells = ["Balance Sheet", "Current Assets", ""]
Good: "Cash & Equivalents"

Poor: "Total"
Context: Left cells = ["Personnel Cost", "Marketing", "R&D"]
Good: "Operating Expenses Total"
```

**Context Window Extraction**:

```python
def _extract_context_window(sheet: str, cell: str, cells: Dict[str, CellInfo]) -> Dict[str, List[str]]:
    """
    Extract surrounding cells to provide context for AI recovery.
    
    Returns a context window with 3-5 cells in each direction.
    """
    # Parse cell address (e.g., "E92" -> col=E, row=92)
    col, row = parse_cell_address(cell)
    
    context = {
        "left": [],
        "above": [],
        "right": [],
        "below": []
    }
    
    # Get 3 cells to the left (same row)
    for i in range(1, 4):
        left_col = get_column_letter(column_index_from_string(col) - i)
        left_cell = f"{sheet}!{left_col}{row}"
        if left_cell in cells:
            context["left"].append(str(cells[left_cell].value))
    
    # Get 5 cells above (same column)
    for i in range(1, 6):
        above_cell = f"{sheet}!{col}{row - i}"
        if above_cell in cells:
            context["above"].append(str(cells[above_cell].value))
    
    # Get 3 cells to the right (same row)
    for i in range(1, 4):
        right_col = get_column_letter(column_index_from_string(col) + i)
        right_cell = f"{sheet}!{right_col}{row}"
        if right_cell in cells:
            context["right"].append(str(cells[right_cell].value))
    
    # Get 3 cells below (same column)
    for i in range(1, 4):
        below_cell = f"{sheet}!{col}{row + i}"
        if below_cell in cells:
            context["below"].append(str(cells[below_cell].value))
    
    return context
```

**Expected Behavior**:

```
Before Quality Filter:
Risk: Hidden Hardcode at BS!E92
Context: "E92" ❌ (garbage - cell address)

After Quality Filter + AI Recovery:
Risk: Hidden Hardcode at BS!E92  
Context: "Cash Balance" ✓ (meaningful)

Log Output:
[AI] Poor quality context 'E92' detected for BS!E92
[AI] ✓ Recovered: 'Cash Balance'
```

## Data Models

### Core Data Structures

```python
@dataclass
class CellInfo:
    """Represents a single Excel cell with metadata"""
    sheet: str
    address: str
    value: Any
    formula: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    is_dynamic: bool = False
    is_merged: bool = False
    merged_range: Optional[str] = None
    row_number: int = 0
    col_number: int = 0
    
@dataclass
class RiskAlert:
    """Represents a detected risk"""
    risk_type: str
    severity: str
    sheet: str
    cell: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    row_label: Optional[str] = None
    col_label: Optional[str] = None
    
@dataclass
class ModelAnalysis:
    """Complete analysis result for an Excel file"""
    filename: str
    sheets: List[str]
    cells: Dict[str, CellInfo]  # Key: "Sheet!Address"
    risks: List[RiskAlert]
    health_score: int
    dependency_graph: nx.DiGraph
    merged_ranges: Dict[str, List[str]]
    upload_timestamp: datetime = field(default_factory=datetime.now)
    
@dataclass
class DiffResult:
    """Comparison result between two models"""
    old_score: int
    new_score: int
    score_delta: int
    logic_changes: List[ChangeCategory]
    input_updates: List[ChangeCategory]
    improved_risks: List[RiskAlert]
    degraded_risks: List[RiskAlert]
    structural_changes: List[str]
    row_mapping: Dict[int, int]  # old_row → new_row
```

## Error Handling Strategy

### Graceful Failure Principles

1. **Never Crash**: All exceptions must be caught and converted to user-friendly messages
2. **Specific Messages**: Provide actionable guidance, not generic errors
3. **Partial Success**: If 90% of cells parse successfully, show results with warnings
4. **Logging**: Log all errors for debugging without exposing to user

### Error Handling Layers

```python
# Layer 1: File Upload
try:
    workbook = openpyxl.load_workbook(file_obj)
except InvalidFileException as e:
    if "password" in str(e).lower():
        raise ValueError("このファイルはパスワード保護されています。パスワードを解除してから再度アップロードしてください。")
    else:
        raise ValueError("ファイルが破損しているか、無効な形式です。")

# Layer 2: Cell Parsing
try:
    cell_value = cell.value
    cell_formula = cell.value if isinstance(cell.value, str) and cell.value.startswith('=') else None
except Exception as e:
    logger.warning(f"Failed to parse cell {cell.coordinate}: {e}")
    # Continue parsing other cells

# Layer 3: Dependency Extraction
try:
    dependencies = self._extract_dependencies(formula, sheet_name)
except Exception as e:
    logger.warning(f"Failed to extract dependencies for {cell.coordinate}: {e}")
    dependencies = []  # Continue with empty dependencies

# Layer 4: Graph Construction
try:
    graph = self._build_dependency_graph(cells)
except Exception as e:
    logger.error(f"Failed to build dependency graph: {e}")
    graph = nx.DiGraph()  # Return empty graph, continue with analysis
```

## Testing Strategy

### Unit Tests

1. **Virtual Fill Tests**:
   - Test single merged cell (A1:A1)
   - Test horizontal merge (A1:C1)
   - Test vertical merge (A1:A5)
   - Test rectangular merge (A1:C5)
   - Test multiple non-overlapping merges
   - Test formula propagation in merged cells

2. **Composite Key Tests**:
   - Test exact key matching
   - Test key with special characters
   - Test key with Japanese characters
   - Test missing key columns
   - Test duplicate keys (error handling)

3. **Dependency Extraction Tests**:
   - Test simple cell reference (A1)
   - Test range reference (A1:B10)
   - Test cross-sheet reference (Sheet2!A1)
   - Test dynamic reference (INDIRECT)
   - Test merged cell reference

### Integration Tests

1. **Spaghetti Excel Test Suite** (Priority 1):
   - Create test files with various Japanese Excel patterns:
     - Heavy merged cells (headers, labels)
     - Complex grid layouts
     - Mixed Japanese/English text
     - Circular references
     - Cross-sheet dependencies
   - Validate parser handles all cases without crashing

2. **Monthly Guardian Test Suite**:
   - Create old/new file pairs with:
     - Row insertions
     - Row deletions
     - Row reordering
     - Formula changes
     - Value changes
   - Validate composite key matching works correctly

### Property-Based Tests

1. **Virtual Fill Invariants**:
   - Property: All cells in merged range have same value
   - Property: Dependency graph includes all virtual cells
   - Property: No cell is lost during Virtual Fill

2. **Composite Key Invariants**:
   - Property: Same key always maps to same row
   - Property: All old rows are either matched or marked as deleted
   - Property: All new rows are either matched or marked as added

## Performance Considerations

### Optimization Strategies

1. **Caching**:
   - Use Streamlit @st.cache_data for parse results
   - Cache key: file content hash
   - Invalidate on file change

2. **Lazy Loading**:
   - Parse only visible sheets initially
   - Load dependency graph on demand
   - Defer AI suggestions until requested

3. **Limits**:
   - Max cells: 100,000 (configurable)
   - Max dependency graph nodes: 10,000 for visualization
   - Timeout: 60 seconds for parsing

4. **Memory Management**:
   - Stream large files instead of loading entirely
   - Clear old session data periodically
   - Use generators for large iterations

## Model Maturity Scoring (Excel Rehab Gamification)

### Purpose

Transform the user experience from "fixing bugs" (negative) to "leveling up" (positive) through a gamified maturity progression system. Users progress from Level 1 (Critical Condition - Static Model) to Level 3 (Healthy Athlete - Strategic Model) by fixing issues, unlocking advanced features along the way.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Maturity Scoring Engine                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Heuristic   │  │   Level      │  │   Feature    │     │
│  │  Scorer      │  │  Calculator  │  │   Unlocker   │     │
│  │  (Fast)      │  │              │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    UI Gamification Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Progress    │  │  "Teasing    │  │  AI Persona  │     │
│  │  Badge       │  │   Lock" UX   │  │  Adjuster    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Maturity Level Definitions

**Level 1: Critical Condition (Static Model) 🏥**
- **Criteria**: More than 5 Hidden Hardcode risks in critical rows
- **Status**: "🏥 Maturity Level 1: Static Model"
- **Locked Features**: Goal Seek, Scenario Planning
- **AI Persona**: "Coach" focused on decomposition and variable creation
- **Message Tone**: "Your model is static. Let's resurrect it by adding variables."

**Level 2: Rehabilitating (Unstable Model) 🩹**
- **Criteria**: Fewer than 5 Hidden Hardcodes BUT contains Circular References or high-severity risks
- **Status**: "🩹 Maturity Level 2: Unstable Model"
- **Locked Features**: Goal Seek
- **AI Persona**: Focus on stability improvements and error fixes
- **Message Tone**: "Your model is improving. Let's fix these stability issues."

**Level 3: Healthy Athlete (Strategic Model) 🏆**
- **Criteria**: No Critical risks AND fewer than 3 High-severity risks
- **Status**: "🏆 Maturity Level 3: Strategic Model"
- **Unlocked Features**: Strategy Mode (Goal Seek, Scenario Planning)
- **AI Persona**: Focus on strategic optimization and scenario planning
- **Message Tone**: "Your model is healthy! Ready for strategic planning."

### Scoring Algorithm (Two-Phase Approach)

**Phase 1: Heuristic Scoring (Fast - 3 Second Target)**

Purpose: Provide immediate feedback on file upload to hook the user.

```python
def calculate_maturity_level_heuristic(model: ModelAnalysis) -> MaturityLevel:
    """
    Fast heuristic-based scoring for initial diagnosis.
    Target: Complete within 3 seconds of file upload.
    """
    # Count risks by severity (already available from quick scan)
    critical_count = len([r for r in model.risks if r.severity == "Critical"])
    high_count = len([r for r in model.risks if r.severity == "High"])
    
    # Heuristic 1: Critical risks present → Level 1 or 2
    if critical_count > 0:
        # Check if circular references (Critical severity)
        has_circular = any(r.risk_type == "Circular Reference" for r in model.risks)
        if has_circular:
            return MaturityLevel.LEVEL_2  # Unstable
        else:
            return MaturityLevel.LEVEL_1  # Static (likely hardcodes)
    
    # Heuristic 2: High hardcode count → Level 1
    hardcode_count = len([r for r in model.risks if r.risk_type == "Hidden Hardcode"])
    if hardcode_count > 5:
        return MaturityLevel.LEVEL_1  # Static
    
    # Heuristic 3: Some high risks → Level 2
    if high_count > 3:
        return MaturityLevel.LEVEL_2  # Unstable
    
    # Heuristic 4: Clean model → Level 3
    return MaturityLevel.LEVEL_3  # Healthy
```

**Phase 2: Deep Scoring (Accurate - Background)**

Purpose: Refine the score after full analysis completes.

```python
def calculate_maturity_level_deep(model: ModelAnalysis) -> MaturityLevel:
    """
    Accurate scoring after full dependency analysis.
    Uses detailed risk context and KPI involvement.
    """
    # Identify critical rows (KPI-related, high impact)
    critical_rows = identify_critical_rows(model)
    
    # Count hardcodes in critical rows specifically
    critical_hardcodes = count_hardcodes_in_critical_rows(model, critical_rows)
    
    # Level 1: High hardcode count in critical rows
    if critical_hardcodes > 5:
        return MaturityLevel.LEVEL_1
    
    # Level 2: Circular refs or high-severity risks
    has_circular = any(r.risk_type == "Circular Reference" for r in model.risks)
    high_severity_count = len([r for r in model.risks if r.severity in ["Critical", "High"]])
    
    if has_circular or high_severity_count > 3:
        return MaturityLevel.LEVEL_2
    
    # Level 3: Clean model
    return MaturityLevel.LEVEL_3
```

### Critical UX Constraint: "The Teasing Lock" (Psychology)

**Problem**: Simply disabling/graying out locked features doesn't drive engagement.

**Solution**: Make locked features visible, attractive, and clickable to trigger desire.

**Implementation**:

```python
def render_goal_seek_button(maturity_level: MaturityLevel, remaining_issues: int):
    """
    Render Goal Seek button with "teasing lock" UX.
    
    The button is ALWAYS visible and looks premium.
    Clicking it triggers different behavior based on maturity level.
    """
    if maturity_level == MaturityLevel.LEVEL_3:
        # Unlocked: Full functionality
        if st.button("🎯 Goal Seek (Strategy Mode)", type="primary"):
            launch_goal_seek_mode()
    else:
        # Locked: Teasing lock with premium appearance
        # Use custom CSS to make it look attractive (not grayed out)
        st.markdown("""
            <style>
            .locked-premium-button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                cursor: pointer;
                opacity: 0.9;
                border: 2px solid gold;
            }
            .locked-premium-button:hover {
                opacity: 1.0;
                transform: scale(1.02);
            }
            </style>
        """, unsafe_allow_html=True)
        
        if st.button("🔒 Goal Seek (Strategy Mode) - Premium", 
                     key="locked_goal_seek",
                     help="Unlock by fixing issues"):
            # Trigger popup with explicit unlock requirements
            st.warning(f"""
            ### 🏆 Unlock Strategy Mode
            
            **Current Level**: {maturity_level.display_name}
            
            **To unlock Goal Seek, you need to:**
            - Fix **{remaining_issues} more hardcodes** in critical rows
            - Reach Level 3: Strategic Model
            
            💡 **Tip**: Click "✨ Suggest Improvement" on the Top 3 Killers to get AI recommendations.
            
            **Progress**: {calculate_progress_percentage(maturity_level)}% complete
            """)
            
            # Show progress bar
            st.progress(calculate_progress_percentage(maturity_level) / 100)
```

**Key UX Elements**:

1. **Premium Appearance**: Button uses gradient, gold border, looks attractive
2. **Explicit Cost Display**: Popup shows exact requirements ("Fix 3 more hardcodes")
3. **Progress Visualization**: Progress bar shows how close user is to unlocking
4. **Actionable Guidance**: Direct link to AI Suggestion feature
5. **Psychological Hook**: User sees the feature, wants it, knows exactly what to do

### Algorithm Constraint: Speed over Accuracy (First Impressions)

**Requirement**: Initial maturity diagnosis must render within 3 seconds of file upload.

**Implementation Strategy**:

```python
def analyze_with_progressive_scoring(file_obj: BytesIO) -> ModelAnalysis:
    """
    Two-phase analysis: Fast heuristic first, deep analysis in background.
    """
    # Phase 1: Quick scan (3 second target)
    start_time = time.time()
    
    # Parse only essential data for heuristic scoring
    quick_model = quick_parse(file_obj)  # Minimal parsing
    quick_risks = quick_risk_scan(quick_model)  # Surface-level risk detection
    
    # Calculate heuristic maturity level
    heuristic_level = calculate_maturity_level_heuristic(quick_model)
    
    elapsed = time.time() - start_time
    print(f"[Maturity] Heuristic scoring completed in {elapsed:.2f}s")
    
    # Display initial results immediately
    display_maturity_badge(heuristic_level)
    display_quick_risks(quick_risks)
    
    # Phase 2: Deep analysis (background, can take longer)
    with st.spinner("Running deep analysis..."):
        full_model = full_parse(file_obj)  # Complete parsing with Virtual Fill
        full_risks = full_risk_detection(full_model)  # All risk types
        deep_level = calculate_maturity_level_deep(full_model)
        
        # Update display if level changed
        if deep_level != heuristic_level:
            st.info(f"Maturity level updated: {deep_level.display_name}")
            display_maturity_badge(deep_level)
    
    return full_model
```

**Optimization Techniques for 3-Second Target**:

1. **Lazy Parsing**: Parse only first 1,000 cells for heuristic
2. **Skip Virtual Fill**: Don't apply Virtual Fill in Phase 1
3. **Skip Dependency Graph**: Don't build full graph in Phase 1
4. **Simple Risk Detection**: Count only obvious risks (hardcodes, circular refs)
5. **Cache Results**: Cache heuristic results by file hash

### AI Persona Adjustment by Maturity Level

**Level 1 Persona: "Coach" (Decomposition Focus)**

```python
LEVEL_1_SYSTEM_PROMPT = """
Role: You are a Coach helping resurrect a "dead" Excel model.

Context: This model is static (Level 1). It contains many hardcoded values that prevent scenario analysis.

Your Goal: Convince the user to decompose hardcoded values into driver-based formulas.

Tone: Encouraging, motivational, focused on "bringing the model to life"

Example Output:
"このモデルは現在「静的」です。10,000という固定値を使用していますが、これを変数に分解することで、シナリオ分析が可能になります。

提案: 10,000 = [昨年実績] × [成長率]

この分解により、成長率を変更するだけで、複数のシナリオをテストできるようになります。"

DO NOT say: "This is an error" or "This is wrong"
DO say: "Let's make this dynamic" or "Let's add flexibility"
"""
```

**Level 2 Persona: "Mechanic" (Stability Focus)**

```python
LEVEL_2_SYSTEM_PROMPT = """
Role: You are a Mechanic fixing stability issues in a rehabilitating model.

Context: This model is improving (Level 2) but has stability issues like circular references or logic errors.

Your Goal: Help the user fix errors and improve model stability.

Tone: Technical, precise, focused on "fixing what's broken"

Example Output:
"このモデルは改善中ですが、循環参照が検出されました。

問題: セルA1がB1を参照し、B1がA1を参照しています。

解決策: 循環を断ち切るために、一方の参照を削除するか、別のセルに移動してください。"

DO say: "This causes instability" or "This creates calculation errors"
"""
```

**Level 3 Persona: "Strategist" (Optimization Focus)**

```python
LEVEL_3_SYSTEM_PROMPT = """
Role: You are a Strategist helping optimize a healthy model for advanced scenarios.

Context: This model is healthy (Level 3). The user is ready for strategic planning.

Your Goal: Suggest optimizations and advanced scenario planning techniques.

Tone: Strategic, forward-looking, focused on "what's possible now"

Example Output:
"おめでとうございます！モデルは健全です。戦略モードが利用可能になりました。

次のステップ:
1. ゴールシークを使用して、目標達成に必要な成長率を逆算
2. シナリオプランニングで、楽観・悲観・現実的なケースを比較
3. 感度分析で、最も影響力のあるドライバーを特定

提案: 売上目標を設定し、必要な顧客獲得数を自動計算してみましょう。"

DO say: "Now you can..." or "Let's explore scenarios"
"""
```

### Data Models

```python
from enum import Enum
from dataclasses import dataclass

class MaturityLevel(Enum):
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    
    @property
    def display_name(self) -> str:
        return {
            MaturityLevel.LEVEL_1: "🏥 Maturity Level 1: Static Model",
            MaturityLevel.LEVEL_2: "🩹 Maturity Level 2: Unstable Model",
            MaturityLevel.LEVEL_3: "🏆 Maturity Level 3: Strategic Model"
        }[self]
    
    @property
    def locked_features(self) -> List[str]:
        return {
            MaturityLevel.LEVEL_1: ["Goal Seek", "Scenario Planning"],
            MaturityLevel.LEVEL_2: ["Goal Seek"],
            MaturityLevel.LEVEL_3: []
        }[self]

@dataclass
class MaturityScore:
    """Represents the maturity assessment of a model"""
    level: MaturityLevel
    critical_hardcode_count: int
    circular_ref_count: int
    high_severity_count: int
    remaining_issues_to_next_level: int
    progress_percentage: float
    unlock_message: str
    scoring_method: str  # "heuristic" or "deep"
    
@dataclass
class UnlockRequirement:
    """Represents requirements to unlock a feature"""
    feature_name: str
    current_level: MaturityLevel
    required_level: MaturityLevel
    remaining_issues: int
    actionable_steps: List[str]
```

### Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

**Property 1: Maturity level monotonicity**
*For any* model, if issues are fixed (risk count decreases), the maturity level should never decrease (can stay same or increase)
**Validates: Requirements 19.1, 19.12**

**Property 2: Feature unlock consistency**
*For any* maturity level, the set of locked features should be a subset of the previous level's locked features (Level 1 locks ⊇ Level 2 locks ⊇ Level 3 locks)
**Validates: Requirements 19.5, 19.6**

**Property 3: Unlock requirement accuracy**
*For any* locked feature, the displayed remaining issues count should equal the actual number of issues preventing the next level
**Validates: Requirements 19.7**

**Property 4: AI persona consistency**
*For any* maturity level, all AI suggestions generated should use the persona defined for that level
**Validates: Requirements 19.8, 19.9, 19.10**

**Property 5: Heuristic scoring speed**
*For any* uploaded file, the heuristic maturity scoring should complete within 5 seconds (allowing 2s buffer from 3s target)
**Validates: Requirements 19.1, Performance**

**Property 6: Progress visualization accuracy**
*For any* maturity level, the progress percentage should accurately reflect the ratio of fixed issues to total issues required for next level
**Validates: Requirements 19.11**

**Property 7: Risk classification consistency**
*For any* detected risk, it should be classified into exactly one of the three triage categories (Fatal Error, Integrity Risk, or Structural Debt)
**Validates: Requirements 20.1, 20.2, 20.3, 20.4, 20.5, 20.6, 20.7, 20.8, 20.9**

**Property 8: Tab count accuracy**
*For any* risk analysis, the sum of risks across all three tabs should equal the total number of detected risks
**Validates: Requirements 20.13**

## 3-Tier Risk Triage System

### Overview

The 3-Tier Risk Triage System reorganizes risk display from technical severity to business impact, helping users prioritize "must fix" issues over "should fix" maintenance tasks.

### Classification Logic

```python
class RiskCategory(Enum):
    FATAL_ERROR = "fatal_error"          # Tab 1: Calculation Breakage
    INTEGRITY_RISK = "integrity_risk"    # Tab 2: Suspicion of Error
    STRUCTURAL_DEBT = "structural_debt"  # Tab 3: Maintenance Issues

def classify_risk(risk: RiskAlert) -> RiskCategory:
    """
    Classify risk by business impact.
    
    Fatal Errors: Model is broken or uncomputable
    Integrity Risks: Model runs but logic/values seem wrong (HIGHEST PRIORITY)
    Structural Debt: Works correctly but hard to maintain
    """
    
    # Tab 1: Fatal Errors (Calculation Breakage)
    if risk.risk_type in ["circular_reference", "phantom_link"]:
        return RiskCategory.FATAL_ERROR
    
    if risk.risk_type == "formula_error":
        # #REF!, #VALUE!, #DIV/0!, etc.
        return RiskCategory.FATAL_ERROR
    
    # Tab 2: Integrity Risks (Suspicion of Error) - HIGHEST PRIORITY
    if risk.risk_type == "inconsistent_formula":
        # Row pattern breaks - logic may be wrong
        return RiskCategory.INTEGRITY_RISK
    
    if risk.risk_type == "inconsistent_value":
        # Same label, different hardcoded values - update omission
        return RiskCategory.INTEGRITY_RISK
    
    if risk.risk_type == "logic_alert":
        # Semantic oddities from Logic Translator
        return RiskCategory.INTEGRITY_RISK
    
    # Tab 3: Structural Debt (Maintenance Issues)
    if risk.risk_type == "hidden_hardcode":
        # Only if values are CONSISTENT
        # If inconsistent, should be in Tab 2 as integrity risk
        if risk.metadata.get("is_consistent", True):
            return RiskCategory.STRUCTURAL_DEBT
        else:
            return RiskCategory.INTEGRITY_RISK
    
    if risk.risk_type == "merged_cell":
        return RiskCategory.STRUCTURAL_DEBT
    
    # Default to structural debt for unknown types
    return RiskCategory.STRUCTURAL_DEBT
```

### UI Design

**Tab Layout**:
```
┌─────────────────────────────────────────────────────────────┐
│  [Fatal Errors (3)] [Integrity Risks (7)] [Structural Debt (12)] │
└─────────────────────────────────────────────────────────────┘
```

**Tab 1: Fatal Errors** (Red Theme)
- Color: Red (#DC2626)
- Icon: 🔴
- Description: "The model is broken or uncomputable"
- Risks: Circular References, Phantom Links, Formula Errors
- Priority: CRITICAL - Must fix immediately

**Tab 2: Integrity Risks** (Orange/Yellow Theme) - **VISUALLY PROMINENT**
- Color: Orange (#F59E0B)
- Icon: ⚠️
- Description: "The model runs, but logic/values seem wrong"
- Risks: Inconsistent Formulas, Inconsistent Values, Logic Alerts
- Priority: HIGH - Hidden bugs live here
- Visual Treatment: Make this tab stand out with:
  - Slightly larger font
  - Pulsing border animation
  - Warning badge: "🔍 Review Priority"

**Tab 3: Structural Debt** (Blue/Gray Theme)
- Color: Blue (#3B82F6)
- Icon: 🔧
- Description: "Works correctly now, but hard to maintain"
- Risks: Consistent Hardcodes, Merged Cells
- Priority: MEDIUM - Technical debt

### Risk Table Format

Each tab displays risks in a consistent table format:

| Cell | Sheet | Context | Description | Actions |
|------|-------|---------|-------------|---------|
| A15 | Budget | Revenue @ Q1-2025 | Circular reference detected | [Trace] [Fix] |
| B23 | Forecast | COGS @ Q2-2025 | Inconsistent formula pattern | [Compare] [AI Suggest] |

**Columns**:
- **Cell**: Cell address (clickable to highlight in heatmap)
- **Sheet**: Sheet name
- **Context**: Row label @ Column label
- **Description**: Human-readable risk description
- **Actions**: Context-specific action buttons

### Implementation Components

**1. Risk Classifier**:
```python
class RiskTriageEngine:
    def __init__(self, risks: List[RiskAlert]):
        self.risks = risks
        self.fatal_errors = []
        self.integrity_risks = []
        self.structural_debt = []
    
    def classify_all(self):
        """Classify all risks into three categories"""
        for risk in self.risks:
            category = classify_risk(risk)
            if category == RiskCategory.FATAL_ERROR:
                self.fatal_errors.append(risk)
            elif category == RiskCategory.INTEGRITY_RISK:
                self.integrity_risks.append(risk)
            else:
                self.structural_debt.append(risk)
    
    def get_tab_counts(self) -> Dict[str, int]:
        """Return risk counts for tab labels"""
        return {
            "fatal": len(self.fatal_errors),
            "integrity": len(self.integrity_risks),
            "structural": len(self.structural_debt)
        }
```

**2. UI Renderer**:
```python
def render_risk_triage_tabs(triage_engine: RiskTriageEngine):
    """Render 3-tier triage tabs in Streamlit"""
    
    counts = triage_engine.get_tab_counts()
    
    tab1, tab2, tab3 = st.tabs([
        f"🔴 Fatal Errors ({counts['fatal']})",
        f"⚠️ Integrity Risks ({counts['integrity']})",
        f"🔧 Structural Debt ({counts['structural']})"
    ])
    
    with tab1:
        st.markdown("### The model is broken or uncomputable")
        render_risk_table(triage_engine.fatal_errors, "fatal")
    
    with tab2:
        # Make this tab visually prominent
        st.markdown("### 🔍 Review Priority: Hidden Bugs")
        st.markdown("The model runs, but logic/values seem wrong")
        render_risk_table(triage_engine.integrity_risks, "integrity")
    
    with tab3:
        st.markdown("### Works correctly, but hard to maintain")
        render_risk_table(triage_engine.structural_debt, "structural")
```

**3. Hardcode Consistency Checker**:
```python
def check_hardcode_consistency(risk: RiskAlert, all_risks: List[RiskAlert]) -> bool:
    """
    Check if a hardcode risk has consistent values across similar contexts.
    
    Returns True if consistent (Structural Debt), False if inconsistent (Integrity Risk)
    """
    if risk.risk_type != "hidden_hardcode":
        return True
    
    # Find all hardcodes with same row label
    same_label_risks = [
        r for r in all_risks 
        if r.risk_type == "hidden_hardcode" 
        and r.row_label == risk.row_label
    ]
    
    if len(same_label_risks) <= 1:
        return True  # Only one instance, assume consistent
    
    # Check if all values are the same
    values = [r.metadata.get("hardcoded_value") for r in same_label_risks]
    return len(set(values)) == 1  # True if all values identical
```

### Migration from Current System

**Current State**: Single "Detected Risks" list with severity-based sorting
**New State**: Three tabs with business-impact-based classification

**Migration Steps**:
1. Add `RiskCategory` enum to `models.py`
2. Implement `classify_risk()` function in `analyzer.py`
3. Create `RiskTriageEngine` class in `analyzer.py`
4. Update `app.py` to use tabbed interface instead of single list
5. Add consistency checking for hardcodes
6. Update risk display logic to use new classification

**Backward Compatibility**: 
- Keep existing `severity` field on `RiskAlert` for internal use
- Add new `category` field for triage classification
- Existing risk detection logic remains unchanged

## Professional Minimalism & Master-Detail Layout ("The Cockpit")

### Overview

Transform the UI from a "long-scroll website" to a "Bloomberg Terminal-style workstation" optimized for finance professionals who value speed and data density over decoration.

**Design Philosophy**: "Stop making a website. Start making a workstation."

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Compact Header                            │
│  File: budget.xlsx | Health: 72 | Level: 🩹 Rehabilitating      │
└─────────────────────────────────────────────────────────────────┘
┌──────────────────────────────┬──────────────────────────────────┐
│   MASTER PANEL (60%)         │   DETAIL PANEL (40%)             │
│                              │                                  │
│  ┌────────────────────────┐  │  ┌────────────────────────────┐ │
│  │  Risk Table            │  │  │  [No Selection]            │ │
│  │  ==================    │  │  │                            │ │
│  │  Location | Context    │  │  │  Select a risk from the    │ │
│  │  ---------|----------  │  │  │  table to inspect details  │ │
│  │  BS!E92   | Cash Bal   │  │  │                            │ │
│  │  PL!F24   | Revenue    │  │  └────────────────────────────┘ │
│  │  BS!G15   | AR Total   │  │                                  │
│  │  ...      | ...        │  │  [When Row Selected]             │
│  │                        │  │                                  │
│  │  [15-20 visible rows]  │  │  ┌────────────────────────────┐ │
│  │                        │  │  │  Logic X-Ray               │ │
│  │  Single-row selection  │  │  │  ─────────────────────     │ │
│  │  Sorted by severity    │  │  │  F4 (201.26)               │ │
│  │  Color: Red for danger │  │  │    ➔ F24 (Cost Calc)       │ │
│  │  No emojis in data     │  │  │    ➔ G30 (Total)           │ │
│  └────────────────────────┘  │  └────────────────────────────┘ │
│                              │                                  │
│                              │  ┌────────────────────────────┐ │
│                              │  │  The Cure (AI)             │ │
│                              │  │  ─────────────────────     │ │
│                              │  │  [✨ Suggest Fix]          │ │
│                              │  │                            │ │
│                              │  │  Refactoring Recipe:       │ │
│                              │  │  1. Extract to cell A1     │ │
│                              │  │  2. Reference from F4      │ │
│                              │  │  3. Add label "Growth %"   │ │
│                              │  └────────────────────────────┘ │
└──────────────────────────────┴──────────────────────────────────┘
```

### Key Design Decisions

**1. Split-View Layout (60/40)**
- **Rationale**: Maximize visible risks while providing adequate detail space
- **Master Panel (60%)**: Shows 15-20 risks above the fold at 1920x1080
- **Detail Panel (40%)**: Sufficient for dependency traces and AI suggestions
- **Responsive**: Adjusts to 50/50 on smaller screens (1280x720)

**2. Single-Row Selection**
- **Rationale**: Focus on one risk at a time, reduce cognitive load
- **Implementation**: `st.dataframe(selection_mode="single-row")`
- **Behavior**: Click row → detail panel updates immediately
- **State Management**: Store selected index in `st.session_state.selected_risk_index`

**3. Emoji-Free Data Display**
- **Rationale**: Emojis reduce information density and look unprofessional
- **Rule**: Emojis allowed in headers/labels, NEVER in data cells
- **Example**: 
  - ❌ "🔴 Circular Reference" in table cell
  - ✅ "Circular Reference" in table cell
  - ✅ "🔴 Fatal Errors (3)" in tab header

**4. Color Coding Strategy**
- **Rationale**: Color should signal danger, not decorate
- **Critical/High**: Bold red text (#DC2626) or light red background (#FEE2E2)
- **Medium/Low**: Default black/gray text (#374151)
- **No color**: Green, blue, yellow for non-danger states
- **Implementation**: Conditional formatting in dataframe

**5. Intelligent Sorting**
- **Primary Sort**: Severity (Critical → High → Medium → Low)
- **Secondary Sort**: Impact Count (descending)
- **Rationale**: Most dangerous risk always at top, no scrolling needed
- **Implementation**: Pre-sort before rendering table

### Component Design

#### 1. Master Panel: Risk Table

**Data Structure**:
```python
@dataclass
class RiskTableRow:
    """Represents a row in the master risk table"""
    location: str        # "Sheet!Cell" (e.g., "BS!E92")
    context: str         # "Row Label @ Col Label" (e.g., "Cash Balance @ Q1-2025")
    risk_type: str       # "Circular Reference", "Hidden Hardcode", etc.
    value: str           # Cell value or formula snippet
    severity: str        # "Critical", "High", "Medium", "Low"
    impact_count: int    # Number of dependent cells
    risk_object: RiskAlert  # Full risk object for detail panel
```

**Rendering Function**:
```python
def render_master_risk_table(risks: List[RiskAlert]) -> Optional[int]:
    """
    Render master risk table with single-row selection.
    
    Returns: Selected risk index (None if no selection)
    """
    # Sort risks by priority
    sorted_risks = sort_risks_by_priority(risks)
    
    # Convert to table rows
    table_data = []
    for risk in sorted_risks:
        table_data.append({
            "Location": f"{risk.sheet}!{risk.cell}",
            "Context": format_context(risk.row_label, risk.col_label),
            "Risk Type": risk.risk_type,  # NO EMOJI
            "Value": truncate_value(risk.details.get("value", ""), max_length=30),
            "Severity": risk.severity,
            "Impact": risk.details.get("impact_count", 0)
        })
    
    # Create DataFrame
    df = pd.DataFrame(table_data)
    
    # Apply conditional formatting
    def highlight_severity(row):
        if row["Severity"] in ["Critical", "High"]:
            return ["background-color: #FEE2E2; color: #DC2626"] * len(row)
        else:
            return [""] * len(row)
    
    styled_df = df.style.apply(highlight_severity, axis=1)
    
    # Render with single-row selection
    selection = st.dataframe(
        styled_df,
        selection_mode="single-row",
        use_container_width=True,
        height=600,  # Show 15-20 rows
        hide_index=True
    )
    
    # Return selected index
    if selection and len(selection["selection"]["rows"]) > 0:
        return selection["selection"]["rows"][0]
    return None
```

**Sorting Function**:
```python
def sort_risks_by_priority(risks: List[RiskAlert]) -> List[RiskAlert]:
    """
    Sort risks by severity (desc) then impact count (desc).
    
    Ensures most dangerous risk is always at top.
    """
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    
    return sorted(
        risks,
        key=lambda r: (
            severity_order.get(r.severity, 99),
            -r.details.get("impact_count", 0)
        )
    )
```

#### 2. Detail Panel: Inspection View

**Section A: Logic X-Ray**

Purpose: Show dependency trace in simple, readable format

```python
def render_logic_xray(risk: RiskAlert, model: ModelAnalysis):
    """
    Render dependency trace for selected risk.
    """
    st.markdown("### Logic X-Ray")
    st.markdown("---")
    
    # Get dependency trace
    trace = get_dependency_trace(risk, model)
    
    if not trace:
        st.info("No dependencies found")
        return
    
    # Render trace in simple text format
    st.markdown("**Dependency Chain:**")
    
    for i, cell_info in enumerate(trace):
        indent = "  " * i
        arrow = "➔ " if i > 0 else ""
        
        # Format: F4 (201.26) ➔ F24 (Cost Calculation)
        cell_ref = f"{cell_info.sheet}!{cell_info.address}"
        cell_value = format_value(cell_info.value)
        cell_label = cell_info.row_label or "Unlabeled"
        
        st.code(f"{indent}{arrow}{cell_ref} ({cell_value}) - {cell_label}")
    
    # Show impact count
    impact_count = len(trace) - 1
    if impact_count > 0:
        st.warning(f"⚠️ This cell affects {impact_count} other cells")
```

**Section B: The Cure (AI Suggestion)**

Purpose: Display AI-powered refactoring suggestions

```python
def render_ai_cure(risk: RiskAlert, model: ModelAnalysis):
    """
    Render AI suggestion section.
    """
    st.markdown("### The Cure")
    st.markdown("---")
    
    # Check if AI is enabled
    if not st.session_state.get("ai_enabled"):
        st.info("💡 Enable AI in sidebar to get refactoring suggestions")
        return
    
    # Suggest button
    if st.button("✨ Suggest Fix", key=f"ai_suggest_{risk.cell}"):
        with st.spinner("Analyzing..."):
            suggestion = generate_ai_suggestion(risk, model)
            st.session_state[f"suggestion_{risk.cell}"] = suggestion
    
    # Display suggestion if available
    suggestion = st.session_state.get(f"suggestion_{risk.cell}")
    if suggestion:
        st.markdown("**Refactoring Recipe:**")
        
        # Parse suggestion into steps
        steps = parse_suggestion_steps(suggestion)
        
        for i, step in enumerate(steps, 1):
            st.markdown(f"{i}. {step}")
        
        # Copy button
        if st.button("📋 Copy to Clipboard", key=f"copy_{risk.cell}"):
            st.write("Copied!")  # In real implementation, use clipboard API
```

#### 3. Professional Styling

**Custom CSS**:
```python
def inject_professional_css():
    """
    Inject custom CSS for Bloomberg Terminal aesthetic.
    """
    st.markdown("""
    <style>
    /* Remove Streamlit branding and padding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    
    /* Clean typography */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        font-size: 14px;
        line-height: 1.4;
    }
    
    /* Compact header */
    h1, h2, h3 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
    }
    
    /* Remove rounded corners */
    .stDataFrame, .stButton button {
        border-radius: 0px;
    }
    
    /* Sharp borders */
    .stDataFrame {
        border: 1px solid #E5E7EB;
    }
    
    /* Compact table rows */
    .stDataFrame tbody tr {
        height: 32px;
    }
    
    /* Detail panel sections */
    .detail-section {
        border-left: 3px solid #3B82F6;
        padding-left: 12px;
        margin-bottom: 16px;
    }
    
    /* Monospace for cell references */
    code {
        font-family: "SF Mono", Monaco, "Cascadia Code", monospace;
        font-size: 13px;
    }
    
    /* Remove decorative elements */
    .stProgress > div > div {
        background-color: #DC2626;  /* Red only */
    }
    </style>
    """, unsafe_allow_html=True)
```

### Data Flow

```
User uploads file
    ↓
Parse & analyze
    ↓
Sort risks by priority
    ↓
Render master-detail layout
    ↓
┌─────────────────────────────────────┐
│  Master Panel                       │
│  - Display sorted risk table        │
│  - Enable single-row selection      │
│  - Apply color coding               │
└─────────────────────────────────────┘
    ↓ (User clicks row)
┌─────────────────────────────────────┐
│  Detail Panel                       │
│  - Get selected risk from state     │
│  - Render Logic X-Ray               │
│  - Render AI Cure section           │
└─────────────────────────────────────┘
    ↓ (User clicks AI Suggest)
┌─────────────────────────────────────┐
│  AI Suggestion                      │
│  - Build context from risk          │
│  - Call AI API                      │
│  - Parse and display recipe         │
│  - Store in session state           │
└─────────────────────────────────────┘
```

### Performance Considerations

**1. Table Rendering**
- **Challenge**: Large risk lists (100+ rows) can slow rendering
- **Solution**: Use `st.dataframe()` with virtualization (built-in)
- **Target**: Render 100 rows in <500ms

**2. Selection Handling**
- **Challenge**: Re-rendering detail panel on every selection
- **Solution**: Use `st.session_state` to cache selected risk
- **Target**: Selection response time <100ms

**3. AI Suggestions**
- **Challenge**: API calls can take 2-5 seconds
- **Solution**: Show spinner, cache results in session state
- **Target**: Display cached suggestion instantly on re-selection

### Migration Strategy

**Phase 1: Parallel Implementation**
- Keep existing UI intact
- Build new master-detail layout in separate module
- Test with real users

**Phase 2: Feature Flag**
- Add toggle in settings: "Use Professional Layout"
- Allow users to switch between old and new UI
- Gather feedback

**Phase 3: Full Migration**
- Make professional layout default
- Remove old UI code
- Update documentation

### Correctness Properties

**Property 9: Risk sorting consistency**
*For any* list of risks, after sorting, all Critical risks should appear before High risks, and within the same severity level, risks with higher impact counts should appear first
**Validates: Requirements 21.7**

**Property 10: Selection state consistency**
*For any* selected risk, the detail panel should always display information for that specific risk and no other
**Validates: Requirements 21.8**

**Property 11: Color coding accuracy**
*For any* risk displayed in the table, if severity is Critical or High, the row should have red color coding; otherwise, it should use default colors
**Validates: Requirements 21.5, 21.6**

**Property 12: Data density maximization**
*For any* standard screen resolution (1920x1080), the master panel should display at least 15 visible risk rows without scrolling
**Validates: Requirements 21.12**

## Security Considerations

1. **API Key Storage**:
   - Store only in Streamlit session_state
   - Never persist to disk or logs
   - Clear on session end

2. **File Upload**:
   - Validate file size (max 50MB)
   - Validate file type (.xlsx only)
   - Scan for macros (reject if present)

3. **Data Privacy**:
   - No data sent to external services except AI API
   - User controls AI feature activation
   - Clear uploaded files after session

## Deployment Architecture

### MVP Deployment (Phase 1)

```
┌─────────────────────────────────────┐
│     Streamlit Cloud / Local         │
│  ┌───────────────────────────────┐  │
│  │   Streamlit App (Python)      │  │
│  │   - Parser                    │  │
│  │   - Analyzer                  │  │
│  │   - Diff Engine               │  │
│  │   - UI Components             │  │
│  └───────────────────────────────┘  │
│                                     │
│  Session State (In-Memory)          │
│  - Uploaded files                   │
│  - Analysis results                 │
│  - API keys                         │
└─────────────────────────────────────┘
         │                    │
         ▼                    ▼
   OpenAI API          Google Gemini API
```

### Future Production Deployment (Phase 2)

- Database for file history
- Redis for caching
- Background workers for large file processing
- Load balancer for multiple instances

---

## Critical Success Factors

### 1. Virtual Fill Robustness
- **Must handle**: All merged cell patterns in Japanese Excel
- **Must not**: Lose any cell data or dependencies
- **Must be**: Fast enough for real-time analysis (<60s for typical files)

### 2. Composite Key Accuracy
- **Must match**: 95%+ of rows correctly even with insertions/deletions
- **Must detect**: All logic changes vs input updates
- **Must provide**: Clear confidence scores for matches

### 3. Graceful Error Handling
- **Must never**: Show Python stack traces to users
- **Must always**: Provide actionable error messages in Japanese
- **Must continue**: Partial analysis even when some cells fail

These three factors are our competitive moat. If we execute them well, we win the Japanese FP&A market.

## Risk Review System with Session-Based Tracking

### Overview

The Risk Review System enables users to systematically work through detected risks by marking them as reviewed with checkboxes. The system provides real-time progress tracking and dynamic health score updates based on unreviewed risks only, creating a gamified experience that motivates users to address issues.

**Design Philosophy**: "Transform risk management from overwhelming to achievable through progressive disclosure and immediate feedback."

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Risk Review System                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Checkbox    │  │   Score      │  │   Filter     │     │
│  │  State Mgr   │  │  Calculator  │  │   Engine     │     │
│  │  (Session)   │  │  (Dynamic)   │  │              │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                    UI Components                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Checkbox    │  │  Progress    │  │  CSV Export  │     │
│  │  Column      │  │  Display     │  │  with State  │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

### Key Features

**1. Session-Based State Management**
- Review state stored in `st.session_state`
- No persistence across sessions (intentional - fresh start each time)
- Immediate UI updates on checkbox changes
- State keyed by risk unique identifier (sheet + cell + risk_type)

**2. Dynamic Health Score Calculation**
- Initial Score: Based on all detected risks
- Current Score: Based on unreviewed risks only
- Improvement Delta: Current - Initial (shows progress)
- Formula: `100 - (Unreviewed_Critical×10) - (Unreviewed_High×5) - (Unreviewed_Medium×2)`

**3. Visual Feedback**
- Reviewed risks: Grayed out with 0.6 opacity
- Unreviewed risks: Normal display
- Progress indicator: "確認済み: 45/131 (34%)"
- Color-coded improvement: Green for positive delta

**4. Filter System**
- "すべて" (All): Show all risks
- "未確認のみ" (Unreviewed Only): Show only unchecked risks
- "確認済みのみ" (Reviewed Only): Show only checked risks

**5. CSV Export with Review State**
- Includes "確認済み" column (TRUE/FALSE)
- Includes "エクスポート日時" column (timestamp)
- Audit trail for review progress

### Data Models

```python
@dataclass
class RiskReviewState:
    """Represents the review state for a single risk"""
    risk_id: str  # Unique identifier: f"{sheet}_{cell}_{risk_type}"
    is_reviewed: bool
    reviewed_at: Optional[datetime] = None
    
@dataclass
class ReviewProgress:
    """Represents overall review progress"""
    total_risks: int
    reviewed_count: int
    unreviewed_count: int
    percentage: float
    initial_score: int
    current_score: int
    improvement_delta: int
    
    @property
    def display_text(self) -> str:
        return f"確認済み: {self.reviewed_count}/{self.total_risks} ({self.percentage:.0f}%)"
```

### Implementation Components

#### 1. State Manager

```python
class RiskReviewStateManager:
    """Manages review state in session_state"""
    
    def __init__(self):
        if "risk_review_states" not in st.session_state:
            st.session_state.risk_review_states = {}
    
    def get_risk_id(self, risk: RiskAlert) -> str:
        """Generate unique identifier for a risk"""
        return f"{risk.sheet}_{risk.cell}_{risk.risk_type}"
    
    def is_reviewed(self, risk: RiskAlert) -> bool:
        """Check if a risk is marked as reviewed"""
        risk_id = self.get_risk_id(risk)
        return st.session_state.risk_review_states.get(risk_id, False)
    
    def set_reviewed(self, risk: RiskAlert, reviewed: bool):
        """Mark a risk as reviewed or unreviewed"""
        risk_id = self.get_risk_id(risk)
        st.session_state.risk_review_states[risk_id] = reviewed
    
    def get_reviewed_count(self, risks: List[RiskAlert]) -> int:
        """Count how many risks are reviewed"""
        return sum(1 for risk in risks if self.is_reviewed(risk))
    
    def get_unreviewed_risks(self, risks: List[RiskAlert]) -> List[RiskAlert]:
        """Get list of unreviewed risks"""
        return [risk for risk in risks if not self.is_reviewed(risk)]
    
    def clear_all(self):
        """Clear all review states (session end)"""
        st.session_state.risk_review_states = {}
```

#### 2. Dynamic Score Calculator

```python
class DynamicScoreCalculator:
    """Calculates health scores based on review state"""
    
    def calculate_initial_score(self, risks: List[RiskAlert]) -> int:
        """Calculate initial score based on all risks"""
        score = 100
        for risk in risks:
            if risk.severity == "Critical":
                score -= 10
            elif risk.severity == "High":
                score -= 5
            elif risk.severity == "Medium":
                score -= 2
        return max(0, score)
    
    def calculate_current_score(
        self, 
        risks: List[RiskAlert], 
        state_manager: RiskReviewStateManager
    ) -> int:
        """Calculate current score based on unreviewed risks only"""
        unreviewed_risks = state_manager.get_unreviewed_risks(risks)
        return self.calculate_initial_score(unreviewed_risks)
    
    def calculate_progress(
        self, 
        risks: List[RiskAlert], 
        state_manager: RiskReviewStateManager
    ) -> ReviewProgress:
        """Calculate complete review progress"""
        total = len(risks)
        reviewed = state_manager.get_reviewed_count(risks)
        unreviewed = total - reviewed
        percentage = (reviewed / total * 100) if total > 0 else 0
        
        initial_score = self.calculate_initial_score(risks)
        current_score = self.calculate_current_score(risks, state_manager)
        improvement_delta = current_score - initial_score
        
        return ReviewProgress(
            total_risks=total,
            reviewed_count=reviewed,
            unreviewed_count=unreviewed,
            percentage=percentage,
            initial_score=initial_score,
            current_score=current_score,
            improvement_delta=improvement_delta
        )
```

#### 3. UI Components

**Checkbox Column Renderer**:

```python
def render_risk_table_with_checkboxes(
    risks: List[RiskAlert],
    state_manager: RiskReviewStateManager,
    filter_mode: str = "all"
) -> pd.DataFrame:
    """
    Render risk table with checkbox column.
    
    Args:
        risks: List of risks to display
        state_manager: Review state manager
        filter_mode: "all", "unreviewed", or "reviewed"
    
    Returns:
        DataFrame with checkbox column and risk data
    """
    # Apply filter
    if filter_mode == "unreviewed":
        filtered_risks = [r for r in risks if not state_manager.is_reviewed(r)]
    elif filter_mode == "reviewed":
        filtered_risks = [r for r in risks if state_manager.is_reviewed(r)]
    else:
        filtered_risks = risks
    
    # Build table data
    table_data = []
    for risk in filtered_risks:
        is_reviewed = state_manager.is_reviewed(risk)
        
        table_data.append({
            "確認": is_reviewed,
            "場所": f"{risk.sheet}!{risk.cell}",
            "コンテキスト": format_context(risk.row_label, risk.col_label),
            "リスク種別": risk.risk_type,
            "重要度": risk.severity,
            "説明": risk.description
        })
    
    df = pd.DataFrame(table_data)
    
    # Apply visual feedback for reviewed risks
    def apply_reviewed_style(row):
        if row["確認"]:
            # Gray out reviewed risks
            return ["opacity: 0.6; color: #9CA3AF;"] * len(row)
        else:
            return [""] * len(row)
    
    styled_df = df.style.apply(apply_reviewed_style, axis=1)
    
    return styled_df
```

**Progress Display**:

```python
def render_progress_display(progress: ReviewProgress):
    """
    Render progress display with scores and improvement delta.
    """
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="初期スコア",
            value=progress.initial_score,
            delta=None
        )
    
    with col2:
        st.metric(
            label="現在スコア",
            value=progress.current_score,
            delta=f"+{progress.improvement_delta}" if progress.improvement_delta > 0 else None,
            delta_color="normal" if progress.improvement_delta > 0 else "off"
        )
    
    with col3:
        st.metric(
            label="確認済み",
            value=f"{progress.reviewed_count}/{progress.total_risks}",
            delta=f"{progress.percentage:.0f}%"
        )
    
    with col4:
        st.metric(
            label="未確認",
            value=progress.unreviewed_count,
            delta=None
        )
    
    # Progress bar
    st.progress(progress.percentage / 100)
    
    # Encouraging message
    if progress.percentage == 100:
        st.success("🎉 すべてのリスクを確認しました！")
    elif progress.percentage >= 50:
        st.info(f"💪 あと{progress.unreviewed_count}個です！")
```

**Filter Controls**:

```python
def render_filter_controls() -> str:
    """
    Render filter radio buttons.
    
    Returns:
        Selected filter mode: "all", "unreviewed", or "reviewed"
    """
    filter_mode = st.radio(
        "表示フィルター",
        options=["all", "unreviewed", "reviewed"],
        format_func=lambda x: {
            "all": "すべて",
            "unreviewed": "未確認のみ",
            "reviewed": "確認済みのみ"
        }[x],
        horizontal=True
    )
    
    return filter_mode
```

**CSV Export with Review State**:

```python
def export_risks_with_review_state(
    risks: List[RiskAlert],
    state_manager: RiskReviewStateManager
) -> str:
    """
    Export risks to CSV with review state column.
    
    Returns:
        CSV string with review state
    """
    export_data = []
    
    for risk in risks:
        is_reviewed = state_manager.is_reviewed(risk)
        
        export_data.append({
            "確認済み": "TRUE" if is_reviewed else "FALSE",
            "シート": risk.sheet,
            "セル": risk.cell,
            "コンテキスト": format_context(risk.row_label, risk.col_label),
            "リスク種別": risk.risk_type,
            "重要度": risk.severity,
            "説明": risk.description,
            "エクスポート日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    df = pd.DataFrame(export_data)
    return df.to_csv(index=False, encoding="utf-8-sig")
```

#### 4. Main Integration

```python
def render_risk_review_interface(risks: List[RiskAlert]):
    """
    Main function to render complete risk review interface.
    """
    # Initialize managers
    state_manager = RiskReviewStateManager()
    score_calculator = DynamicScoreCalculator()
    
    # Calculate progress
    progress = score_calculator.calculate_progress(risks, state_manager)
    
    # Render progress display
    st.markdown("### 📊 レビュー進捗")
    render_progress_display(progress)
    
    st.markdown("---")
    
    # Render filter controls
    filter_mode = render_filter_controls()
    
    # Render risk table with checkboxes
    st.markdown("### 📋 リスク一覧")
    
    styled_df = render_risk_table_with_checkboxes(
        risks, 
        state_manager, 
        filter_mode
    )
    
    # Display table with checkbox interaction
    edited_df = st.data_editor(
        styled_df,
        column_config={
            "確認": st.column_config.CheckboxColumn(
                "確認",
                help="このリスクを確認済みにする",
                default=False
            )
        },
        disabled=["場所", "コンテキスト", "リスク種別", "重要度", "説明"],
        hide_index=True,
        use_container_width=True
    )
    
    # Update state based on checkbox changes
    for idx, row in edited_df.iterrows():
        risk = risks[idx]
        new_state = row["確認"]
        state_manager.set_reviewed(risk, new_state)
    
    # Export button
    st.markdown("---")
    csv_data = export_risks_with_review_state(risks, state_manager)
    
    st.download_button(
        label="📥 CSVエクスポート（確認状態を含む）",
        data=csv_data,
        file_name=f"risk_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
```

### User Flow

```
User uploads file
    ↓
System analyzes and detects risks
    ↓
Display initial score: 65/100 (131 risks)
    ↓
┌─────────────────────────────────────┐
│  Progress Display                   │
│  - Initial Score: 65                │
│  - Current Score: 65                │
│  - Reviewed: 0/131 (0%)             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Risk Table with Checkboxes         │
│  [☐] BS!E92 | Cash Balance | ...   │
│  [☐] PL!F24 | Revenue | ...        │
│  [☐] BS!G15 | AR Total | ...       │
└─────────────────────────────────────┘
    ↓ (User checks first risk)
┌─────────────────────────────────────┐
│  Progress Display (Updated)         │
│  - Initial Score: 65                │
│  - Current Score: 70 (+5)           │
│  - Reviewed: 1/131 (1%)             │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Risk Table (Visual Feedback)       │
│  [☑] BS!E92 | Cash Balance | ...   │  ← Grayed out
│  [☐] PL!F24 | Revenue | ...        │
│  [☐] BS!G15 | AR Total | ...       │
└─────────────────────────────────────┘
    ↓ (User continues reviewing)
Progress updates in real-time
    ↓ (User reviews all risks)
┌─────────────────────────────────────┐
│  🎉 すべてのリスクを確認しました！   │
│  - Initial Score: 65                │
│  - Current Score: 100 (+35)         │
│  - Reviewed: 131/131 (100%)         │
└─────────────────────────────────────┘
    ↓
User exports CSV with review state
```

### Performance Considerations

**1. State Management**
- **Challenge**: Large risk lists (100+ risks) with checkbox state
- **Solution**: Use dictionary lookup by risk_id (O(1) access)
- **Target**: State update <50ms

**2. Real-Time Score Calculation**
- **Challenge**: Recalculate score on every checkbox change
- **Solution**: Incremental calculation (only update delta)
- **Target**: Score update <100ms

**3. Table Rendering**
- **Challenge**: Re-render table on every state change
- **Solution**: Use Streamlit's built-in optimization (st.data_editor)
- **Target**: Render 100 rows <500ms

### Correctness Properties

**Property 13: Review state consistency**
*For any* risk, if it is marked as reviewed, it should not contribute to the current health score calculation
**Validates: Requirements 22.2, 22.4, 22.11**

**Property 14: Progress calculation accuracy**
*For any* set of risks, the review progress percentage should equal (reviewed_count / total_count) × 100
**Validates: Requirements 22.5**

**Property 15: Filter correctness**
*For any* filter mode, the displayed risks should match the filter criteria exactly (all reviewed, all unreviewed, or all risks)
**Validates: Requirements 22.7, 22.8, 22.9**

**Property 16: CSV export completeness**
*For any* CSV export, it should include all risks with their current review state and a timestamp
**Validates: Requirements 22.6**

**Property 17: Session isolation**
*For any* new session, the review state should be empty (no persistence from previous sessions)
**Validates: Requirements 22.10**

**Property 18: Score improvement monotonicity**
*For any* risk marked as reviewed, the current score should never decrease (can stay same or increase)
**Validates: Requirements 22.11, 22.12**

### Integration with Existing System

**1. Master-Detail Layout Integration**
- Add checkbox column as leftmost column in master panel
- Maintain single-row selection for detail panel
- Update detail panel to show review state

**2. Triage System Integration**
- Apply review system to all three tabs (Fatal, Integrity, Structural)
- Calculate separate progress for each tab
- Allow filtering within each tab

**3. Health Score Integration**
- Replace static health score with dynamic score
- Show both initial and current scores
- Display improvement delta prominently

**4. Export Integration**
- Extend existing CSV export to include review state
- Add timestamp column
- Maintain backward compatibility

### Migration Strategy

**Phase 1: Add Checkbox Column**
- Add checkbox column to existing risk table
- Implement state management
- No score changes yet

**Phase 2: Dynamic Score Calculation**
- Implement current score calculation
- Display both initial and current scores
- Add improvement delta

**Phase 3: Filter System**
- Add filter controls
- Implement filter logic
- Test with large risk lists

**Phase 4: CSV Export Enhancement**
- Add review state column to export
- Add timestamp column
- Test export/import workflow

### Testing Strategy

**Unit Tests**:
1. Test state manager get/set operations
2. Test score calculator with various risk combinations
3. Test filter logic for all three modes
4. Test CSV export format

**Integration Tests**:
1. Test checkbox interaction updates state correctly
2. Test score updates in real-time
3. Test filter changes update table correctly
4. Test export includes all required columns

**Property Tests**:
1. Test review state consistency property
2. Test progress calculation accuracy property
3. Test filter correctness property
4. Test score improvement monotonicity property

### Security Considerations

**1. State Isolation**
- Review state stored per session only
- No cross-session data leakage
- Clear state on session end

**2. CSV Export**
- No sensitive data in export (only risk metadata)
- Timestamp for audit trail
- UTF-8 encoding for Japanese characters

**3. Performance Limits**
- Limit risk count to 1000 per session
- Warn user if approaching limit
- Suggest filtering to reduce load
