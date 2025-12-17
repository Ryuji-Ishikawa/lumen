"""
Master-Detail UI Components for Professional Minimalism Layout
Bloomberg Terminal-style interface for finance professionals
"""

import streamlit as st
import pandas as pd
from typing import List, Optional, Dict, Any
from src.models import RiskAlert, ModelAnalysis
from src.risk_review import render_risk_review_interface


def sort_risks_by_priority(risks: List[RiskAlert]) -> List[RiskAlert]:
    """
    Sort risks by severity (desc) then impact count (desc).
    
    Ensures most dangerous risk is always at top.
    """
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    
    return sorted(
        risks,
        key=lambda r: (
            severity_order.get(r.severity, 99),
            -r.details.get("impact_count", 0)
        )
    )


def format_context(row_label: Optional[str], col_label: Optional[str], lang: str = 'ja') -> str:
    """
    Format context label for display.
    
    Rules:
    - If col_label looks like a date (YYYY-MM, Q1, FY2024), don't show it
    - Only show row_label for cleaner context
    - Date columns are not useful context for users
    """
    import re
    
    # Check if col_label is a date pattern
    is_date_column = False
    if col_label:
        date_patterns = [
            r'\d{2}-\d{4}',  # 04-2024
            r'\d{4}-\d{2}',  # 2024-04
            r'[A-Z][a-z]{2}\s+\d{4}',  # Apr 2024
            r'Q\d',  # Q1, Q2, etc.
            r'FY\s*\d{4}',  # FY2024, FY 2024
        ]
        for pattern in date_patterns:
            if re.search(pattern, col_label):
                is_date_column = True
                break
    
    # Format context
    if row_label and col_label and not is_date_column:
        # Non-date column: show both
        return f"{row_label} @ {col_label}"
    elif row_label:
        # Date column or no column: show only row label
        return row_label
    elif col_label and not is_date_column:
        return col_label
    else:
        # No context available - show localized message
        return "（項目名不明）" if lang == 'ja' else "(No context)"


def truncate_value(value: Any, max_length: int = 30) -> str:
    """Truncate value for display"""
    value_str = str(value) if value is not None else ""
    if len(value_str) > max_length:
        return value_str[:max_length] + "..."
    return value_str


def translate_risk_type(risk_type: str, lang: str = 'ja') -> str:
    """Translate risk type name to the specified language"""
    from src.i18n import t
    
    # Create mapping key from risk type
    key_map = {
        "Hidden Hardcode": "risk_type_hidden_hardcode",
        "Inconsistent Formula": "risk_type_inconsistent_formula",
        "Inconsistent Value": "risk_type_inconsistent_value",
        "Row Inconsistency": "risk_type_inconsistent_formula",  # Unified with Inconsistent Formula
        "Value Conflict": "risk_type_value_conflict",
        "Circular Reference": "risk_type_circular_reference",
        "External Link": "risk_type_external_link",
        "Formula Error": "risk_type_formula_error",
        "Merged Cell": "risk_type_merged_cell",
        "Logic Alert": "risk_type_logic_alert",
    }
    
    key = key_map.get(risk_type)
    if key:
        return t(key, lang)
    return risk_type  # Fallback to original if not found


def translate_description(description: str, lang: str = 'ja') -> str:
    """Translate risk description to the specified language"""
    import re
    
    if lang != 'ja':
        return description
    
    # Pattern 1: "Formula pattern differs from X other cells in this row. [Likelihood]."
    pattern1 = r'Formula pattern differs from (\d+) other cells in this row\. (.+)\.'
    match1 = re.match(pattern1, description)
    if match1:
        count = match1.group(1)
        likelihood = match1.group(2)
        
        # Translate likelihood assessment
        likelihood_ja = likelihood
        if "Likely error" in likelihood:
            likelihood_ja = "エラーの可能性が高い"
        elif "Uncertain" in likelihood:
            likelihood_ja = "不確実"
        elif "Possibly intentional" in likelihood:
            likelihood_ja = "意図的な可能性あり"
        elif "Likely intentional" in likelihood:
            if "single column difference" in likelihood:
                likelihood_ja = "意図的な可能性が高い（単一列の違い）"
            else:
                likelihood_ja = "意図的な可能性が高い"
        
        return f"この行の他の{count}個のセルとは数式パターンが異なります。{likelihood_ja}。"
    
    # Pattern 2: "Hardcoded value 'X' (Y instances)"
    pattern2 = r"Hardcoded value '(.+)' \((\d+) instances\)"
    match2 = re.match(pattern2, description)
    if match2:
        value = match2.group(1)
        count = match2.group(2)
        return f"ベタ打ち値 '{value}' （{count}箇所）"
    
    # Pattern 3: "Inconsistent formula pattern (X instances)"
    pattern3 = r'Inconsistent formula pattern \((\d+) instances\)'
    match3 = re.match(pattern3, description)
    if match3:
        count = match3.group(1)
        return f"数式パターンの不整合（{count}箇所）"
    
    # Pattern 4: "External link detected (X instances)"
    pattern4 = r'External link detected \((\d+) instances\)'
    match4 = re.match(pattern4, description)
    if match4:
        count = match4.group(1)
        return f"外部リンクを検出（{count}箇所）"
    
    # Pattern 5: "Conflicting values detected (X instances)"
    pattern5 = r'Conflicting values detected \((\d+) instances\)'
    match5 = re.match(pattern5, description)
    if match5:
        count = match5.group(1)
        return f"値の競合を検出（{count}箇所）"
    
    # Fallback: return original if no pattern matches
    return description


def render_master_risk_table(risks: List[RiskAlert], table_key: str = "master_risk_table", lang: str = 'ja') -> Optional[int]:
    """
    Render master risk table grouped by Risk Type.
    
    Args:
        risks: List of risk alerts to display
        table_key: Unique key for this table instance
        lang: Language code for translations
    
    Returns: Selected risk index (None if no selection)
    """
    from src.i18n import t
    
    if not risks:
        st.info("No risks detected")
        return None
    
    # Sort risks by priority first
    sorted_risks = sort_risks_by_priority(risks)
    
    # Group risks by Risk Type
    from collections import defaultdict
    risk_groups = defaultdict(list)
    for i, risk in enumerate(sorted_risks):
        risk_groups[risk.risk_type].append((i, risk))
    
    selected_index = None
    selected_risk = None
    
    # Display each Risk Type group
    for risk_type, group_risks in risk_groups.items():
        # Translate risk type name
        translated_risk_type = translate_risk_type(risk_type, lang)
        
        # Risk Type header with count - same size as "Risk Table"
        st.markdown(f'<p style="font-size: 18px; font-weight: 600; margin-bottom: 0.5rem;"><strong>{translated_risk_type}</strong> ({len(group_risks)} items)</p>', unsafe_allow_html=True)
        
        # Prepare table data for this group
        table_data = []
        index_mapping = []  # Map table row to original risk index
        
        for original_index, risk in group_risks:
            # Get value from multiple possible sources with better fallback
            # For Inconsistent Formula, prioritize formula over value
            value = None
            if risk.risk_type == "Inconsistent Formula":
                # For formula inconsistencies, show the formula first
                if "formula" in risk.details and risk.details["formula"]:
                    value = risk.details["formula"]
                elif "value" in risk.details and risk.details["value"] is not None:
                    value = risk.details["value"]
                elif "cell_value" in risk.details and risk.details["cell_value"] is not None:
                    value = risk.details["cell_value"]
            else:
                # For other risk types, prioritize value
                if "value" in risk.details and risk.details["value"] is not None:
                    value = risk.details["value"]
                elif "cell_value" in risk.details and risk.details["cell_value"] is not None:
                    value = risk.details["cell_value"]
                elif "hardcoded_value" in risk.details and risk.details["hardcoded_value"] is not None:
                    value = risk.details["hardcoded_value"]
                elif "formula" in risk.details and risk.details["formula"]:
                    value = risk.details["formula"]
            
            # Fallback to empty string if nothing found
            if value is None:
                value = ""
            
            table_data.append({
                t('table_location', lang): f"{risk.sheet}!{risk.cell}",
                t('table_context', lang): format_context(risk.row_label, risk.col_label, lang),
                t('table_value', lang): truncate_value(value, max_length=30),
                t('table_severity', lang): risk.severity,
                t('table_impact', lang): risk.details.get("impact_count", 0)
            })
            index_mapping.append(original_index)
        
        # Create DataFrame for this group
        df = pd.DataFrame(table_data)
        
        # Get translated column names for styling
        severity_col = t('table_severity', lang)
        
        # Apply conditional formatting with white background and dark text
        def style_row(row):
            if row[severity_col] in ["Critical", "High"]:
                # Light red background for danger with dark red text
                return ["background-color: #FEE2E2; color: #991B1B; font-weight: 600"] * len(row)
            else:
                # White background with dark text
                return ["background-color: #FFFFFF; color: #111827"] * len(row)
        
        # Apply header styling - light gray background with dark text
        def style_header(s):
            return ["background-color: #F3F4F6; color: #111827; font-weight: 600"] * len(s)
        
        styled_df = df.style.apply(style_row, axis=1).apply(style_header, axis=0)
        
        # Display table with selection (unique key per group)
        group_key = f"{table_key}_{risk_type.replace(' ', '_').replace('/', '_')}"
        event = st.dataframe(
            styled_df,
            selection_mode="single-row",
            use_container_width=True,
            height=min(200 + len(group_risks) * 35, 400),  # Dynamic height per group
            hide_index=True,
            on_select="rerun",
            key=group_key
        )
        
        # Check if a row was selected in this group
        if event and hasattr(event, 'selection') and event.selection.get('rows'):
            selected_rows = event.selection['rows']
            if selected_rows:
                # Map back to original risk index and get the actual risk object
                selected_index = index_mapping[selected_rows[0]]
                selected_risk = sorted_risks[selected_index]
        
        # Add spacing between groups
        st.markdown("---")
    
    # Return the selected risk object directly instead of index
    return selected_risk


def render_detail_panel(risk: Optional[RiskAlert], model: ModelAnalysis, lang: str = 'ja'):
    """
    Render detail panel for selected risk.
    
    Shows Logic X-Ray and AI Cure sections.
    """
    from src.i18n import t
    
    if risk is None:
        # No selection - show instructions
        select_msg = t('select_risk', lang)
        st.info(select_msg)
        
        # Add warning about first click behavior (Streamlit limitation)
        if lang == 'ja':
            st.caption("「詳細」を初回クリック時のみ、「ファイル情報」タブにジャンプする場合があります。2回目以降は正常に動作します。")
        else:
            st.caption("First click on 'Detail' may jump to 'File Info' tab. Subsequent clicks will work normally.")
        return
    
    # Risk selected - show details
    st.markdown("---")
    
    # Risk header
    location_label = "Location" if lang == 'en' else "場所"
    context_label = "Context" if lang == 'en' else "項目名"
    type_label = "Type" if lang == 'en' else "リスクのタイプ"
    severity_label = "Severity" if lang == 'en' else "重要度"
    desc_label = "Description" if lang == 'en' else "説明"
    
    st.markdown(f"**{location_label}:** `{risk.sheet}!{risk.cell}`")
    if risk.get_context():
        st.markdown(f"**{context_label}:** {risk.get_context()}")
    
    # Translate risk type to Japanese
    translated_risk_type = translate_risk_type(risk.risk_type, lang)
    st.markdown(f"**{type_label}:** {translated_risk_type}")
    
    # Translate severity to Japanese
    severity_ja = {
        "Critical": "最優先",
        "High": "高",
        "Medium": "中",
        "Low": "低"
    }
    severity_display = severity_ja.get(risk.severity, risk.severity) if lang == 'ja' else risk.severity
    st.markdown(f"**{severity_label}:** {severity_display}")
    
    # Show description with likelihood assessment
    if risk.description:
        # Translate description to Japanese if needed
        translated_desc = translate_description(risk.description, lang)
        st.markdown(f"**{desc_label}:** {translated_desc}")
    
    st.markdown("---")
    
    # Section A: Logic X-Ray
    render_logic_xray(risk, model, lang)
    
    st.markdown("---")
    
    # Section B: Logic Translator (Formula Meaning)
    render_logic_translator(risk, model, lang)
    
    st.markdown("---")
    
    # Section C: The Cure (Suggest Fix)
    render_ai_cure(risk, model, lang)


def render_logic_xray(risk: RiskAlert, model: ModelAnalysis, lang: str = 'ja'):
    """
    Render dependency trace for selected risk.
    
    Shows structured view with Excel terminology:
    - Precedents (参照元): cells this cell depends on
    - Current (分析対象): the selected risk cell
    - Dependents (影響先): cells that depend on this cell
    """
    title = "Logic X-Ray" if lang == 'en' else "ロジックX線"
    # Match "数式の不整合" font size (18px, font-weight 600)
    st.markdown(f'<p style="font-size: 18px; font-weight: 600; margin-bottom: 0.5rem;">{title}</p>', unsafe_allow_html=True)
    
    # Show note for compressed risks (ranges)
    # Match table description style (14px, color #1F2937)
    if ':' in risk.cell or ',' in risk.cell:
        first_cell = risk.cell.split(':')[0] if ':' in risk.cell else risk.cell.split(',')[0].strip()
        note_text = f"Showing dependencies for {first_cell} (representative of {risk.cell})" if lang == 'en' else f"{first_cell} の依存関係を表示中（{risk.cell} の代表）"
        st.markdown(f'<p style="font-size: 14px; color: #1F2937; margin-bottom: 0.5rem;">{note_text}</p>', unsafe_allow_html=True)
    
    # Get dependency trace
    trace = get_dependency_trace(risk, model, lang)
    
    if not trace:
        no_dep_text = "No dependencies found" if lang == 'en' else "依存関係が見つかりません"
        st.markdown(f'<p style="font-size: 14px; color: #1F2937; margin-bottom: 0.5rem;">{no_dep_text}</p>', unsafe_allow_html=True)
        return
    
    # Find current cell index
    cell_for_trace = risk.cell
    if ':' in risk.cell:
        cell_for_trace = risk.cell.split(':')[0]
    elif ',' in risk.cell:
        cell_for_trace = risk.cell.split(',')[0].strip()
    
    current_index = next((i for i, t in enumerate(trace) if t['sheet'] == risk.sheet and t['address'] == cell_for_trace), 0)
    
    # Split trace into sections
    precedents = trace[:current_index]
    current_cell = trace[current_index] if current_index < len(trace) else None
    dependents = trace[current_index + 1:]
    
    # Section 1: Precedents (参照元)
    if precedents:
        if lang == 'ja':
            st.markdown("**【 参照元 】** このセルの値を決めている要素")
        else:
            st.markdown("**[ Precedents ]** Elements determining this cell's value")
        
        precedent_lines = []
        prev_sheet = None
        for cell_info in precedents:
            sheet = cell_info['sheet']
            address = cell_info['address']
            label = cell_info.get('label', 'No context' if lang == 'en' else 'コンテキストなし')
            
            if sheet == prev_sheet:
                cell_ref = address
            else:
                cell_ref = f"{sheet}!{address}"
                prev_sheet = sheet
            
            precedent_lines.append(f'<span style="color: #1F2937;">  • {cell_ref} ({label})</span>')
        
        precedent_html = "<br>".join(precedent_lines)
        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; padding: 12px; border-radius: 4px; border: 1px solid #D1D5DB;
                        font-family: monospace; font-size: 13px; line-height: 1.8; color: #1F2937;">
                {precedent_html}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("")  # Spacing
    
    # Section 2: Current Cell (分析対象)
    if current_cell:
        if lang == 'ja':
            st.markdown("**【 分析対象 】**")
        else:
            st.markdown("**[ Target Cell ]**")
        
        sheet = current_cell['sheet']
        address = current_cell['address']
        label = current_cell.get('label', 'No context' if lang == 'en' else 'コンテキストなし')
        cell_ref = f"{sheet}!{address}"
        
        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; padding: 12px; border-radius: 4px; border: 1px solid #D1D5DB;
                        font-family: monospace; font-size: 13px; line-height: 1.8; color: #1F2937;">
                <span style="color: #1F2937; background-color: #F3F4F6; padding: 3px 8px; border-radius: 3px; font-size: 15px; font-weight: 600;">  {cell_ref}</span> <span style="color: #1F2937;">({label})</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("")  # Spacing
    
    # Section 3: Dependents (影響先)
    if dependents:
        if lang == 'ja':
            st.markdown("**【 影響先 】** このセルを使って計算している箇所")
        else:
            st.markdown("**[ Dependents ]** Places calculating using this cell")
        
        dependent_lines = []
        prev_sheet = None
        for cell_info in dependents:
            sheet = cell_info['sheet']
            address = cell_info['address']
            label = cell_info.get('label', 'No context' if lang == 'en' else 'コンテキストなし')
            
            if sheet == prev_sheet:
                cell_ref = address
            else:
                cell_ref = f"{sheet}!{address}"
                prev_sheet = sheet
            
            dependent_lines.append(f'<span style="color: #1F2937;">  • {cell_ref} ({label})</span>')
        
        dependent_html = "<br>".join(dependent_lines)
        st.markdown(
            f"""
            <div style="background-color: #FFFFFF; padding: 12px; border-radius: 4px; border: 1px solid #D1D5DB;
                        max-height: 300px; overflow-y: auto; font-family: monospace; 
                        font-size: 13px; line-height: 1.8; color: #1F2937;">
                {dependent_html}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown("")  # Spacing
    
    # Footer: Impact Summary
    # Match table description style (14px, color #1F2937)
    downstream_count = len(dependents)
    
    if downstream_count > 0:
        if lang == 'ja':
            summary_text = f"影響範囲サマリ: このセルを変更すると、少なくとも {downstream_count}箇所 のセル計算結果が変わります。（上位10件を表示中）"
        else:
            summary_text = f"Impact Summary: Changing this cell will affect at least {downstream_count} cells. (Showing top 10)"
        st.markdown(f'<p style="font-size: 14px; color: #1F2937; margin-top: 0.5rem;">{summary_text}</p>', unsafe_allow_html=True)
    else:
        if lang == 'ja':
            summary_text = "影響範囲サマリ: このセルには下流の依存関係がありません。"
        else:
            summary_text = "Impact Summary: This cell has no downstream dependencies."
        st.markdown(f'<p style="font-size: 14px; color: #1F2937; margin-top: 0.5rem;">{summary_text}</p>', unsafe_allow_html=True)


def render_logic_translator(risk: RiskAlert, model: ModelAnalysis, lang: str = 'ja'):
    """
    Render Logic Translator section - translates formula to semantic labels.
    
    Purpose: Excel Understanding (Readability)
    - Shows what the formula means in plain language
    - Helps users understand complex formulas without jumping between sheets
    
    Example:
    - Original: =F12*F13+G12*G13
    - Translated: =[Unit Price] * [Quantity] + [Tax Rate] * [Subtotal]
    """
    # Get formula from risk details or model.cells
    formula = risk.details.get("formula", "")
    
    # If formula not in details (compressed risk), try to get from model.cells
    if not formula and model and model.cells:
        # Extract first cell from compressed risk
        first_cell = risk.cell
        if ':' in risk.cell:
            first_cell = risk.cell.split(':')[0]
        elif ',' in risk.cell:
            first_cell = risk.cell.split(',')[0].strip()
        
        # Look up cell in model
        cell_key = f"{risk.sheet}!{first_cell}"
        if cell_key in model.cells:
            cell_info = model.cells[cell_key]
            formula = cell_info.formula or ""
    
    # Only show if formula exists
    if not formula:
        return
    
    title = "数式の意味" if lang == 'ja' else "Formula Meaning"
    st.markdown(f"#### {title}")
    
    # Translate formula using existing method
    from src.analyzer import ModelAnalyzer
    analyzer = ModelAnalyzer()
    
    # Extract sheet and address from risk
    sheet = risk.sheet
    cell_address = risk.cell
    if ':' in cell_address:
        cell_address = cell_address.split(':')[0]
    elif ',' in cell_address:
        cell_address = cell_address.split(',')[0].strip()
    
    translated = analyzer.translate_formula_to_labels(formula, cell_address, model.cells, sheet)
    
    # Show original and translated formulas
    if lang == 'ja':
        st.markdown(f"""
**元の数式:**
```
{formula if formula.startswith('=') else '=' + formula}
```

**意味:**
```
{translated}
```
""")
        st.caption("💡 この翻訳により、数式が何を参照しているか一目で分かります。シートをジャンプして確認する必要がありません。")
    else:
        st.markdown(f"""
**Original Formula:**
```
{formula if formula.startswith('=') else '=' + formula}
```

**Meaning:**
```
{translated}
```
""")
        st.caption("💡 This translation shows what the formula references at a glance. No need to jump between sheets.")


def render_ai_cure(risk: RiskAlert, model: ModelAnalysis, lang: str = 'ja'):
    """
    Render suggestion section - Rule-based for Hidden Hardcode only.
    
    Design Decision:
    - Hidden Hardcode: Rule-based suggestions (no AI needed - fixes are standardized)
    - Inconsistent Formula: No suggestions (use Logic Translator instead)
    - Other risks: No suggestions (simple warnings are sufficient)
    """
    # ONLY show for Hidden Hardcode risks
    if risk.risk_type != "Hidden Hardcode":
        return  # No suggest fix for other risk types
    
    title = "修正案" if lang == 'ja' else "Suggested Fix"
    st.markdown(f"#### {title}")
    
    # Generate rule-based suggestion (no AI needed)
    hardcoded_value = risk.details.get("hardcoded_value", "")
    row_label = risk.row_label or ("この項目" if lang == 'ja' else "this item")
    col_label = risk.col_label or ("この期間" if lang == 'ja' else "this period")
    
    # Get formula for example
    formula = risk.details.get("formula", "")
    
    # If formula not in details (compressed risk), try to get from model.cells
    if not formula and model and model.cells:
        # Extract first cell from compressed risk (e.g., "AZ19:BW19" -> "AZ19")
        first_cell = risk.cell
        if ':' in risk.cell:
            first_cell = risk.cell.split(':')[0]
        elif ',' in risk.cell:
            first_cell = risk.cell.split(',')[0].strip()
        
        # Look up cell in model
        cell_key = f"{risk.sheet}!{first_cell}"
        if cell_key in model.cells:
            cell_info = model.cells[cell_key]
            formula = cell_info.formula or ""
    
    # Generate example variable name based on row label
    example_var_name = "変数名"
    if row_label and row_label != "この項目":
        # Clean row label for variable name (remove special characters)
        clean_label = row_label.replace(" ", "_").replace("(", "").replace(")", "").replace("*", "")
        example_var_name = f"{clean_label}_係数"
    
    # Create before/after formula example
    formula_before = ""
    formula_after = ""
    if formula:
        # Show original formula (ensure it starts with =)
        formula_before = f"={formula}" if not formula.startswith('=') else formula
        
        # Create example with variable name replacing hardcoded value
        # Try to replace the hardcoded value in the formula
        if str(hardcoded_value) in formula_before:
            formula_after = formula_before.replace(str(hardcoded_value), example_var_name, 1)
        else:
            # If exact match not found, still show the example with placeholder
            formula_after = f"{formula_before.rstrip('=')}...{example_var_name}..."
    
    # Build suggestion text
    if lang == 'ja':
        # Benefits section with smaller font
        benefits = """
<div style="font-size: 0.9em; color: #666;">

**メリット：**
- 値の変更が1箇所で済みます
- 計算ロジックが明確になります
- メンテナンス性が向上します

</div>
"""
        
        suggestion = f"""
{benefits}

**推奨される修正手順：**

**1. 直接書き込んでいる固定値を変数に変える**
- 空いているセルもしくは新規シート（例：変数シート）に、固定値（`{hardcoded_value}`）を入力
- エクセル数式バー左横に表示されているセル番号をクリック
- セル番号を適切な名前に書き換える（例：mil_百万、為替、{example_var_name}など）

**2. 数式を修正**
- セル `{risk.cell}` の数式から固定値 `{hardcoded_value}` を削除し、代わりに上記のセル名を入れる
"""
        
        # Add formula example if available
        if formula_before and formula_after:
            suggestion += f"""

**例：**
- 修正前: `{formula_before}`
- 修正後: `{formula_after}`
"""
    else:
        # Benefits section with smaller font
        benefits = """
<div style="font-size: 0.9em; color: #666;">

**Benefits:**
- Change the value in one place
- Calculation logic becomes clear
- Improved maintainability

</div>
"""
        
        suggestion = f"""
{benefits}

**Recommended Fix Steps:**

**1. Convert hardcoded value to a variable**
- Enter value `{hardcoded_value}` in an empty cell or new sheet (e.g., "Variables" sheet)
- Click the cell address shown to the left of the formula bar
- Rename the cell to an appropriate name (e.g., mil_million, exchange_rate, {example_var_name})

**2. Update the formula**
- Remove hardcoded value `{hardcoded_value}` from cell `{risk.cell}` and reference the named cell instead
"""
        
        # Add formula example if available
        if formula_before and formula_after:
            suggestion += f"""

**Example:**
- Before: `{formula_before}`
- After: `{formula_after}`
"""
    
    # Use markdown with HTML for styling
    st.markdown(suggestion, unsafe_allow_html=True)


def get_dependency_trace(risk: RiskAlert, model: ModelAnalysis, lang: str = 'ja') -> List[Dict[str, Any]]:
    """
    Get dependency trace for a risk showing upstream to downstream flow.
    
    Example: A1 >> B1 >> C1 >> D1
    - A1: 10
    - B1: A1 + 10 (depends on A1)
    - C1: A1 + 10 (depends on A1)
    - D1: C1 * 10 (depends on C1)
    
    When B1 is selected: shows A1 >> B1
    When C1 is selected: shows A1 >> C1 >> D1
    
    Handles compressed risks (e.g., G9:I9) by using the first cell as representative.
    
    Returns list of cell info dicts with sheet, address, value, label.
    """
    import networkx as nx
    
    trace = []
    
    # Handle compressed risks (ranges like "G9:I9" or "D5, E5")
    # Extract first cell as representative
    cell_for_trace = risk.cell
    if ':' in risk.cell:
        # Range format "G9:I9" -> "G9"
        cell_for_trace = risk.cell.split(':')[0]
    elif ',' in risk.cell:
        # List format "D5, E5" -> "D5"
        cell_for_trace = risk.cell.split(',')[0].strip()
    
    cell_address = f"{risk.sheet}!{cell_for_trace}"
    
    # Step 1: Get all upstream cells (predecessors) - cells this cell depends on
    upstream_cells = []
    if cell_address in model.dependency_graph:
        try:
            # Get all ancestors (cells that this cell depends on, directly or indirectly)
            ancestors = nx.ancestors(model.dependency_graph, cell_address)
            
            # Build paths from each root to current cell
            for ancestor in ancestors:
                # Check if this is a root (no predecessors)
                if model.dependency_graph.in_degree(ancestor) == 0:
                    # Find shortest path from root to current cell
                    try:
                        path = nx.shortest_path(model.dependency_graph, ancestor, cell_address)
                        if len(path) > len(upstream_cells):
                            upstream_cells = path[:-1]  # Exclude current cell
                    except:
                        pass
        except Exception as e:
            pass
    
    # Add upstream cells to trace
    for cell in upstream_cells:
        if '!' in cell:
            sheet, address = cell.split('!', 1)
        else:
            sheet = risk.sheet
            address = cell
        
        cell_info = model.cells.get(cell)
        if cell_info:
            from src.analyzer import ModelAnalyzer
            analyzer = ModelAnalyzer()
            row_label, col_label = analyzer._get_context_labels(sheet, address, model.cells)
            
            trace.append({
                'sheet': sheet,
                'address': address,
                'value': cell_info.value if cell_info.value is not None else '',
                'label': format_context(row_label, col_label)
            })
    
    # Add the current cell (use the representative cell for compressed risks)
    trace.append({
        'sheet': risk.sheet,
        'address': cell_for_trace,  # Use representative cell, not full range
        'value': risk.details.get('value', ''),
        'label': format_context(risk.row_label, risk.col_label, lang)
    })
    
    # Step 2: Get downstream cells (successors) - cells that depend on this cell
    if cell_address in model.dependency_graph:
        try:
            # Use NetworkX descendants to get ALL downstream cells
            # Then limit to first 10 for display
            import networkx as nx
            
            # DEBUG: Check direct successors first
            direct_successors = list(model.dependency_graph.successors(cell_address))
            
            # Get all descendants (cells that depend on this cell, directly or indirectly)
            all_descendants = nx.descendants(model.dependency_graph, cell_address)
            
            # DEBUG: Log counts
            import streamlit as st
            if len(direct_successors) != len(all_descendants):
                st.caption(f"🔍 Debug: {cell_address} has {len(direct_successors)} direct dependents, {len(all_descendants)} total (including indirect)")
            
            # Convert to list and limit to 10
            downstream_cells = list(all_descendants)[:10]
            
            # Add downstream cells to trace
            for cell in downstream_cells:
                if '!' in cell:
                    sheet, address = cell.split('!', 1)
                else:
                    sheet = risk.sheet
                    address = cell
                
                cell_info = model.cells.get(cell)
                if cell_info:
                    from src.analyzer import ModelAnalyzer
                    analyzer = ModelAnalyzer()
                    row_label, col_label = analyzer._get_context_labels(sheet, address, model.cells)
                    
                    trace.append({
                        'sheet': sheet,
                        'address': address,
                        'value': cell_info.value if cell_info.value is not None else '',
                        'label': format_context(row_label, col_label)
                    })
        except Exception as e:
            # Log error for debugging
            import streamlit as st
            st.warning(f"⚠️ Error getting dependents for {cell_address}: {str(e)}")
    
    return trace


def format_value(value: Any) -> str:
    """Format cell value for display"""
    if value is None:
        return "None"
    if isinstance(value, (int, float)):
        return f"{value:,.2f}"
    return str(value)[:20]


def render_professional_header(model: ModelAnalysis, filename: str, parse_time: float = None, lang: str = 'ja'):
    """
    Render professional header with aligned metrics dashboard.
    Matches Bloomberg Terminal aesthetic.
    """
    from src.i18n import t
    
    # File info section - professional typography
    ai_status = "ON" if st.session_state.get("ai_enabled", False) else "OFF"
    parse_time_str = f"<p style='font-size: 13px; margin: 0.25rem 0 0 0; color: #6B7280; font-weight: 400;'>{t('header_parsed_in', lang).format(time=f'{parse_time:.2f}')}</p>" if parse_time else ""
    
    st.markdown(f"""
    <div style="margin-bottom: 1.5rem; padding-bottom: 1rem; border-bottom: 2px solid #E5E7EB;">
        <p style="font-size: 14px; margin: 0; color: #6B7280; font-weight: 600; letter-spacing: 0.5px;">{t('header_file_to_check', lang).upper()}</p>
        <p style="font-size: 20px; margin: 0.5rem 0 0 0; font-weight: 600; color: #111827;">{filename}</p>
        {parse_time_str}
        <p style="font-size: 13px; margin: 0.75rem 0 0 0; color: #6B7280; font-weight: 400;"><span style="font-weight: 600;">{t('header_powered_by_ai', lang)}:</span> {ai_status}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics dashboard - aligned grid layout
    col1, col2, col3 = st.columns([1.2, 1, 0.8])
    
    with col1:
        # Task 39: Integration - Dynamic Health Score with Review Progress
        from src.risk_review import RiskReviewStateManager, DynamicScoreCalculator
        
        state_manager = RiskReviewStateManager()
        score_calculator = DynamicScoreCalculator()
        progress = score_calculator.calculate_progress(model.risks, state_manager)
        
        # Health Score - match "リスク一覧" label size (22px to match #### markdown)
        # Show current score with improvement delta
        current_score = progress.current_score
        improvement_delta = progress.improvement_delta
        
        # Build improvement indicator
        improvement_html = ""
        if improvement_delta > 0:
            improvement_html = f'<span style="font-size: 16px; color: #10B981; font-weight: 600; margin-left: 0.5rem;">+{improvement_delta}</span>'
        
        st.markdown(f"""
        <div style="margin-bottom: 2rem;">
            <p style="font-size: 22px; margin: 0; font-weight: 600; color: #6B7280; letter-spacing: 0.5px;">{t('header_health_score', lang).upper()}</p>
            <p style="font-size: 32px; margin: 0.5rem 0 0 0; font-weight: 700; color: #111827;">{current_score}<span style="font-size: 20px; color: #6B7280; font-weight: 400;"> / 100</span>{improvement_html}</p>
            <p style="font-size: 13px; margin: 0.25rem 0 0 0; color: #9CA3AF; font-style: italic;">{t('header_health_score_desc', lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show initial score if improvement exists (no icon)
        if improvement_delta > 0:
            st.caption(f"初期スコア: {progress.initial_score} → 改善: +{improvement_delta}")
        
        # Maturity Level - match "リスク一覧" label size (22px to match #### markdown)
        maturity_label = get_maturity_label(model.maturity_level, lang)
        st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <p style="font-size: 22px; margin: 0; font-weight: 600; color: #6B7280; letter-spacing: 0.5px;">{t('header_maturity_level', lang).upper()}</p>
            <p style="font-size: 24px; margin: 0.5rem 0 0 0; font-weight: 700; color: #111827;">{model.maturity_level}<span style="font-size: 16px; color: #6B7280; font-weight: 400;"> / 5 : {maturity_label}</span></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Risk Density - show risk cells / total cells
        total_cells = len(model.cells)
        risk_cells = len(model.risks)
        density_pct = (risk_cells / total_cells * 100) if total_cells > 0 else 0
        st.markdown(f"""
        <div style="margin-bottom: 1.5rem;">
            <p style="font-size: 22px; margin: 0; font-weight: 600; color: #6B7280; letter-spacing: 0.5px;">{t('header_risk_density', lang).upper()}</p>
            <p style="font-size: 24px; margin: 0.5rem 0 0 0; font-weight: 700; color: #111827;">{risk_cells:,}<span style="font-size: 16px; color: #6B7280; font-weight: 400;"> / {total_cells:,} ({density_pct:.1f}%)</span></p>
            <p style="font-size: 13px; margin: 0.25rem 0 0 0; color: #9CA3AF; font-style: italic;">{t('header_risk_density_desc', lang)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Show Interactive Dependency Graph checkbox
        if st.checkbox(t('header_show_graph', lang), value=False, help=t('header_show_graph_help', lang), key="dep_graph_header"):
            st.session_state["show_dep_graph"] = True
        else:
            st.session_state["show_dep_graph"] = False
    
    with col2:
        # Risk counts - match "リスク一覧" font size (22px for label to match #### markdown, 32px for numbers)
        risk_counts = count_risks_by_severity(model.risks)
        
        # Header - match "リスク一覧" size (22px to match #### markdown)
        st.markdown(f'<p style="font-size: 22px; font-weight: 600; margin-bottom: 1rem; color: #6B7280; letter-spacing: 0.5px;">{t("header_risks", lang).upper()}</p>', unsafe_allow_html=True)
        
        # Each risk level - match health score number size (32px)
        st.markdown(f'<p style="font-size: 18px; margin: 0.5rem 0; color: #111827; display: flex; justify-content: space-between; max-width: 220px;"><span style="font-weight: 600;">{t("header_critical", lang)}</span><span style="font-size: 32px; font-weight: 700; margin-left: 1rem;">{risk_counts.get("Critical", 0)}</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size: 18px; margin: 0.5rem 0; color: #111827; display: flex; justify-content: space-between; max-width: 220px;"><span style="font-weight: 600;">{t("header_high", lang)}</span><span style="font-size: 32px; font-weight: 700; margin-left: 1rem;">{risk_counts.get("High", 0)}</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size: 18px; margin: 0.5rem 0; color: #111827; display: flex; justify-content: space-between; max-width: 220px;"><span style="font-weight: 600;">{t("header_medium", lang)}</span><span style="font-size: 32px; font-weight: 700; margin-left: 1rem;">{risk_counts.get("Medium", 0)}</span></p>', unsafe_allow_html=True)
        st.markdown(f'<p style="font-size: 18px; margin: 0.5rem 0; color: #111827; display: flex; justify-content: space-between; max-width: 220px;"><span style="font-weight: 600;">{t("header_low", lang)}</span><span style="font-size: 32px; font-weight: 700; margin-left: 1rem;">{risk_counts.get("Low", 0)}</span></p>', unsafe_allow_html=True)
    
    with col3:
        # Export button - use download_button with CSV icon
        st.markdown('<div style="height: 0.5rem;"></div>', unsafe_allow_html=True)
        
        # Generate CSV data
        import pandas as pd
        import io
        
        export_data = []
        for risk in model.risks:
            export_data.append({
                'Location': risk.get_location(),
                'Sheet': risk.sheet,
                'Cell': risk.cell,
                'Risk Type': risk.risk_type,
                'Severity': risk.severity,
                'Description': risk.description,
                'Context': risk.get_context(),
                'Row Label': risk.row_label or '',
                'Column Label': risk.col_label or '',
                'Value': str(risk.details.get('value', '')) if risk.details.get('value') is not None else '',
                'Formula': risk.details.get('formula', ''),
                'Impact Score': risk.details.get('impact_score', 0)
            })
        
        df_export = pd.DataFrame(export_data)
        csv_buffer = io.StringIO()
        df_export.to_csv(csv_buffer, index=False)
        csv_string = csv_buffer.getvalue()
        
        # Use download_button without icon
        st.download_button(
            label=t('header_export', lang),
            data=csv_string,
            file_name=f"{model.filename.replace('.xlsx', '')}_risks.csv",
            mime="text/csv",
            use_container_width=True,
            key="export_csv_btn"
        )
    
    # Separator
    st.markdown('<hr style="margin: 1.5rem 0; border: none; border-top: 1px solid #E5E7EB;">', unsafe_allow_html=True)


def get_maturity_label(level: int, lang: str = 'ja') -> str:
    """Get maturity level label"""
    if lang == 'ja':
        labels = {
            1: "静的モデル",
            2: "基本構造",
            3: "文書化モデル",
            4: "管理モデル",
            5: "ベストプラクティス"
        }
        return labels.get(level, "不明")
    else:
        labels = {
            1: "Static Model",
            2: "Basic Structure",
            3: "Documented Model",
            4: "Managed Model",
            5: "Best Practice"
        }
        return labels.get(level, "Unknown")


def count_risks_by_severity(risks: List[RiskAlert]) -> Dict[str, int]:
    """Count risks by severity level"""
    counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for risk in risks:
        if risk.severity in counts:
            counts[risk.severity] += 1
    return counts


def inject_professional_css():
    """
    Inject custom CSS for Excel-like light mode aesthetic.
    Optimized for business users (経営企画).
    """
    st.markdown("""
    <style>
    /* Remove Streamlit branding and padding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    
    /* Clean typography - Excel風 */
    body {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Yu Gothic", "Meiryo", sans-serif;
        font-size: 14px;
        line-height: 1.4;
        background-color: #FFFFFF;
    }
    
    /* Compact header */
    h1, h2, h3 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: 600;
        color: #1F2937;
    }
    
    /* Excel-like borders */
    .stDataFrame, .stButton button {
        border-radius: 2px;
    }
    
    /* Excel-style borders */
    .stDataFrame {
        border: 1px solid #D1D5DB;
    }
    
    /* Compact table rows */
    .stDataFrame tbody tr {
        height: 32px;
    }
    
    /* Detail panel sections */
    .detail-section {
        border-left: 3px solid #2563EB;
        padding-left: 12px;
        margin-bottom: 16px;
    }
    
    /* Monospace for cell references */
    code {
        font-family: "SF Mono", Monaco, "Cascadia Code", "MS Gothic", monospace;
        font-size: 13px;
        background-color: #F3F4F6;
        color: #1F2937;
        padding: 2px 4px;
        border-radius: 2px;
    }
    
    /* Progress bar */
    .stProgress > div > div {
        background-color: #DC2626;
    }
    
    /* Make tab labels bigger */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 22px !important;
        font-weight: 600 !important;
        color: #1F2937 !important;
    }
    
    /* Tab button styling */
    .stTabs [data-baseweb="tab-list"] button {
        font-size: 22px !important;
        background-color: #F9FAFB;
    }
    
    /* Active tab */
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] {
        background-color: #FFFFFF;
        border-bottom: 3px solid #2563EB;
    }
    
    /* Excel-like table styling */
    .stDataFrame {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
    }
    
    /* Table container background */
    .stDataFrame > div,
    .stDataFrame > div > div,
    .stDataFrame > div > div > div,
    .stDataFrame iframe,
    [data-testid="stDataFrame"],
    [data-testid="stDataFrame"] > div,
    [data-testid="stDataFrame"] iframe {
        background-color: #FFFFFF !important;
    }
    
    /* Table headers - Excel style */
    .stDataFrame thead tr th {
        background-color: #F3F4F6 !important;
        color: #1F2937 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #D1D5DB !important;
    }
    
    /* Table body - Excel style */
    .stDataFrame tbody tr td {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
        border-bottom: 1px solid #E5E7EB !important;
    }
    
    /* Table body rows - alternating colors like Excel */
    .stDataFrame tbody tr:nth-child(even) {
        background-color: #F9FAFB !important;
    }
    
    .stDataFrame tbody tr:nth-child(odd) {
        background-color: #FFFFFF !important;
    }
    
    /* Selected row highlight - Excel blue */
    .stDataFrame tbody tr:hover {
        background-color: #EFF6FF !important;
    }
    
    /* Info/Alert messages */
    .stAlert {
        background-color: #F3F4F6;
        color: #1F2937;
    }
    
    .stAlert [data-testid="stMarkdownContainer"] p {
        color: #1F2937 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #F9FAFB;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
        color: #1F2937;
    }
    </style>
    """, unsafe_allow_html=True)



def render_master_detail_ui(risks: List[RiskAlert], model: ModelAnalysis, lang: str = 'ja', tab_key: str = 'default'):
    """
    Render master-detail UI with integrated Risk Review System.
    Task 39: Integration (Simplified UX)
    
    This function provides:
    - Very compact progress display
    - Master-detail layout with checkbox column
    - Detail panel on the right
    - CSV export with review state
    - No filter controls (removed)
    - No icons (removed)
    
    Args:
        risks: List of risks to display
        model: ModelAnalysis object
        lang: Language code ('ja' or 'en')
        tab_key: Unique key for this tab instance (to avoid duplicate keys)
    """
    if not risks:
        st.info("このカテゴリにはリスクがありません。")
        return
    
    # Initialize managers
    from src.risk_review import RiskReviewStateManager, DynamicScoreCalculator
    state_manager = RiskReviewStateManager()
    score_calculator = DynamicScoreCalculator()
    
    # Calculate progress
    progress = score_calculator.calculate_progress(risks, state_manager)
    
    # Render very compact progress display at the top
    from src.risk_review import render_progress_display
    render_progress_display(progress, lang)
    
    st.markdown("---")
    
    # Create two columns: master (left) with checkboxes and detail (right)
    # Use gap parameter to add spacing between columns
    master_col, detail_col = st.columns([3, 2], gap="medium")
    
    with master_col:
        # Header row with title and CSV download button
        header_col1, header_col2 = st.columns([2, 1])
        with header_col1:
            st.markdown("#### リスク一覧")
        with header_col2:
            # CSV download button next to the title with smaller font
            from src.risk_review import export_risks_with_review_state
            from datetime import datetime
            
            csv_data = export_risks_with_review_state(risks, state_manager, lang)
            
            # Add custom CSS for smaller button text
            st.markdown("""
            <style>
            div[data-testid="stDownloadButton"] button {
                font-size: 0.7rem !important;
                padding: 0.25rem 0.5rem !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            st.download_button(
                label="一覧をダウンロード（CSV）",
                data=csv_data,
                file_name=f"risk_review_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="確認状態とタイムスタンプを含むCSVファイルをダウンロード",
                key=f"master_detail_csv_download_{tab_key}",
                use_container_width=True
            )
        
        # AI feature hint message
        if lang == 'ja':
            st.caption("AI機能をONにすると、読み込みの精度が向上します")
        else:
            st.caption("Enabling AI features improves reading accuracy")
        
        # Render master risk table with checkboxes (no filter controls)
        # Use unique table_key based on risk types to avoid duplicate keys
        import hashlib
        risk_types_hash = hashlib.md5("_".join(sorted(set(r.risk_type for r in risks))).encode()).hexdigest()[:8]
        selected_risk = render_master_risk_table_with_checkboxes(
            risks, 
            state_manager, 
            table_key=f"master_table_{risk_types_hash}", 
            lang=lang
        )
    
    with detail_col:
        # Always show the detail column header
        st.markdown("#### リスク詳細")
        
        # Create a scrollable container for the detail panel with fixed height
        # This ensures users can scroll to see all content
        detail_container = st.container(height=700)
        with detail_container:
            # Render detail panel for selected risk
            render_detail_panel(selected_risk, model, lang)



def render_master_risk_table_with_checkboxes(
    risks: List[RiskAlert], 
    state_manager,
    table_key: str = "master_risk_table", 
    lang: str = 'ja'
) -> Optional[RiskAlert]:
    """
    Render master risk table with inline checkboxes for review tracking.
    Checkboxes are clickable and update review state immediately.
    Reviewed rows show strikethrough styling.
    
    Args:
        risks: List of risk alerts to display
        state_manager: RiskReviewStateManager instance
        table_key: Unique key for this table instance
        lang: Language code for translations
    
    Returns: Selected risk object (None if no selection)
    """
    from collections import defaultdict
    from src.i18n import t
    
    if not risks:
        st.info("No risks detected")
        return None
    
    # Sort risks by priority first
    sorted_risks = sort_risks_by_priority(risks)
    
    # Group risks by Risk Type
    risk_groups = defaultdict(list)
    for i, risk in enumerate(sorted_risks):
        risk_groups[risk.risk_type].append((i, risk))
    
    selected_risk = None
    
    # Display each Risk Type group
    for risk_type, group_risks in risk_groups.items():
        # Translate risk type name (no icon)
        translated_risk_type = translate_risk_type(risk_type, lang)
        
        # Risk Type header with count (no icon)
        st.markdown(f'<p style="font-size: 18px; font-weight: 600; margin-bottom: 0.5rem;"><strong>{translated_risk_type}</strong> ({len(group_risks)})</p>', unsafe_allow_html=True)
        
        # Build table data for this group
        table_data = []
        risk_mapping = []  # Keep track of risk objects for state updates
        
        for idx, (original_index, risk) in enumerate(group_risks):
            # Get review state
            is_reviewed = state_manager.is_reviewed(risk)
            
            # Get value from multiple possible sources
            value = None
            if "value" in risk.details and risk.details["value"] is not None:
                value = risk.details["value"]
            elif "cell_value" in risk.details and risk.details["cell_value"] is not None:
                value = risk.details["cell_value"]
            elif "hardcoded_value" in risk.details and risk.details["hardcoded_value"] is not None:
                value = risk.details["hardcoded_value"]
            elif "formula" in risk.details and risk.details["formula"]:
                value = risk.details["formula"]
            else:
                value = ""
            
            table_data.append({
                "詳細": False,  # Checkbox for detail view
                t('table_location', lang): f"{risk.sheet}!{risk.cell}",
                t('table_context', lang): format_context(risk.row_label, risk.col_label, lang),
                t('table_value', lang): truncate_value(value, max_length=15),
                t('table_severity', lang): risk.severity,
                t('table_impact', lang): risk.details.get("impact_count", 0),
                "確認": is_reviewed
            })
            risk_mapping.append(risk)
        
        # Create DataFrame
        df = pd.DataFrame(table_data)
        
        # Use data_editor with checkbox columns
        group_key = f"{table_key}_{risk_type.replace(' ', '_').replace('/', '_')}"
        edited_df = st.data_editor(
            df,
            column_config={
                "詳細": st.column_config.CheckboxColumn(
                    "詳細",
                    help="詳細を表示",
                    default=False,
                    width="small"
                ),
                t('table_location', lang): st.column_config.TextColumn(
                    t('table_location', lang),
                    width="small"
                ),
                t('table_context', lang): st.column_config.TextColumn(
                    t('table_context', lang),
                    width="small"
                ),
                t('table_value', lang): st.column_config.TextColumn(
                    t('table_value', lang),
                    width="medium"
                ),
                t('table_severity', lang): st.column_config.TextColumn(
                    t('table_severity', lang),
                    width="small"
                ),
                t('table_impact', lang): st.column_config.NumberColumn(
                    t('table_impact', lang),
                    width="small"
                ),
                "確認": st.column_config.CheckboxColumn(
                    "確認",
                    help="確認したらチェック",
                    default=False,
                    width="small"
                )
            },
            disabled=[t('table_location', lang), t('table_context', lang), t('table_value', lang), t('table_severity', lang), t('table_impact', lang)],
            hide_index=True,
            use_container_width=True,
            key=group_key
        )
        
        # Check for detail view selection and confirmation changes
        for idx, row in edited_df.iterrows():
            if idx < len(risk_mapping):
                risk = risk_mapping[idx]
                
                # Handle detail view selection
                if row["詳細"]:
                    selected_risk = risk
                
                # Handle confirmation checkbox
                new_state = row["確認"]
                current_state = state_manager.is_reviewed(risk)
                
                # Only update if state changed
                if new_state != current_state:
                    state_manager.set_reviewed(risk, new_state)
                    st.rerun()  # Rerun to update progress
        

        
        # Add spacing between groups
        st.markdown("---")
    
    return selected_risk
