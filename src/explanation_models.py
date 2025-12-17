"""
Explanation Mode Data Models

This module defines the data structures for Explanation Mode features:
- Factor: Leaf nodes in causal tree (input values)
- CausalNode: Nodes in the causal tree hierarchy
- PeriodAttribute: Period classification (ACTUAL/FORECAST/UNCERTAIN)
- EvidenceMemo: User-attached explanations for factors
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class PeriodAttribute:
    """
    Period classification for a specific column.
    Attached to Factor × Column.
    
    Attributes:
        column_index: 0-based column index
        column_label: Column header label (e.g., "2024/01", "Q1 2024")
        period_type: Classification ("ACTUAL", "FORECAST", "UNCERTAIN")
        confidence: Confidence level ("HIGH", "MEDIUM", "LOW")
        inference_method: How this was determined
        inference_details: Additional metadata about inference
        is_user_overridden: Whether user manually set this
    """
    column_index: int
    column_label: str
    period_type: str  # "ACTUAL", "FORECAST", "UNCERTAIN"
    confidence: str  # "HIGH", "MEDIUM", "LOW"
    inference_method: str  # "header_keyword", "column_majority", "date_fallback", "user_override"
    inference_details: Dict[str, Any] = field(default_factory=dict)
    is_user_overridden: bool = False


@dataclass
class Factor:
    """
    A Factor is a leaf node in the causal tree.
    It represents an input value that cannot or need not be traced further.
    
    Attributes:
        id: Unique identifier (format: "Sheet1!H10" or "Sheet1!Row10")
        sheet: Sheet name
        address: Cell address or "Row10" for series
        label: Display label from Context Labeling or "[No Label] (Address)"
        factor_type: "scalar" or "series"
        series_range: Range for series factors (e.g., "H10:BW10")
        period_attrs: Period attributes per column (for series)
        is_fixed: Exclude from sensitivity analysis
        is_confirmed: User confirmed this is a Factor
        evidence_memo: User-attached explanation text
    """
    id: str
    sheet: str
    address: str
    label: str
    factor_type: str  # "scalar" or "series"
    
    # For series factors
    series_range: Optional[str] = None
    
    # Period attributes (per column for series)
    period_attrs: Dict[int, PeriodAttribute] = field(default_factory=dict)
    
    # User flags
    is_fixed: bool = False
    is_confirmed: bool = False
    
    # Evidence
    evidence_memo: Optional[str] = None


@dataclass
class CausalNode:
    """
    A node in the causal tree.
    Can be either a Factor (leaf) or a Calculated Node (has formula).
    
    Attributes:
        id: Unique identifier (format: "Sheet1!C10")
        sheet: Sheet name
        address: Cell address
        label: Display label from Context Labeling
        is_factor: Whether this is a Factor (leaf node)
        factor: Factor object if is_factor=True
        formula: Original formula string
        formula_readable: Human-readable formula from Logic Translator
        children: Child nodes (precedents)
        depth: Depth in tree (0 = root/target)
        is_expanded: UI expansion state
        is_untraceable: Cannot be decomposed further
        untraceable_reason: Explanation for why untraceable
        has_semantic_warning: Semantic inconsistency detected
        semantic_warning_msg: Warning message
    """
    id: str
    sheet: str
    address: str
    label: str
    
    # Node type
    is_factor: bool
    factor: Optional[Factor] = None
    
    # Formula info
    formula: Optional[str] = None
    formula_readable: Optional[str] = None
    
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


@dataclass
class EvidenceMemo:
    """
    User-attached memo for a Factor or Node.
    Persisted to [ExcelName].lumen.json
    
    Attributes:
        factor_id: Factor ID (format: "Sheet1!H10")
        factor_label: Display label for factor
        memo_text: User-written explanation
        created_at: ISO 8601 timestamp
        updated_at: ISO 8601 timestamp
    """
    factor_id: str
    factor_label: str
    memo_text: str
    created_at: str  # ISO 8601
    updated_at: str  # ISO 8601


@dataclass
class ExplanationModeData:
    """
    Container for all Explanation Mode data.
    This extends ModelAnalysis without modifying the core model.
    
    Attributes:
        factors: List of detected factors
        causal_trees: Causal trees by target ID
        global_date_override: Global date boundary (YYYY-MM format)
        evidence_memos: List of user memos
    """
    factors: List[Factor] = field(default_factory=list)
    causal_trees: Dict[str, CausalNode] = field(default_factory=dict)
    global_date_override: Optional[str] = None
    evidence_memos: List[EvidenceMemo] = field(default_factory=list)
