# V0.4 UI Implementation Plan

## Summary

Implementing two missing V0.4 visual components in app.py:

### 1. Task 11: Interactive Dependency Graph ✅
- Install: streamlit-agraph (already installed)
- Location: After "Dependency Graph" metrics section
- Implementation: Add interactive graph visualization with filtering

### 2. Task 21: Maturity Badge & Gamification ✅
- Location: After Health Score display
- Implementation: 
  - Calculate maturity level from health score and risk counts
  - Display maturity badge (🏥 Level 1, 🩹 Level 2, 🏆 Level 3)
  - Add "Teasing Lock" buttons for Goal Seek/Strategy Mode
  - Show progress bar and unlock requirements

## Changes Required

### File: app.py

#### Change 1: Add imports
```python
from streamlit_agraph import agraph, Node, Edge, Config
```

#### Change 2: Add maturity calculation function (after imports)
```python
def calculate_maturity_level(model: ModelAnalysis) -> tuple:
    """Calculate maturity level based on risks"""
    risk_counts = model.get_risk_counts()
    
    # Count hardcodes in critical rows (simplified: use all hardcodes)
    hardcode_count = len([r for r in model.risks if r.risk_type == "Hidden Hardcode"])
    
    # Level 1: > 5 hardcodes
    if hardcode_count > 5:
        return 1, "🏥 Maturity Level 1: Static Model", hardcode_count - 5
    
    # Level 2: Circular refs OR > 3 high risks
    if risk_counts["Critical"] > 0 or risk_counts["High"] > 3:
        remaining = max(risk_counts["Critical"], risk_counts["High"] - 3)
        return 2, "🩹 Maturity Level 2: Unstable Model", remaining
    
    # Level 3: Clean model
    return 3, "🏆 Maturity Level 3: Strategic Model", 0
```

#### Change 3: Inject maturity badge after health score (line ~458)
Replace:
```python
st.markdown(f"## {score_color} Health Score: {model.health_score}/100")
```

With:
```python
# Calculate maturity level
maturity_level, maturity_display, remaining_issues = calculate_maturity_level(model)

# Display health score and maturity together
col1, col2 = st.columns([1, 1])
with col1:
    st.markdown(f"## {score_color} Health Score: {model.health_score}/100")
with col2:
    st.markdown(f"## {maturity_display}")

# Show progress and locked features
if maturity_level < 3:
    progress = max(0, 1 - (remaining_issues / 10))
    st.progress(progress)
    st.caption(f"Fix {remaining_issues} more issues to reach Level {maturity_level + 1}")
    
    # Teasing Lock buttons
    st.markdown("#### 🔒 Locked Features")
    if st.button("🎯 Goal Seek (Strategy Mode) - Premium", disabled=True, use_container_width=True):
        pass
    st.warning(f"""
    **Unlock Strategy Mode**
    
    Current Level: {maturity_display}
    
    To unlock Goal Seek, you need to:
    - Fix **{remaining_issues} more issues**
    - Reach Level 3: Strategic Model
    
    💡 Tip: Use AI suggestions to fix hardcoded values
    """)
else:
    st.success("🎉 All features unlocked! Your model is healthy.")
    if st.button("🎯 Goal Seek (Strategy Mode)", use_container_width=True):
        st.info("Goal Seek feature coming soon!")
```

#### Change 4: Add interactive graph after dependency metrics (line ~430)
After the dependency graph metrics, add:
```python
# Interactive Dependency Visualization
if st.checkbox("Show Interactive Dependency Graph", value=False):
    st.markdown("#### 🕸️ Interactive Dependency Graph")
    
    # Limit nodes for performance
    max_nodes = 500
    total_nodes = model.dependency_graph.number_of_nodes()
    
    if total_nodes > max_nodes:
        st.warning(f"⚠️ Graph has {total_nodes} nodes. Showing first {max_nodes} for performance.")
    
    # Build graph for visualization
    nodes = []
    edges = []
    
    node_list = list(model.dependency_graph.nodes())[:max_nodes]
    
    for node in node_list:
        # Determine color based on risk
        color = "#90EE90"  # Green default
        for risk in model.risks:
            if risk.get_location() == node:
                if risk.severity == "Critical":
                    color = "#FF6B6B"  # Red
                elif risk.severity == "High":
                    color = "#FFD93D"  # Yellow
                break
        
        # Extract sheet and address
        if '!' in node:
            sheet, addr = node.split('!')
            label = addr
        else:
            label = node
        
        nodes.append(Node(id=node, label=label, size=10, color=color))
    
    # Add edges
    for node in node_list:
        for successor in model.dependency_graph.successors(node):
            if successor in node_list:
                edges.append(Edge(source=node, target=successor))
    
    # Configure graph
    config = Config(
        width="100%",
        height=600,
        directed=True,
        physics=True,
        hierarchical=False
    )
    
    # Render graph
    if nodes:
        agraph(nodes=nodes, edges=edges, config=config)
        
        st.caption("""
        **Legend:** 🔴 Critical Risk | 🟡 High Risk | 🟢 No Risk
        
        **Tip:** Click and drag to explore. Zoom with mouse wheel.
        """)
    else:
        st.info("No dependencies to visualize")
```

## Testing

After implementation:
1. Run the app: `streamlit run app.py`
2. Upload a test file
3. Verify maturity badge displays correctly
4. Verify locked buttons show unlock requirements
5. Verify interactive graph renders (with checkbox)

## Status

Ready to implement.
