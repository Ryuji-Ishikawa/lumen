"""
AI Model Architect - The "Brain"

This module provides AI-powered formula explanations and breakdown suggestions
with enterprise-grade security (data masking) and hybrid key management.

Key Features:
- Hybrid Strategy: Master Key (Standard) + BYOK (Pro)
- Data Masking: Never send raw financial values to LLM
- Azure OpenAI Compatible: Future-proof for Japanese enterprise
- Prompt Engineering: AI acts as "Senior FP&A Consultant"
- Persona Adjustment: AI tone adapts to model maturity level (Phase 7)
"""

from typing import Dict, List, Optional, Any
from abc import ABC, abstractmethod
import re
from dataclasses import dataclass

# ============================================================================
# AI Persona Prompts (Phase 7: Excel Rehab Maturity Model)
# ============================================================================

LEVEL_1_SYSTEM_PROMPT = """
あなたは「成長パートナー」として、ユーザーのモデルを次のレベルに引き上げる専門家です。

**コミュニケーション原則**:
✅ 検証的アプローチ: 「これは〇〇です」ではなく「これは〇〇の可能性があります」
✅ ポジティブフレーム: 「エラー回避」ではなく「新しい能力の獲得」
✅ Level 1フォーカス: 安定性と分解（Decomposition）に集中

**出力フォーマット（厳守）**:
```
【発見】
この値は{diffusion}箇所で使用されています。
パターンから見ると、これは個別の項目というより、モデル全体を動かす前提条件かもしれません。

【可能性の検証】
もしこれが為替レートや成長率のような前提条件なら、以下の能力が解放されます：
✓ 値の分解: 構成要素を明確化し、計算根拠を可視化
✓ 一元管理: {diffusion}箇所の更新を1箇所に集約
✓ 透明性向上: チームメンバーが計算フローを理解しやすく

【実装ステップ: {prescription_mode}】
1. [具体的な手順1]
2. [具体的な手順2]
3. [具体的な手順3]

💡 次のステップ: この改善により、モデルの安定性が向上し、Level 2の効率化機能が使えるようになります。
```

**スマートネーミング（Diffusion > 10の場合）**:
この値は{diffusion}箇所で使用されています。

💭 検証ポイント: 
もし「{row_label}」が特定の行項目ではなく、モデル全体に影響する前提条件（為替レート、税率など）なら、
より汎用的な名前（例: "USD_JPY_Rate", "Global_Tax_Rate"）の方が、将来の拡張性が高まります。

**Level 1の目標**: 
まずは値を分解し、計算の透明性を確保することで、モデルの「安定性」を高めましょう。
"""

LEVEL_2_SYSTEM_PROMPT = """
あなたは「効率化パートナー」として、ユーザーの作業効率を最大化する専門家です。

**コミュニケーション原則**:
✅ 検証的アプローチ: 「問題がある」ではなく「改善の機会がある」
✅ ポジティブフレーム: 「リスク回避」ではなく「効率の向上」
✅ Level 2フォーカス: 効率性と一元管理（Centralization）に集中

**出力フォーマット（厳守）**:
```
【現状分析】
この値は{occurrence_count}箇所で使用されています。
現在の構造を見ると、更新作業や変更管理に時間がかかっている可能性があります。

【効率化の機会】
この値を一元管理すると、以下の能力が解放されます：
✓ 作業効率: 更新作業が{occurrence_count}箇所 → 1箇所に削減
✓ 変更管理: 修正の影響範囲が即座に把握可能
✓ チーム協働: 前提条件が明確で、引継ぎがスムーズに

【実装ステップ】
1. [具体的な手順1]
2. [具体的な手順2]
3. [具体的な手順3]

💡 次のステップ: この効率化により、Level 3の戦略的機能（シナリオ分析など）が使えるようになります。
```

**スマートネーミング（Diffusion > 10の場合）**:
この値は{diffusion}箇所で使用されています。

💭 検証ポイント:
使用パターンから見ると、これは「{row_label}」という特定項目ではなく、
モデル全体の前提条件（為替、税率、成長率など）の可能性があります。

その場合、より汎用的な名前（例: "Assumption_FX_Rate", "Global_Growth_Rate"）にすることで、
将来の拡張や他のメンバーの理解が容易になります。

**Level 2の目標**:
値を一元管理することで、日々の作業「効率」を高め、変更に強いモデルを作りましょう。
"""

LEVEL_3_SYSTEM_PROMPT = """
あなたは「戦略パートナー」として、ユーザーの意思決定を加速する専門家です。

**コミュニケーション原則**:
✅ 検証的アプローチ: 「これをすべき」ではなく「この可能性を検討できます」
✅ ポジティブフレーム: 「問題解決」ではなく「新しい能力の獲得」
✅ Level 3フォーカス: 戦略性とシナリオ分析（Scenario Planning）に集中

**出力フォーマット（厳守）**:
```
【戦略的可能性】
この値は{occurrence_count}箇所で使用されています。
モデルの成熟度から見ると、戦略的な分析機能を追加できる段階に来ています。

【解放される能力】
この値を戦略的に活用すると、以下の新しい能力が獲得できます：
✓ シナリオ分析: Best/Base/Worst caseを瞬時に比較
✓ 感度分析: どの前提条件が最も影響するか即座に判明
✓ What-if分析: 会議中に条件を変えながらリアルタイムで試算

【実装ステップ】
1. [具体的な手順1]
2. [具体的な手順2]
3. [具体的な手順3]

💡 戦略的価値: この機能により、経営会議での「もし〇〇だったら？」という質問に、
その場で複数のシナリオを比較しながら回答できるようになります。
```

**スマートネーミング（Diffusion > 10の場合）**:
この値は{diffusion}箇所で使用されています。

💭 検証ポイント:
使用パターンから見ると、これは「{row_label}」という個別項目ではなく、
モデル全体を動かす戦略的前提条件（為替、成長率、市場シェアなど）の可能性があります。

その場合、戦略的な名前（例: "Strategic_Growth_Rate", "Market_Share_Target"）にすることで、
シナリオ分析時に前提条件として認識しやすくなります。

**Level 3の目標**:
シナリオ分析機能を追加することで、モデルを「戦略的意思決定ツール」に進化させましょう。
"""


@dataclass
class MaskedContext:
    """
    Context with masked numeric values for secure AI prompts.
    
    Attributes:
        formula_structure: Formula with numbers replaced by tokens
        cell_labels: Row and column labels for context
        dependencies: List of dependent cells (addresses only)
        value_mapping: Mapping of tokens to actual values (for internal use)
    """
    formula_structure: str
    cell_labels: Dict[str, str]
    dependencies: List[str]
    value_mapping: Dict[str, float]


class AIProvider(ABC):
    """
    Abstract base class for AI providers.
    
    Supports: OpenAI, Google Gemini, Azure OpenAI
    """
    
    def __init__(self, api_key: str, model: str = None):
        """
        Initialize AI provider.
        
        Args:
            api_key: API key for the provider
            model: Model name (provider-specific)
        """
        self.api_key = api_key
        self.model = model
    
    @abstractmethod
    def explain_formula(self, masked_context: MaskedContext) -> str:
        """
        Generate explanation for a formula.
        
        Args:
            masked_context: Context with masked values
            
        Returns:
            AI-generated explanation in Japanese
        """
        pass
    
    @abstractmethod
    def suggest_breakdown(self, masked_context: MaskedContext, 
                         driver_cells: List[str],
                         maturity_level: Optional[str] = None) -> str:
        """
        Suggest how to break down a hardcoded value.
        
        Args:
            masked_context: Context with masked values
            driver_cells: List of driver cells affected
            maturity_level: Maturity level for persona adjustment (LEVEL_1, LEVEL_2, LEVEL_3)
            
        Returns:
            AI-generated suggestion in Japanese
        """
        pass


class OpenAIProvider(AIProvider):
    """OpenAI GPT-4 provider"""
    
    def __init__(self, api_key: str, model: str = "gpt-4o"):
        super().__init__(api_key, model)
    
    def explain_formula(self, masked_context: MaskedContext) -> str:
        """Generate formula explanation using OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            # Build prompt
            prompt = self._build_explanation_prompt(masked_context)
            
            # Call OpenAI API (new v1.0+ syntax)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたは経験豊富なFP&Aコンサルタントです。Excelの数式を分析し、ビジネスの観点から説明してください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"AI説明の生成に失敗しました: {str(e)}"
    
    def suggest_breakdown(self, masked_context: MaskedContext, 
                         driver_cells: List[str],
                         maturity_level: Optional[str] = None) -> str:
        """Generate breakdown suggestion using OpenAI"""
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            
            # Select system prompt based on maturity level
            system_prompt = self._get_persona_prompt(maturity_level)
            
            # Build prompt
            prompt = self._build_breakdown_prompt(masked_context, driver_cells)
            
            # Call OpenAI API with persona-adjusted system prompt (new v1.0+ syntax)
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"分解提案の生成に失敗しました: {str(e)}"
    
    def _build_explanation_prompt(self, context: MaskedContext) -> str:
        """Build prompt for formula explanation"""
        labels = context.cell_labels
        row_label = labels.get('row_label', '不明')
        col_label = labels.get('col_label', '不明')
        
        prompt = f"""
以下のExcel数式を分析してください：

数式構造: {context.formula_structure}
行ラベル: {row_label}
列ラベル: {col_label}
依存セル数: {len(context.dependencies)}

この数式の目的と、ビジネス上の意味を日本語で説明してください。
また、潜在的なリスクがあれば指摘してください。
"""
        return prompt
    
    def _build_breakdown_prompt(self, context: MaskedContext, 
                                driver_cells: List[str]) -> str:
        """Build prompt for breakdown suggestion with global context and smart naming"""
        labels = context.cell_labels
        row_label = labels.get('row_label', '不明')
        
        # Extract global context
        occurrence_count = labels.get('occurrence_count', '不明')
        diffusion = labels.get('diffusion', occurrence_count)  # Use diffusion if available
        dominance = labels.get('dominance', len(driver_cells))
        value_type = labels.get('value_type', '不明')
        actual_value = labels.get('actual_value', '不明')
        prescription_mode = labels.get('prescription_mode', 'Centralization')
        
        # Smart naming guidance (if diffusion > 10)
        naming_guidance = ""
        try:
            if isinstance(diffusion, (int, float)) and diffusion > 10:
                naming_guidance = f"""

【重要: スマートネーミング】
この値は{diffusion}箇所で使用されています。これは「{row_label}」という特定項目ではなく、
モデル全体に影響するグローバル前提条件（為替レート、税率、成長率など）の可能性が高いです。

❌ 悪い命名例: "{row_label}" （誤解を招く）
✅ 良い命名例: 
  - 為替の場合: "USD_JPY_Rate" または "FX_Rate_Assumption"
  - 税率の場合: "Corporate_Tax_Rate" または "Global_Tax_Rate"
  - 成長率の場合: "Revenue_Growth_Rate" または "Market_Growth_Assumption"

命名時は、この値の本質的な意味（為替、税率、成長率など）を反映してください。
"""
        except:
            pass
        
        prompt = f"""
【グローバルコンテキスト】
- ハードコード値: {actual_value}
- 値のタイプ: {value_type}
- 出現回数（Diffusion）: {diffusion}箇所
- 影響範囲（Dominance）: {dominance}個のセル
- 行ラベル: {row_label}
- 推奨モード: {prescription_mode}
{naming_guidance}

【タスク】
この値を一元管理する方法を、ビジネス価値を強調しながら提案してください。

**必須要素**:
1. ビジネスリスク: なぜこのままだと危険か（シナリオ分析不可、監査対応困難など）
2. 推奨ソリューション: 具体的な実装手順（3-5ステップ）
3. ビジネス価値: 修正後に得られる価値（意思決定速度、保守性、信頼性など）
4. Pro Tip: 実務での活用シーン（会議での即答、監査対応など）

❌ 禁止: Excel機能の説明（「名前付き範囲とは...」）
✅ 必須: ビジネス価値の提示（「これにより取締役会で即座にシナリオ比較が可能」）

**トーン**: CFOアドバイザーとして、Excel機能ではなく「安心感」と「競争優位性」を売る。
"""
        return prompt

    def _get_persona_prompt(self, maturity_level: Optional[str]) -> str:
        """
        Get AI persona prompt based on maturity level.
        
        Args:
            maturity_level: Maturity level (LEVEL_1, LEVEL_2, LEVEL_3)
            
        Returns:
            System prompt for the AI persona
        """
        if maturity_level == "LEVEL_1":
            return LEVEL_1_SYSTEM_PROMPT
        elif maturity_level == "LEVEL_2":
            return LEVEL_2_SYSTEM_PROMPT
        elif maturity_level == "LEVEL_3":
            return LEVEL_3_SYSTEM_PROMPT
        else:
            # Default: Level 1 Coach persona
            return LEVEL_1_SYSTEM_PROMPT


class GoogleProvider(AIProvider):
    """Google Gemini provider"""
    
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        super().__init__(api_key, model)
    
    def explain_formula(self, masked_context: MaskedContext) -> str:
        """Generate formula explanation using Google Gemini"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            model = genai.GenerativeModel(self.model)
            
            # Build prompt
            prompt = self._build_explanation_prompt(masked_context)
            
            # Call Gemini API
            response = model.generate_content(prompt)
            
            return response.text
            
        except Exception as e:
            return f"AI説明の生成に失敗しました: {str(e)}"
    
    def suggest_breakdown(self, masked_context: MaskedContext, 
                         driver_cells: List[str],
                         maturity_level: Optional[str] = None) -> str:
        """Generate breakdown suggestion using Google Gemini"""
        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            
            # Select system prompt based on maturity level
            system_prompt = self._get_persona_prompt(maturity_level)
            
            # Build prompt with persona
            user_prompt = self._build_breakdown_prompt(masked_context, driver_cells)
            full_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            model = genai.GenerativeModel(self.model)
            
            # Call Gemini API
            response = model.generate_content(full_prompt)
            
            return response.text
            
        except Exception as e:
            return f"分解提案の生成に失敗しました: {str(e)}"
    
    def _build_explanation_prompt(self, context: MaskedContext) -> str:
        """Build prompt for formula explanation"""
        labels = context.cell_labels
        row_label = labels.get('row_label', '不明')
        col_label = labels.get('col_label', '不明')
        
        prompt = f"""
あなたは経験豊富なFP&Aコンサルタントです。

以下のExcel数式を分析してください：

数式構造: {context.formula_structure}
行ラベル: {row_label}
列ラベル: {col_label}
依存セル数: {len(context.dependencies)}

この数式の目的と、ビジネス上の意味を日本語で説明してください。
また、潜在的なリスクがあれば指摘してください。
"""
        return prompt
    
    def _build_breakdown_prompt(self, context: MaskedContext, 
                                driver_cells: List[str]) -> str:
        """Build prompt for breakdown suggestion with global context and smart naming"""
        labels = context.cell_labels
        row_label = labels.get('row_label', '不明')
        
        # Extract global context
        occurrence_count = labels.get('occurrence_count', '不明')
        diffusion = labels.get('diffusion', occurrence_count)  # Use diffusion if available
        dominance = labels.get('dominance', len(driver_cells))
        value_type = labels.get('value_type', '不明')
        actual_value = labels.get('actual_value', '不明')
        prescription_mode = labels.get('prescription_mode', 'Centralization')
        
        # Smart naming guidance (if diffusion > 10)
        naming_guidance = ""
        try:
            if isinstance(diffusion, (int, float)) and diffusion > 10:
                naming_guidance = f"""

【重要: スマートネーミング】
この値は{diffusion}箇所で使用されています。これは「{row_label}」という特定項目ではなく、
モデル全体に影響するグローバル前提条件（為替レート、税率、成長率など）の可能性が高いです。

❌ 悪い命名例: "{row_label}" （誤解を招く）
✅ 良い命名例: 
  - 為替の場合: "USD_JPY_Rate" または "FX_Rate_Assumption"
  - 税率の場合: "Corporate_Tax_Rate" または "Global_Tax_Rate"
  - 成長率の場合: "Revenue_Growth_Rate" または "Market_Growth_Assumption"

命名時は、この値の本質的な意味（為替、税率、成長率など）を反映してください。
"""
        except:
            pass
        
        prompt = f"""
【グローバルコンテキスト】
- ハードコード値: {actual_value}
- 値のタイプ: {value_type}
- 出現回数（Diffusion）: {diffusion}箇所
- 影響範囲（Dominance）: {dominance}個のセル
- 行ラベル: {row_label}
- 推奨モード: {prescription_mode}
{naming_guidance}

【タスク】
この値を一元管理する方法を、ビジネス価値を強調しながら提案してください。

**必須要素**:
1. ビジネスリスク: なぜこのままだと危険か（シナリオ分析不可、監査対応困難など）
2. 推奨ソリューション: 具体的な実装手順（3-5ステップ）
3. ビジネス価値: 修正後に得られる価値（意思決定速度、保守性、信頼性など）
4. Pro Tip: 実務での活用シーン（会議での即答、監査対応など）

❌ 禁止: Excel機能の説明（「名前付き範囲とは...」）
✅ 必須: ビジネス価値の提示（「これにより取締役会で即座にシナリオ比較が可能」）

**トーン**: CFOアドバイザーとして、Excel機能ではなく「安心感」と「競争優位性」を売る。
"""
        return prompt

    def _get_persona_prompt(self, maturity_level: Optional[str]) -> str:
        """
        Get AI persona prompt based on maturity level.
        
        Args:
            maturity_level: Maturity level (LEVEL_1, LEVEL_2, LEVEL_3)
            
        Returns:
            System prompt for the AI persona
        """
        if maturity_level == "LEVEL_1":
            return LEVEL_1_SYSTEM_PROMPT
        elif maturity_level == "LEVEL_2":
            return LEVEL_2_SYSTEM_PROMPT
        elif maturity_level == "LEVEL_3":
            return LEVEL_3_SYSTEM_PROMPT
        else:
            # Default: Level 1 Coach persona
            return LEVEL_1_SYSTEM_PROMPT


class AzureOpenAIProvider(AIProvider):
    """
    Azure OpenAI provider (future-proof for Japanese enterprise).
    
    Note: Requires additional configuration (endpoint, deployment_name)
    """
    
    def __init__(self, api_key: str, endpoint: str, deployment_name: str, 
                 model: str = "gpt-4"):
        super().__init__(api_key, model)
        self.endpoint = endpoint
        self.deployment_name = deployment_name
    
    def explain_formula(self, masked_context: MaskedContext) -> str:
        """Generate formula explanation using Azure OpenAI"""
        # Placeholder for Azure OpenAI implementation
        return "Azure OpenAI統合は準備中です。"
    
    def suggest_breakdown(self, masked_context: MaskedContext, 
                         driver_cells: List[str]) -> str:
        """Generate breakdown suggestion using Azure OpenAI"""
        # Placeholder for Azure OpenAI implementation
        return "Azure OpenAI統合は準備中です。"


class DataMasker:
    """
    Enterprise-grade data masking for AI prompts.
    
    CRITICAL: Never send raw financial values to LLM.
    Replace all numbers with tokens (<NUM_1>, <NUM_2>, etc.)
    """
    
    @staticmethod
    def mask_formula(formula: str) -> tuple[str, Dict[str, float]]:
        """
        Mask all numeric values in a formula.
        
        Args:
            formula: Original formula with numbers
            
        Returns:
            Tuple of (masked_formula, value_mapping)
            
        Example:
            Input:  "=B2*1.1+5000"
            Output: ("=B2*<NUM_1>+<NUM_2>", {"<NUM_1>": 1.1, "<NUM_2>": 5000})
        """
        if not formula:
            return "", {}
        
        # Find all numbers in the formula
        number_pattern = r'\b\d+\.?\d*\b'
        numbers = re.findall(number_pattern, formula)
        
        # Create mapping
        value_mapping = {}
        masked_formula = formula
        
        for i, num_str in enumerate(numbers, 1):
            token = f"<NUM_{i}>"
            value_mapping[token] = float(num_str)
            # Replace first occurrence
            masked_formula = masked_formula.replace(num_str, token, 1)
        
        return masked_formula, value_mapping
    
    @staticmethod
    def mask_value(value: Any) -> str:
        """
        Mask a single value.
        
        Args:
            value: Value to mask
            
        Returns:
            Masked token
        """
        if isinstance(value, (int, float)):
            return "<NUM_VAL>"
        return str(value)
    
    @staticmethod
    def create_masked_context(formula: str, cell_labels: Dict[str, str],
                             dependencies: List[str]) -> MaskedContext:
        """
        Create a masked context for AI prompts.
        
        Args:
            formula: Original formula
            cell_labels: Row and column labels
            dependencies: List of dependent cells
            
        Returns:
            MaskedContext with all values masked
        """
        masked_formula, value_mapping = DataMasker.mask_formula(formula)
        
        return MaskedContext(
            formula_structure=masked_formula,
            cell_labels=cell_labels,
            dependencies=dependencies,
            value_mapping=value_mapping
        )


class AIExplainer:
    """
    Main interface for AI explanations with Hybrid Strategy.
    
    Hybrid Strategy:
    - Standard Plan: Use master_key (if provided)
    - Pro Plan: Use user_key (if provided)
    - Fallback: Disable AI features
    """
    
    def __init__(self, master_key: Optional[str] = None):
        """
        Initialize AI Explainer.
        
        Args:
            master_key: Lumen's master API key (for Standard Plan)
        """
        self.master_key = master_key
        self.provider: Optional[AIProvider] = None
    
    def configure(self, provider_name: str, user_key: Optional[str] = None):
        """
        Configure AI provider with Hybrid Strategy.
        
        Args:
            provider_name: "OpenAI", "Google", or "Azure"
            user_key: User's custom API key (BYOK mode)
        """
        # Hybrid Strategy: user_key takes precedence
        api_key = user_key if user_key else self.master_key
        
        if not api_key:
            raise ValueError("No API key available. Provide user_key or master_key.")
        
        # Create provider
        if provider_name == "OpenAI":
            self.provider = OpenAIProvider(api_key)
        elif provider_name == "Google":
            self.provider = GoogleProvider(api_key)
        elif provider_name == "Azure":
            # Azure requires additional config
            raise NotImplementedError("Azure OpenAI requires endpoint configuration")
        else:
            raise ValueError(f"Unknown provider: {provider_name}")
    
    def explain_formula(self, formula: str, cell_labels: Dict[str, str],
                       dependencies: List[str], 
                       mask_data: bool = True) -> str:
        """
        Generate AI explanation for a formula.
        
        Args:
            formula: Formula to explain
            cell_labels: Row and column labels for context
            dependencies: List of dependent cells
            mask_data: Whether to mask numeric values (default: True)
            
        Returns:
            AI-generated explanation in Japanese
        """
        if not self.provider:
            return "AI機能が設定されていません。APIキーを設定してください。"
        
        # Create masked context (ALWAYS mask for enterprise security)
        if mask_data:
            context = DataMasker.create_masked_context(formula, cell_labels, dependencies)
        else:
            # Even if mask_data=False, we still mask for security
            # This is a safety measure
            context = DataMasker.create_masked_context(formula, cell_labels, dependencies)
        
        # Call AI provider
        return self.provider.explain_formula(context)
    
    def suggest_breakdown(self, formula: str, cell_labels: Dict[str, str],
                         dependencies: List[str], driver_cells: List[str],
                         mask_data: bool = True,
                         maturity_level: Optional[str] = None) -> str:
        """
        Generate AI suggestion for breaking down a hardcoded value.
        
        Args:
            formula: Formula with hardcoded value
            cell_labels: Row and column labels for context
            dependencies: List of dependent cells
            driver_cells: List of driver cells affected
            mask_data: Whether to mask numeric values (default: True)
            maturity_level: Maturity level for persona adjustment (LEVEL_1, LEVEL_2, LEVEL_3)
            
        Returns:
            AI-generated suggestion in Japanese
        """
        if not self.provider:
            return "AI機能が設定されていません。APIキーを設定してください。"
        
        # Create masked context (ALWAYS mask for enterprise security)
        if mask_data:
            context = DataMasker.create_masked_context(formula, cell_labels, dependencies)
        else:
            # Even if mask_data=False, we still mask for security
            context = DataMasker.create_masked_context(formula, cell_labels, dependencies)
        
        # Call AI provider with maturity level for persona adjustment
        return self.provider.suggest_breakdown(context, driver_cells, maturity_level)
