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
    st.markdown(f"## 🔍 {t('explanation_mode_title', lang)}")
    st.caption(t('explanation_mode_subtitle', lang))
    
    st.markdown("---")
    
    # Check if model has been analyzed
    if not model.cells:
        st.warning(t('explanation_mode_no_data', lang))
        return
    
    # Phase 2 MVP: Simple placeholder UI
    # This will be replaced with full implementation in Phase 3
    
    st.info("🚧 " + ("Explanation Mode は開発中です" if lang == 'ja' else "Explanation Mode is under development"))
    
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
    
    # Placeholder for future features
    st.markdown(f"### {t('coming_soon', lang)}")
    
    features = [
        ("🌳", "Causal Tree", "因果ツリー", "Hierarchical breakdown of KPI calculations"),
        ("📊", "Period Analysis", "期間分析", "Actual vs Forecast classification"),
        ("📝", "Evidence Memos", "エビデンスメモ", "Attach explanations to factors"),
        ("🎯", "Target Selection", "ターゲット選択", "Select KPI to analyze"),
    ]
    
    for icon, name_en, name_ja, desc_en in features:
        name = name_ja if lang == 'ja' else name_en
        desc = desc_en  # Keep English for now
        st.markdown(f"{icon} **{name}** - {desc}")
    
    st.markdown("---")
    
    # Development status
    st.markdown(f"### {t('development_status', lang)}")
    
    progress_items = [
        ("✅", "Data Models", "データモデル", "Complete"),
        ("✅", "Factor Detection", "因数検出", "Complete"),
        ("✅", "Period Inference", "期間推論", "Complete"),
        ("✅", "Causal Tree Builder", "因果ツリー構築", "Complete"),
        ("🚧", "UI Implementation", "UI実装", "In Progress"),
    ]
    
    for icon, name_en, name_ja, status in progress_items:
        name = name_ja if lang == 'ja' else name_en
        st.markdown(f"{icon} **{name}** - {status}")


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
