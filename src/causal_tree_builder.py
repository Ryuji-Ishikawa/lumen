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
        
        Criteria:
        - Must contain "売上" or "Revenue" in label
        - Has formula (calculated metric)
        - Has dependencies (not a pure input)
        - Limit to top 10
        
        Args:
            model: ModelAnalysis object
            factors: List of factors
            
        Returns:
            List of candidate dictionaries with id, label, sheet, address
        """
        candidates = []
        
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
            
            # Add to candidates
            candidates.append({
                'id': cell_id,
                'label': label,
                'sheet': cell_info.sheet,
                'address': cell_info.address
            })
        
        # Limit to top 10
        return candidates[:10]
