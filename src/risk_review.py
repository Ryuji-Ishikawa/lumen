"""
Risk Review System for Project Lumen

This module implements the session-based risk review system that allows users to:
- Mark risks as reviewed with checkboxes
- Track review progress in real-time
- Calculate dynamic health scores based on unreviewed risks
- Filter risks by review state
- Export review state to CSV

Key Components:
- RiskReviewStateManager: Manages review state in session_state
- DynamicScoreCalculator: Calculates health scores dynamically
- Filter and export utilities
"""

from typing import List, Dict, Optional
from datetime import datetime
import streamlit as st
import pandas as pd

from src.models import RiskAlert, ReviewProgress, RiskReviewState
from src.i18n import t


class RiskReviewStateManager:
    """
    Manages review state for risks in session_state.
    
    State is stored in st.session_state.risk_review_states as a dictionary:
    {
        "Sheet1_A1_Hidden Hardcode": True,
        "Sheet2_B5_Circular Reference": False,
        ...
    }
    
    State is session-based only - no persistence across sessions.
    """
    
    def __init__(self):
        """Initialize state manager and ensure session_state is ready"""
        if "risk_review_states" not in st.session_state:
            st.session_state.risk_review_states = {}
    
    def get_risk_id(self, risk: RiskAlert) -> str:
        """
        Generate unique identifier for a risk.
        
        Format: "{sheet}_{cell}_{risk_type}"
        Example: "Budget_E92_Hidden Hardcode"
        
        Args:
            risk: RiskAlert object
            
        Returns:
            Unique identifier string
        """
        # Use underscores to separate components
        # Replace spaces in risk_type with underscores for consistency
        risk_type_clean = risk.risk_type.replace(" ", "_")
        return f"{risk.sheet}_{risk.cell}_{risk_type_clean}"
    
    def is_reviewed(self, risk: RiskAlert) -> bool:
        """
        Check if a risk is marked as reviewed.
        
        Args:
            risk: RiskAlert object
            
        Returns:
            True if reviewed, False otherwise
        """
        risk_id = self.get_risk_id(risk)
        return st.session_state.risk_review_states.get(risk_id, False)
    
    def set_reviewed(self, risk: RiskAlert, reviewed: bool):
        """
        Mark a risk as reviewed or unreviewed.
        
        Args:
            risk: RiskAlert object
            reviewed: True to mark as reviewed, False to unmark
        """
        risk_id = self.get_risk_id(risk)
        st.session_state.risk_review_states[risk_id] = reviewed
    
    def get_reviewed_count(self, risks: List[RiskAlert]) -> int:
        """
        Count how many risks are marked as reviewed.
        
        Args:
            risks: List of RiskAlert objects
            
        Returns:
            Number of reviewed risks
        """
        return sum(1 for risk in risks if self.is_reviewed(risk))
    
    def get_unreviewed_risks(self, risks: List[RiskAlert]) -> List[RiskAlert]:
        """
        Get list of risks that are not yet reviewed.
        
        Args:
            risks: List of RiskAlert objects
            
        Returns:
            List of unreviewed risks
        """
        return [risk for risk in risks if not self.is_reviewed(risk)]
    
    def get_reviewed_risks(self, risks: List[RiskAlert]) -> List[RiskAlert]:
        """
        Get list of risks that are marked as reviewed.
        
        Args:
            risks: List of RiskAlert objects
            
        Returns:
            List of reviewed risks
        """
        return [risk for risk in risks if self.is_reviewed(risk)]
    
    def clear_all(self):
        """
        Clear all review states.
        
        This is called when starting a new session or when user wants to reset.
        """
        st.session_state.risk_review_states = {}
    
    def get_all_states(self) -> Dict[str, bool]:
        """
        Get all review states as a dictionary.
        
        Returns:
            Dictionary mapping risk_id to review state
        """
        return st.session_state.risk_review_states.copy()


class DynamicScoreCalculator:
    """
    Calculates health scores dynamically based on review state.
    
    Initial Score: Based on all detected risks
    Current Score: Based on unreviewed risks only
    Improvement Delta: Current - Initial (shows progress)
    
    Formula: 100 - (Critical×10) - (High×5) - (Medium×2)
    """
    
    def calculate_initial_score(self, risks: List[RiskAlert]) -> int:
        """
        Calculate initial health score based on all risks.
        Uses the same calculation method as analyzer.py with category-based weighting.
        
        This is the baseline score when no risks have been reviewed yet.
        
        Args:
            risks: List of all detected risks
            
        Returns:
            Health score (30-100) - minimum 30 for psychological safety
        """
        from src.models import RiskCategory
        
        score = 100.0
        
        # Define base penalties for Fatal Error (same as analyzer.py)
        fatal_penalties = {
            "Critical": 5.0,
            "High": 4.0,
            "Medium": 3.0,
            "Low": 1.0
        }
        
        # Category multipliers (same as analyzer.py)
        category_multipliers = {
            RiskCategory.FATAL_ERROR: 1.0,      # 100%
            RiskCategory.INTEGRITY_RISK: 0.5,   # 50%
            RiskCategory.STRUCTURAL_DEBT: 0.1   # 10%
        }
        
        # Apply penalties for each risk
        for risk in risks:
            category = risk.category if hasattr(risk, 'category') else None
            severity = risk.severity
            
            # Skip if category or severity is not recognized
            if category not in category_multipliers:
                continue
            
            if severity not in fatal_penalties:
                continue
            
            # Calculate penalty
            base_penalty = fatal_penalties[severity]
            multiplier = category_multipliers[category]
            penalty = base_penalty * multiplier
            
            score -= penalty
        
        # Floor: Minimum 30 (psychological safety - same as analyzer.py)
        return max(30, int(score))
    
    def calculate_current_score(
        self, 
        risks: List[RiskAlert], 
        state_manager: RiskReviewStateManager
    ) -> int:
        """
        Calculate current health score based on unreviewed risks only.
        
        This score improves as users review risks, providing immediate feedback.
        
        Args:
            risks: List of all detected risks
            state_manager: RiskReviewStateManager instance
            
        Returns:
            Current health score (0-100)
        """
        unreviewed_risks = state_manager.get_unreviewed_risks(risks)
        return self.calculate_initial_score(unreviewed_risks)
    
    def calculate_progress(
        self, 
        risks: List[RiskAlert], 
        state_manager: RiskReviewStateManager
    ) -> ReviewProgress:
        """
        Calculate complete review progress including scores and counts.
        
        Args:
            risks: List of all detected risks
            state_manager: RiskReviewStateManager instance
            
        Returns:
            ReviewProgress object with all metrics
        """
        total = len(risks)
        reviewed = state_manager.get_reviewed_count(risks)
        unreviewed = total - reviewed
        percentage = (reviewed / total * 100) if total > 0 else 0.0
        
        initial_score = self.calculate_initial_score(risks)
        current_score = self.calculate_current_score(risks, state_manager)
        improvement_delta = current_score - initial_score
        
        return ReviewProgress(
            total_risks=total,
            reviewed_count=reviewed,
            unreviewed_count=unreviewed,
            percentage=percentage,
            initial_score=initial_score,
            current_score=current_score,
            improvement_delta=improvement_delta
        )


# ============================================================================
# UI Components (Task 35-38)
# ============================================================================

def format_context(row_label: Optional[str], col_label: Optional[str]) -> str:
    """
    Format context labels for display.
    
    Args:
        row_label: Row label (e.g., "Revenue")
        col_label: Column label (e.g., "Q1")
        
    Returns:
        Formatted context string
    """
    if row_label and col_label:
        return f"{row_label} × {col_label}"
    elif row_label:
        return row_label
    elif col_label:
        return col_label
    else:
        return "-"


def render_progress_display(progress: ReviewProgress, lang: str = 'ja'):
    """
    Render very compact progress display (smaller version).
    Task 36: Progress Display Component (Simplified)
    
    Args:
        progress: ReviewProgress object with metrics
        lang: Language code ('ja' or 'en')
    """
    # Very compact single-line display with smaller text
    progress_text = f"確認済み: {progress.reviewed_count}/{progress.total_risks} ({progress.percentage:.0f}%)"
    if progress.improvement_delta > 0:
        progress_text += f" | スコア改善: +{progress.improvement_delta}"
    
    st.caption(progress_text)
    st.progress(progress.percentage / 100)


def render_filter_controls(lang: str = 'ja') -> str:
    """
    Render filter radio buttons.
    Task 37: Filter System
    
    Args:
        lang: Language code ('ja' or 'en')
        
    Returns:
        Selected filter mode: "all", "unreviewed", or "reviewed"
    """
    filter_mode = st.radio(
        t('display_filter', lang),
        options=["all", "unreviewed", "reviewed"],
        format_func=lambda x: {
            "all": t('filter_all', lang),
            "unreviewed": t('filter_unreviewed', lang),
            "reviewed": t('filter_reviewed', lang)
        }[x],
        horizontal=True,
        key="risk_review_filter"
    )
    
    return filter_mode


def render_risk_table_with_checkboxes(
    risks: List[RiskAlert],
    state_manager: RiskReviewStateManager,
    filter_mode: str = "all",
    lang: str = 'ja'
) -> pd.DataFrame:
    """
    Render risk table with checkbox column.
    Task 35: Checkbox UI Implementation
    
    Args:
        risks: List of risks to display
        state_manager: Review state manager
        filter_mode: "all", "unreviewed", or "reviewed"
        lang: Language code ('ja' or 'en')
        
    Returns:
        DataFrame with checkbox column and risk data
    """
    # Apply filter
    if filter_mode == "unreviewed":
        filtered_risks = [r for r in risks if not state_manager.is_reviewed(r)]
    elif filter_mode == "reviewed":
        filtered_risks = [r for r in risks if state_manager.is_reviewed(r)]
    else:
        filtered_risks = risks
    
    if not filtered_risks:
        st.info(f"フィルター '{filter_mode}' に該当するリスクがありません。")
        return pd.DataFrame()
    
    # Build table data
    table_data = []
    for risk in filtered_risks:
        is_reviewed = state_manager.is_reviewed(risk)
        table_data.append({
            t('review_checkbox', lang): is_reviewed,
            t('table_location', lang): f"{risk.sheet}!{risk.cell}",
            t('table_context', lang): format_context(risk.row_label, risk.col_label),
            "リスク種別": risk.risk_type,
            t('table_severity', lang): risk.severity,
            "説明": risk.description
        })
    
    df = pd.DataFrame(table_data)
    
    # Display table with checkbox interaction
    edited_df = st.data_editor(
        df,
        column_config={
            t('review_checkbox', lang): st.column_config.CheckboxColumn(
                t('review_checkbox', lang),
                help=t('review_checkbox_help', lang),
                default=False
            )
        },
        disabled=[t('table_location', lang), t('table_context', lang), "リスク種別", t('table_severity', lang), "説明"],
        hide_index=True,
        use_container_width=True,
        key=f"risk_table_{filter_mode}"
    )
    
    # Update state based on checkbox changes
    checkbox_col = t('review_checkbox', lang)
    for idx, row in edited_df.iterrows():
        if idx < len(filtered_risks):  # Safety check
            risk = filtered_risks[idx]
            new_state = row[checkbox_col]
            current_state = state_manager.is_reviewed(risk)
            
            # Only update if state changed
            if new_state != current_state:
                state_manager.set_reviewed(risk, new_state)
    
    return edited_df


def export_risks_with_review_state(
    risks: List[RiskAlert],
    state_manager: RiskReviewStateManager,
    lang: str = 'ja'
) -> str:
    """
    Export risks to CSV with review state column.
    Task 38: CSV Export Enhancement
    
    Args:
        risks: List of risks to export
        state_manager: Review state manager
        lang: Language code ('ja' or 'en')
        
    Returns:
        CSV string with review state
    """
    export_data = []
    
    for risk in risks:
        is_reviewed = state_manager.is_reviewed(risk)
        export_data.append({
            "確認済み": "TRUE" if is_reviewed else "FALSE",
            "シート": risk.sheet,
            "セル": risk.cell,
            "コンテキスト": format_context(risk.row_label, risk.col_label),
            "リスク種別": risk.risk_type,
            "重要度": risk.severity,
            "説明": risk.description,
            "エクスポート日時": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    
    df = pd.DataFrame(export_data)
    return df.to_csv(index=False, encoding="utf-8-sig")


def render_risk_review_interface(risks: List[RiskAlert], lang: str = 'ja'):
    """
    Main function to render complete risk review interface.
    Task 39: Integration
    
    This function integrates all components:
    - Progress display
    - Filter controls  
    - Risk table with checkboxes
    - CSV export
    
    Args:
        risks: List of risks to display
        lang: Language code ('ja' or 'en')
    """
    if not risks:
        st.info("リスクが検出されませんでした。")
        return
    
    # Initialize managers
    state_manager = RiskReviewStateManager()
    score_calculator = DynamicScoreCalculator()
    
    # Calculate progress
    progress = score_calculator.calculate_progress(risks, state_manager)
    
    # Render progress display (no icon)
    st.markdown(f"### {t('review_progress', lang)}")
    render_progress_display(progress, lang)
    
    st.markdown("---")
    
    # Render risk table with checkboxes (no filter controls)
    st.markdown("### リスク一覧")
    edited_df = render_risk_table_with_checkboxes(
        risks, 
        state_manager, 
        "all",  # Always show all risks (no filter)
        lang
    )
    
    # Export button (no icon)
    if not edited_df.empty:
        st.markdown("---")
        csv_data = export_risks_with_review_state(risks, state_manager, lang)
        
        st.download_button(
            label=t('export_with_review_state', lang),
            data=csv_data,
            file_name=f"risk_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            help="確認状態とタイムスタンプを含むCSVファイルをダウンロード",
            key="risk_review_csv_download"
        )
