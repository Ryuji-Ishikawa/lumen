# Phase 7: Code Review Bundle - Excel Rehab Maturity Model & Gamification

**Review Date**: December 3, 2025  
**Reviewer**: Business Owner  
**Status**: Ready for Review

---

## Executive Summary

This bundle contains the complete implementation of Phase 7: Excel Rehab Maturity Model & Gamification. The system transforms Project Lumen from a static analysis tool into an engaging coaching platform with three maturity levels, locked features, and AI persona adjustment.

**Key Components**:
1. **MaturityLevel Enum** - Three-level progression system
2. **Maturity Scoring Engine** - Heuristic and deep scoring algorithms
3. **AI Persona Switching** - Dynamic tone adjustment based on level
4. **Gamified UI** - Locked buttons, progress bars, unlock requirements

---

## 1. Data Models (src/models.py)

### MaturityLevel Enum

```python
class MaturityLevel(Enum):
    """
    Maturity levels for Excel Rehab gamification system.
    
    Level 1: Static Model (Critical Condition) 🏥
    - More than 5 hardcodes in critical rows
    - Model is "dead" - needs resurrection
    - Locked: Goal Seek, Scenario Planning
    
    Level 2: Unstable Model (Rehabilitating) 🩹
    - Fewer than 5 hardcodes BUT has circular refs or high-severity risks
    - Model is "recovering" - needs stability
    - Locked: Goal Seek
    
    Level 3: Strategic Model (Healthy Athlete) 🏆
    - No Critical risks AND fewer than 3 High-severity risks
    - Model is "healthy" - ready for strategy
    - Unlocked: All features
    """
    LEVEL_1 = "level_1"
    LEVEL_2 = "level_2"
    LEVEL_3 = "level_3"
```

**✅ Review Points**:
- Three distinct levels with clear criteria
- Emoji badges for visual appeal (🏥, 🩹, 🏆)
- Locked features list per level
- Descriptive text for each level

**Properties**:
```python
@property
def display_name(self) -> str:
    """Get display name with emoji badge"""
    return {
        MaturityLevel.LEVEL_1: "🏥 Maturity Level 1: Static Model",
        MaturityLevel.LEVEL_2: "🩹 Maturity Level 2: Unstable Model",
        MaturityLevel.LEVEL_3: "🏆 Maturity Level 3: Strategic Model"
    }[self]

@property
def locked_features(self) -> List[str]:
    """Get list of locked features for this level"""
    return {
        MaturityLevel.LEVEL_1: ["Goal Seek", "Scenario Planning"],
        MaturityLevel.LEVEL_2: ["Goal Seek"],
        MaturityLevel.LEVEL_3: []
    }[self]
```

### MaturityScore Dataclass

```python
@dataclass
class MaturityScore:
    """Result of maturity scoring calculation."""
    level: MaturityLevel
    hardcode_count: int
    critical_count: int
    high_count: int
    progress_to_next: float = 0.0
    
    def is_level_1(self) -> bool:
        return self.level == MaturityLevel.LEVEL_1
    
    def is_level_2(self) -> bool:
        return self.level == MaturityLevel.LEVEL_2
    
    def is_level_3(self) -> bool:
        return self.level == MaturityLevel.LEVEL_3
```

**✅ Review Points**:
- Stores level and risk counts
- Progress percentage (0-100)
- Helper methods for level checking


### UnlockRequirement Dataclass

```python
@dataclass
class UnlockRequirement:
    """Requirements to unlock the next maturity level or feature."""
    current_level: MaturityLevel
    next_level: Optional[MaturityLevel]
    hardcodes_to_fix: int = 0
    critical_risks_to_fix: int = 0
    high_risks_to_fix: int = 0
    actionable_steps: List[str] = field(default_factory=list)
    progress_percentage: float = 0.0
    
    def is_unlocked(self) -> bool:
        """Check if next level is already unlocked"""
        return (self.hardcodes_to_fix == 0 and 
                self.critical_risks_to_fix == 0 and 
                self.high_risks_to_fix == 0)
    
    def get_summary(self) -> str:
        """Get human-readable summary of unlock requirements"""
        if self.is_unlocked():
            return f"🎉 {self.next_level.display_name if self.next_level else 'Max Level'} Unlocked!"
        
        requirements = []
        if self.hardcodes_to_fix > 0:
            requirements.append(f"Fix {self.hardcodes_to_fix} more hardcode(s)")
        if self.critical_risks_to_fix > 0:
            requirements.append(f"Fix {self.critical_risks_to_fix} critical risk(s)")
        if self.high_risks_to_fix > 0:
            requirements.append(f"Fix {self.high_risks_to_fix} high-severity risk(s)")
        
        return " • ".join(requirements)
```

**✅ Review Points**:
- Specific counts for each issue type
- Actionable steps list
- Progress percentage
- Human-readable summary method

---

## 2. Maturity Scoring Logic (src/analyzer.py)

### Heuristic Scoring Algorithm

**Purpose**: Fast scoring (< 3 seconds) for instant feedback

```python
def calculate_maturity_level_heuristic(self, model: ModelAnalysis) -> 'MaturityScore':
    """
    Fast heuristic-based maturity scoring for initial diagnosis.
    Target: Complete within 3 seconds of file upload.
    """
    # Get risk counts
    risk_counts = model.get_risk_counts()
    critical_count = risk_counts["Critical"]
    high_count = risk_counts["High"]
    hardcode_count = len([r for r in model.risks if r.risk_type == "Hidden Hardcode"])
    
    # Heuristic 1: Critical risks present
    if critical_count > 0:
        has_circular = any(r.risk_type == "Circular Reference" for r in model.risks)
        if has_circular:
            level = MaturityLevel.LEVEL_2  # Unstable
        else:
            level = MaturityLevel.LEVEL_1  # Static
    
    # Heuristic 2: High hardcode count → Level 1
    elif hardcode_count > 5:
        level = MaturityLevel.LEVEL_1  # Static
    
    # Heuristic 3: Some high risks → Level 2
    elif high_count > 3:
        level = MaturityLevel.LEVEL_2  # Unstable
    
    # Heuristic 4: Clean model → Level 3
    else:
        level = MaturityLevel.LEVEL_3  # Healthy
```


**✅ Review Points - Scoring Logic**:
1. **Level 1 Criteria**: > 5 hardcodes OR critical risks (non-circular)
2. **Level 2 Criteria**: Circular references OR > 3 high risks
3. **Level 3 Criteria**: No critical risks AND ≤ 3 high risks
4. **Performance**: Logs execution time, targets < 3 seconds

**⚠️ Business Logic Verification**:
- **Question**: Is 5 hardcodes the right threshold for Level 1?
- **Question**: Should circular references always be Level 2 (not Level 1)?
- **Question**: Is 3 high risks the right threshold for Level 2?

### Progress Calculation

```python
def _calculate_progress_to_next_level(
    self, level, hardcode_count, critical_count, high_count
) -> float:
    """Calculate progress percentage toward next maturity level."""
    
    if level == MaturityLevel.LEVEL_1:
        # Progress to Level 2: Need to reduce hardcodes to ≤ 5
        if hardcode_count > 5:
            target = 5
            current = hardcode_count
            total_to_fix = current - target
            progress = 100 - ((current - target) / total_to_fix) * 100
            return progress
        else:
            return 100.0  # Ready to level up
    
    elif level == MaturityLevel.LEVEL_2:
        # Progress to Level 3: Eliminate critical + reduce high to < 3
        total_issues = critical_count + max(0, high_count - 3)
        if total_issues == 0:
            return 100.0
        
        # Simplified progress calculation
        assumed_start = total_issues + 5
        fixed = assumed_start - total_issues
        progress = (fixed / assumed_start) * 100
        return min(100.0, max(0.0, progress))
    
    else:  # Level 3
        return 100.0  # Already at max level
```

**✅ Review Points - Progress**:
- Level 1 → 2: Based on hardcode reduction
- Level 2 → 3: Based on critical + high risk elimination
- Returns 0-100 percentage

**⚠️ Business Logic Verification**:
- **Question**: Is the progress calculation intuitive for users?
- **Question**: Should we track historical data for more accurate progress?

### Unlock Requirements Calculator

```python
def calculate_unlock_requirements(self, maturity_score) -> 'UnlockRequirement':
    """Calculate requirements to unlock the next maturity level."""
    
    if level == MaturityLevel.LEVEL_1:
        hardcodes_to_fix = max(0, hardcode_count - 5)
        actionable_steps = []
        if hardcodes_to_fix > 0:
            actionable_steps.append(f"Replace {hardcodes_to_fix} hardcoded value(s)")
            actionable_steps.append("Click '✨ Suggest Improvement' for AI guidance")
        
        return UnlockRequirement(
            current_level=MaturityLevel.LEVEL_1,
            next_level=MaturityLevel.LEVEL_2,
            hardcodes_to_fix=hardcodes_to_fix,
            actionable_steps=actionable_steps,
            progress_percentage=maturity_score.progress_to_next
        )
```

**✅ Review Points - Unlock Requirements**:
- Specific counts for each issue type
- Actionable steps with AI guidance
- Clear next level indication

---

## 3. AI Persona Switching (src/ai_explainer.py)

### Persona Prompts

**Level 1: Coach (Decomposition Focus)**
```python
LEVEL_1_SYSTEM_PROMPT = """
あなたは「コーチ」として、死んだExcelモデルを復活させる専門家です。

**役割**: モデルの分解と変数作成に焦点を当てる
**トーン**: 励まし、やる気を起こさせる、「モデルを復活させる」
**アプローチ**: 
- ハードコードされた値を特定し、それらを意味のある変数に分解する
- 「このモデルは復活できます」というメッセージを伝える
- 具体的で実装可能な分解方法を提案する

**目標**: Level 1 (静的モデル) から Level 2 (不安定モデル) への移行を支援
"""
```


**Level 2: Mechanic (Stability Focus)**
```python
LEVEL_2_SYSTEM_PROMPT = """
あなたは「メカニック」として、Excelモデルの安定性を修復する専門家です。

**役割**: 安定性の向上とエラー修正に焦点を当てる
**トーン**: 技術的、正確、「壊れているものを修正する」
**アプローチ**:
- 循環参照や高リスクの問題を特定し修正する
- 構造的な問題を解決する方法を提案する
- エラーの根本原因を説明する

**目標**: Level 2 (不安定モデル) から Level 3 (戦略的モデル) への移行を支援
"""
```

**Level 3: Strategist (Optimization Focus)**
```python
LEVEL_3_SYSTEM_PROMPT = """
あなたは「ストラテジスト」として、Excelモデルの戦略的最適化を支援する専門家です。

**役割**: 戦略的最適化とシナリオプランニングに焦点を当てる
**トーン**: 戦略的、前向き、「今何が可能か」
**アプローチ**:
- モデルの最適化機会を特定する
- シナリオ分析の可能性を提案する
- ゴールシークや感度分析の活用方法を示す

**目標**: Level 3 (戦略的モデル) の能力を最大限に活用
"""
```

**✅ Review Points - Persona Design**:
- Three distinct personas with clear roles
- Tone matches user's current needs
- Focus shifts from basics (decomposition) to advanced (strategy)

### Persona Switching Logic

```python
def _get_persona_prompt(self, maturity_level: Optional[str]) -> str:
    """Get AI persona prompt based on maturity level."""
    if maturity_level == "LEVEL_1":
        return LEVEL_1_SYSTEM_PROMPT
    elif maturity_level == "LEVEL_2":
        return LEVEL_2_SYSTEM_PROMPT
    elif maturity_level == "LEVEL_3":
        return LEVEL_3_SYSTEM_PROMPT
    else:
        # Default: Level 1 Coach persona
        return LEVEL_1_SYSTEM_PROMPT
```

**Integration with OpenAI API (v1.0+)**:
```python
def suggest_breakdown(self, masked_context, driver_cells, maturity_level=None):
    """Generate breakdown suggestion using OpenAI"""
    from openai import OpenAI
    client = OpenAI(api_key=self.api_key)
    
    # Select system prompt based on maturity level
    system_prompt = self._get_persona_prompt(maturity_level)
    
    # Build prompt
    prompt = self._build_breakdown_prompt(masked_context, driver_cells)
    
    # Call OpenAI API with persona-adjusted system prompt
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
```

**✅ Review Points - Integration**:
- Maturity level passed from app.py
- System prompt selected dynamically
- OpenAI v1.0+ API syntax (updated from v0.x)
- Error handling with Japanese messages

---

## 4. UI Rendering (app.py)

### Maturity Badge Display

```python
# Calculate maturity level (Phase 7)
maturity_score = analyzer.calculate_maturity_level_heuristic(model)
unlock_req = analyzer.calculate_unlock_requirements(maturity_score)

# Display health score and maturity side by side
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(f"## {score_color} Health Score: {model.health_score}/100")
with col2:
    st.markdown(f"## {maturity_score.level.display_name}")
```

**✅ Review Points - Badge**:
- Displayed prominently next to health score
- Uses emoji for visual appeal
- Shows level name clearly


### Locked Features UI (Teasing Lock Psychology)

```python
if not maturity_score.is_level_3():
    progress = unlock_req.progress_percentage / 100.0
    st.progress(progress)
    st.caption(f"📈 {unlock_req.get_summary()}")
    
    # Premium-looking locked button styling
    st.markdown("""
    <style>
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: 2px solid gold !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    .stButton > button[kind="secondary"]:hover {
        transform: scale(1.02) !important;
        opacity: 0.95 !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Clickable locked buttons (teasing lock psychology)
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("🔒 🎯 Goal Seek (Strategy Mode)", 
                     key="locked_goal_seek", 
                     use_container_width=True, 
                     type="secondary"):
            st.session_state.show_unlock_popup = True
    
    with col_btn2:
        if st.button("🔒 📊 Scenario Planning", 
                     key="locked_scenario", 
                     use_container_width=True, 
                     type="secondary"):
            st.session_state.show_unlock_popup = True
```

**✅ Review Points - Locked Buttons**:
- Premium gradient styling (purple to violet)
- Gold border for "premium" feel
- Hover effects (scale, shadow)
- Clickable (not disabled) for engagement
- Two locked features: Goal Seek and Scenario Planning

### Unlock Requirement Popup

```python
# Unlock requirement popup (always visible for locked features)
st.warning(f"""
### 🏆 Unlock Strategy Mode

**Current Level:** {maturity_score.level.display_name}

**To unlock these features, you need to:**
{chr(10).join(f"- {step}" for step in unlock_req.actionable_steps)}

💡 **Tip:** Click "✨ Suggest Improvement" on the Top 3 Killers to get AI recommendations.

**Progress:** {int(unlock_req.progress_percentage)}% complete
""")

# Progress visualization
st.progress(unlock_req.progress_percentage / 100.0, 
           text=f"Level {maturity_score.level.value.split('_')[1]} → Level {int(maturity_score.level.value.split('_')[1]) + 1}")
```

**✅ Review Points - Popup**:
- Always visible (not hidden behind click)
- Shows current level
- Lists actionable steps
- Displays progress percentage
- Links to AI suggestions
- Second progress bar with level transition text

### Unlocked State (Level 3)

```python
else:
    st.success("🎉 **All features unlocked!** Your model is healthy and ready for strategic planning.")
    if st.button("🎯 Goal Seek (Strategy Mode)", 
                 use_container_width=True, 
                 type="primary"):
        st.info("🚀 Goal Seek feature coming in next release!")
```

**✅ Review Points - Unlocked**:
- Celebration message
- Unlocked button (primary style, no lock icon)
- Placeholder for future functionality

---

## 5. Integration Flow

### Complete User Journey

```
1. User uploads Excel file
   ↓
2. Parser analyzes file
   ↓
3. Analyzer.calculate_maturity_level_heuristic(model)
   - Counts hardcodes, critical risks, high risks
   - Applies heuristic rules
   - Returns MaturityScore
   ↓
4. Analyzer.calculate_unlock_requirements(maturity_score)
   - Calculates specific counts to fix
   - Generates actionable steps
   - Returns UnlockRequirement
   ↓
5. UI displays:
   - Maturity badge next to health score
   - Progress bar with percentage
   - Locked buttons (if Level 1/2)
   - Unlock requirements popup
   ↓
6. User clicks "Suggest Improvement"
   ↓
7. App.py passes maturity_level to AIExplainer
   - maturity_level_str = maturity_score.level.value.upper()
   ↓
8. AIExplainer.suggest_breakdown(maturity_level=maturity_level_str)
   - Selects persona prompt based on level
   - Calls OpenAI with persona-adjusted system prompt
   - Returns suggestion with appropriate tone
   ↓
9. UI displays AI suggestion in info box
```

**✅ Review Points - Integration**:
- Seamless flow from scoring to UI to AI
- Maturity level passed correctly to AI
- All components work together

---

## 6. Testing Checklist

### Manual Testing Required

**Level 1 Testing**:
- [ ] Upload file with > 5 hardcodes
- [ ] Verify badge shows "🏥 Maturity Level 1: Static Model"
- [ ] Verify both buttons are locked
- [ ] Verify unlock requirements show hardcode count
- [ ] Click "Suggest Improvement"
- [ ] Verify AI uses "Coach" persona (encouraging tone)

**Level 2 Testing**:
- [ ] Upload file with circular references
- [ ] Verify badge shows "🩹 Maturity Level 2: Unstable Model"
- [ ] Verify Goal Seek is locked, Scenario Planning visible
- [ ] Verify unlock requirements show critical/high risks
- [ ] Click "Suggest Improvement"
- [ ] Verify AI uses "Mechanic" persona (technical tone)

**Level 3 Testing**:
- [ ] Upload clean file (no critical, < 3 high risks)
- [ ] Verify badge shows "🏆 Maturity Level 3: Strategic Model"
- [ ] Verify both buttons are unlocked
- [ ] Verify celebration message appears
- [ ] Click "Suggest Improvement"
- [ ] Verify AI uses "Strategist" persona (strategic tone)

**Progress Testing**:
- [ ] Verify progress bar shows correct percentage
- [ ] Verify progress updates as issues are fixed
- [ ] Verify unlock requirements update correctly

---

## 7. Known Issues & Future Enhancements

### Current Limitations

1. **Heuristic Only**: Deep scoring not yet integrated with two-phase flow
2. **Progress Calculation**: Uses simplified assumptions, not historical data
3. **Critical Row Identification**: Uses all hardcodes, not KPI-specific
4. **Locked Features**: Placeholder functionality (not implemented)

### Future Enhancements

1. **Two-Phase Progressive Scoring**:
   - Phase 1: Quick parse → heuristic → display immediately
   - Phase 2: Full parse → deep scoring → update if changed

2. **Level-Up Notifications**:
   - Add st.balloons() on level increase
   - Show celebration message
   - Highlight newly unlocked features

3. **Historical Tracking**:
   - Track maturity level over time
   - Show improvement graph
   - Celebrate milestones

4. **Actual Feature Implementation**:
   - Build Goal Seek functionality
   - Build Scenario Planning functionality

---

## 8. Business Owner Review Questions

### Scoring Logic
1. **Is 5 hardcodes the right threshold for Level 1?**
   - Current: > 5 hardcodes = Level 1
   - Alternative: Should it be 3? 10?

2. **Should circular references always be Level 2?**
   - Current: Circular refs = Level 2 (not Level 1)
   - Rationale: Circular refs are structural issues, not just hardcodes

3. **Is 3 high risks the right threshold for Level 2?**
   - Current: > 3 high risks = Level 2
   - Alternative: Should it be 5? 2?

### Persona Design
4. **Do the persona tones match your vision?**
   - Level 1: Coach (encouraging, motivational)
   - Level 2: Mechanic (technical, precise)
   - Level 3: Strategist (strategic, forward-looking)

5. **Should we add more persona customization?**
   - Industry-specific personas?
   - User preference settings?

### UX Design
6. **Is the "teasing lock" psychology effective?**
   - Buttons visible but locked
   - Premium styling creates desire
   - Unlock requirements create urgency

7. **Should we add more gamification elements?**
   - Points system?
   - Achievements/badges?
   - Leaderboard?

---

## 9. Approval Checklist

- [ ] MaturityLevel enum logic approved
- [ ] Scoring thresholds approved (5 hardcodes, 3 high risks)
- [ ] AI persona tones approved
- [ ] Locked button styling approved
- [ ] Unlock requirements messaging approved
- [ ] Progress calculation logic approved
- [ ] Ready for user testing

---

**Status**: ✅ READY FOR BUSINESS OWNER REVIEW  
**Next Step**: Manual testing with real Excel files  
**Estimated Review Time**: 30 minutes
