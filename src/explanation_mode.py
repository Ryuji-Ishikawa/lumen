"""
Explanation Mode UI

This module provides the main UI for Explanation Mode, which helps users
understand "why this number?" by showing:
- Causal Tree: Hierarchical breakdown of KPI calculations
- Period Analysis: Actual vs Forecast classification
- Evidence Memos: User-attached explanations

Layout:
- Left Sidebar (10%): Navigation
- Main Area (90%):
  - Left Panel (60%): Causal Tree (AgGrid)
  - Right Panel (40%): Detail View (Time-Series + Evidence Memo)
"""

import streamlit as st
from typing import Optional
from src.models import ModelAnalysis
from src.i18n import t


def render_explanation_mode(model: ModelAnalysis, lang: str):
    """
    Main entry point for Explanation Mode UI.
    
    Args:
        model: Analyzed model with risks and dependency graph
        lang: Language code ('ja' or 'en')
    """
    # Header
    st.markdown(f"## {t('explanation_mode_title', lang)}")
    st.caption(t('explanation_mode_subtitle', lang))
    
    st.markdown("---")
    
    # Check if model has been analyzed
    if not model.cells:
        st.warning(t('explanation_mode_no_data', lang))
        return
    
    # Detect factors (needed for KPI candidates)
    from src.factor_detector import FactorDetector
    from src.causal_tree_builder import CausalTreeBuilder
    
    detector = FactorDetector()
    factors = detector.detect_factors(model)
    
    builder = CausalTreeBuilder()
    
    # Get KPI candidates
    kpi_candidates = builder.get_kpi_candidates(model, factors)
    
    # Target Selection UI
    st.markdown(f"### {t('target_selection_title', lang)}")
    
    if kpi_candidates:
        # Create options for selectbox
        options = [
            f"{candidate['label']} ({candidate['sheet']}!{candidate['address']})"
            for candidate in kpi_candidates
        ]
        
        # Add index for mapping back to candidate
        selected_index = st.selectbox(
            t('target_selection_label', lang),
            range(len(options)),
            format_func=lambda i: options[i],
            help=t('target_selection_help', lang)
        )
        
        # Store selected target in session state
        if selected_index is not None:
            selected_candidate = kpi_candidates[selected_index]
            st.session_state['target_metric'] = selected_candidate['id']
            
            # Show selection confirmation
            st.success(
                t('target_selected', lang).format(
                    label=selected_candidate['label'],
                    address=f"{selected_candidate['sheet']}!{selected_candidate['address']}"
                )
            )
    else:
        # No KPI candidates found
        st.warning(t('no_kpi_candidates', lang))
        
        # Fallback: Manual cell address input
        st.markdown(f"#### {t('manual_selection_title', lang)}")
        
        manual_input = st.text_input(
            t('manual_selection_label', lang),
            placeholder="Sheet1!C10",
            help=t('manual_selection_help', lang)
        )
        
        if manual_input:
            # Validate format
            if '!' in manual_input and manual_input in model.cells:
                st.session_state['target_metric'] = manual_input
                st.success(t('manual_target_selected', lang).format(address=manual_input))
            else:
                st.error(t('invalid_cell_address', lang))
    
    st.markdown("---")
    
    # Show basic model info
    st.markdown(f"### {t('model_overview', lang)}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(t('metric_sheets', lang), len(model.sheets))
    
    with col2:
        st.metric(t('metric_cells', lang), len(model.cells))
    
    with col3:
        formula_count = sum(1 for cell in model.cells.values() if cell.formula)
        st.metric(t('metric_formulas', lang), formula_count)
    
    st.markdown("---")
    
    # Development status
    st.markdown(f"### {t('development_status', lang)}")
    
    progress_items = [
        ("Complete", "Data Models", "データモデル"),
        ("Complete", "Factor Detection", "因数検出"),
        ("Complete", "Period Inference", "期間推論"),
        ("Complete", "Causal Tree Builder", "因果ツリー構築"),
        ("Complete", "Target Selection", "ターゲット選択"),
        ("In Progress", "Tree Display", "ツリー表示"),
    ]
    
    for status, name_en, name_ja in progress_items:
        name = name_ja if lang == 'ja' else name_en
        st.markdown(f"**{name}**: {status}")


# Placeholder for future functions
def render_target_selection(model: ModelAnalysis, lang: str) -> Optional[str]:
    """
    Render target selection dropdown.
    
    Args:
        model: ModelAnalysis object
        lang: Language code
        
    Returns:
        Selected target ID or None
    """
    # TODO: Implement in Phase 2
    pass


def render_causal_tree(model: ModelAnalysis, target_id: str, lang: str):
    """
    Render causal tree using AgGrid.
    
    Args:
        model: ModelAnalysis object
        target_id: Target cell ID
        lang: Language code
    """
    # TODO: Implement in Phase 3
    pass


def render_detail_panel(model: ModelAnalysis, selected_node_id: Optional[str], lang: str):
    """
    Render detail panel with time-series and evidence memo.
    
    Args:
        model: ModelAnalysis object
        selected_node_id: Selected node ID or None
        lang: Language code
    """
    # TODO: Implement in Phase 3
    pass
