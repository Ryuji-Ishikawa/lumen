# Explanation Mode - Design Document

**Project**: Lumen v1.1  
**Feature**: Explanation Mode (Causal Tree + Period Analysis + Evidence Memo)  
**Date**: 2025-12-17  
**Target Launch**: 2025-01-15  
**Status**: Design Phase

---

## 1. Overview

Explanation Mode は、Excel の事業計画・予算ワークブックの「なぜこの数字なのか？」を説明するための新機能です。既存の Risk Review モードと並列で動作し、因果ツリー、実績/予測の境界分析、エビデンスメモを提供します。

### 1.1 Core Value Proposition

- **Causal Tree**: KPI を構成する要素を階層的に可視化
- **Period Analysis**: 実績/予測の境界を自動推論 + 手動調整
- **Evidence Memo**: 各要素に説明メモを添付・永続化

### 1.2 Design Principles

1. **Read-Only**: Excel ファイルは絶対に変更しない
2. **Incremental**: 既存の Risk Review 機能を壊さない
3. **Transparent**: AI 使用時は明示的にバッジ表示
4. **Persistent**: 分析結果は JSON で保存（監査証跡）

---

## 2. Architecture

### 2.1 System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit UI Layer                    │
├──────────────┬──────────────────────────────────────────┤
│ Risk Review  │  Explanation Mode (NEW)                  │
│ (Existing)   │  ├─ Target Selection                     │
│              │  ├─ Causal Tree (AgGrid)                 │
│              │  ├─ Period Inference Engine              │
│              │  ├─ Global Date Override                 │
│              │  └─ Evidence Memo Manager                │
├──────────────┴──────────────────────────────────────────┤
│              Analysis Engine (Extended)                  │
│  ├─ Factor Detector (NEW)                               │
│  ├─ Causal Tree Builder (NEW)                           │
│  ├─ Period Attribute Analyzer (NEW)                     │
│  └─ Existing: Risk Detector, Context Labeling           │
├──────────────────────────────────────────────────────────┤
│              Data Layer                                  │
│  ├─ ModelAnalysis (Extended)                            │
│  ├─ Factor, CausalNode, PeriodAttribute (NEW)           │
│  └─ Evidence Memo Storage (JSON)                        │
├──────────────────────────────────────────────────────────┤
│              Excel Parser (Existing)                     │
│  └─ openpyxl + Dependency Graph                         │
└──────────────────────────────────────────────────────────┘
```

### 2.2 Data Flow

```
1. Excel Upload
   ↓
2. Parse (Existing: cells, formulas, dependencies)
   ↓
3. Risk Analysis (Existing: 9 risk types)
   ↓
4. Factor Detection (NEW)
   ├─ Identify leaf nodes (no formula or simple reference)
   ├─ Apply Context Labeling
   └─ Mark as Factor if referenced by important calculations
   ↓
5. Period Inference (NEW)
   ├─ Column Majority Vote (hardcode vs formula)
   ├─ Header Keywords (Act, Est, 実績, 予測)
   └─ Date Fallback (< Current - 3 months)
   ↓
6. Causal Tree Construction (NEW)
   ├─ Select Target (KPI candidates)
   ├─ Build tree from dependency graph
   └─ Translate formulas to readable equations
   ↓
7. UI Rendering
   ├─ AgGrid Tree (expandable hierarchy)
   ├─ Global Date Override (period boundary adjustment)
   └─ Evidence Memo (load from JSON, edit, save)
```

---

## 3. Data Models

### 3.1 Factor (NEW)

```python
@dataclass
class Factor:
    """
    A Factor is a leaf node in the causal tree.
    It represents an input value that cannot or need not be traced further.
    """
    id: str  # Format: "Sheet1!H10" or "Sheet1!Row10"
    sheet: str
    address: str  # Cell address or "Row10" for series
    label: str  # From Context Labeling, or "[No Label] (H10)"
    factor_type: str  # "scalar" or "series"
    
    # For series factors
    series_range: Optional[str] = None  # e.g., "H10:BW10"
    
    # CRITICAL: Numeric data storage
    values: Dict[int, Any] = field(default_factory=dict)  # Key: column_index, Value: cell value
    formatted_values: Dict[int, str] = field(default_factory=dict)  # Excel display format applied
    
    # Period attributes (per column for series)
    period_attrs: Dict[int, PeriodAttribute] = field(default_factory=dict)  # Key: column_index
    
    # User flags
    is_fixed: bool = False  # Exclude from sensitivity analysis
    is_confirmed: bool = False  # User confirmed this is a Factor
    
    # Evidence
    evidence_memo: Optional[str] = None
```

### 3.2 CausalNode (NEW)

```python
@dataclass
class CausalNode:
    """
    A node in the causal tree.
    Can be either a Factor (leaf) or a Calculated Node (has formula).
    """
    id: str  # Format: "Sheet1!C10"
    sheet: str
    address: str
    label: str  # From Context Labeling
    
    # Node type
    is_factor: bool
    factor: Optional[Factor] = None
    
    # Formula info
    formula: Optional[str] = None
    formula_readable: Optional[str] = None  # From Logic Translator
    
    # CRITICAL: Numeric data storage (for calculated nodes)
    values: Dict[int, Any] = field(default_factory=dict)  # Key: column_index, Value: calculated value
    formatted_values: Dict[int, str] = field(default_factory=dict)  # Excel display format applied
    
    # Tree structure
    children: List['CausalNode'] = field(default_factory=list)
    depth: int = 0
    
    # Display state
    is_expanded: bool = False
    is_untraceable: bool = False
    untraceable_reason: Optional[str] = None
    
    # Semantic warning
    has_semantic_warning: bool = False
    semantic_warning_msg: Optional[str] = None
```

### 3.3 PeriodAttribute (NEW)

```python
@dataclass
class PeriodAttribute:
    """
    Period classification for a specific column.
    Attached to Factor × Column.
    """
    column_index: int  # 0-based column index
    column_label: str  # e.g., "2024/01", "Q1 2024"
    
    # Classification
    period_type: str  # "ACTUAL", "FORECAST", "UNCERTAIN"
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    
    # Inference source
    inference_method: str  # "header_keyword", "column_majority", "date_fallback", "user_override"
    inference_details: Dict[str, Any] = field(default_factory=dict)
    
    # User override
    is_user_overridden: bool = False
```

### 3.4 EvidenceMemo (NEW)

```python
@dataclass
class EvidenceMemo:
    """
    User-attached memo for a Factor or Node.
    Persisted to [ExcelName].lumen.json
    """
    factor_id: str  # "Sheet1!H10"
    factor_label: str
    memo_text: str
    created_at: str  # ISO 8601
    updated_at: str  # ISO 8601
```

### 3.5 ModelAnalysis (Extended)

```python
@dataclass
class ModelAnalysis:
    # Existing fields
    filename: str
    sheets: List[str]
    cells: Dict[str, CellInfo]
    risks: List[RiskAlert]
    health_score: int
    dependency_graph: nx.DiGraph
    merged_ranges: Dict[str, List[str]]
    maturity_level: Optional[str] = None
    
    # NEW: Explanation Mode data
    factors: List[Factor] = field(default_factory=list)
    causal_trees: Dict[str, CausalNode] = field(default_factory=dict)  # Key: target_id
    global_date_override: Optional[str] = None  # "2024-09"
    evidence_memos: List[EvidenceMemo] = field(default_factory=list)
```

---

## 4. Components

### 4.1 Factor Detector

**Purpose**: Identify leaf nodes (Factors) in the dependency graph.

**Algorithm**:
```python
def detect_factors(model: ModelAnalysis) -> List[Factor]:
    factors = []
    
    for cell_key, cell_info in model.cells.items():
        # Condition 1: No formula OR simple reference (e.g., =Sheet1!A10)
        if not cell_info.formula or is_simple_reference(cell_info.formula):
            
            # Condition 2: Has Context Label OR is referenced by important calculations
            label = get_context_label(cell_info)
            if not label:
                if not is_referenced_by_important_calc(cell_key, model):
                    continue
                label = f"[No Label] ({cell_info.address})"
            
            # Condition 3: Has downstream dependencies
            if model.dependency_graph.out_degree(cell_key) == 0:
                continue
            
            # Determine factor type
            factor_type = detect_factor_type(cell_key, model)
            
            factors.append(Factor(
                id=cell_key,
                sheet=cell_info.sheet,
                address=cell_info.address,
                label=label,
                factor_type=factor_type
            ))
    
    return factors
```

**Key Functions**:
- `is_simple_reference()`: Check if formula is just `=Sheet1!A10`
- `is_referenced_by_important_calc()`: Check if downstream has high impact
- `detect_factor_type()`: Determine "scalar" vs "series"

---

### 4.2 Period Inference Engine

**Purpose**: Classify each column as ACTUAL / FORECAST / UNCERTAIN.

**Algorithm: Column Majority Vote**

```python
def infer_period_attributes(model: ModelAnalysis) -> Dict[int, PeriodAttribute]:
    """
    For each column, determine period type based on majority vote of constituent cells.
    """
    period_attrs = {}
    
    # Get all columns with data
    columns = get_all_columns(model)
    
    for col_idx in columns:
        col_label = get_column_header(col_idx, model)
        
        # Priority 1: Header Keywords
        if has_keyword(col_label, ["Act", "実績", "Actual"]):
            period_attrs[col_idx] = PeriodAttribute(
                column_index=col_idx,
                column_label=col_label,
                period_type="ACTUAL",
                confidence="HIGH",
                inference_method="header_keyword"
            )
            continue
        
        if has_keyword(col_label, ["Est", "Plan", "予測", "Forecast"]):
            period_attrs[col_idx] = PeriodAttribute(
                column_index=col_idx,
                column_label=col_label,
                period_type="FORECAST",
                confidence="HIGH",
                inference_method="header_keyword"
            )
            continue
        
        # Priority 2: Column Majority Vote
        constituent_cells = get_constituent_cells(col_idx, model)
        hardcode_count = sum(1 for c in constituent_cells if not c.formula)
        formula_count = len(constituent_cells) - hardcode_count
        
        if hardcode_count > formula_count:
            period_type = "ACTUAL"
            confidence = "MEDIUM"
        elif formula_count > hardcode_count:
            period_type = "FORECAST"
            confidence = "MEDIUM"
        else:
            period_type = "UNCERTAIN"
            confidence = "LOW"
        
        # Priority 3: Date Fallback
        if period_type == "UNCERTAIN":
            col_date = parse_date_from_header(col_label)
            if col_date and col_date < (datetime.now() - timedelta(days=90)):
                period_type = "ACTUAL"
                confidence = "LOW"
                inference_method = "date_fallback"
        
        period_attrs[col_idx] = PeriodAttribute(
            column_index=col_idx,
            column_label=col_label,
            period_type=period_type,
            confidence=confidence,
            inference_method="column_majority"
        )
    
    return period_attrs
```

---

### 4.3 Causal Tree Builder

**Purpose**: Construct hierarchical tree from dependency graph.

**Algorithm**:
```python
def build_causal_tree(target_id: str, model: ModelAnalysis, max_depth: int = 1) -> CausalNode:
    """
    Build causal tree starting from target node.
    Initial depth = 1 (target + direct precedents).
    """
    target_cell = model.cells[target_id]
    
    # Create root node
    root = CausalNode(
        id=target_id,
        sheet=target_cell.sheet,
        address=target_cell.address,
        label=get_context_label(target_cell),
        is_factor=is_factor(target_id, model.factors),
        formula=target_cell.formula,
        formula_readable=translate_formula(target_cell.formula, model),
        depth=0
    )
    
    # Check if untraceable
    if is_untraceable(target_cell, model):
        root.is_untraceable = True
        root.untraceable_reason = get_untraceable_reason(target_cell, model)
        return root
    
    # Build children (precedents)
    if max_depth > 0:
        precedents = model.dependency_graph.predecessors(target_id)
        for prec_id in precedents:
            child = build_causal_tree(prec_id, model, max_depth - 1)
            child.depth = root.depth + 1
            root.children.append(child)
    
    return root
```

---

### 4.4 Global Date Override

**Purpose**: Allow user to set a single date boundary for all UNCERTAIN periods.

**UI Component**:
```python
def render_global_date_override(model: ModelAnalysis):
    """
    Render date picker at top of Explanation Mode.
    """
    st.markdown("### 📅 Global Actual End Date")
    st.caption("Set the boundary between Actual and Forecast periods")
    
    # Date picker
    override_date = st.date_input(
        "Actual data ends on:",
        value=datetime(2024, 9, 30),
        key="global_date_override"
    )
    
    if st.button("Apply to All Uncertain Periods"):
        apply_global_override(model, override_date)
        st.success(f"Applied: Columns ≤ {override_date} → ACTUAL, Columns > {override_date} → FORECAST")
```

**Logic**:
```python
def apply_global_override(model: ModelAnalysis, cutoff_date: datetime):
    """
    Override all UNCERTAIN period attributes based on cutoff date.
    """
    for factor in model.factors:
        for col_idx, period_attr in factor.period_attrs.items():
            if period_attr.period_type != "UNCERTAIN":
                continue  # Don't override definite classifications
            
            col_date = parse_date_from_header(period_attr.column_label)
            if not col_date:
                continue  # Can't parse date, skip
            
            if col_date <= cutoff_date:
                period_attr.period_type = "ACTUAL"
            else:
                period_attr.period_type = "FORECAST"
            
            period_attr.is_user_overridden = True
            period_attr.inference_method = "user_override"
    
    model.global_date_override = cutoff_date.strftime("%Y-%m")
```

---

### 4.5 Evidence Memo Manager

**Purpose**: Persist user memos to JSON file.

**JSON Structure**:
```json
{
  "excel_file": "Business_Plan.xlsx",
  "analysis_date": "2025-01-10T14:30:00",
  "global_date_override": "2024-09",
  "memos": [
    {
      "factor_id": "Sheet1!H10",
      "factor_label": "売上",
      "memo_text": "Q4に大型案件が確定したため上方修正",
      "created_at": "2025-01-10T14:35:00",
      "updated_at": "2025-01-10T15:20:00"
    }
  ]
}
```

**Save/Load Functions**:
```python
def save_evidence_memos(model: ModelAnalysis, excel_path: str):
    """
    Save memos to [ExcelName].lumen.json in same directory.
    """
    json_path = excel_path.replace(".xlsx", ".lumen.json")
    
    data = {
        "excel_file": os.path.basename(excel_path),
        "analysis_date": datetime.now().isoformat(),
        "global_date_override": model.global_date_override,
        "memos": [
            {
                "factor_id": memo.factor_id,
                "factor_label": memo.factor_label,
                "memo_text": memo.memo_text,
                "created_at": memo.created_at,
                "updated_at": memo.updated_at
            }
            for memo in model.evidence_memos
        ]
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_evidence_memos(excel_path: str) -> List[EvidenceMemo]:
    """
    Load memos from [ExcelName].lumen.json if exists.
    """
    json_path = excel_path.replace(".xlsx", ".lumen.json")
    
    if not os.path.exists(json_path):
        return []
    
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    return [
        EvidenceMemo(
            factor_id=m["factor_id"],
            factor_label=m["factor_label"],
            memo_text=m["memo_text"],
            created_at=m["created_at"],
            updated_at=m["updated_at"]
        )
        for m in data.get("memos", [])
    ]
```

---

## 5. UI Components

### 5.1 Mode Toggle

```python
def render_mode_toggle():
    """
    Top-level segmented control to switch between modes.
    """
    mode = st.radio(
        "Mode",
        ["Risk Review", "Explanation Mode"],
        horizontal=True,
        key="app_mode"
    )
    return mode
```

### 5.2 Target Selection

```python
def render_target_selection(model: ModelAnalysis) -> Optional[str]:
    """
    Smart dropdown for KPI selection.
    """
    # Get KPI candidates
    candidates = get_kpi_candidates(model)
    
    # Filter: Must contain "売上" or "Revenue"
    candidates = [c for c in candidates if "売上" in c.label or "Revenue" in c.label.lower()]
    
    # Limit to top 10
    candidates = candidates[:10]
    
    if not candidates:
        st.warning("No KPI candidates found")
        return None
    
    # Dropdown
    selected = st.selectbox(
        "Select Target Metric",
        options=[c.id for c in candidates],
        format_func=lambda x: get_label_for_id(x, candidates),
        key="target_metric"
    )
    
    return selected
```

### 5.3 Causal Tree (AgGrid) - Left Panel

**Design Philosophy**: Focus on structure visualization, not time-series data.

```python
def render_causal_tree(root: CausalNode, model: ModelAnalysis):
    """
    Render tree using Streamlit-AgGrid in Tree Data mode.
    
    Column Strategy:
    - [Label]: Factor/Node name
    - [Formula]: Readable equation
    - [Representative Value]: Single value (latest actual, total, or most recent)
    
    NO monthly columns to avoid horizontal scroll and maintain clarity.
    """
    from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
    
    # Convert tree to flat list with hierarchy info
    rows = flatten_tree(root)
    
    # Build AgGrid options
    gb = GridOptionsBuilder.from_dataframe(pd.DataFrame(rows))
    gb.configure_default_column(editable=False, groupable=True)
    
    # Column configuration (SIMPLE - no monthly expansion)
    gb.configure_column("label", headerName="Factor/Node", width=300)
    gb.configure_column("formula_readable", headerName="Formula", width=400)
    gb.configure_column("representative_value", headerName="Value", width=120)
    
    # Enable tree data mode
    gb.configure_grid_options(
        treeData=True,
        getDataPath=lambda row: row['path'],  # Hierarchy path
        autoGroupColumnDef={
            "headerName": "Structure",
            "minWidth": 300,
            "cellRendererParams": {"suppressCount": True}
        }
    )
    
    grid_options = gb.build()
    
    # Render
    grid_response = AgGrid(
        pd.DataFrame(rows),
        gridOptions=grid_options,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        allow_unsafe_jscode=True,
        height=600
    )
    
    return grid_response

def flatten_tree(node: CausalNode, path: List[str] = None) -> List[Dict]:
    """
    Convert tree to flat list for AgGrid.
    """
    if path is None:
        path = []
    
    current_path = path + [node.label]
    
    # Get representative value (latest actual or total)
    representative_value = get_representative_value(node)
    
    row = {
        "id": node.id,
        "label": node.label,
        "formula_readable": node.formula_readable or "",
        "representative_value": representative_value,
        "path": current_path,
        "depth": node.depth,
        "is_factor": node.is_factor,
        "has_warning": node.has_semantic_warning
    }
    
    rows = [row]
    
    # Add children
    for child in node.children:
        rows.extend(flatten_tree(child, current_path))
    
    return rows

def get_representative_value(node: CausalNode) -> str:
    """
    Get a single representative value for display in tree.
    
    Priority:
    1. Latest ACTUAL value (most recent confirmed data)
    2. Total/Sum (if series)
    3. Most recent value (any period)
    """
    if not node.values:
        return "-"
    
    # Try to find latest ACTUAL
    actual_cols = [
        col_idx for col_idx, period_attr in node.factor.period_attrs.items()
        if period_attr.period_type == "ACTUAL"
    ] if node.is_factor and node.factor else []
    
    if actual_cols:
        latest_actual_col = max(actual_cols)
        if latest_actual_col in node.formatted_values:
            return node.formatted_values[latest_actual_col]
        if latest_actual_col in node.values:
            return str(node.values[latest_actual_col])
    
    # Fallback: Most recent value
    if node.formatted_values:
        latest_col = max(node.formatted_values.keys())
        return node.formatted_values[latest_col]
    
    if node.values:
        latest_col = max(node.values.keys())
        return str(node.values[latest_col])
    
    return "-"
```

### 5.4 Detail Panel (Right) - Time Series & Evidence

**Design Philosophy**: Show detailed time-series data and divergence analysis for selected node.

```python
def render_detail_panel(selected_node: CausalNode, model: ModelAnalysis):
    """
    Right panel: Time-series view + Evidence memo.
    
    Components:
    1. Time-Series Chart/Table (NEW)
    2. Divergence Analysis (Actual vs Forecast)
    3. Evidence Memo Editor
    """
    if not selected_node:
        st.info("Select a node from the tree to view details")
        return
    
    st.markdown(f"### 📊 {selected_node.label}")
    
    # Section 1: Time-Series View
    render_time_series_view(selected_node, model)
    
    st.markdown("---")
    
    # Section 2: Evidence Memo
    render_evidence_memo_editor(selected_node, model)

def render_time_series_view(node: CausalNode, model: ModelAnalysis):
    """
    Display time-series data for selected node.
    
    Shows:
    - Chart: Line chart with Actual/Forecast distinction
    - Table: Period-by-period values with period classification
    - Divergence: Highlight where Forecast deviates from Actual trend
    """
    st.markdown("#### 📈 Time Series")
    
    if not node.values:
        st.warning("No time-series data available for this node")
        return
    
    # Prepare data for display
    time_series_data = []
    for col_idx in sorted(node.values.keys()):
        # Get period info
        period_attr = None
        if node.is_factor and node.factor:
            period_attr = node.factor.period_attrs.get(col_idx)
        
        period_type = period_attr.period_type if period_attr else "UNKNOWN"
        col_label = period_attr.column_label if period_attr else f"Col {col_idx}"
        
        # Get value
        value = node.values[col_idx]
        formatted_value = node.formatted_values.get(col_idx, str(value))
        
        time_series_data.append({
            "Period": col_label,
            "Value": value,
            "Formatted": formatted_value,
            "Type": period_type
        })
    
    df = pd.DataFrame(time_series_data)
    
    # Display as chart
    import plotly.express as px
    
    # Color by period type
    color_map = {"ACTUAL": "blue", "FORECAST": "orange", "UNCERTAIN": "gray"}
    df["Color"] = df["Type"].map(color_map)
    
    fig = px.line(
        df, 
        x="Period", 
        y="Value",
        markers=True,
        title=f"{node.label} - Time Series"
    )
    
    # Add color coding for Actual vs Forecast
    for period_type, color in color_map.items():
        mask = df["Type"] == period_type
        if mask.any():
            fig.add_scatter(
                x=df[mask]["Period"],
                y=df[mask]["Value"],
                mode="markers",
                marker=dict(color=color, size=10),
                name=period_type
            )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Display as table
    st.markdown("#### 📋 Detailed Values")
    st.dataframe(
        df[["Period", "Formatted", "Type"]],
        use_container_width=True,
        hide_index=True
    )
    
    # Divergence analysis (if applicable)
    render_divergence_analysis(df, node)

def render_divergence_analysis(df: pd.DataFrame, node: CausalNode):
    """
    Analyze divergence between Actual trend and Forecast values.
    
    Simple heuristic for MVP:
    - Calculate average growth rate from Actual periods
    - Compare Forecast values against projected trend
    - Highlight significant deviations
    """
    actual_df = df[df["Type"] == "ACTUAL"]
    forecast_df = df[df["Type"] == "FORECAST"]
    
    if len(actual_df) < 2 or len(forecast_df) == 0:
        return  # Not enough data for divergence analysis
    
    st.markdown("#### ⚠️ Divergence Check")
    
    # Calculate actual trend (simple: last value vs first value)
    actual_values = actual_df["Value"].tolist()
    actual_growth = (actual_values[-1] - actual_values[0]) / actual_values[0] if actual_values[0] != 0 else 0
    
    # Project trend to forecast periods
    projected_value = actual_values[-1] * (1 + actual_growth)
    
    # Compare with first forecast value
    first_forecast = forecast_df.iloc[0]["Value"]
    divergence_pct = ((first_forecast - projected_value) / projected_value * 100) if projected_value != 0 else 0
    
    if abs(divergence_pct) > 10:  # Threshold: 10%
        st.warning(f"⚠️ Forecast deviates {divergence_pct:.1f}% from Actual trend")
        st.caption(f"Projected: {projected_value:.2f}, Forecast: {first_forecast:.2f}")
    else:
        st.success("✓ Forecast aligns with Actual trend")

def render_evidence_memo_editor(selected_node: CausalNode, model: ModelAnalysis):
    """
    Evidence memo editor (existing functionality).
    """
    st.markdown("#### 📝 Evidence Memo")
    
    # Find existing memo
    existing_memo = next(
        (m for m in model.evidence_memos if m.factor_id == selected_node.id),
        None
    )
    
    # Text area
    memo_text = st.text_area(
        f"Memo for {selected_node.label}",
        value=existing_memo.memo_text if existing_memo else "",
        height=200,
        key=f"memo_{selected_node.id}",
        placeholder="Enter explanation, rationale, or evidence for this factor..."
    )
    
    # Save button
    if st.button("Save Memo", key=f"save_memo_{selected_node.id}"):
        if existing_memo:
            existing_memo.memo_text = memo_text
            existing_memo.updated_at = datetime.now().isoformat()
        else:
            model.evidence_memos.append(EvidenceMemo(
                factor_id=selected_node.id,
                factor_label=selected_node.label,
                memo_text=memo_text,
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            ))
        
        save_evidence_memos(model, st.session_state.excel_path)
        st.success("Memo saved!")
```

---

## 6. Integration with Existing Code

### 6.1 Reuse Existing Components

| Existing Component | Usage in Explanation Mode |
|--------------------|---------------------------|
| `Context Labeling` | Factor label detection |
| `Logic Translator` | Formula → readable equation |
| `Dependency Graph` | Causal tree construction |
| `Risk Detection` | UNTRACEABLE node marking |

### 6.2 Extension Points

**src/models.py**:
- Add `Factor`, `CausalNode`, `PeriodAttribute`, `EvidenceMemo` classes
- Extend `ModelAnalysis` with new fields

**src/analyzer.py**:
- Add `FactorDetector` class
- Add `PeriodInferenceEngine` class
- Add `CausalTreeBuilder` class

**src/explanation_mode.py** (NEW):
- Main UI rendering logic
- AgGrid tree component
- Evidence memo manager

**app.py**:
- Add mode toggle at top level
- Route to `render_explanation_mode()` when selected

---

## 7. Error Handling

### 7.1 UNTRACEABLE Nodes

**Conditions**:
- Formula error (`#REF!`, `#DIV/0!`)
- Hidden hardcode (no further decomposition)
- Inconsistent formula (detected by Risk Review)
- Missing reference

**Behavior**:
- Mark node as `is_untraceable = True`
- Set `untraceable_reason` with explanation
- Stop tree expansion below this node
- Evidence memo remains available

### 7.2 No KPI Candidates

**Condition**: No rows match KPI criteria

**Behavior**:
- Show warning message
- Suggest user to manually select a cell
- Provide fallback: "Select any cell with formula"

### 7.3 JSON Save Failure

**Condition**: Cannot write to file system

**Behavior**:
- Show error message
- Offer to download JSON as file
- Keep memos in session state (temporary)

---

## 8. Performance Considerations

### 8.1 Tree Expansion Limit

- Initial depth: 1 level
- User-triggered expansion: On-demand per node
- Max total nodes: 1000 (prevent UI freeze)

### 8.2 AgGrid Optimization

- Virtual scrolling enabled
- Lazy loading for large trees
- Debounce user interactions

### 8.3 JSON File Size

- Typical size: < 100 KB
- Max memos: 1000 (reasonable limit)
- Compression: Not needed for MVP

---

## 9. Testing Strategy

### 9.1 Unit Tests

- `test_factor_detection.py`: Factor identification logic
- `test_period_inference.py`: Column majority vote
- `test_causal_tree.py`: Tree construction
- `test_evidence_memo.py`: JSON save/load

### 9.2 Integration Tests

- End-to-end: Upload Excel → Build tree → Save memo
- Mode switching: Risk Review ↔ Explanation Mode
- Global override: Apply date → Verify period changes

### 9.3 Manual Testing

- Test with real business plan Excel files
- Verify KPI candidates are sensible
- Check tree readability (formula translation)
- Confirm JSON persistence across sessions

---

## 10. Future Enhancements (Post-MVP)

- **Divergence Checklist**: Actual vs Forecast comparison with historical data
- **Semantic Inconsistency**: AI-powered type checking
- **Multi-level Expansion**: One-click full tree expansion
- **Export**: PDF report generation
- **Collaboration**: Multi-user memo sharing

---

**End of Design Document**
