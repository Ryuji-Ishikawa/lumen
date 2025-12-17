"""
Script to fix AI prompts in ai_explainer.py to prevent labeling fallacy
"""

# Read the file
with open('src/ai_explainer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the old prompt section
old_prompt = """        # Extract global context
        occurrence_count = labels.get('occurrence_count', '不明')
        value_type = labels.get('value_type', '不明')
        actual_value = labels.get('actual_value', '不明')
        
        prompt = f\"\"\"
【グローバルコンテキスト】
- ハードコード値: {actual_value}
- 値のタイプ: {value_type}
- 出現回数: {occurrence_count}箇所
- 行ラベル: {row_label}
- 影響を受けるドライバー: {len(driver_cells)}個のセル

【タスク】
この値の一元管理方法を、具体的な手順で提案してください。
「前提条件シート」「名前付き範囲」「セル参照の置換」などの実装手順を含めてください。

❌ ビジネス概念の説明は不要です
✅ Excelでの具体的な操作手順を提示してください。
\"\"\"
        return prompt"""

# Define the new prompt section
new_prompt = """        # Extract global context (PHASE 7.5: Prevent labeling fallacy)
        occurrence_count = labels.get('occurrence_count', '不明')
        affected_locations = labels.get('affected_locations', 1)
        diffusion = labels.get('diffusion', 0)
        value_type = labels.get('value_type', '不明')
        actual_value = labels.get('actual_value', '不明')
        
        # CRITICAL: Detect if this is a global parameter (appears many times)
        is_global_param = diffusion > 3
        
        if is_global_param:
            # Global parameter: DO NOT use local row label for naming
            prompt = f\"\"\"
【グローバルコンテキスト - グローバルパラメータ検出】
- ベタ打ち値: {actual_value}
- 値のタイプ: {value_type}
- 出現回数: {occurrence_count}箇所 (ワークブック全体で{affected_locations}つの異なる場所に分散)
- 最初の出現場所: {row_label}
- 影響を受けるセル: {len(driver_cells)}個

⚠️ **重要な制約**: この値は{occurrence_count}箇所で使用されています。これはグローバルパラメータ（為替レート、税率、成長率など）の可能性が高いです。

❌ **禁止事項**: 最初の行ラベル「{row_label}」をパラメータ名として使用しないでください。これは誤解を招きます。

✅ **推奨アプローチ**:
1. ユーザーに確認を促す: 「この値 {actual_value} は何を表していますか？（例: 為替レート、税率、成長率）」
2. 汎用的な名前を提案: 「Param_{actual_value}」または「グローバル定数_{actual_value}」
3. 前提条件シートに配置し、名前付き範囲で管理

【タスク】
この値の一元管理方法を、具体的な手順で提案してください。
「前提条件シート」「名前付き範囲」「セル参照の置換」などの実装手順を含めてください。

❌ ビジネス概念の説明は不要です
❌ 最初の行ラベルを使った具体的な名前（例: 「全体開発費」）を提案しないでください
✅ Excelでの具体的な操作手順を提示してください
✅ ユーザーに値の意味を確認するよう促してください
\"\"\"
        else:
            # Local parameter: Can use row label
            prompt = f\"\"\"
【グローバルコンテキスト - ローカルパラメータ】
- ベタ打ち値: {actual_value}
- 値のタイプ: {value_type}
- 出現回数: {occurrence_count}箇所
- 行ラベル: {row_label}
- 影響を受けるセル: {len(driver_cells)}個

【タスク】
この値の一元管理方法を、具体的な手順で提案してください。
「前提条件シート」「名前付き範囲」「セル参照の置換」などの実装手順を含めてください。

❌ ビジネス概念の説明は不要です
✅ Excelでの具体的な操作手順を提示してください
\"\"\"
        
        return prompt"""

# Replace all occurrences
content = content.replace(old_prompt, new_prompt)

# Write back
with open('src/ai_explainer.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed AI prompts in ai_explainer.py")
print(f"   Updated {content.count('グローバルパラメータ検出')} provider(s)")
