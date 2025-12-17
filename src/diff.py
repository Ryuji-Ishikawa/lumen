"""
Diff engine for comparing Excel models - Monthly Guardian

This module provides the DiffEngine class with Composite Key Matching
for intelligent monthly variance analysis.

Key Features:
- Composite Key Matching: Match rows by content (e.g., "Account Name"), not row numbers
- Logic Change Detection: Distinguish formula changes from value changes
- Uniqueness Validation: Warn if selected keys are not unique
"""

from typing import List, Set, Dict, Optional, Tuple
from src.models import ModelAnalysis, RiskAlert, DiffResult, CompositeKey, RowMapping, ChangeCategory, CellInfo
import re


class DiffEngine:
    """
    Engine for comparing two Excel models with Composite Key Matching.
    
    This is our competitive moat for monthly variance analysis.
    """
    
    def __init__(self):
        """Initialize the diff engine"""
        pass
    
    def compare(self, old_model: ModelAnalysis, new_model: ModelAnalysis, 
                key_columns: Optional[List[str]] = None, 
                sheet_name: Optional[str] = None) -> DiffResult:
        """
        Compare two Excel models using Composite Key Matching.
        
        Args:
            old_model: The reference/old model
            new_model: The target/new model
            key_columns: List of column letters for composite key (e.g., ["A", "B"])
            sheet_name: Sheet to analyze (if None, analyze all sheets)
            
        Returns:
            DiffResult containing all changes
        """
        # Calculate health scores
        old_score = old_model.health_score
        new_score = new_model.health_score
        score_delta = new_score - old_score
        
        # Build row mapping using composite keys (if provided)
        row_mapping = {}
        if key_columns and sheet_name:
            row_mapping = self._match_rows_by_composite_key(
                old_model, new_model, key_columns, sheet_name
            )
        
        # Detect logic changes and input updates
        logic_changes, input_updates = self._detect_changes(
            old_model, new_model, row_mapping, sheet_name
        )
        
        # Detect risk changes
        improved_risks, degraded_risks = self._compare_risks(
            old_model.risks, new_model.risks, row_mapping
        )
        
        # Detect structural changes
        structural_changes = self._detect_structural_changes(old_model, new_model)
        
        return DiffResult(
            old_score=old_score,
            new_score=new_score,
            score_delta=score_delta,
            logic_changes=logic_changes,
            input_updates=input_updates,
            improved_risks=improved_risks,
            degraded_risks=degraded_risks,
            structural_changes=structural_changes,
            row_mapping=row_mapping
        )
    
    def build_composite_keys(self, model: ModelAnalysis, key_columns: List[str], 
                            sheet_name: str) -> Dict[str, CompositeKey]:
        """
        Build composite keys for all rows in a sheet.
        
        Args:
            model: ModelAnalysis object
            key_columns: List of column letters (e.g., ["A", "B"])
            sheet_name: Sheet name to process
            
        Returns:
            Dictionary mapping normalized_key -> CompositeKey
            
        Note: If duplicate keys exist, only the last occurrence is kept in the dict.
        Use validate_key_uniqueness() to check for duplicates before matching.
        """
        composite_keys = {}
        
        # Get all cells from the specified sheet
        sheet_cells = {k: v for k, v in model.cells.items() if v.sheet == sheet_name}
        
        # Group cells by row
        rows = {}
        for cell_key, cell in sheet_cells.items():
            row_num = self._extract_row_number(cell.address)
            if row_num not in rows:
                rows[row_num] = {}
            col_letter = self._extract_column_letter(cell.address)
            rows[row_num][col_letter] = cell
        
        # Build composite key for each row
        for row_num, row_cells in rows.items():
            key_values = []
            for col in key_columns:
                cell = row_cells.get(col)
                if cell and cell.value:
                    key_values.append(str(cell.value).strip())
                else:
                    key_values.append("")
            
            # Create composite key
            key_value = "|".join(key_values)
            normalized_key = key_value.lower().replace("  ", " ").strip()
            
            # Skip empty keys
            if not normalized_key or normalized_key == "|" * (len(key_columns) - 1):
                continue
            
            composite_key = CompositeKey(
                key_columns=key_columns,
                key_value=key_value,
                normalized_key=normalized_key,
                sheet=sheet_name,
                row_number=row_num
            )
            
            composite_keys[normalized_key] = composite_key
        
        return composite_keys
    
    def build_composite_keys_with_duplicates(self, model: ModelAnalysis, key_columns: List[str], 
                                            sheet_name: str) -> List[CompositeKey]:
        """
        Build composite keys for all rows, preserving duplicates.
        
        Args:
            model: ModelAnalysis object
            key_columns: List of column letters (e.g., ["A", "B"])
            sheet_name: Sheet name to process
            
        Returns:
            List of CompositeKey objects (may contain duplicates)
        """
        composite_keys = []
        
        # Get all cells from the specified sheet
        sheet_cells = {k: v for k, v in model.cells.items() if v.sheet == sheet_name}
        
        # Group cells by row
        rows = {}
        for cell_key, cell in sheet_cells.items():
            row_num = self._extract_row_number(cell.address)
            if row_num not in rows:
                rows[row_num] = {}
            col_letter = self._extract_column_letter(cell.address)
            rows[row_num][col_letter] = cell
        
        # Build composite key for each row
        for row_num, row_cells in rows.items():
            key_values = []
            for col in key_columns:
                cell = row_cells.get(col)
                if cell and cell.value:
                    key_values.append(str(cell.value).strip())
                else:
                    key_values.append("")
            
            # Create composite key
            key_value = "|".join(key_values)
            normalized_key = key_value.lower().replace("  ", " ").strip()
            
            # Skip empty keys
            if not normalized_key or normalized_key == "|" * (len(key_columns) - 1):
                continue
            
            composite_key = CompositeKey(
                key_columns=key_columns,
                key_value=key_value,
                normalized_key=normalized_key,
                sheet=sheet_name,
                row_number=row_num
            )
            
            composite_keys.append(composite_key)
        
        return composite_keys
    
    def validate_key_uniqueness(self, model: ModelAnalysis, key_columns: List[str], 
                               sheet_name: str) -> Tuple[float, List[str]]:
        """
        Validate that composite keys are unique.
        
        Args:
            model: ModelAnalysis object
            key_columns: List of column letters
            sheet_name: Sheet name to process
            
        Returns:
            Tuple of (uniqueness_rate, duplicate_keys)
        """
        # Build all keys including duplicates
        all_keys = self.build_composite_keys_with_duplicates(model, key_columns, sheet_name)
        
        if not all_keys:
            return 1.0, []
        
        # Count occurrences of each normalized key
        key_counts = {}
        for composite_key in all_keys:
            normalized = composite_key.normalized_key
            key_counts[normalized] = key_counts.get(normalized, 0) + 1
        
        # Find duplicates
        duplicates = [k for k, count in key_counts.items() if count > 1]
        
        # Calculate uniqueness rate
        total_keys = len(all_keys)
        unique_keys = len([k for k, count in key_counts.items() if count == 1])
        uniqueness_rate = unique_keys / total_keys if total_keys > 0 else 0.0
        
        return uniqueness_rate, duplicates
    
    def _match_rows_by_composite_key(self, old_model: ModelAnalysis, 
                                     new_model: ModelAnalysis,
                                     key_columns: List[str], 
                                     sheet_name: str) -> Dict[int, int]:
        """
        Match rows between old and new models using composite keys.
        
        Args:
            old_model: Old model
            new_model: New model
            key_columns: List of column letters for key
            sheet_name: Sheet to analyze
            
        Returns:
            Dictionary mapping old_row -> new_row
        """
        # Build composite keys for both models
        old_keys = self.build_composite_keys(old_model, key_columns, sheet_name)
        new_keys = self.build_composite_keys(new_model, key_columns, sheet_name)
        
        # Match rows by key
        row_mapping = {}
        for key, old_composite in old_keys.items():
            if key in new_keys:
                new_composite = new_keys[key]
                row_mapping[old_composite.row_number] = new_composite.row_number
        
        return row_mapping
    
    def _detect_changes(self, old_model: ModelAnalysis, new_model: ModelAnalysis,
                       row_mapping: Dict[int, int], sheet_name: Optional[str]) -> Tuple[List[ChangeCategory], List[ChangeCategory]]:
        """
        Detect logic changes and input updates.
        
        Args:
            old_model: Old model
            new_model: New model
            row_mapping: Row mapping from composite key matching
            sheet_name: Sheet to analyze
            
        Returns:
            Tuple of (logic_changes, input_updates)
        """
        logic_changes = []
        input_updates = []
        
        # If no row mapping, fall back to simple cell-by-cell comparison
        if not row_mapping:
            return self._simple_cell_comparison(old_model, new_model, sheet_name)
        
        # Compare matched rows
        for old_row, new_row in row_mapping.items():
            # Get cells from both rows
            old_row_cells = {k: v for k, v in old_model.cells.items() 
                           if v.sheet == sheet_name and self._extract_row_number(v.address) == old_row}
            new_row_cells = {k: v for k, v in new_model.cells.items() 
                           if v.sheet == sheet_name and self._extract_row_number(v.address) == new_row}
            
            # Compare each cell in the row
            for old_key, old_cell in old_row_cells.items():
                col_letter = self._extract_column_letter(old_cell.address)
                new_key = f"{sheet_name}!{col_letter}{new_row}"
                new_cell = new_model.cells.get(new_key)
                
                if new_cell:
                    # Check for logic change (formula modified)
                    if old_cell.formula != new_cell.formula:
                        logic_changes.append(ChangeCategory(
                            change_type="logic_change",
                            severity="critical",
                            old_value=old_cell.formula,
                            new_value=new_cell.formula,
                            description=f"Formula changed at {new_cell.sheet}!{new_cell.address}"
                        ))
                    # Check for input update (value changed, formula same)
                    elif old_cell.value != new_cell.value:
                        input_updates.append(ChangeCategory(
                            change_type="input_update",
                            severity="normal",
                            old_value=old_cell.value,
                            new_value=new_cell.value,
                            description=f"Value updated at {new_cell.sheet}!{new_cell.address}"
                        ))
        
        return logic_changes, input_updates
    
    def _simple_cell_comparison(self, old_model: ModelAnalysis, new_model: ModelAnalysis,
                                sheet_name: Optional[str]) -> Tuple[List[ChangeCategory], List[ChangeCategory]]:
        """
        Simple cell-by-cell comparison (fallback when no row mapping).
        
        Args:
            old_model: Old model
            new_model: New model
            sheet_name: Sheet to analyze
            
        Returns:
            Tuple of (logic_changes, input_updates)
        """
        logic_changes = []
        input_updates = []
        
        # Compare cells with same address
        for cell_key, old_cell in old_model.cells.items():
            if sheet_name and old_cell.sheet != sheet_name:
                continue
            
            new_cell = new_model.cells.get(cell_key)
            if new_cell:
                # Check for logic change
                if old_cell.formula != new_cell.formula:
                    logic_changes.append(ChangeCategory(
                        change_type="logic_change",
                        severity="critical",
                        old_value=old_cell.formula,
                        new_value=new_cell.formula,
                        description=f"Formula changed at {cell_key}"
                    ))
                # Check for input update
                elif old_cell.value != new_cell.value:
                    input_updates.append(ChangeCategory(
                        change_type="input_update",
                        severity="normal",
                        old_value=old_cell.value,
                        new_value=new_cell.value,
                        description=f"Value updated at {cell_key}"
                    ))
        
        return logic_changes, input_updates
    
    def _compare_risks(self, old_risks: List[RiskAlert], new_risks: List[RiskAlert],
                      row_mapping: Dict[int, int]) -> Tuple[List[RiskAlert], List[RiskAlert]]:
        """
        Compare risks between two models.
        
        Args:
            old_risks: Risks from the old model
            new_risks: Risks from the new model
            row_mapping: Row mapping for intelligent matching
            
        Returns:
            Tuple of (improved_risks, degraded_risks)
        """
        # Create risk signatures for matching
        old_risk_sigs = {self._risk_signature(r): r for r in old_risks}
        new_risk_sigs = {self._risk_signature(r): r for r in new_risks}
        
        # Find removed risks (improvements)
        improved_sigs = set(old_risk_sigs.keys()) - set(new_risk_sigs.keys())
        improved_risks = [old_risk_sigs[sig] for sig in improved_sigs]
        
        # Find new risks (degradations)
        degraded_sigs = set(new_risk_sigs.keys()) - set(old_risk_sigs.keys())
        degraded_risks = [new_risk_sigs[sig] for sig in degraded_sigs]
        
        return improved_risks, degraded_risks
    
    def _risk_signature(self, risk: RiskAlert) -> str:
        """Create a unique signature for a risk"""
        return f"{risk.risk_type}|{risk.sheet}|{risk.cell}"
    
    def _detect_structural_changes(self, old_model: ModelAnalysis, 
                                   new_model: ModelAnalysis) -> List[str]:
        """Detect structural changes between models"""
        changes = []
        
        old_sheets = set(old_model.sheets)
        new_sheets = set(new_model.sheets)
        
        # Detect added sheets
        added_sheets = new_sheets - old_sheets
        for sheet in added_sheets:
            changes.append(f"➕ Sheet added: {sheet}")
        
        # Detect removed sheets
        removed_sheets = old_sheets - new_sheets
        for sheet in removed_sheets:
            changes.append(f"➖ Sheet removed: {sheet}")
        
        return changes
    
    def _extract_row_number(self, address: str) -> int:
        """Extract row number from cell address (e.g., 'A5' -> 5)"""
        match = re.match(r'[A-Z]+(\d+)', address)
        return int(match.group(1)) if match else 0
    
    def _extract_column_letter(self, address: str) -> str:
        """Extract column letter from cell address (e.g., 'A5' -> 'A')"""
        match = re.match(r'([A-Z]+)\d+', address)
        return match.group(1) if match else ""
