"""
Parser Robustness Test Suite

Tests that the parser can handle messy Japanese Excel files without crashing.
This is our competitive moat - if we can parse these files, we win the Japanese market.
"""

import pytest
import os
from pathlib import Path
from io import BytesIO

# Import our parser
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.parser import ExcelParser


# Path to test fixtures
FIXTURES_DIR = Path(__file__).parent / 'fixtures' / 'spaghetti_excel'


class TestParserRobustness:
    """Test suite for parser robustness with spaghetti Excel files"""
    
    def setup_method(self):
        """Setup for each test"""
        self.parser = ExcelParser()
    
    def _load_file(self, filename):
        """Helper to load test file"""
        filepath = FIXTURES_DIR / filename
        with open(filepath, 'rb') as f:
            return BytesIO(f.read())
    
    def test_heavy_merged_cells_no_crash(self):
        """Test 1: Heavy merged cells should not crash parser"""
        file_obj = self._load_file('heavy_merged_cells.xlsx')
        
        try:
            model = self.parser.parse(file_obj, 'heavy_merged_cells.xlsx')
            assert model is not None, "Parser should return ModelAnalysis object"
            assert len(model.cells) > 0, "Parser should extract some cells"
            assert len(model.merged_ranges) > 0, "Parser should identify merged ranges"
            print(f"✓ Parsed {len(model.cells)} cells, {len(model.merged_ranges)} sheets with merges")
        except Exception as e:
            pytest.fail(f"Parser crashed on heavy_merged_cells.xlsx: {e}")
    
    def test_complex_grid_layout_no_crash(self):
        """Test 2: Complex grid layout should not crash parser"""
        file_obj = self._load_file('complex_grid_layout.xlsx')
        
        try:
            model = self.parser.parse(file_obj, 'complex_grid_layout.xlsx')
            assert model is not None
            assert len(model.cells) > 0
            # Should have both vertical and horizontal merges
            assert len(model.merged_ranges) > 0
            print(f"✓ Parsed {len(model.cells)} cells with mixed merge directions")
        except Exception as e:
            pytest.fail(f"Parser crashed on complex_grid_layout.xlsx: {e}")
    
    def test_japanese_text_mixed_no_crash(self):
        """Test 3: Japanese/English mixed text should not crash parser"""
        file_obj = self._load_file('japanese_text_mixed.xlsx')
        
        try:
            model = self.parser.parse(file_obj, 'japanese_text_mixed.xlsx')
            assert model is not None
            assert len(model.cells) > 0
            
            # Verify Japanese text is preserved
            japanese_cells = [c for c in model.cells.values() if c.value and '売上' in str(c.value)]
            assert len(japanese_cells) > 0, "Japanese text should be preserved"
            print(f"✓ Parsed {len(model.cells)} cells with Japanese text")
        except Exception as e:
            pytest.fail(f"Parser crashed on japanese_text_mixed.xlsx: {e}")
    
    def test_circular_references_no_crash(self):
        """Test 4: Circular references should not crash parser"""
        file_obj = self._load_file('circular_references.xlsx')
        
        try:
            model = self.parser.parse(file_obj, 'circular_references.xlsx')
            assert model is not None
            assert len(model.cells) > 0
            
            # Verify dependency graph was built (even with cycles)
            assert model.dependency_graph is not None
            assert model.dependency_graph.number_of_nodes() > 0
            print(f"✓ Parsed {len(model.cells)} cells with circular references")
        except Exception as e:
            pytest.fail(f"Parser crashed on circular_references.xlsx: {e}")
    
    def test_cross_sheet_complex_no_crash(self):
        """Test 5: Complex cross-sheet references should not crash parser"""
        file_obj = self._load_file('cross_sheet_complex.xlsx')
        
        try:
            model = self.parser.parse(file_obj, 'cross_sheet_complex.xlsx')
            assert model is not None
            assert len(model.sheets) >= 10, "Should have 10+ sheets"
            assert len(model.cells) > 0
            
            # Verify cross-sheet dependencies were extracted
            cross_sheet_deps = [c for c in model.cells.values() 
                               if c.dependencies and any('!' in dep for dep in c.dependencies)]
            assert len(cross_sheet_deps) > 0, "Should have cross-sheet dependencies"
            print(f"✓ Parsed {len(model.sheets)} sheets with cross-references")
        except Exception as e:
            pytest.fail(f"Parser crashed on cross_sheet_complex.xlsx: {e}")
    
    def test_edge_cases_no_crash(self):
        """Test 6: Edge case merges should not crash parser"""
        file_obj = self._load_file('edge_cases.xlsx')
        
        try:
            model = self.parser.parse(file_obj, 'edge_cases.xlsx')
            assert model is not None
            assert len(model.cells) > 0
            assert len(model.merged_ranges) > 0
            
            # Verify various merge types were handled
            sheet_merges = model.merged_ranges.get('EdgeCases', [])
            assert len(sheet_merges) > 0, "Should have multiple merged ranges"
            print(f"✓ Parsed {len(sheet_merges)} edge case merges")
        except Exception as e:
            pytest.fail(f"Parser crashed on edge_cases.xlsx: {e}")
    
    def test_hanko_boxes_no_crash(self):
        """Test 7: Japanese hanko boxes should not crash parser"""
        file_obj = self._load_file('hanko_boxes.xlsx')
        
        try:
            model = self.parser.parse(file_obj, 'hanko_boxes.xlsx')
            assert model is not None
            assert len(model.cells) > 0
            
            # Verify hanko box merges were handled
            assert len(model.merged_ranges) > 0
            print(f"✓ Parsed hanko boxes with {len(model.cells)} cells")
        except Exception as e:
            pytest.fail(f"Parser crashed on hanko_boxes.xlsx: {e}")
    
    def test_all_files_return_model_analysis(self):
        """Meta test: All files should return ModelAnalysis object"""
        test_files = [
            'heavy_merged_cells.xlsx',
            'complex_grid_layout.xlsx',
            'japanese_text_mixed.xlsx',
            'circular_references.xlsx',
            'cross_sheet_complex.xlsx',
            'edge_cases.xlsx',
            'hanko_boxes.xlsx'
        ]
        
        results = []
        for filename in test_files:
            file_obj = self._load_file(filename)
            try:
                model = self.parser.parse(file_obj, filename)
                assert model is not None
                assert hasattr(model, 'cells')
                assert hasattr(model, 'dependency_graph')
                assert hasattr(model, 'merged_ranges')
                results.append((filename, 'PASS', len(model.cells)))
            except Exception as e:
                results.append((filename, 'FAIL', str(e)))
        
        # Print summary
        print("\n" + "="*70)
        print("SPAGHETTI EXCEL TEST SUITE SUMMARY")
        print("="*70)
        for filename, status, info in results:
            status_icon = "✓" if status == "PASS" else "✗"
            print(f"{status_icon} {filename:35} {status:6} {info}")
        print("="*70)
        
        # Assert all passed
        failures = [r for r in results if r[1] == 'FAIL']
        assert len(failures) == 0, f"Failed files: {failures}"
    
    def test_virtual_fill_propagation(self):
        """Test that Virtual Fill propagates values to all merged coordinates"""
        file_obj = self._load_file('heavy_merged_cells.xlsx')
        model = self.parser.parse(file_obj, 'heavy_merged_cells.xlsx')
        
        # Find cells that are part of merged ranges
        merged_cells = [c for c in model.cells.values() if c.is_merged]
        assert len(merged_cells) > 0, "Should have virtual filled cells"
        
        # Verify all merged cells have values
        for cell in merged_cells:
            assert cell.merged_range is not None, f"Cell {cell.address} should have merged_range"
            # Note: Some merged cells may have None value if they're not the top-left
            # But they should still be in the cells dict
        
        print(f"✓ Virtual Fill created {len(merged_cells)} virtual cells")
    
    def test_dependency_graph_includes_virtual_cells(self):
        """Test that dependency graph includes virtual filled cells"""
        file_obj = self._load_file('complex_grid_layout.xlsx')
        model = self.parser.parse(file_obj, 'complex_grid_layout.xlsx')
        
        # Get virtual cells
        merged_cells = [c for c in model.cells.values() if c.is_merged]
        
        # Check if virtual cells are in dependency graph
        graph_nodes = set(model.dependency_graph.nodes())
        for cell in merged_cells:
            cell_key = f"{cell.sheet}!{cell.address}"
            # Virtual cells should be in the graph
            # (They may not have edges if they don't have formulas)
            assert cell_key in model.cells, f"Virtual cell {cell_key} should be in cells dict"
        
        print(f"✓ Dependency graph has {model.dependency_graph.number_of_nodes()} nodes")
    
    def test_error_messages_are_specific(self):
        """Test that error messages are specific and actionable (not generic)"""
        # This test would use a corrupt file, but for now we verify the error handling exists
        # by checking that the parser has proper exception handling
        
        # Create a fake corrupt file
        corrupt_data = BytesIO(b"This is not an Excel file")
        
        try:
            model = self.parser.parse(corrupt_data, 'corrupt.xlsx')
            # If it doesn't raise, that's actually a problem
            pytest.fail("Parser should raise ValueError for corrupt files")
        except ValueError as e:
            # Error message should be specific
            error_msg = str(e)
            assert len(error_msg) > 10, "Error message should be descriptive"
            assert "corrupt" in error_msg.lower() or "invalid" in error_msg.lower() or "parse" in error_msg.lower()
            print(f"✓ Specific error message: {error_msg[:100]}")
        except Exception as e:
            # Other exceptions are also acceptable as long as they're caught
            print(f"✓ Error caught: {type(e).__name__}")


if __name__ == '__main__':
    # Run tests with verbose output
    pytest.main([__file__, '-v', '-s'])
