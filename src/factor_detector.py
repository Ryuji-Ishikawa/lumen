"""
Factor Detection Engine

This module identifies "Factors" (leaf nodes) in the dependency graph.
Factors are input values that cannot or need not be traced further.

Detection Criteria:
1. No formula OR simple reference (e.g., =Sheet1!A10)
2. Has Context Label OR is referenced by important calculations
3. Has downstream dependencies (out_degree > 0)

Rescue: If no label, use "[No Label] (Address)"
"""

import re
from typing import Dict, List, Optional
from src.models import ModelAnalysis, CellInfo
from src.explanation_models import Factor


class FactorDetector:
    """
    Detects factors (leaf nodes) in the causal tree.
    """
    
    def __init__(self):
        """Initialize the detector"""
        pass
    
    def detect_factors(self, model: ModelAnalysis) -> List[Factor]:
        """
        Identify all factors in the model.
        
        Args:
            model: ModelAnalysis object with cells and dependency graph
            
        Returns:
            List of Factor objects
        """
        factors = []
        
        for cell_key, cell_info in model.cells.items():
            # Condition 1: No formula OR simple reference
            if not self._is_factor_candidate(cell_info):
                continue
            
            # Condition 2: Has Context Label OR is referenced by important calc
            label = self._get_context_label(cell_info, model)
            if not label:
                # Check if referenced by important calculation
                if not self._is_referenced_by_important_calc(cell_key, model):
                    continue
                # Rescue: Use address as label
                label = f"[No Label] ({cell_info.address})"
            
            # Condition 3: Has downstream dependencies
            if model.dependency_graph.out_degree(cell_key) == 0:
                continue
            
            # Determine factor type (scalar vs series)
            factor_type = self._detect_factor_type(cell_key, cell_info, model)
            
            # Create Factor
            factor = Factor(
                id=cell_key,
                sheet=cell_info.sheet,
                address=cell_info.address,
                label=label,
                factor_type=factor_type
            )
            
            # For series factors, detect range
            if factor_type == "series":
                factor.series_range = self._detect_series_range(cell_key, cell_info, model)
            
            factors.append(factor)
        
        return factors
    
    def _is_factor_candidate(self, cell_info: CellInfo) -> bool:
        """
        Check if cell is a factor candidate (Condition 1).
        
        Factor candidates:
        - No formula (hardcoded value)
        - Simple reference (e.g., =Sheet1!A10)
        
        Args:
            cell_info: Cell to check
            
        Returns:
            True if candidate, False otherwise
        """
        # No formula = hardcoded value = factor candidate
        if not cell_info.formula:
            return True
        
        # Check if formula is a simple reference
        return self._is_simple_reference(cell_info.formula)
    
    def _is_simple_reference(self, formula: str) -> bool:
        """
        Check if formula is a simple cell reference.
        
        Simple reference patterns:
        - =A10
        - =Sheet1!A10
        - ='Sheet Name'!A10
        
        Args:
            formula: Formula string
            
        Returns:
            True if simple reference, False otherwise
        """
        if not formula:
            return False
        
        # Remove leading '='
        formula = formula.strip()
        if formula.startswith('='):
            formula = formula[1:].strip()
        
        # Pattern: Optional sheet reference + cell address
        # Examples: A10, Sheet1!A10, 'Sheet Name'!A10
        pattern = r"^(?:'[^']+!'|[^!]+!)?[A-Z]+\d+$"
        
        return bool(re.match(pattern, formula))
    
    def _get_context_label(self, cell_info: CellInfo, model: ModelAnalysis) -> Optional[str]:
        """
        Get context label for a cell.
        
        This reuses the existing Context Labeling logic from analyzer.
        For MVP, we'll use a simplified version that looks for row headers.
        
        Args:
            cell_info: Cell to get label for
            model: ModelAnalysis object
            
        Returns:
            Context label or None
        """
        # Look for row header in columns A-G (common pattern)
        # Extract row number from cell address
        match = re.match(r'([A-Z]+)(\d+)', cell_info.address)
        if not match:
            return None
        
        row_num = match.group(2)
        
        # Check columns A-G for labels
        for col_letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
            label_key = f"{cell_info.sheet}!{col_letter}{row_num}"
            label_cell = model.cells.get(label_key)
            
            if label_cell and label_cell.value:
                # Found a label
                label_text = str(label_cell.value).strip()
                
                # Filter out poor quality labels
                if self._is_valid_label(label_text):
                    return label_text
        
        return None
    
    def _is_valid_label(self, text: str) -> bool:
        """
        Check if label text is meaningful.
        
        Args:
            text: Label text
            
        Returns:
            True if valid, False if poor quality
        """
        if not text or len(text) < 2:
            return False
        
        # Skip formula debris
        if text.startswith('='):
            return False
        
        # Skip cell addresses
        if re.match(r'^[A-Z]+\d+$', text):
            return False
        
        # Skip pure numbers
        if re.match(r'^[-0-9\s.]+$', text):
            return False
        
        return True
    
    def _is_referenced_by_important_calc(self, cell_key: str, model: ModelAnalysis) -> bool:
        """
        Check if cell is referenced by important calculations.
        
        "Important" means:
        - Has many downstream dependents (>= 5)
        - OR is referenced by a cell with a meaningful label
        
        Args:
            cell_key: Cell to check
            model: ModelAnalysis object
            
        Returns:
            True if referenced by important calc
        """
        # Get all dependents (cells that depend on this cell)
        dependents = model.get_dependents(cell_key)
        
        # If many dependents, it's important
        if len(dependents) >= 5:
            return True
        
        # Check if any dependent has a meaningful label
        for dep_key in dependents:
            dep_cell = model.cells.get(dep_key)
            if dep_cell:
                label = self._get_context_label(dep_cell, model)
                if label:
                    return True
        
        return False
    
    def _detect_factor_type(self, cell_key: str, cell_info: CellInfo, 
                           model: ModelAnalysis) -> str:
        """
        Determine if factor is "scalar" or "series".
        
        Series Factor: Time-series data in a single row (or column).
        Detection: Check if adjacent cells in same row have similar patterns.
        
        Args:
            cell_key: Cell key
            cell_info: Cell info
            model: ModelAnalysis object
            
        Returns:
            "scalar" or "series"
        """
        # Extract row and column from address
        match = re.match(r'([A-Z]+)(\d+)', cell_info.address)
        if not match:
            return "scalar"
        
        col_letter = match.group(1)
        row_num = match.group(2)
        
        # Check if there are adjacent cells in the same row with values
        # Look 3 cells to the right
        adjacent_count = 0
        for offset in range(1, 4):
            next_col = self._increment_column(col_letter, offset)
            next_key = f"{cell_info.sheet}!{next_col}{row_num}"
            next_cell = model.cells.get(next_key)
            
            if next_cell and next_cell.value is not None:
                adjacent_count += 1
        
        # If 2+ adjacent cells have values, it's likely a series
        return "series" if adjacent_count >= 2 else "scalar"
    
    def _increment_column(self, col_letter: str, offset: int) -> str:
        """
        Increment column letter by offset.
        
        Args:
            col_letter: Column letter (e.g., "A", "Z", "AA")
            offset: Number of columns to increment
            
        Returns:
            New column letter
        """
        from openpyxl.utils import column_index_from_string, get_column_letter
        
        col_num = column_index_from_string(col_letter)
        new_col_num = col_num + offset
        return get_column_letter(new_col_num)
    
    def _detect_series_range(self, cell_key: str, cell_info: CellInfo, 
                            model: ModelAnalysis) -> Optional[str]:
        """
        Detect the full range of a series factor.
        
        Scans left and right to find the extent of the series.
        Stops at empty cells or meaning boundaries.
        
        Args:
            cell_key: Cell key
            cell_info: Cell info
            model: ModelAnalysis object
            
        Returns:
            Range string (e.g., "H10:BW10") or None
        """
        # Extract row and column
        match = re.match(r'([A-Z]+)(\d+)', cell_info.address)
        if not match:
            return None
        
        col_letter = match.group(1)
        row_num = match.group(2)
        
        # Find leftmost cell in series
        leftmost = col_letter
        for offset in range(1, 100):  # Limit search to 100 columns
            prev_col = self._increment_column(col_letter, -offset)
            if prev_col == col_letter:  # Reached column A
                break
            
            prev_key = f"{cell_info.sheet}!{prev_col}{row_num}"
            prev_cell = model.cells.get(prev_key)
            
            if not prev_cell or prev_cell.value is None:
                # Empty cell = boundary
                break
            
            leftmost = prev_col
        
        # Find rightmost cell in series
        rightmost = col_letter
        for offset in range(1, 100):  # Limit search to 100 columns
            next_col = self._increment_column(col_letter, offset)
            next_key = f"{cell_info.sheet}!{next_col}{row_num}"
            next_cell = model.cells.get(next_key)
            
            if not next_cell or next_cell.value is None:
                # Empty cell = boundary
                break
            
            rightmost = next_col
        
        # Return range
        if leftmost == rightmost:
            return None  # Single cell, not a series
        
        return f"{leftmost}{row_num}:{rightmost}{row_num}"
