"""
Internationalization (i18n) module for Lumen
Provides bilingual support for Japanese and English
"""

TEXTS = {
    'en': {
        # App Title & Branding
        'app_title': 'Lumen',
        'app_subtitle': 'Excel Model Audit & Diagnostic System',
        'page_title': 'Lumen - Excel Model Audit System',
        
        # Welcome Screen
        'welcome_title': 'Excel Model Audit & Diagnostic System',
        'welcome_subtitle': 'Automatically diagnose Excel model health and identify hidden errors and structural defects that could lead to incorrect business decisions.',
        'welcome_cta': 'Upload an Excel file to start diagnosis',
        
        # What It Does
        'what_it_does_title': '1. What It Does',
        'what_it_does_desc': 'Automatically diagnose Excel model health and identify hidden errors and structural defects.',
        
        # Key Detection Items
        'detection_title': '2. Key Detection Items',
        'detection_external': 'External references to other workbooks (risk of broken links when sharing)',
        'detection_inconsistent_formula': 'Cells with different formulas in the same row (risk of copy-paste errors)',
        'detection_inconsistent_value': 'Cells with different hardcoded values for the same item (signs of manual adjustments or update omissions)',
        'detection_hardcode': 'Hardcoded numbers directly in formulas (causes update omissions and prevents flexible simulations)',
        'detection_circular': 'Circular reference errors (calculation logic breakdown, unreliable numbers)',
        
        # Usage Steps
        'usage_title': '3. Usage Steps',
        'usage_step1': 'Basic Settings: Enter fiscal year and other prerequisites',
        'usage_step2': 'File Selection: Upload Excel file from sidebar',
        'usage_step3': 'Run Diagnosis: Review risk detection results and remediation suggestions',
        'usage_step4': 'Diff Analysis: (Optional) Compare before/after files',
        'usage_step5': 'AI Consultation: (Recommended) Consult AI for complex logic and remediation suggestions',
        
        # Sidebar
        'sidebar_file_upload': 'File Upload',
        'sidebar_reference_file': 'Upload Reference File (Old)',
        'sidebar_reference_help': 'Upload the original Excel model for comparison',
        'sidebar_target_file': 'Upload Target File (New)',
        'sidebar_target_help': 'Upload the updated Excel model to analyze',
        'sidebar_settings': 'Settings',
        'sidebar_fiscal_year': 'Fiscal Year Start Month',
        'sidebar_fiscal_year_help': 'Select the starting month of your fiscal year',
        'sidebar_allowed_constants': 'Allowed Constants (comma separated)',
        'sidebar_allowed_constants_help': 'Among hardcoded numbers, numeric values that are acceptable as constants (e.g., months=12, days=30/365, quarters=3)',
        'sidebar_context_labels': 'Context Labels',
        'sidebar_label_columns': 'Label Source Columns (Range)',
        'sidebar_label_columns_help': 'Column range to use for row labels. Concatenates left→right to capture hierarchy',
        'sidebar_ai_config': 'AI Configuration',
        'sidebar_ai_provider': 'AI Provider',
        'sidebar_ai_provider_help': 'Select your preferred AI provider for formula explanations',
        'sidebar_api_key': 'API Key',
        'sidebar_api_key_help': 'Enter your API key (stored only in session, never persisted)',
        'sidebar_api_configured': '✓ API Key configured',
        'sidebar_api_disabled': 'AI explanations disabled (no API key)',
        
        # Tabs
        'tab_file_info': 'File Information',
        'tab_fatal_errors': 'Fatal Errors',
        'tab_integrity_risks': 'Integrity Risks',
        'tab_structural_debt': 'Structural Debt',
        'tab_driver_xray': 'Driver X-Ray',
        
        # File Information Tab
        'file_details': 'File Details',
        'metric_sheets': 'Sheets',
        'metric_cells': 'Total Cells',
        'metric_formulas': 'Formulas',
        'sheets_in_workbook': 'Sheets in Workbook',
        'merged_ranges': 'Merged Cell Ranges',
        'dependency_graph': 'Dependency Graph',
        'metric_nodes': 'Nodes',
        'metric_edges': 'Edges',
        
        # Header Section
        'header_file_to_check': 'FILE TO CHECK',
        'header_parsed_in': 'Parsed in {time}s',
        'header_powered_by_ai': 'Powered by AI',
        'header_health_score': 'OVERALL HEALTH SCORE',
        'header_health_score_desc': 'Weighted by risk category and severity',
        'header_maturity_level': 'MATURITY LEVEL',
        'header_risk_density': 'RISK DENSITY',
        'header_risk_density_desc': 'Percentage of cells with detected risks',
        'header_risks': 'RISKS',
        'header_critical': 'Critical',
        'header_high': 'High',
        'header_medium': 'Medium',
        'header_low': 'Low',
        'header_show_graph': 'Show Interactive Dependency Graph',
        'header_show_graph_help': 'Visualize cell dependencies (limited to 500 nodes for performance)',
        'header_export': 'Download CSV',
        
        # Risk Table Headers
        'table_location': 'Location',
        'table_context': 'Context',
        'table_value': 'Value',
        'table_severity': 'Severity',
        'table_impact': 'Impact',
        
        # Risk Type Names (for table headers)
        'risk_type_hidden_hardcode': 'Hidden Hardcode',
        'risk_type_inconsistent_formula': 'Inconsistent Formula',
        'risk_type_inconsistent_value': 'Inconsistent Value',
        'risk_type_value_conflict': 'Value Conflict',
        'risk_type_circular_reference': 'Circular Reference',
        'risk_type_external_link': 'External Link',
        'risk_type_formula_error': 'Formula Error',
        'risk_type_merged_cell': 'Merged Cell',
        'risk_type_logic_alert': 'Logic Alert',
        
        # Risk Categories
        'fatal_caption': 'The model is broken or uncomputable',
        'integrity_caption': 'Review Priority: Hidden bugs live here',
        'structural_caption': 'Works correctly now, but hard to maintain',
        
        # Help Text
        'help_fatal_title': 'What are Fatal Errors?',
        'help_fatal_desc': 'Fatal Errors are issues that prevent your model from working correctly',
        'help_fatal_circular': 'Circular Reference: Cells that reference themselves',
        'help_fatal_external': 'External Link: References to other files (breaks when sharing)',
        'help_fatal_formula_error': 'Formula Error: Excel errors like #REF!, #VALUE!, #DIV/0!',
        'help_fatal_priority': 'Priority: Fix immediately - your model cannot calculate correctly',
        
        'help_integrity_title': 'What are Integrity Risks?',
        'help_integrity_desc': 'Integrity Risks are the most dangerous - your model runs but may have hidden bugs',
        'help_integrity_inconsistent': 'Inconsistent Formula: Formula pattern suddenly changes in a row/column',
        'help_integrity_value': 'Inconsistent Value: Same label but different hardcoded values',
        'help_integrity_logic': 'Logic Alert: Semantically odd calculations',
        'help_integrity_priority': 'Priority: Review immediately - high chance of calculation errors',
        
        'help_structural_title': 'What is Structural Debt?',
        'help_structural_desc': 'Structural Debt means your model works now but is hard to maintain',
        'help_structural_hardcode': 'Hidden Hardcode: Fixed values embedded in formulas',
        'help_structural_merged': 'Merged Cell: Cell merging makes analysis difficult',
        'help_structural_priority': 'Priority: Fix when you have time - improves maintainability',
        
        # Status Messages
        'no_fatal_errors': '✅ No fatal errors detected',
        'no_integrity_risks': '✅ No integrity risks detected',
        'no_structural_debt': '✅ No structural debt detected',
        'no_risks': '🎉 No risks detected! Your Excel model looks great!',
        
        # Master-Detail UI
        'risk_table': 'Risk Table',
        'detail_panel': 'Detail Panel',
        'select_risk': 'Select a risk from the table to view details',
        'risk_selected_hint': 'When you select a risk item, it will jump to "File Information" on the first time. To view details, please click this tab again.',
        
        # Driver X-Ray
        'xray_title': '🎯 Executive Diagnosis - Top Risks',
        'xray_subtitle': 'Auto-Diagnosis: We\'ve analyzed your model and identified the most dangerous hardcoded values.',
        'xray_top3': '🚨 Most Dangerous Hardcoded Values - Top 3',
        'xray_aggregated': '💡 Risks with the same value are aggregated to show total impact',
        'xray_metric_occurrences': 'Occurrences',
        'xray_metric_impact': 'Impact Cells (Total)',
        'xray_metric_severity': 'Severity',
        'xray_metric_kpi': 'KPI Impact',
        'xray_kpi_yes': '⚠️ Yes',
        'xray_kpi_no': 'None',
        'xray_impact_breakdown': 'Impact Breakdown:',
        'xray_direct_impact': '📍 Direct Impact',
        'xray_indirect_impact': '🔗 Indirect Impact',
        'xray_export_csv': '📥 Export Impact Cells to CSV',
        'xray_download_csv': '💾 Download: impact_cells_{value}.csv',
        'xray_export_success': '✓ {count} impact cells ready for export',
        'xray_value': 'Hardcoded Value:',
        'xray_scope': 'Impact Scope:',
        'xray_locations': 'locations',
        'xray_show_all': '📍 Show All Locations',
        'xray_more_locations': '... and {count} more',
        'xray_ai_suggest': '✨ Suggest Improvement',
        'xray_ai_analyzing': '🤖 AI Consultant is analyzing...',
        'xray_ai_recommendation': '💡 AI Consultant Recommendation:',
        'xray_ai_enable': '💡 Enable AI Suggestions: Enter your API key in the sidebar',
        'xray_impact_trace': '📊 Impact Trace',
        'xray_analysis_summary': '📖 Analysis Summary',
        'xray_source': '⬆️ SOURCE',
        'xray_source_caption': 'Where the value comes from',
        'xray_consequences': '⬇️ CONSEQUENCES',
        'xray_consequences_caption': 'What this affects',
        'xray_no_sources': '🚨 No sources - likely hardcoded',
        'xray_no_consequences': 'No consequences',
        'xray_formula': 'Formula:',
        'xray_translated': 'Translated:',
        'xray_translation_help': '💡 Formula with semantic labels - makes logic errors obvious',
        'xray_remaining': '📊 {count} additional hardcoded values detected. Focus on the top 3 first for maximum impact.',
        'xray_no_risks': 'No risks detected. Upload a file with risks to use Driver X-Ray.',
        
        # Diff Mode
        'diff_composite_key': '🔑 Composite Key Matching',
        'diff_composite_desc': 'Select key columns to match rows intelligently, even when rows are inserted, deleted, or reordered.',
        'diff_select_sheet': 'Select Sheet to Compare',
        'diff_key_columns': 'Key Columns (comma separated)',
        'diff_key_columns_help': 'Enter column letters to use as composite key',
        'diff_uniqueness': 'Key Uniqueness Validation',
        'diff_keys_unique': '✅ Keys are unique ({rate}% unique)',
        'diff_keys_good': 'These columns provide good matching accuracy.',
        'diff_keys_not_unique': '⚠️ Keys are not unique ({rate}% unique)',
        'diff_preview_matches': '🔍 Preview Row Matches',
        'diff_preview_title': 'Row Matching Preview',
        'diff_matched_rows': 'Matched {count} rows between old and new files:',
        'diff_showing_first': 'Showing first 10 of {count} matched rows',
        'diff_no_matches': 'No rows could be matched with the selected key columns',
        'diff_comparison_summary': '📊 Comparison Summary',
        'diff_improved': '🎉 Model Health Improved!',
        'diff_degraded': '⚠️ Model Health Decreased',
        'diff_no_change': '➡️ No Change in Health Score',
        'diff_old_score': 'Old Score',
        'diff_new_score': 'New Score',
        'diff_change': 'Change',
        'diff_changes_detected': '📋 Changes Detected',
        'diff_tab_improved': 'Improved',
        'diff_tab_degraded': 'Degraded',
        'diff_tab_structural': 'Structural',
        'diff_risks_fixed': '✅ {count} Risks Fixed',
        'diff_new_risks': '⚠️ {count} New Risks',
        'diff_structural_changes': '{count} Structural Changes',
        'diff_no_improvements': 'No improvements detected',
        'diff_no_new_risks': 'No new risks detected',
        'diff_no_structural': 'No structural changes detected',
        
        # Parsing & Status
        'parsing': '🔄 Parsing Excel model... This may take a minute.',
        'parsed_in': 'Parsed in {time}s',
        'using_cached': 'Using cached analysis',
        
        # Errors
        'error_attention': '⚠️ Attention Required',
        'error_tip': '💡 Tip: Make sure your file is a valid .xlsx format and not password-protected.',
        'error_unexpected': '⚠️ Unexpected Issue',
        'error_unexpected_desc': 'We encountered an issue while analyzing your file: {error}',
        'error_tip_contact': '💡 Tip: Try uploading a different file or contact support if the issue persists.',
        'show_debug_log': '🔍 Show Debug Log',
        
        # Misc
        'month': 'Month {num}',
        'cells': 'cells',
        'cell': 'cell',
        
        # Explanation Mode
        'explanation_mode_title': 'Explanation Mode',
        'explanation_mode_subtitle': 'Understand "why this number?" through causal tree analysis',
        'explanation_mode_no_data': 'No data available for analysis',
        'model_overview': 'Model Overview',
        'coming_soon': 'Coming Soon',
        'development_status': 'Development Status',
        
        # Target Selection
        'target_selection_title': 'Select Target Metric',
        'target_selection_label': 'Choose a KPI to analyze',
        'target_selection_help': 'Select a key performance indicator (KPI) to build a causal tree',
        'target_selected': 'Selected: {label} at {address}',
        'no_kpi_candidates': 'No KPI candidates found (must contain "Revenue" in label)',
        'manual_selection_title': 'Manual Selection',
        'manual_selection_label': 'Enter cell address manually',
        'manual_selection_help': 'Format: Sheet1!C10',
        'manual_target_selected': 'Selected: {address}',
        'invalid_cell_address': 'Invalid cell address or cell not found',
        
        # Causal Tree Display
        'causal_tree_title': 'Causal Tree',
        'causal_tree_subtitle': 'Hierarchical breakdown showing how this metric is calculated',
        'tree_build_error': 'Error building tree: {error}',
        'cell_address': 'Cell Address',
        'value': 'Value',
        'formula': 'Formula',
        'formula_readable': 'Readable Formula',
        'untraceable': 'UNTRACEABLE',
        'untraceable_reason': 'Reason',
        'precedents': 'Precedents',
        'precedents_count': 'Number of precedents',
        
        # Risk Review System
        'review_checkbox': 'Review',
        'review_checkbox_help': 'Mark this risk as reviewed',
        'initial_score': 'Initial Score',
        'current_score': 'Current Score',
        'improvement': 'Improvement',
        'reviewed_count': 'Reviewed',
        'unreviewed_count': 'Unreviewed',
        'filter_all': 'All',
        'filter_unreviewed': 'Unreviewed Only',
        'filter_reviewed': 'Reviewed Only',
        'export_with_review_state': 'Download CSV (with review state)',
        'all_reviewed_message': '🎉 All risks reviewed!',
        'keep_going_message': '💪 {count} more to go!',
        'review_progress': 'Review Progress',
        'display_filter': 'Display Filter',
    },
    'ja': {
        # App Title & Branding
        'app_title': 'Lumen',
        'app_subtitle': 'Excelモデル監査・診断システム',
        'page_title': 'Lumen - Excelモデル監査システム',
        
        # Welcome Screen
        'welcome_title': 'Excelモデル監査・診断システム',
        'welcome_subtitle': 'Excelモデルの健全性を自動診断し、経営判断を誤らせる「隠れたエラー」や「構造的な欠陥」を即座に特定します。',
        'welcome_cta': 'Excelファイルをアップロードして診断を開始',
        
        # What It Does
        'what_it_does_title': '1. できること',
        'what_it_does_desc': 'Excelモデルの健全性を自動診断し、隠れたエラーや構造的な欠陥を特定します。',
        
        # Key Detection Items
        'detection_title': '2. 主な検知項目',
        'detection_external': '他のブックなど外部データを参照しているセル（共有時にリンク切れでモデルが壊れるリスク）',
        'detection_inconsistent_formula': '同一の行の中で、他と異なる数式が使われているセル（コピペミスなどで、誤って式が作成・更新されているリスク）',
        'detection_inconsistent_value': '同一の行・項目の中で、異なる数値が混在しているセル（無理な数値調整の痕跡や、修正漏れの可能性）',
        'detection_hardcode': '数式の中に直接書き込まれた「ベタ打ち数値」（更新漏れの原因となり、為替や利率などの柔軟なシミュレーションを阻害）',
        'detection_circular': '循環参照エラー（計算ロジックが破綻し、数値が信頼できなくなるリスク）',
        
        # Usage Steps
        'usage_title': '3. 利用手順',
        'usage_step1': '基本設定: 会計年度の開始月などの前提条件を入力',
        'usage_step2': 'ファイル選択: サイドバーからExcelファイルをアップロード',
        'usage_step3': '診断実行: リスク検出結果と修正案を確認',
        'usage_step4': '差分分析: （任意）修正前後のファイルを比較',
        'usage_step5': 'AI活用: （推奨）複雑なロジックや修正案をAIに相談',
        
        # Sidebar
        'sidebar_file_upload': 'ファイル選択',
        'sidebar_reference_file': '参照ファイル（旧）をアップロード',
        'sidebar_reference_help': '比較用の元のExcelモデルをアップロード',
        'sidebar_target_file': '対象ファイル（新）をアップロード',
        'sidebar_target_help': '分析する更新後のExcelモデルをアップロード',
        'sidebar_settings': '基本設定',
        'sidebar_fiscal_year': '会計年度の開始月',
        'sidebar_fiscal_year_help': '会計年度の開始月を選択',
        'sidebar_allowed_constants': '許可する定数（カンマ区切り）',
        'sidebar_allowed_constants_help': 'ベタ打ち数値のなかで、定数として許可する数値（例：月=12、日=30/365、四半期=3）',
        'sidebar_context_labels': 'コンテキストラベル',
        'sidebar_label_columns': 'ラベル元列（範囲）',
        'sidebar_label_columns_help': '行ラベルに使用する列範囲。左→右に連結して階層を取得',
        'sidebar_ai_config': 'AI設定',
        'sidebar_ai_provider': 'AIプロバイダー',
        'sidebar_ai_provider_help': '数式説明に使用するAIプロバイダーを選択',
        'sidebar_api_key': 'APIキー',
        'sidebar_api_key_help': 'APIキーを入力（セッションのみ保存、永続化されません）',
        'sidebar_api_configured': '✓ APIキー設定済み',
        'sidebar_api_disabled': 'AI説明は無効（APIキーなし）',
        
        # Tabs
        'tab_file_info': 'ファイル情報',
        'tab_fatal_errors': '最優先項目',
        'tab_integrity_risks': '整合性リスク',
        'tab_structural_debt': '構造的負債',
        'tab_driver_xray': 'ドライバーX線',
        
        # File Information Tab
        'file_details': 'ファイル詳細',
        'metric_sheets': 'シート数',
        'metric_cells': '総セル数',
        'metric_formulas': '数式数',
        'sheets_in_workbook': 'ワークブック内のシート',
        'merged_ranges': '結合セル範囲',
        'dependency_graph': '依存関係グラフ',
        'metric_nodes': 'ノード数',
        'metric_edges': 'エッジ数',
        
        # Header Section
        'header_file_to_check': '診断対象ファイル',
        'header_parsed_in': '{time}秒で解析完了',
        'header_powered_by_ai': 'AI機能',
        'header_health_score': '総合健全性スコア',
        'header_health_score_desc': 'リスクカテゴリーと重要度で重み付け',
        'header_maturity_level': '成熟度レベル',
        'header_risk_density': 'リスク密度',
        'header_risk_density_desc': 'リスクが検出されたセルの割合',
        'header_risks': 'リスク',
        'header_critical': '最優先',
        'header_high': '高',
        'header_medium': '中',
        'header_low': '低',
        'header_show_graph': 'インタラクティブ依存関係グラフを表示',
        'header_show_graph_help': 'セル依存関係を可視化（パフォーマンスのため500ノードに制限）',
        'header_export': 'CSVをダウンロード',
        
        # Risk Table Headers
        'table_location': '対象セル',
        'table_context': '項目名',
        'table_value': '数式・数値',
        'table_severity': '重要度',
        'table_impact': '影響範囲',
        
        # Risk Type Names (for table headers)
        'risk_type_hidden_hardcode': '隠れたベタ打ち',
        'risk_type_inconsistent_formula': '数式の不整合',
        'risk_type_inconsistent_value': '値の不整合',
        'risk_type_value_conflict': '値の不整合',
        'risk_type_circular_reference': '循環参照',
        'risk_type_external_link': '外部リンク',
        'risk_type_formula_error': '数式エラー',
        'risk_type_merged_cell': '結合セル',
        'risk_type_logic_alert': 'ロジック警告',
        
        # Risk Categories
        'fatal_caption': 'モデルが壊れているか計算不能',
        'integrity_caption': '優先度：隠れたバグがここにあります',
        'structural_caption': '現在は正常に動作しますが、保守が困難',
        
        # Help Text
        'help_fatal_title': '致命的エラーとは？',
        'help_fatal_desc': '計算そのものが破綻している、または第三者がファイルを開いた際に正しく動作しない恐れがある問題です。',
        'help_fatal_circular': '**循環参照：** セルが自分自身を参照しており、計算が無限ループしている可能性があります。',
        'help_fatal_external': '**外部リンク：** 他のファイルを参照しているため、ファイルを共有した際にリンク切れ（#REF!）を起こす恐れがあります。',
        'help_fatal_formula_error': '**数式エラー：** #REF!、#VALUE!、#DIV/0! などのエラーが発生しており、正しく計算できていません。',
        'help_fatal_priority': '**【推奨アクション】** 最優先で修正してください。モデルの信頼性が損なわれています。',
        
        'help_integrity_title': '整合性リスクとは？',
        'help_integrity_desc': '計算自体は回っていますが、作成者の意図とは異なる「隠れたバグ（計算ミス）」が含まれている可能性が高い項目です。',
        'help_integrity_inconsistent': '**数式の不整合：** 同じ行や列の並びの中で、このセルだけ数式のパターンが異なっています（コピペミスの可能性があります）。',
        'help_integrity_value': '**値の不整合：** 同じ項目名（ラベル）であるにもかかわらず、箇所によって異なる数値が入力されています（更新漏れの可能性があります）。',
        'help_integrity_logic': '**ロジック警告：** 意味的に不自然な計算（例：売上 × 販管費）が行われている可能性があります。',
        'help_integrity_priority': '**【推奨アクション】** 必ず中身を確認してください。計算結果が誤っている疑いがあります。',
        
        'help_structural_title': '構造的負債とは？',
        'help_structural_desc': '現時点では動作していますが、将来のメンテナンスやシミュレーションを困難にする要因です。',
        'help_structural_hardcode': '**隠れたベタ打ち：** 数式の中に数値が直接書き込まれており、将来の変更やシミュレーションを阻害する可能性があります。',
        'help_structural_merged': '**結合セル：** セルが結合されており、データの並べ替えや集計などの加工がしにくい状態です。',
        'help_structural_priority': '**【推奨アクション】** 時間のある時に修正しておくと、モデルの使い勝手と拡張性が向上します。',
        
        # Status Messages
        'no_fatal_errors': '✅ 致命的エラーは検出されませんでした',
        'no_integrity_risks': '✅ 整合性リスクは検出されませんでした',
        'no_structural_debt': '✅ 構造的負債は検出されませんでした',
        'no_risks': '🎉 リスクは検出されませんでした！Excelモデルは良好です！',
        
        # Master-Detail UI
        'risk_table': 'リスク一覧',
        'detail_panel': '詳細パネル',
        'select_risk': 'テーブルからリスクを選択して詳細を表示',
        'risk_selected_hint': 'リスク項目を選択すると、初回のみ「ファイル情報」にジャンプします。詳細を表示するには、再度このタブをクリックしてください。',
        
        # Driver X-Ray
        'xray_title': '🎯 エグゼクティブ診断 - トップリスク',
        'xray_subtitle': '自動診断：モデルを分析し、最も危険なハードコード値を特定しました。',
        'xray_top3': '🚨 最も危険なベタ打ち数値 Top 3',
        'xray_aggregated': '💡 同じ値のリスクを集約して、全体の影響を表示しています',
        'xray_metric_occurrences': '出現箇所数',
        'xray_metric_impact': '影響セル数（合計）',
        'xray_metric_severity': '深刻度',
        'xray_metric_kpi': 'KPI影響',
        'xray_kpi_yes': '⚠️ あり',
        'xray_kpi_no': 'なし',
        'xray_impact_breakdown': '影響の内訳:',
        'xray_direct_impact': '📍 直接影響',
        'xray_indirect_impact': '🔗 間接影響',
        'xray_export_csv': '📥 影響セルをCSVエクスポート',
        'xray_download_csv': '💾 ダウンロード: impact_cells_{value}.csv',
        'xray_export_success': '✓ {count}件の影響セルをエクスポート準備完了',
        'xray_value': 'ベタ打ち値:',
        'xray_scope': '影響範囲:',
        'xray_locations': '箇所',
        'xray_show_all': '📍 すべての場所を表示',
        'xray_more_locations': '... 他 {count}箇所',
        'xray_ai_suggest': '✨ 改善提案',
        'xray_ai_analyzing': '🤖 AIコンサルタントが分析中...',
        'xray_ai_recommendation': '💡 AIコンサルタント推奨事項:',
        'xray_ai_enable': '💡 AI提案を有効化: サイドバーでAPIキーを入力してください',
        'xray_impact_trace': '📊 影響トレース',
        'xray_analysis_summary': '📖 分析サマリー',
        'xray_source': '⬆️ ソース',
        'xray_source_caption': '値の由来',
        'xray_consequences': '⬇️ 影響',
        'xray_consequences_caption': 'この値が影響するもの',
        'xray_no_sources': '🚨 ソースなし - ハードコードの可能性',
        'xray_no_consequences': '影響なし',
        'xray_formula': '数式:',
        'xray_translated': '翻訳:',
        'xray_translation_help': '💡 意味ラベル付き数式 - ロジックエラーが明確に',
        'xray_remaining': '📊 {count}個の追加ハードコード値が検出されました。まずトップ3に集中してください。',
        'xray_no_risks': 'リスクが検出されませんでした。リスクのあるファイルをアップロードしてDriver X-Rayを使用してください。',
        
        # Diff Mode
        'diff_composite_key': '🔑 複合キーマッチング',
        'diff_composite_desc': 'キー列を選択して、行が挿入、削除、並べ替えられた場合でもインテリジェントにマッチングします。',
        'diff_select_sheet': '比較するシートを選択',
        'diff_key_columns': 'キー列（カンマ区切り）',
        'diff_key_columns_help': '複合キーとして使用する列文字を入力',
        'diff_uniqueness': 'キー一意性検証',
        'diff_keys_unique': '✅ キーは一意です（{rate}%一意）',
        'diff_keys_good': 'これらの列は良好なマッチング精度を提供します。',
        'diff_keys_not_unique': '⚠️ キーは一意ではありません（{rate}%一意）',
        'diff_preview_matches': '🔍 行マッチングをプレビュー',
        'diff_preview_title': '行マッチングプレビュー',
        'diff_matched_rows': '新旧ファイル間で{count}行がマッチしました:',
        'diff_showing_first': '{count}マッチ行のうち最初の10行を表示',
        'diff_no_matches': '選択したキー列で行をマッチングできませんでした',
        'diff_comparison_summary': '📊 比較サマリー',
        'diff_improved': '🎉 モデルの健全性が向上しました！',
        'diff_degraded': '⚠️ モデルの健全性が低下しました',
        'diff_no_change': '➡️ ヘルススコアに変化なし',
        'diff_old_score': '旧スコア',
        'diff_new_score': '新スコア',
        'diff_change': '変化',
        'diff_changes_detected': '📋 検出された変更',
        'diff_tab_improved': '改善',
        'diff_tab_degraded': '悪化',
        'diff_tab_structural': '構造的',
        'diff_risks_fixed': '✅ {count}件のリスクが修正されました',
        'diff_new_risks': '⚠️ {count}件の新しいリスク',
        'diff_structural_changes': '{count}件の構造的変更',
        'diff_no_improvements': '改善は検出されませんでした',
        'diff_no_new_risks': '新しいリスクは検出されませんでした',
        'diff_no_structural': '構造的変更は検出されませんでした',
        
        # Parsing & Status
        'parsing': '🔄 Excelモデルを解析中... 少々お待ちください。',
        'parsed_in': '{time}秒で解析完了',
        'using_cached': 'キャッシュされた分析を使用',
        
        # Errors
        'error_attention': '⚠️ 注意が必要',
        'error_tip': '💡 ヒント: ファイルが有効な.xlsx形式で、パスワード保護されていないことを確認してください。',
        'error_unexpected': '⚠️ 予期しない問題',
        'error_unexpected_desc': 'ファイルの分析中に問題が発生しました: {error}',
        'error_tip_contact': '💡 ヒント: 別のファイルをアップロードするか、問題が解決しない場合はサポートに連絡してください。',
        'show_debug_log': '🔍 デバッグログを表示',
        
        # Misc
        'month': '{num}月',
        'cells': 'セル',
        'cell': 'セル',
        
        # Explanation Mode
        'explanation_mode_title': 'Explanation Mode（説明モード）',
        'explanation_mode_subtitle': '因果ツリー分析で「なぜこの数字なのか？」を理解',
        'explanation_mode_no_data': '分析可能なデータがありません',
        'model_overview': 'モデル概要',
        
        # Target Selection
        'target_selection_title': 'ターゲット指標の選択',
        'target_selection_label': '分析するKPIを選択',
        'target_selection_help': '因果ツリーを構築する重要業績評価指標（KPI）を選択してください',
        'target_selected': '選択: {label} ({address})',
        'no_kpi_candidates': 'KPI候補が見つかりません（ラベルに「売上」を含む必要があります）',
        'manual_selection_title': '手動選択',
        'manual_selection_label': 'セルアドレスを手動入力',
        'manual_selection_help': '形式: Sheet1!C10',
        'manual_target_selected': '選択: {address}',
        'invalid_cell_address': '無効なセルアドレスまたはセルが見つかりません',
        
        # Causal Tree Display
        'causal_tree_title': '因果ツリー',
        'causal_tree_subtitle': 'この指標がどのように計算されているかを階層的に表示',
        'tree_build_error': 'ツリー構築エラー: {error}',
        'cell_address': 'セルアドレス',
        'value': '値',
        'formula': '数式',
        'formula_readable': '読みやすい数式',
        'untraceable': '追跡不可',
        'untraceable_reason': '理由',
        'precedents': '参照元',
        'precedents_count': '参照元の数',
        'coming_soon': '近日公開',
        'development_status': '開発状況',
        
        # Risk Review System
        'review_checkbox': '確認',
        'review_checkbox_help': 'このリスクを確認済みにする',
        'initial_score': '初期スコア',
        'current_score': '現在スコア',
        'improvement': '改善',
        'reviewed_count': '確認済み',
        'unreviewed_count': '未確認',
        'filter_all': 'すべて',
        'filter_unreviewed': '未確認のみ',
        'filter_reviewed': '確認済みのみ',
        'export_with_review_state': 'CSVダウンロード（確認状態を含む）',
        'all_reviewed_message': '🎉 すべてのリスクを確認しました！',
        'keep_going_message': '💪 あと{count}個です！',
        'review_progress': 'レビュー進捗',
        'display_filter': '表示フィルター',
    }
}

def t(key: str, lang: str = 'ja') -> str:
    """
    Translate a key to the specified language
    
    Args:
        key: Translation key
        lang: Language code ('en' or 'ja')
    
    Returns:
        Translated string, or the key itself if not found
    """
    return TEXTS.get(lang, {}).get(key, key)

def get_language_name(lang: str) -> str:
    """Get display name for language code"""
    return '日本語' if lang == 'ja' else 'English'
