"""
Lumen - Excel Model Audit & Diagnostic System
A Streamlit application for analyzing Excel financial models
"""

import streamlit as st
import pandas as pd
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple
from src.parser import parse_excel_file
from src.analyzer import ModelAnalyzer
from src.models import ModelAnalysis
from src.smart_context import SmartContextRecovery
from src.risk_review import RiskReviewStateManager, DynamicScoreCalculator
from src.i18n import t, get_language_name
from streamlit_agraph import agraph, Node, Edge, Config

# Initialize language in session state
if 'language' not in st.session_state:
    st.session_state.language = 'ja'  # Default to Japanese

# Configure page
st.set_page_config(
    page_title=t('page_title', st.session_state.language),
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for debug logs
if 'debug_logs' not in st.session_state:
    st.session_state.debug_logs = []

if 'parse_time' not in st.session_state:
    st.session_state.parse_time = None

def add_debug_log(level: str, message: str, details: Dict[str, Any] = None):
    """Add entry to debug log"""
    log_entry = {
        'timestamp': datetime.now().strftime('%H:%M:%S'),
        'level': level,
        'message': message,
        'details': details or {}
    }
    st.session_state.debug_logs.append(log_entry)

# Removed old calculate_maturity_level function - now using analyzer.calculate_maturity_level_heuristic()

def main():
    """Main application entry point"""
    
    # Sidebar
    with st.sidebar:
        # App Title at the very top - compact
        lang = st.session_state.language
        app_title = t('app_title', lang)
        app_subtitle = t('app_subtitle', lang)
        st.markdown(f"""
        <div style="margin-bottom: 0.5rem; padding-bottom: 0.25rem;">
            <h2 style="font-size: 38.4px; margin: 0; font-weight: 600; color: #133463;">🔬 {app_title}</h2>
            <p style="font-size: 14px; margin: 0.25rem 0 0 0; color: #6B7280;">{app_subtitle}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Settings (with language selector inside)
        st.title(f"⚙️ {t('sidebar_settings', st.session_state.language)}")
        
        # Language Selector (moved inside settings)
        lang_label = "Language / 言語" if lang == 'ja' else "Language / 言語"
        lang_options = ['日本語', 'English']
        current_index = 0 if st.session_state.language == 'ja' else 1
        selected_lang = st.radio(
            lang_label,
            lang_options,
            index=current_index,
            horizontal=True
        )
        st.session_state.language = 'ja' if selected_lang == '日本語' else 'en'
        
        fiscal_year_start = st.selectbox(
            t('sidebar_fiscal_year', st.session_state.language),
            options=list(range(1, 13)),
            index=0,
            format_func=lambda x: t('month', st.session_state.language).format(num=x),
            help=t('sidebar_fiscal_year_help', st.session_state.language)
        )
        
        allowed_constants = st.text_input(
            t('sidebar_allowed_constants', st.session_state.language),
            value="3, 12, 30, 365",
            placeholder="e.g. 3, 12, 30, 365, 1.5",
            help=t('sidebar_allowed_constants_help', st.session_state.language)
        )
        
        # DIAGNOSTIC FEATURE 1: Multi-Column Context Selector - compact
        label_columns = st.text_input(
            t('sidebar_label_columns', st.session_state.language),
            value="A:D",
            placeholder="e.g. A:D or B:C",
            help=t('sidebar_label_columns_help', st.session_state.language)
        )
        
        st.divider()
        
        # AI Configuration - compact
        st.title(f"🤖 {t('sidebar_ai_config', st.session_state.language)}")
        
        ai_provider = st.selectbox(
            t('sidebar_ai_provider', st.session_state.language),
            options=["OpenAI", "Google"],
            index=0,
            help=t('sidebar_ai_provider_help', st.session_state.language)
        )
        
        api_key = st.text_input(
            t('sidebar_api_key', st.session_state.language),
            type="password",
            help=t('sidebar_api_key_help', st.session_state.language)
        )
        
        # Compact status message and set ai_enabled flag
        if api_key:
            st.caption("✓ " + t('sidebar_api_configured', st.session_state.language))
            st.session_state["ai_enabled"] = True
        else:
            st.session_state["ai_enabled"] = False
        
        st.divider()
        
        # File Upload - compact
        st.title(f"📁 {t('sidebar_file_upload', st.session_state.language)}")
        
        # File uploaders - target file first (main), reference file second (optional)
        target_file = st.file_uploader(
            t('sidebar_target_file', st.session_state.language),
            type=['xlsx'],
            key="target_file",
            help=t('sidebar_target_help', st.session_state.language)
        )
        
        # Optional reference file for comparison
        optional_label = "（任意）" if st.session_state.language == 'ja' else "(Optional)"
        reference_file = st.file_uploader(
            f"{t('sidebar_reference_file', st.session_state.language)} {optional_label}",
            type=['xlsx'],
            key="reference_file",
            help=t('sidebar_reference_help', st.session_state.language)
        )
    
    # Main area
    lang = st.session_state.language
    
    if not reference_file and not target_file:
        # Show welcome message when no files uploaded - compact layout
        
        # What it does section
        st.markdown(f"### {t('what_it_does_title', lang)}")
        st.markdown(t('what_it_does_desc', lang))
        
        # Key detection items
        st.markdown(f"### {t('detection_title', lang)}")
        st.markdown(f"- {t('detection_external', lang)}")
        st.markdown(f"- {t('detection_inconsistent_formula', lang)}")
        st.markdown(f"- {t('detection_inconsistent_value', lang)}")
        st.markdown(f"- {t('detection_hardcode', lang)}")
        st.markdown(f"- {t('detection_circular', lang)}")
        
        # Usage steps
        st.markdown(f"### {t('usage_title', lang)}")
        st.markdown(f"1. {t('usage_step1', lang)}")
        st.markdown(f"2. {t('usage_step2', lang)}")
        st.markdown(f"3. {t('usage_step3', lang)}")
        st.markdown(f"4. {t('usage_step4', lang)}")
        st.markdown(f"5. {t('usage_step5', lang)}")
        
        st.markdown("---")
        
        # Call-to-action button
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button(f"📤 {t('welcome_cta', lang)}", use_container_width=True, type="primary"):
                st.session_state['show_upload_hint'] = True
        
        # Show hint if button was clicked
        if st.session_state.get('show_upload_hint', False):
            st.success("👈 " + ("左側のサイドバーから「ファイル選択」セクションでExcelファイルをアップロードしてください" if lang == 'ja' else "Please upload your Excel file in the 'File Upload' section on the left sidebar"))
    
    # Show status based on uploaded files
    if reference_file or target_file:
        # MODE TOGGLE: Risk Review vs Explanation Mode
        # Only show for single file analysis (not diff mode)
        if not (reference_file and target_file):
            st.markdown("---")
            mode = st.radio(
                "📊 " + ("分析モード" if lang == 'ja' else "Analysis Mode"),
                ["Risk Review", "Explanation Mode"],
                horizontal=True,
                key="app_mode",
                help=("リスク検出 vs 因果ツリー分析" if lang == 'ja' else "Risk Detection vs Causal Tree Analysis")
            )
            st.markdown("---")
        else:
            # Diff mode always uses Risk Review
            mode = "Risk Review"
        
        # Check if we're in diff mode
        is_diff_mode = reference_file and target_file
        
        # Get file name for header
        file_name = ""
        if is_diff_mode:
            file_name = f"{reference_file.name}, {target_file.name}"
        elif reference_file:
            file_name = reference_file.name
        elif target_file:
            file_name = target_file.name
        
        # Parse the file(s)
        st.markdown("---")
        
        # Clear previous debug logs
        st.session_state.debug_logs = []
        
        try:
            if is_diff_mode:
                # Parse both files with timing
                add_debug_log("INFO", f"Starting parse of {reference_file.name}")
                add_debug_log("INFO", f"File size: {len(reference_file.getvalue()) / 1024 / 1024:.2f} MB")
                
                start_time = time.time()
                
                with st.spinner(t('parsing', lang)):
                    old_bytes = reference_file.getvalue()
                    new_bytes = target_file.getvalue()
                    
                    # Parse old file
                    old_start = time.time()
                    old_model = parse_excel_file(old_bytes, reference_file.name)
                    old_time = time.time() - old_start
                    add_debug_log("SUCCESS", f"Parsed {reference_file.name} in {old_time:.2f}s", {
                        'sheets': len(old_model.sheets),
                        'cells': len(old_model.cells)
                    })
                    
                    # Parse new file
                    new_start = time.time()
                    new_model = parse_excel_file(new_bytes, target_file.name)
                    new_time = time.time() - new_start
                    add_debug_log("SUCCESS", f"Parsed {target_file.name} in {new_time:.2f}s", {
                        'sheets': len(new_model.sheets),
                        'cells': len(new_model.cells)
                    })
                
                total_time = time.time() - start_time
                st.session_state.parse_time = total_time
                
                st.caption(t('parsed_in', lang).format(time=f"{total_time:.2f}"))
                
                # Analyze both models
                # PHASE 5: Initialize Smart Context Recovery if API key provided
                smart_context = None
                if api_key:
                    smart_context = SmartContextRecovery(ai_provider, api_key)
                    add_debug_log("INFO", f"Smart Context Recovery enabled ({ai_provider})")
                
                analyzer = ModelAnalyzer(smart_context=smart_context)
                
                # Parse allowed constants
                allowed_values = []
                if allowed_constants:
                    try:
                        allowed_values = [float(x.strip()) for x in allowed_constants.split(',') if x.strip()]
                    except ValueError:
                        st.warning("⚠️ Invalid format in Allowed Constants. Using defaults.")
                        allowed_values = [30, 365]
                
                old_model = analyzer.analyze(old_model, fiscal_year_start, allowed_constants=allowed_values)
                new_model = analyzer.analyze(new_model, fiscal_year_start, allowed_constants=allowed_values)
                
                # Composite Key Matching Configuration
                st.markdown("### 🔑 Composite Key Matching")
                st.markdown("""
                Select key columns to match rows intelligently, even when rows are inserted, deleted, or reordered.
                **Example:** Use "Account Name" (勘定科目) to match P&L rows across months.
                """)
                
                # Sheet selector
                common_sheets = list(set(old_model.sheets) & set(new_model.sheets))
                if common_sheets:
                    selected_sheet = st.selectbox(
                        "Select Sheet to Compare",
                        options=common_sheets,
                        index=0,
                        help="Choose the sheet you want to analyze for changes"
                    )
                    
                    # Key column selector
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        key_columns_input = st.text_input(
                            "Key Columns (comma separated)",
                            value="A",
                            placeholder="e.g., A or A,B",
                            help="Enter column letters to use as composite key (e.g., 'A' for Account Name)"
                        )
                    
                    # Parse key columns
                    key_columns = [col.strip().upper() for col in key_columns_input.split(',') if col.strip()]
                    
                    # Validate uniqueness
                    if key_columns:
                        from src.diff import DiffEngine
                        diff_engine = DiffEngine()
                        
                        # Validate uniqueness for both files
                        try:
                            old_uniqueness, old_duplicates = diff_engine.validate_key_uniqueness(old_model, key_columns, selected_sheet)
                            new_uniqueness, new_duplicates = diff_engine.validate_key_uniqueness(new_model, key_columns, selected_sheet)
                            
                            # Use the lower uniqueness rate
                            uniqueness_rate = min(old_uniqueness, new_uniqueness)
                            
                            # Display uniqueness status
                            st.markdown("#### Key Uniqueness Validation")
                            
                            if uniqueness_rate >= 0.95:
                                st.success(f"✅ **Keys are unique** ({uniqueness_rate*100:.1f}% unique)")
                                st.markdown("These columns provide good matching accuracy.")
                            else:
                                st.error(f"⚠️ **Keys are not unique** ({uniqueness_rate*100:.1f}% unique)")
                                st.warning("""
                                **Warning:** These columns contain duplicate values, which will cause inaccurate row matching.
                                
                                **Recommendation:** Add another column like 'Department' or 'Category' to ensure unique keys.
                                
                                **Example:** Instead of just 'A', try 'A,B' to combine multiple columns.
                                """)
                                
                                # Show sample duplicates
                                if old_duplicates or new_duplicates:
                                    with st.expander("Show Duplicate Keys"):
                                        if old_duplicates:
                                            st.markdown(f"**Old File Duplicates:** {', '.join(old_duplicates[:5])}")
                                        if new_duplicates:
                                            st.markdown(f"**New File Duplicates:** {', '.join(new_duplicates[:5])}")
                            
                            # Preview Matches button
                            if st.button("🔍 Preview Row Matches", help="See how rows will be matched between files"):
                                st.markdown("#### Row Matching Preview")
                                
                                # Build keys for preview
                                old_keys = diff_engine.build_composite_keys(old_model, key_columns, selected_sheet)
                                new_keys = diff_engine.build_composite_keys(new_model, key_columns, selected_sheet)
                                
                                # Build row mapping
                                row_mapping = diff_engine._match_rows_by_composite_key(
                                    old_model, new_model, key_columns, selected_sheet
                                )
                                
                                if row_mapping:
                                    # Show sample mappings
                                    st.markdown(f"**Matched {len(row_mapping)} rows** between old and new files:")
                                    
                                    # Create preview table
                                    preview_data = []
                                    for old_row, new_row in sorted(list(row_mapping.items())[:10]):
                                        # Get key values
                                        old_key_obj = [k for k in old_keys.values() if k.row_number == old_row]
                                        new_key_obj = [k for k in new_keys.values() if k.row_number == new_row]
                                        
                                        key_value = old_key_obj[0].key_value if old_key_obj else "N/A"
                                        
                                        preview_data.append({
                                            "Key": key_value,
                                            "Old Row": old_row,
                                            "New Row": new_row,
                                            "Status": "✓ Matched"
                                        })
                                    
                                    df_preview = pd.DataFrame(preview_data)
                                    st.dataframe(df_preview, width="stretch", hide_index=True)
                                    
                                    if len(row_mapping) > 10:
                                        st.info(f"Showing first 10 of {len(row_mapping)} matched rows")
                                else:
                                    st.warning("No rows could be matched with the selected key columns")
                            
                        except Exception as e:
                            st.error(f"Error validating keys: {str(e)}")
                            key_columns = None
                    
                    st.markdown("---")
                else:
                    st.warning("No common sheets found between the two files")
                    selected_sheet = None
                    key_columns = None
                
                # Run diff analysis
                from src.diff import DiffEngine
                diff_engine = DiffEngine()
                
                # Use composite key matching if configured
                if 'selected_sheet' in locals() and selected_sheet and 'key_columns' in locals() and key_columns:
                    diff_result = diff_engine.compare(old_model, new_model, key_columns, selected_sheet)
                else:
                    diff_result = diff_engine.compare(old_model, new_model)
                
                # Display diff summary
                st.markdown("### 📊 Comparison Summary")
                
                # Show improvement message
                if diff_result.is_improved():
                    st.success(f"🎉 **Model Health Improved!**")
                elif diff_result.is_degraded():
                    st.warning(f"⚠️ **Model Health Decreased**")
                else:
                    st.info(f"➡️ **No Change in Health Score**")
                
                # Show score delta
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Old Score", diff_result.old_score)
                with col2:
                    st.metric("New Score", diff_result.new_score, delta=diff_result.score_delta)
                with col3:
                    delta_str = f"+{diff_result.score_delta}" if diff_result.score_delta > 0 else str(diff_result.score_delta)
                    st.metric("Change", delta_str)
                
                # Show categorized changes
                st.markdown("---")
                st.markdown("#### 📋 Changes Detected")
                
                tab1, tab2, tab3 = st.tabs(["Improved", "Degraded", "Structural"])
                
                with tab1:
                    if diff_result.improved_risks:
                        st.success(f"✅ **{len(diff_result.improved_risks)} Risks Fixed**")
                        for risk in diff_result.improved_risks:
                            st.markdown(f"- **{risk.risk_type}** at {risk.get_location()}: {risk.description}")
                    else:
                        st.info("No improvements detected")
                
                with tab2:
                    if diff_result.degraded_risks:
                        st.warning(f"⚠️ **{len(diff_result.degraded_risks)} New Risks**")
                        for risk in diff_result.degraded_risks:
                            st.markdown(f"- **{risk.risk_type}** at {risk.get_location()}: {risk.description}")
                    else:
                        st.info("No new risks detected")
                
                with tab3:
                    if diff_result.structural_changes:
                        st.info(f"**{len(diff_result.structural_changes)} Structural Changes**")
                        for change in diff_result.structural_changes:
                            st.markdown(f"- {change}")
                    else:
                        st.info("No structural changes detected")
                
            else:
                # Single file analysis
                file_to_analyze = reference_file if reference_file else target_file
                file_name = file_to_analyze.name
                file_bytes = file_to_analyze.getvalue()
                
                # Create cache key based on file content and settings
                import hashlib
                file_hash = hashlib.md5(file_bytes).hexdigest()
                cache_key = f"{file_name}_{file_hash}_{fiscal_year_start}_{allowed_constants}_{api_key[:8] if api_key else 'no_ai'}"
                
                # Initialize analyzer (needed for both cached and fresh analysis)
                smart_context = None
                if api_key:
                    smart_context = SmartContextRecovery(ai_provider, api_key)
                analyzer = ModelAnalyzer(smart_context=smart_context)
                
                # Check if we have cached analysis for this exact file + settings
                if "analysis_cache_key" in st.session_state and st.session_state.analysis_cache_key == cache_key:
                    # Use cached model (instant!)
                    model = st.session_state.cached_model
                    parse_time = st.session_state.parse_time
                    add_debug_log("INFO", f"Using cached analysis for {file_name} (instant)")
                else:
                    # Fresh analysis needed
                    file_size_mb = len(file_bytes) / 1024 / 1024
                    add_debug_log("INFO", f"Starting parse of {file_name}")
                    add_debug_log("INFO", f"File size: {file_size_mb:.2f} MB")
                    
                    # Show spinner while parsing
                    start_time = time.time()
                    with st.spinner("🔄 Parsing Excel model... This may take a minute."):
                        # Parse the file
                        model = parse_excel_file(file_bytes, file_name)
                    
                    parse_time = time.time() - start_time
                    st.session_state.parse_time = parse_time
                    
                    add_debug_log("SUCCESS", f"Parsed {file_name} in {parse_time:.2f}s", {
                        'sheets': len(model.sheets),
                        'cells': len(model.cells),
                        'merged_ranges': sum(len(ranges) for ranges in model.merged_ranges.values())
                    })
                    
                    # Parse allowed constants
                    allowed_values = []
                    if allowed_constants:
                        try:
                            allowed_values = [float(x.strip()) for x in allowed_constants.split(',') if x.strip()]
                        except ValueError:
                            st.warning("⚠️ Invalid format in Allowed Constants. Using defaults.")
                            allowed_values = [30, 365]
                    
                    # Run risk analysis (analyzer already initialized above)
                    if api_key:
                        add_debug_log("INFO", f"Smart Context Recovery enabled ({ai_provider})")
                    
                    model = analyzer.analyze(model, fiscal_year_start, allowed_constants=allowed_values)
                    
                    # Calculate maturity level
                    maturity_score = analyzer.calculate_maturity_level_heuristic(model)
                    model.maturity_level = maturity_score.level.value  # Store maturity level in model
                    
                    # Cache the analyzed model
                    st.session_state.cached_model = model
                    st.session_state.analysis_cache_key = cache_key
                    add_debug_log("SUCCESS", f"Analysis cached for future use")
            
            # Route to appropriate mode
            if mode == "Explanation Mode":
                # NEW: Explanation Mode UI
                from src.explanation_mode import render_explanation_mode
                render_explanation_mode(model, lang)
            else:
                # Existing: Risk Review Mode
                # Display risks in tabs
                if model.risks:
                    # PHASE 9: Professional Minimalism & Master-Detail Layout ("The Cockpit")
                    # Bloomberg Terminal-style interface for finance professionals
                    from src.analyzer import RiskTriageEngine
                    from src.models import RiskCategory
                    from src.master_detail_ui import (
                        render_master_risk_table,
                        render_detail_panel,
                        inject_professional_css,
                        sort_risks_by_priority,
                        render_professional_header,
                        render_master_detail_ui
                    )
                    
                    # Inject professional CSS
                    inject_professional_css()
                    
                    # Render professional header with metrics dashboard
                    render_professional_header(model, file_name, parse_time, lang)
                    
                    # Interactive Dependency Visualization (controlled by header checkbox)
                    if st.session_state.get("show_dep_graph", False):
                        st.markdown("##### Interactive Dependency Visualization")
                        
                        # Limit nodes for performance
                        max_nodes = 500
                        total_nodes = model.dependency_graph.number_of_nodes()
                        
                        if total_nodes > max_nodes:
                            st.warning(f"⚠️ Graph has {total_nodes} nodes. Showing first {max_nodes} for performance.")
                        
                        # Build graph for visualization
                        nodes = []
                        edges = []
                        
                        node_list = list(model.dependency_graph.nodes())[:max_nodes]
                        
                        # Create nodes with risk-based coloring
                        for node in node_list:
                            # Determine color based on risk
                            color = "#90EE90"  # Green default (no risk)
                            size = 10
                            
                            for risk in model.risks:
                                if risk.get_location() == node:
                                    if risk.severity == "Critical":
                                        color = "#FF6B6B"  # Red
                                        size = 15
                                    elif risk.severity == "High":
                                        color = "#FFD93D"  # Yellow
                                        size = 12
                                    break
                            
                            # Extract sheet and address for label
                            if '!' in node:
                                sheet, addr = node.split('!')
                                label = addr
                            else:
                                label = node
                            
                            nodes.append(Node(id=node, label=label, size=size, color=color))
                        
                        # Add edges
                        edge_count = 0
                        for node in node_list:
                            for successor in model.dependency_graph.successors(node):
                                if successor in node_list:
                                    edges.append(Edge(source=node, target=successor))
                                    edge_count += 1
                                    if edge_count > 1000:  # Limit edges for performance
                                        break
                            if edge_count > 1000:
                                break
                        
                        # Configure graph
                        config = Config(
                            width="100%",
                            height=600,
                            directed=True,
                            physics=True,
                            hierarchical=False,
                            nodeHighlightBehavior=True,
                            highlightColor="#F7A7A6",
                            collapsible=False,
                            node={'labelProperty': 'label'},
                            link={'labelProperty': 'label', 'renderLabel': False}
                        )
                        
                        # Render graph
                        if nodes:
                            agraph(nodes=nodes, edges=edges, config=config)
                            
                            st.caption("""
                            **Legend:** 🔴 Critical Risk | 🟡 High Risk | 🟢 No Risk
                            
                            **Tip:** Click and drag nodes to explore. Zoom with mouse wheel. Larger nodes = higher risk.
                            """)
                        else:
                            st.info("No dependencies to visualize")
                        
                        st.markdown("---")
                    
                    # Classify risks by business impact
                    triage = RiskTriageEngine(model.risks)
                    triage.classify_all()
                    counts = triage.get_tab_counts()
                    
                    # Create tabs with File Information as first tab
                    tab0, tab1, tab2, tab3 = st.tabs([
                    t('tab_file_info', lang),
                    f"{t('tab_fatal_errors', lang)} ({counts['fatal']})",
                    f"{t('tab_integrity_risks', lang)} ({counts['integrity']})",
                    f"{t('tab_structural_debt', lang)} ({counts['structural']})"
                    ])
                    
                    with tab0:
                        # Tab 0: File Information
                        st.markdown(f"### {t('file_details', lang)}")
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric(t('metric_sheets', lang), len(model.sheets))
                        
                        with col2:
                            st.metric(t('metric_cells', lang), len(model.cells))
                        
                        with col3:
                            # Count cells with formulas
                            formula_count = sum(1 for cell in model.cells.values() if cell.formula)
                            st.metric(t('metric_formulas', lang), formula_count)
                        
                        # Show sheet names
                        st.markdown(f"#### {t('sheets_in_workbook', lang)}")
                        for i, sheet in enumerate(model.sheets, 1):
                            st.write(f"{i}. {sheet}")
                        
                        # Show merged ranges if any
                        if model.merged_ranges:
                            st.markdown(f"#### {t('merged_ranges', lang)}")
                            for sheet, ranges in model.merged_ranges.items():
                                if ranges:
                                    st.write(f"**{sheet}:** {', '.join(ranges)}")
                        
                        # Show dependency graph info
                        st.markdown(f"#### {t('dependency_graph', lang)}")
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.metric(t('metric_nodes', lang), model.dependency_graph.number_of_nodes())
                        
                        with col2:
                            st.metric(t('metric_edges', lang), model.dependency_graph.number_of_edges())
                    
                    with tab1:
                        # Tab 1: Fatal Errors - MASTER-DETAIL LAYOUT
                        st.caption(t('fatal_caption', lang))
                        
                        # Help expander
                        with st.expander(t('help_fatal_title', lang)):
                            st.markdown(f"""
                            **{t('help_fatal_title', lang)}**
                            
                            {t('help_fatal_desc', lang)}:
                            
                            - {t('help_fatal_circular', lang)}
                            - {t('help_fatal_external', lang)}
                            - {t('help_fatal_formula_error', lang)}
                            
                            {t('help_fatal_priority', lang)}
                            """)
                        
                        if triage.fatal_errors:
                            # Task 39: Integration - Use Master-Detail UI with Risk Review
                            render_master_detail_ui(triage.fatal_errors, model, lang, tab_key='fatal_errors')
                        else:
                            st.success(t('no_fatal_errors', lang))
                    
                    with tab2:
                        # Tab 2: Integrity Risks - MASTER-DETAIL LAYOUT
                        st.caption(t('integrity_caption', lang))
                        
                        # Help expander
                        with st.expander(t('help_integrity_title', lang)):
                            st.markdown(f"""
                            **{t('help_integrity_title', lang)}**
                            
                            {t('help_integrity_desc', lang)}:
                            
                            - {t('help_integrity_inconsistent', lang)}
                            - {t('help_integrity_value', lang)}
                            - {t('help_integrity_row', lang)}
                            - {t('help_integrity_logic', lang)}
                            
                            {t('help_integrity_priority', lang)}
                            """)
                        
                        if triage.integrity_risks:
                            # Task 39: Integration - Use Master-Detail UI with Risk Review
                            render_master_detail_ui(triage.integrity_risks, model, lang, tab_key='integrity_risks')
                        else:
                            st.success(t('no_integrity_risks', lang))
                    
                    with tab3:
                        # Tab 3: Structural Debt - MASTER-DETAIL LAYOUT
                        st.caption(t('structural_caption', lang))
                        
                        # Help expander
                        with st.expander(t('help_structural_title', lang)):
                            st.markdown(f"""
                            **{t('help_structural_title', lang)}**
                            
                            {t('help_structural_desc', lang)}:
                            
                            - {t('help_structural_hardcode', lang)}
                            - {t('help_structural_merged', lang)}
                            
                            {t('help_structural_priority', lang)}
                            """)
                        
                        if triage.structural_debt:
                            # Task 39: Integration - Use Master-Detail UI with Risk Review
                            render_master_detail_ui(triage.structural_debt, model, lang, tab_key='structural_debt')
                        else:
                            st.success(t('no_structural_debt', lang))
                    
                    # Driver X-Ray tab is hidden but code preserved for future use
                    # Driver X-Ray section (currently disabled)
                    # Uncomment the code below to re-enable Driver X-Ray
                    """
                    # PRIORITY 2: Calculate Top 3 Most Dangerous Hardcodes
                    # Rank by: 1) Impact count, 2) KPI involvement, 3) Severity
                    
                    hardcode_risks = [r for r in model.risks if r.risk_type == "Hidden Hardcode"]
                    
                    if hardcode_risks:
                        # [Driver X-Ray implementation code here]
                        pass
                    else:
                        st.info(t('xray_no_risks', lang))
                    """
                
                else:
                    st.success(t('no_risks', lang))
                # End of Risk Review Mode
            
        except ValueError as e:
            # Handle expected errors with Guardian tone
            add_debug_log("ERROR", "File validation error", {
                'error_type': 'ValueError',
                'message': str(e)
            })
            st.error(f"**{t('error_attention', lang)}**")
            st.error(str(e))
            st.info(t('error_tip', lang))
            
            # Show debug log
            with st.expander(t('show_debug_log', lang)):
                for log in st.session_state.debug_logs:
                    st.write(f"[{log['timestamp']}] {log['level']}: {log['message']}")
                    if log['details']:
                        st.json(log['details'])
        
        except Exception as e:
            # Handle unexpected errors
            add_debug_log("ERROR", "Unexpected error during analysis", {
                'error_type': type(e).__name__,
                'message': str(e),
                'traceback': str(e.__traceback__)
            })
            st.error(f"**{t('error_unexpected', lang)}**")
            st.error(t('error_unexpected_desc', lang).format(error=str(e)))
            st.info(t('error_tip_contact', lang))
            
            # Show debug log
            with st.expander(t('show_debug_log', lang)):
                for log in st.session_state.debug_logs:
                    st.write(f"[{log['timestamp']}] {log['level']}: {log['message']}")
                    if log['details']:
                        st.json(log['details'])

if __name__ == "__main__":
    main()
