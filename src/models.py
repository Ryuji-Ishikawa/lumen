"""
Data models for Project Lumen

This module defines the core data structures used throughout the application:
- CellInfo: Represents a single Excel cell with its metadata
- RiskAlert: Represents a detected risk in the model
- ModelAnalysis: Complete analysis result for an Excel file
- DiffResult: Comparison result between two models
- MaturityLevel: Enum for Excel Rehab maturity levels
- MaturityScore: Maturity scoring result
- UnlockRequirement: Feature unlock requirements
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum
import networkx as nx


@dataclass
class CellInfo:
    """
    Represents a single Excel cell with its metadata and dependencies.
    
    Attributes:
        sheet: Sheet name where the cell is located
        address: Cell address (e.g., "A1", "B5")
        value: Current value of the cell
        formula: Formula string if cell contains a formula (None otherwise)
        dependencies: List of cell references in "Sheet!Address" format
        is_dynamic: True if formula contains INDIRECT/OFFSET/ADDRESS
        is_merged: True if cell is part of a merged range
        merged_range: Range notation if merged (e.g., "A1:B3")
    """
    sheet: str
    address: str
    value: Any
    formula: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    is_dynamic: bool = False
    is_merged: bool = False
    merged_range: Optional[str] = None
    
    def get_full_address(self) -> str:
        """Return full address in 'Sheet!Address' format"""
        return f"{self.sheet}!{self.address}"


class RiskCategory(Enum):
    """
    Business impact-based risk categories for 3-tier triage system.
    
    FATAL_ERROR: Model is broken or uncomputable (Tab 1 - Red)
    - Circular references, phantom links, formula errors
    - Priority: CRITICAL - Must fix immediately
    
    INTEGRITY_RISK: Model runs but logic/values seem wrong (Tab 2 - Orange)
    - Inconsistent formulas, inconsistent values, logic alerts
    - Priority: HIGH - Hidden bugs live here
    
    STRUCTURAL_DEBT: Works correctly but hard to maintain (Tab 3 - Blue)
    - Consistent hardcodes, merged cells
    - Priority: MEDIUM - Technical debt
    """
    FATAL_ERROR = "fatal_error"
    INTEGRITY_RISK = "integrity_risk"
    STRUCTURAL_DEBT = "structural_debt"
    
    @property
    def display_name(self) -> str:
        """Get display name for UI"""
        return {
            RiskCategory.FATAL_ERROR: "Fatal Errors",
            RiskCategory.INTEGRITY_RISK: "Integrity Risks",
            RiskCategory.STRUCTURAL_DEBT: "Structural Debt"
        }[self]
    
    @property
    def icon(self) -> str:
        """Get icon for UI"""
        return {
            RiskCategory.FATAL_ERROR: "🔴",
            RiskCategory.INTEGRITY_RISK: "⚠️",
            RiskCategory.STRUCTURAL_DEBT: "🔧"
        }[self]
    
    @property
    def color(self) -> str:
        """Get color code for UI"""
        return {
            RiskCategory.FATAL_ERROR: "#DC2626",  # Red
            RiskCategory.INTEGRITY_RISK: "#F59E0B",  # Orange
            RiskCategory.STRUCTURAL_DEBT: "#3B82F6"  # Blue
        }[self]
    
    @property
    def description(self) -> str:
        """Get description for UI"""
        return {
            RiskCategory.FATAL_ERROR: "The model is broken or uncomputable",
            RiskCategory.INTEGRITY_RISK: "The model runs, but logic/values seem wrong",
            RiskCategory.STRUCTURAL_DEBT: "Works correctly now, but hard to maintain"
        }[self]


@dataclass
class RiskAlert:
    """
    Represents a detected risk in the Excel model.
    
    Attributes:
        risk_type: Type of risk (e.g., "Hidden Hardcode", "Circular Reference")
        severity: Risk severity level ("Critical", "High", "Medium", "Low")
        sheet: Sheet name where risk was detected
        cell: Cell address where risk was detected
        description: Human-readable description of the risk
        details: Additional context and metadata about the risk
        row_label: Optional label for the row (e.g., "Amortization")
        col_label: Optional label for the column (e.g., "04-2025")
        category: Business impact category for 3-tier triage (set during classification)
    """
    risk_type: str
    severity: str
    sheet: str
    cell: str
    description: str
    details: Dict[str, Any] = field(default_factory=dict)
    row_label: Optional[str] = None
    col_label: Optional[str] = None
    category: Optional[RiskCategory] = None
    
    def get_location(self) -> str:
        """Return location in 'Sheet!Cell' format"""
        return f"{self.sheet}!{self.cell}"
    
    def get_context(self) -> str:
        """
        Return contextual label with smart formatting.
        
        SMART CONTEXT FORMATTING:
        - Rule A (Redundancy Check): If row label contains col label, drop col label
        - Rule B (Date-Only Columns): Drop column label if it's just a date (doesn't add value)
        - Rule C (Clean Output): Only add col label if it adds meaningful context
        - Rule D (No Phantoms): Never output "NONE"
        
        Philosophy: Show their data, not our formatting logic.
        """
        if self.row_label and self.col_label:
            # Rule A: Redundancy Check
            # If row label already contains the column label text, don't repeat it
            row_lower = self.row_label.lower()
            col_lower = self.col_label.lower()
            
            # Check if column label is already in row label
            if col_lower in row_lower or row_lower in col_lower:
                # Redundant - just use row label
                return self.row_label
            
            # Rule B: Date-Only Columns
            # If column label is just a date/time period, it usually doesn't add value
            # Date patterns: "2022-08", "2022-09", "2023-01", "FY2024", "Q1", etc.
            import re
            date_only_patterns = [
                r'^\d{4}-\d{2}$',  # 2022-08, 2023-01
                r'^\d{2}-\d{4}$',  # 08-2022, 01-2023
                r'^FY\s*\d{4}$',   # FY2024, FY 2024
                r'^Q\d$',          # Q1, Q2, Q3, Q4
                r'^[A-Z][a-z]{2}\s+\d{4}$',  # Jan 2024, Feb 2024
            ]
            
            is_date_only = any(re.match(pattern, self.col_label.strip()) for pattern in date_only_patterns)
            
            if is_date_only:
                # Date-only column label doesn't add value - just use row label
                return self.row_label
            
            # Rule C: Clean Output
            # If row label is long/specific (>30 chars), it's probably complete
            if len(self.row_label) > 30:
                return self.row_label
            
            # Otherwise, add column label for context (non-date columns only)
            return f"{self.row_label} @ {self.col_label}"
        elif self.row_label:
            return self.row_label
        elif self.col_label:
            # Column only - this shouldn't happen (row label is mandatory)
            return self.col_label
        else:
            return ""


@dataclass
class ModelAnalysis:
    """
    Complete analysis result for an Excel file.
    
    Attributes:
        filename: Name of the analyzed Excel file
        sheets: List of sheet names in the workbook
        cells: Dictionary of all cells, keyed by "Sheet!Address"
        risks: List of all detected risks
        health_score: Calculated health score (0-100)
        dependency_graph: NetworkX directed graph of cell dependencies
        merged_ranges: Dictionary of merged ranges by sheet name
    """
    filename: str
    sheets: List[str]
    cells: Dict[str, CellInfo]
    risks: List[RiskAlert]
    health_score: int
    dependency_graph: nx.DiGraph
    merged_ranges: Dict[str, List[str]] = field(default_factory=dict)
    
    def get_cell(self, sheet: str, address: str) -> Optional[CellInfo]:
        """Get a cell by sheet and address"""
        key = f"{sheet}!{address}"
        return self.cells.get(key)
    
    def get_risks_by_severity(self, severity: str) -> List[RiskAlert]:
        """Get all risks of a specific severity level"""
        return [risk for risk in self.risks if risk.severity == severity]
    
    def get_risk_counts(self) -> Dict[str, int]:
        """Get count of risks by severity"""
        counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for risk in self.risks:
            if risk.severity in counts:
                counts[risk.severity] += 1
        return counts
    
    def get_precedents(self, cell_address: str) -> List[str]:
        """
        Get all cells that this cell depends on (precedents).
        
        Args:
            cell_address: Cell address in "Sheet!Address" format
            
        Returns:
            List of cell addresses that this cell depends on
        """
        if cell_address not in self.dependency_graph:
            return []
        
        # In a directed graph, predecessors are the cells this cell depends on
        return list(self.dependency_graph.predecessors(cell_address))
    
    def get_dependents(self, cell_address: str) -> List[str]:
        """
        Get all cells that depend on this cell (dependents).
        
        CRITICAL FIX: Returns ALL descendants (recursive), not just direct children.
        
        Args:
            cell_address: Cell address in "Sheet!Address" format
            
        Returns:
            List of cell addresses that depend on this cell (includes grandchildren, etc.)
        """
        if cell_address not in self.dependency_graph:
            return []
        
        # FIXED: Use descendants() to get ALL dependent cells recursively
        # This includes direct children, grandchildren, great-grandchildren, etc.
        try:
            return list(nx.descendants(self.dependency_graph, cell_address))
        except:
            return []


@dataclass
class CompositeKey:
    """
    Represents a composite key for row matching in Monthly Guardian.
    
    Attributes:
        key_columns: List of column letters used for key (e.g., ["A", "B"])
        key_value: Raw concatenated value (e.g., "売上高|固定費")
        normalized_key: Normalized for matching (lowercase, stripped)
        sheet: Sheet name
        row_number: Row number in the sheet
    """
    key_columns: List[str]
    key_value: str
    normalized_key: str
    sheet: str
    row_number: int


@dataclass
class RowMapping:
    """
    Represents a mapping between old and new rows.
    
    Attributes:
        old_row: Row number in old model (None if row was added)
        new_row: Row number in new model (None if row was deleted)
        composite_key: The key used for matching
        match_confidence: Confidence score (1.0 = exact match)
    """
    old_row: Optional[int]
    new_row: Optional[int]
    composite_key: str
    match_confidence: float = 1.0
    
    def is_matched(self) -> bool:
        """Check if row was matched between versions"""
        return self.old_row is not None and self.new_row is not None
    
    def is_added(self) -> bool:
        """Check if row was added in new version"""
        return self.old_row is None and self.new_row is not None
    
    def is_deleted(self) -> bool:
        """Check if row was deleted in new version"""
        return self.old_row is not None and self.new_row is None


@dataclass
class ChangeCategory:
    """
    Categorizes a change between two cells.
    
    Attributes:
        change_type: Type of change (logic_change, input_update, risk_improved, risk_degraded)
        severity: Severity level (critical, normal, positive)
        old_value: Value in old model
        new_value: Value in new model
        description: Human-readable description
    """
    change_type: str  # "logic_change", "input_update", "risk_improved", "risk_degraded"
    severity: str     # "critical", "normal", "positive"
    old_value: Any
    new_value: Any
    description: str


@dataclass
class DiffResult:
    """
    Comparison result between two Excel models (Monthly Guardian).
    
    Attributes:
        old_score: Health score of the old/reference model
        new_score: Health score of the new/target model
        score_delta: Change in score (new_score - old_score)
        logic_changes: List of formula/logic changes (Critical)
        input_updates: List of value-only changes (Normal)
        improved_risks: List of risks that were removed or fixed
        degraded_risks: List of new risks that were introduced
        structural_changes: List of structural changes (sheets added/removed)
        row_mapping: Dictionary mapping old row numbers to new row numbers
    """
    old_score: int
    new_score: int
    score_delta: int
    logic_changes: List[ChangeCategory] = field(default_factory=list)
    input_updates: List[ChangeCategory] = field(default_factory=list)
    improved_risks: List[RiskAlert] = field(default_factory=list)
    degraded_risks: List[RiskAlert] = field(default_factory=list)
    structural_changes: List[str] = field(default_factory=list)
    row_mapping: Dict[int, int] = field(default_factory=dict)
    
    def is_improved(self) -> bool:
        """Check if the model improved overall"""
        return self.score_delta > 0
    
    def is_degraded(self) -> bool:
        """Check if the model degraded overall"""
        return self.score_delta < 0
    
    def get_improvement_summary(self) -> str:
        """Get a human-readable summary of the improvement"""
        if self.is_improved():
            return f"🎉 Model Health Improved! Score: {self.old_score} → {self.new_score} (+{self.score_delta})"
        elif self.is_degraded():
            return f"⚠️ Model Health Decreased. Score: {self.old_score} → {self.new_score} ({self.score_delta})"
        else:
            return f"➡️ No Change in Health Score: {self.old_score}"


# ============================================================================
# Excel Rehab Maturity Model (Phase 7)
# ============================================================================

class MaturityLevel(Enum):
    """
    Maturity levels for Excel Rehab gamification system.
    
    Level 1: Static Model (Critical Condition) 🏥
    - More than 5 hardcodes in critical rows
    - Model is "dead" - needs resurrection
    - Locked: Goal Seek, Scenario Planning
    
    Level 2: Unstable Model (Rehabilitating) 🩹
    - Fewer than 5 hardcodes BUT has circular refs or high-severity risks
    - Model is "recovering" - needs stability
    - Locked: Goal Seek
    
    Level 3: Strategic Model (Healthy Athlete) 🏆
    - No Critical risks AND fewer than 3 High-severity risks
    - Model is "healthy" - ready for strategy
    - Unlocked: All features
    """
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
    
    @property
    def display_name(self) -> str:
        """Get display name with emoji badge"""
        return {
            MaturityLevel.LEVEL_1: "🏥 Maturity Level 1: Static Model",
            MaturityLevel.LEVEL_2: "🩹 Maturity Level 2: Unstable Model",
            MaturityLevel.LEVEL_3: "🏆 Maturity Level 3: Strategic Model"
        }[self]
    
    @property
    def locked_features(self) -> List[str]:
        """Get list of locked features for this level"""
        return {
            MaturityLevel.LEVEL_1: ["Goal Seek", "Scenario Planning"],
            MaturityLevel.LEVEL_2: ["Goal Seek"],
            MaturityLevel.LEVEL_3: []
        }[self]
    
    @property
    def description(self) -> str:
        """Get detailed description of this level"""
        return {
            MaturityLevel.LEVEL_1: "Critical Condition - Your model is static with too many hardcoded values. Focus on decomposition and creating variables.",
            MaturityLevel.LEVEL_2: "Rehabilitating - Your model has structural issues. Focus on fixing circular references and high-severity risks.",
            MaturityLevel.LEVEL_3: "Healthy Athlete - Your model is clean and ready for strategic planning. All features unlocked!"
        }[self]


@dataclass
class MaturityScore:
    """
    Result of maturity scoring calculation.
    
    Attributes:
        level: The calculated maturity level
        hardcode_count: Number of hardcoded values detected
        critical_count: Number of critical severity risks
        high_count: Number of high severity risks
        progress_to_next: Progress percentage toward next level (0-100)
    """
    level: MaturityLevel
    hardcode_count: int
    critical_count: int
    high_count: int
    progress_to_next: float = 0.0
    
    def is_level_1(self) -> bool:
        """Check if model is at Level 1"""
        return self.level == MaturityLevel.LEVEL_1
    
    def is_level_2(self) -> bool:
        """Check if model is at Level 2"""
        return self.level == MaturityLevel.LEVEL_2
    
    def is_level_3(self) -> bool:
        """Check if model is at Level 3"""
        return self.level == MaturityLevel.LEVEL_3


@dataclass
class UnlockRequirement:
    """
    Requirements to unlock the next maturity level or feature.
    
    Attributes:
        current_level: Current maturity level
        next_level: Next maturity level to unlock
        hardcodes_to_fix: Number of hardcodes that need to be fixed
        critical_risks_to_fix: Number of critical risks that need to be fixed
        high_risks_to_fix: Number of high-severity risks that need to be fixed
        actionable_steps: List of specific actions user should take
        progress_percentage: Progress toward unlock (0-100)
    """
    current_level: MaturityLevel
    next_level: Optional[MaturityLevel]
    hardcodes_to_fix: int = 0
    critical_risks_to_fix: int = 0
    high_risks_to_fix: int = 0
    actionable_steps: List[str] = field(default_factory=list)
    progress_percentage: float = 0.0
    
    def is_unlocked(self) -> bool:
        """Check if next level is already unlocked"""
        return (self.hardcodes_to_fix == 0 and 
                self.critical_risks_to_fix == 0 and 
                self.high_risks_to_fix == 0)
    
    def get_summary(self) -> str:
        """Get human-readable summary of unlock requirements"""
        if self.is_unlocked():
            return f"🎉 {self.next_level.display_name if self.next_level else 'Max Level'} Unlocked!"
        
        requirements = []
        if self.hardcodes_to_fix > 0:
            requirements.append(f"Fix {self.hardcodes_to_fix} more hardcode(s)")
        if self.critical_risks_to_fix > 0:
            requirements.append(f"Fix {self.critical_risks_to_fix} critical risk(s)")
        if self.high_risks_to_fix > 0:
            requirements.append(f"Fix {self.high_risks_to_fix} high-severity risk(s)")
        
        return " • ".join(requirements)


# ============================================================================
# Risk Review System (Phase 11)
# ============================================================================

from datetime import datetime


@dataclass
class RiskReviewState:
    """
    Represents the review state for a single risk.
    
    Attributes:
        risk_id: Unique identifier for the risk (format: "{sheet}_{cell}_{risk_type}")
        is_reviewed: Whether the risk has been marked as reviewed
        reviewed_at: Timestamp when the risk was reviewed (None if not reviewed)
    """
    risk_id: str
    is_reviewed: bool
    reviewed_at: Optional[datetime] = None


@dataclass
class ReviewProgress:
    """
    Represents overall review progress for a set of risks.
    
    Attributes:
        total_risks: Total number of risks
        reviewed_count: Number of risks marked as reviewed
        unreviewed_count: Number of risks not yet reviewed
        percentage: Percentage of risks reviewed (0-100)
        initial_score: Initial health score based on all risks
        current_score: Current health score based on unreviewed risks only
        improvement_delta: Improvement in score (current_score - initial_score)
    """
    total_risks: int
    reviewed_count: int
    unreviewed_count: int
    percentage: float
    initial_score: int
    current_score: int
    improvement_delta: int
    
    @property
    def display_text(self) -> str:
        """Get display text for progress indicator"""
        return f"確認済み: {self.reviewed_count}/{self.total_risks} ({self.percentage:.0f}%)"
    
    def is_complete(self) -> bool:
        """Check if all risks have been reviewed"""
        return self.reviewed_count == self.total_risks
    
    def is_halfway(self) -> bool:
        """Check if at least 50% of risks have been reviewed"""
        return self.percentage >= 50.0
    
    def get_encouragement_message(self, lang: str = 'ja') -> Optional[str]:
        """Get encouraging message based on progress"""
        from src.i18n import t
        
        if self.is_complete():
            return t('all_reviewed_message', lang)
        elif self.is_halfway():
            return t('keep_going_message', lang).format(count=self.unreviewed_count)
        else:
            return None
