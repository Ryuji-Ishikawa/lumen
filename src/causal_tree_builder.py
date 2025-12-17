"""
Causal Tree Builder

This module constructs hierarchical causal trees from the dependency graph.
Trees show how a target metric (KPI) is calculated from its factors.

Key Features:
- Recursive tree construction from dependency graph
- Integration with Logic Translator for readable formulas
- UNTRACEABLE node detection (formula errors, hardcodes, etc.)
- Depth control for performance (initial depth = 1)
"""

import re
from typing import List, Optional
from src.models import ModelAnalysis, CellInfo
from src.explanation_models import CausalNode, Factor


class CausalTreeBuilder:
    """
    Builds causal trees from dependency graphs.
    """
    
    def __init__(self):
        """Initialize the builder"""
        pass
    
    def build_causal_tree(self, target_id: str, model: ModelAnalysis, 
                         factors: List[Factor], max_depth: int = 1) -> CausalNode:
        """
        Build causal tree starting from target node.
        
        Args:
            target_id: Cell ID of target metric (e.g., "Sheet1!C10")
            model: ModelAnalysis object
            factors: List of detected factors
            max_depth: Maximum depth to expand (default: 1 for initial display)
            
        Returns:
            Root CausalNode
        """
        # Get target cell
        target_cell = model.cells.get(target_id)
        if not target_cell:
            raise ValueError(f"Target cell not found: {target_id}")
        
        # Build tree recursively
        return self._build_node(target_id, target_cell, model, factors, 
                               depth=0, max_depth=max_depth, visited=set())
    
    def _build_node(self, cell_id: str, cell_info: CellInfo, model: ModelAnalysis,
                   factors: List[Factor], depth: int, max_depth: int, 
                   visited: set) -> CausalNode:
        """
        Recursively build a causal node and its children.
        
        Args:
            cell_id: Cell ID
            cell_info: Cell info
            model: ModelAnalysis object
            factors: List of factors
            depth: Current depth in tree
            max_depth: Maximum depth to expand
            visited: Set of visited cell IDs (prevent cycles)
            
        Returns:
            CausalNode
        """
        # Check if this is a factor
        is_factor = any(f.id == cell_id for f in factors)
        factor = next((f for f in factors if f.id == cell_id), None)
        
        # Get context label
        label = self._get_context_label(cell_info, model)
        if not label:
            label = f"[No Label] ({cell_info.address})"
        
        # Get readable formula (from Logic Translator if available)
        formula_readable = None
        if cell_info.formula:
            formula_readable = self._translate_formula(cell_info.formula, model)
        
        # Create node
        node = CausalNode(
            id=cell_id,
            sheet=cell_info.sheet,
            address=cell_info.address,
            label=label,
            is_factor=is_factor,
            factor=factor,
            formula=cell_info.formula,
            formula_readable=formula_readable,
            depth=depth
        )
        
        # Check if untraceable
        if self._is_untraceable(cell_info, model):
            node.is_untraceable = True
            node.untraceable_reason = self._get_untraceable_reason(cell_info, model)
            return node
        
        # Build children (precedents) if not at max depth
        if depth < max_depth and not is_factor:
            # Prevent cycles
            if cell_id in visited:
                node.is_untraceable = True
                node.untraceable_reason = "Circular reference detected"
                return node
            
            visited.add(cell_id)
            
            # Get precedents (cells this cell depends on)
            precedents = model.get_precedents(cell_id)
            
            for prec_id in precedents:
                prec_cell = model.cells.get(prec_id)
                if prec_cell:
                    child = self._build_node(prec_id, prec_cell, model, factors,
                                            depth + 1, max_depth, visited.copy())
                    node.children.append(child)
        
        return node
    
    def _get_context_label(self, cell_info: CellInfo, model: ModelAnalysis) -> Optional[str]:
        """
        Get context label for a cell.
        
        Looks for row headers in columns A-G.
        
        Args:
            cell_info: Cell to get label for
            model: ModelAnalysis object
            
        Returns:
            Context label or None
        """
        # Extract row number
        match = re.match(r'([A-Z]+)(\d+)', cell_info.address)
        if not match:
            return None
        
        row_num = match.group(2)
        
        # Check columns A-G for labels
        for col_letter in ['A', 'B', 'C', 'D', 'E', 'F', 'G']:
            label_key = f"{cell_info.sheet}!{col_letter}{row_num}"
            label_cell = model.cells.get(label_key)
            
            if label_cell and label_cell.value:
                label_text = str(label_cell.value).strip()
                
                # Filter out poor quality labels
                if self._is_valid_label(label_text):
                    return label_text
        
        return None
    
    def _is_valid_label(self, text: str) -> bool:
        """Check if label text is meaningful"""
        if not text or len(text) < 2:
            return False
        
        if text.startswith('='):
            return False
        
        if re.match(r'^[A-Z]+\d+$', text):
            return False
        
        if re.match(r'^[-0-9\s.]+$', text):
            return False
        
        return True
    
    def _translate_formula(self, formula: str, model: ModelAnalysis) -> Optional[str]:
        """
        Translate formula to readable equation.
        
        This is a simplified version. Full implementation would use Logic Translator.
        
        Args:
            formula: Formula string
            model: ModelAnalysis object
            
        Returns:
            Readable formula or None
        """
        if not formula:
            return None
        
        # For MVP, just return the formula as-is
        # Full implementation would integrate with Logic Translator
        return formula
    
    def _is_untraceable(self, cell_info: CellInfo, model: ModelAnalysis) -> bool:
        """
        Check if node cannot be decomposed further.
        
        Untraceable conditions:
        - Formula error (#REF!, #DIV/0!, etc.)
        - No formula and no dependencies (hardcode blob)
        - Dynamic reference (INDIRECT, OFFSET, ADDRESS)
        
        Args:
            cell_info: Cell to check
            model: ModelAnalysis object
            
        Returns:
            True if untraceable
        """
        # Check for formula errors
        if cell_info.value and isinstance(cell_info.value, str):
            if cell_info.value.startswith('#'):
                return True
        
        # Check for dynamic references
        if cell_info.is_dynamic:
            return True
        
        # Check for hardcode with no dependencies
        if not cell_info.formula and not cell_info.dependencies:
            # This is a pure hardcode
            # Only untraceable if it has no context
            return False  # Let it be a factor instead
        
        return False
    
    def _get_untraceable_reason(self, cell_info: CellInfo, model: ModelAnalysis) -> str:
        """
        Get explanation for why node is untraceable.
        
        Args:
            cell_info: Cell info
            model: ModelAnalysis object
            
        Returns:
            Reason string
        """
        # Check for formula errors
        if cell_info.value and isinstance(cell_info.value, str):
            if cell_info.value.startswith('#'):
                return f"Formula error: {cell_info.value}"
        
        # Check for dynamic references
        if cell_info.is_dynamic:
            return "Dynamic reference (INDIRECT/OFFSET/ADDRESS)"
        
        # Check for hardcode
        if not cell_info.formula:
            return "Hardcoded value (no formula)"
        
        return "Cannot decompose further"
    
    def get_kpi_candidates(self, model: ModelAnalysis, factors: List[Factor]) -> List[dict]:
        """
        Get KPI candidates for target selection.
        
        CRITICAL: Groups by (Sheet, Row, Label) to avoid showing every cell in a time series.
        For series data (e.g., monthly revenue), shows ONE row instead of 12 individual cells.
        
        Criteria:
        - Must contain "売上" or "Revenue" in label
        - Has formula (calculated metric)
        - Has dependencies (not a pure input)
        - Groups by row (deduplicates series data)
        - Selects representative cell per row
        - Limit to top 10
        
        Args:
            model: ModelAnalysis object
            factors: List of factors
            
        Returns:
            List of candidate dictionaries with:
            - id: Representative cell ID (for analysis)
            - label: Row label
            - sheet: Sheet name
            - row: Row number
            - representative_address: Address of representative cell
        """
        import re
        
        # Step 1: Collect all KPI cells
        kpi_cells = []
        
        for cell_id, cell_info in model.cells.items():
            # Must have formula
            if not cell_info.formula:
                continue
            
            # Must have dependencies
            if not cell_info.dependencies:
                continue
            
            # Get label
            label = self._get_context_label(cell_info, model)
            if not label:
                continue
            
            # Check for KPI keywords
            label_lower = label.lower()
            if '売上' not in label and 'revenue' not in label_lower:
                continue
            
            # Extract row number from address
            match = re.match(r'([A-Z]+)(\d+)', cell_info.address)
            if not match:
                continue
            
            row_num = int(match.group(2))
            
            kpi_cells.append({
                'id': cell_id,
                'label': label,
                'sheet': cell_info.sheet,
                'row': row_num,
                'address': cell_info.address,
                'cell_info': cell_info
            })
        
        # Step 2: Group by (Sheet, Row, Label)
        from collections import defaultdict
        grouped = defaultdict(list)
        
        for cell in kpi_cells:
            key = (cell['sheet'], cell['row'], cell['label'])
            grouped[key].append(cell)
        
        # Step 3: Select representative cell for each row
        candidates = []
        
        for (sheet, row, label), cells in grouped.items():
            # Select representative cell
            representative = self._select_representative_cell(cells, model)
            
            candidates.append({
                'id': representative['id'],
                'label': label,
                'sheet': sheet,
                'row': row,
                'representative_address': representative['address'],
                'cell_count': len(cells)  # For debugging
            })
        
        # Step 4: Sort by row number and limit to top 10
        candidates.sort(key=lambda x: (x['sheet'], x['row']))
        return candidates[:10]
    
    def _select_representative_cell(self, cells: List[dict], model: ModelAnalysis) -> dict:
        """
        Select representative cell from a row of series data.
        
        Priority:
        1. Cell with SUM formula (合計列)
        2. Rightmost cell with formula (likely last actual or first forecast)
        3. First cell in the list
        
        Args:
            cells: List of cell dictionaries from same row
            model: ModelAnalysis object
            
        Returns:
            Representative cell dictionary
        """
        import re
        
        # Priority 1: Look for SUM formula
        for cell in cells:
            formula = cell['cell_info'].formula
            if formula and 'SUM' in formula.upper():
                return cell
        
        # Priority 2: Rightmost cell (highest column letter)
        # Extract column letters and find max
        cells_with_col = []
        for cell in cells:
            match = re.match(r'([A-Z]+)(\d+)', cell['address'])
            if match:
                col_letter = match.group(1)
                # Convert column letter to number for comparison
                from openpyxl.utils import column_index_from_string
                col_num = column_index_from_string(col_letter)
                cells_with_col.append((col_num, cell))
        
        if cells_with_col:
            # Return cell with highest column number
            cells_with_col.sort(key=lambda x: x[0], reverse=True)
            return cells_with_col[0][1]
        
        # Priority 3: First cell
        return cells[0]
