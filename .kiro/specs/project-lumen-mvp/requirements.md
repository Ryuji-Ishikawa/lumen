# Requirements Document - Project Lumen V0.4

## Introduction

**Project Lumen** is an AI-Powered Strategic Guardian for FP&A professionals in Japan. Unlike global tools that fail on "messy Japanese Excel," Lumen is purpose-built to handle complex merged cells, grid layouts, and intricate formatting common in Japanese financial models. The system goes beyond simple error checking to provide deep structural analysis, intelligent repair suggestions, and AI-powered explanations—transforming Excel models from opaque spreadsheets into transparent, maintainable strategic assets.

**Core Philosophy: "Japan First & Robustness"**
- Handle merged cells logically using Virtual Fill
- Parse complex Japanese Excel layouts that break other tools
- Fail gracefully with helpful messages, never crash
- Provide actionable insights, not just error lists

## Glossary

- **Lumen System**: AI-powered Streamlit application for strategic Excel model analysis and repair
- **Guardian**: The protective persona that helps FP&A managers maintain model integrity
- **Model Analysis Object**: Internal structured representation of a parsed Excel file with cells, formulas, dependencies, and risk metadata
- **Health Score**: Numerical metric (0-100) quantifying model quality based on detected risks
- **Risk Alert**: Detected issue categorized by severity (Critical, High, Medium, Low) with contextual labels
- **Virtual Fill**: Algorithm that propagates merged cell values to all coordinates within the merged range, enabling analysis of Japanese Excel layouts
- **Dependency Graph**: NetworkX-based directed graph representing cell-to-cell formula relationships
- **Driver X-Ray**: Feature that identifies hardcoded numbers and traces them to root drivers
- **Monthly Guardian**: Smart diff engine that distinguishes logic changes from input updates for variance analysis
- **AI Model Architect**: GPT-4o/Gemini-powered feature that suggests driver-based breakdowns for primitive hardcoded rows
- **Composite Key Matching**: Row matching strategy using user-selected key columns (e.g., "Account Name") instead of row numbers
- **Dynamic Reference**: Excel formula containing INDIRECT(), OFFSET(), or ADDRESS() that cannot be statically traced
- **BYOK**: Bring Your Own Key - user-provided API credentials for AI services

## Requirements

### Requirement 1: Robust Japanese Excel Parsing

**User Story:** As an FP&A manager in Japan, I want to upload complex Excel files with merged cells and intricate layouts, so that I can analyze models that global tools cannot parse.

#### Acceptance Criteria

1. WHEN a user accesses the application THEN the Lumen System SHALL display a file upload interface accepting .xlsx format files
2. WHEN a user uploads a password-protected Excel file THEN the Lumen System SHALL reject the file gracefully and display a helpful error message indicating password protection is not supported
3. WHEN a user uploads a legacy .xls format file THEN the Lumen System SHALL reject the file gracefully and display a message requiring .xlsx format
4. WHEN a user uploads a valid .xlsx file THEN the Lumen System SHALL parse the file using openpyxl with data_only=False to extract all formulas
5. WHEN parsing encounters an error THEN the Lumen System SHALL fail gracefully with a specific, actionable error message without crashing the application
6. WHERE two files are uploaded THEN the Lumen System SHALL enable Monthly Guardian differential analysis mode

### Requirement 2: Virtual Fill for Merged Cells (Japan First Priority)

**User Story:** As an FP&A manager working with Japanese Excel models, I want merged cells to be handled logically during analysis, so that formulas referencing merged ranges are accurately evaluated despite complex grid layouts.

#### Acceptance Criteria

1. WHEN the parser encounters a merged cell range THEN the Lumen System SHALL identify all coordinates within that range using openpyxl merged_cells API
2. WHEN analyzing cells within a merged range THEN the Lumen System SHALL apply Virtual Fill by propagating the top-left cell's value and formula to all coordinates in the range
3. WHEN a formula references a range containing merged cells THEN the Lumen System SHALL use the Virtual Fill representation for accurate dependency extraction
4. WHEN Virtual Fill is applied THEN the Lumen System SHALL NOT modify the uploaded file itself, only the internal Model Analysis Object
5. WHEN merged cell parsing fails THEN the Lumen System SHALL log the specific range and continue parsing other cells without crashing

### Requirement 3: Dependency Graph Construction (Foundation for Driver X-Ray)

**User Story:** As an FP&A manager, I want the system to extract cell dependencies and build a dependency graph, so that I can navigate precedents and dependents like in Macabacus.

#### Acceptance Criteria

1. WHEN parsing a cell containing a formula THEN the Lumen System SHALL extract all cell references using openpyxl formula tokenizer
2. WHEN a formula contains range references THEN the Lumen System SHALL extract the complete range notation (e.g., A1:B10)
3. WHEN a formula contains cross-sheet references THEN the Lumen System SHALL extract the sheet name and cell address (e.g., Sheet2!A1)
4. WHEN a formula contains INDIRECT, OFFSET, or ADDRESS functions THEN the Lumen System SHALL tag the cell as dynamic and halt dependency tracing for that branch
5. WHEN dependency extraction is complete THEN the Lumen System SHALL construct a NetworkX directed graph with cells as nodes and dependencies as edges
6. WHEN the dependency graph is constructed THEN the Lumen System SHALL enable navigation between precedents (cells this cell depends on) and dependents (cells that depend on this cell)

### Requirement 4: Hidden Hardcode Detection (Driver X-Ray Foundation)

**User Story:** As an FP&A manager, I want the system to detect hidden hardcoded values in formulas and trace them to root drivers, so that I can identify which assumptions are buried in formulas versus properly referenced.

#### Acceptance Criteria

1. WHEN analyzing a formula containing numeric literals THEN the Lumen System SHALL flag it as a Hidden Hardcode risk using openpyxl tokenizer to distinguish NUMBER tokens from RANGE tokens
2. WHEN a numeric literal is in the user-configured allowed constants list THEN the Lumen System SHALL exclude it from Hidden Hardcode detection
3. WHEN a Hidden Hardcode is detected THEN the Lumen System SHALL create a Risk Alert with severity level High including contextual row and column labels
4. WHEN generating the Risk Alert THEN the Lumen System SHALL include the cell address, sheet name, contextual labels (e.g., "Amortization @ 04-2025"), and the specific numeric literal found
5. WHEN displaying hardcode risks THEN the Lumen System SHALL provide a "Trace to Drivers" option that shows the dependency path from the hardcoded cell to its ultimate dependents

### Requirement 5: Circular Reference Detection

**User Story:** As an FP&A manager, I want to detect circular references in my Excel model, so that I can eliminate calculation errors and infinite loops.

#### Acceptance Criteria

1. WHEN the dependency graph is constructed THEN the Lumen System SHALL analyze it for circular reference patterns using networkx simple_cycles
2. WHEN a circular reference is detected THEN the Lumen System SHALL create a Risk Alert with severity level Critical
3. WHEN reporting a circular reference THEN the Lumen System SHALL identify all cells participating in the cycle with contextual labels
4. WHEN more than 100 circular references are detected THEN the Lumen System SHALL limit reporting to the first 100 and display a summary count

### Requirement 6: Merged Cell Risk Detection

**User Story:** As an FP&A manager, I want to identify formulas that reference merged cell ranges, so that I can avoid sorting and filtering errors common in Japanese Excel models.

#### Acceptance Criteria

1. WHEN a formula references a range THEN the Lumen System SHALL check if any cells within that range are part of a merged cell group
2. WHEN a formula references a range containing merged cells THEN the Lumen System SHALL create a Risk Alert with severity level Medium
3. WHEN reporting merged cell risk THEN the Lumen System SHALL identify the formula location with contextual labels and the merged range coordinates

### Requirement 7: Cross-Sheet Spaghetti Detection

**User Story:** As an FP&A manager, I want to detect excessive cross-sheet dependencies, so that I can simplify my model structure and reduce maintenance complexity.

#### Acceptance Criteria

1. WHEN analyzing a formula THEN the Lumen System SHALL count the number of distinct external sheets referenced
2. WHEN a formula references more than 2 distinct external sheets THEN the Lumen System SHALL create a Risk Alert with severity level Low for Cross-Sheet Spaghetti
3. WHEN reporting cross-sheet spaghetti THEN the Lumen System SHALL list all external sheets referenced by the formula with contextual labels

### Requirement 8: Timeline Gap Detection

**User Story:** As an FP&A manager, I want to detect timeline gaps in date-based row headers, so that I can ensure my financial projections have complete time coverage.

#### Acceptance Criteria

1. WHEN analyzing row headers THEN the Lumen System SHALL identify date patterns using regex matching (MM-YYYY, YYYY-MM, Q1, FY2024, etc.)
2. WHEN date-based headers are identified THEN the Lumen System SHALL check for missing intervals in the sequence
3. WHEN a timeline gap is detected THEN the Lumen System SHALL create a Risk Alert with severity level Medium
4. WHERE a fiscal year start month is configured THEN the Lumen System SHALL use it for timeline validation

### Requirement 9: Health Score Calculation

**User Story:** As an FP&A manager, I want to calculate a health score for my Excel model, so that I can quantify the overall quality and track improvements over time.

#### Acceptance Criteria

1. WHEN all risks are detected THEN the Lumen System SHALL calculate a Health Score starting at 100
2. WHEN calculating the Health Score THEN the Lumen System SHALL subtract 10 points for each Critical risk
3. WHEN calculating the Health Score THEN the Lumen System SHALL subtract 5 points for each High risk
4. WHEN calculating the Health Score THEN the Lumen System SHALL subtract 2 points for each Medium risk
5. WHEN the Health Score calculation is complete THEN the Lumen System SHALL display the final score with visual color coding (Green ≥80, Yellow ≥60, Red <60)

### Requirement 10: Monthly Guardian - Smart Diff with Composite Key Matching

**User Story:** As an FP&A manager performing monthly variance analysis, I want to compare two versions of my Excel model with intelligent row matching, so that I can distinguish between logic changes and normal input updates even when rows are inserted or deleted.

#### Acceptance Criteria

1. WHEN two files are uploaded THEN the Lumen System SHALL enable Monthly Guardian mode with composite key matching
2. WHEN comparing models THEN the Lumen System SHALL allow users to select key columns (e.g., "Account Name") for row matching instead of relying solely on row numbers
3. WHEN a formula is modified THEN the Lumen System SHALL categorize the change as "Logic Change" with Critical severity
4. WHEN only a cell value changes (no formula modification) THEN the Lumen System SHALL categorize the change as "Input Update" with Normal severity
5. WHEN a risk is removed in the new version THEN the Lumen System SHALL categorize the change as Improved
6. WHEN a new risk is added in the new version THEN the Lumen System SHALL categorize the change as Degraded
7. WHEN a sheet is added or removed THEN the Lumen System SHALL categorize the change as Structural
8. WHEN a hardcoded value is replaced with a cell reference THEN the Lumen System SHALL categorize the change as Improved with positive visual feedback
9. WHEN the comparison is complete THEN the Lumen System SHALL calculate and display the health score delta with encouraging messages for improvements

### Requirement 11: Driver X-Ray - Dependency Navigation

**User Story:** As an FP&A manager, I want to visualize the dependency structure and navigate between precedents and dependents, so that I can understand how changes propagate through my model like in Macabacus.

#### Acceptance Criteria

1. WHEN viewing a cell with hardcoded values THEN the Lumen System SHALL provide a "Trace to Drivers" button that highlights the dependency path
2. WHEN viewing the dependency graph THEN the Lumen System SHALL use NetworkX to render an interactive visualization with streamlit-agraph
3. WHEN a user clicks on a cell in the graph THEN the Lumen System SHALL display its precedents (cells it depends on) and dependents (cells that depend on it)
4. WHEN the dependency graph contains more than 2,000 nodes THEN the Lumen System SHALL provide filtering options by sheet and limit display to prevent performance issues
5. WHEN displaying the dependency graph THEN the Lumen System SHALL color-code nodes by risk level (Red = Critical, Yellow = High, Blue = Normal)

### Requirement 12: AI Model Architect - Driver-Based Breakdown Suggestions

**User Story:** As an FP&A manager, I want AI-powered suggestions for breaking down primitive hardcoded rows into driver-based formulas, so that I can transform static assumptions into dynamic, maintainable models.

#### Acceptance Criteria

1. WHEN a user provides an OpenAI or Google API key THEN the Lumen System SHALL store it only in session state without server persistence
2. WHEN analyzing a row with hardcoded values (e.g., "Personnel Cost = 10M") THEN the Lumen System SHALL identify it as a candidate for driver-based breakdown
3. WHEN the user clicks "Suggest Breakdown" THEN the Lumen System SHALL send a prompt to GPT-4o or Gemini-1.5-flash with role "Expert FP&A Consultant"
4. WHEN the AI response is received THEN the Lumen System SHALL display the suggestion in Japanese (e.g., "Suggest: Headcount × Average Salary")
5. WHEN the AI API call fails THEN the Lumen System SHALL display a warning message without crashing the application
6. WHEN no API key is provided THEN the Lumen System SHALL disable AI features while keeping core analysis functional
7. WHEN displaying AI suggestions THEN the Lumen System SHALL output suggestion text only (no auto-writing to Excel in MVP)

### Requirement 12A: AI Smart Context with Quality Filtering

**User Story:** As an FP&A manager, I want the AI to recover meaningful context labels for risks even when the parser finds low-quality labels like cell addresses or generic terms, so that I receive actionable insights instead of garbage labels.

#### Acceptance Criteria

1. WHEN the parser extracts a context label THEN the Lumen System SHALL validate the label quality before accepting it
2. WHEN a context label matches a cell address pattern (e.g., "E92", "AA1") THEN the Lumen System SHALL classify it as poor quality and trigger AI recovery
3. WHEN a context label contains only generic stopwords (e.g., "Total", "Sum", "Subtotal", "Check", "Val", "合計", "小計", "計", "チェック", "検証") THEN the Lumen System SHALL classify it as poor quality and trigger AI recovery
4. WHEN a context label contains only symbols or pure numbers (e.g., "-", "0", "123") THEN the Lumen System SHALL classify it as poor quality and trigger AI recovery
5. WHEN AI Smart Context is enabled and a poor quality label is detected THEN the Lumen System SHALL invoke AI recovery to find a meaningful context label
6. WHEN AI recovery is triggered THEN the Lumen System SHALL log the poor quality label and the recovered label for debugging
7. WHEN AI recovery fails to find a better label THEN the Lumen System SHALL retain the original poor quality label rather than leaving it empty

### Requirement 13: Heatmap Visualization for Risk Areas

**User Story:** As an FP&A manager, I want to see a heatmap of my Excel sheet with color-coded risk areas, so that I can quickly identify which parts of my model need attention.

#### Acceptance Criteria

1. WHEN analysis is complete THEN the Lumen System SHALL generate a grid-based heatmap visualization of the sheet
2. WHEN displaying the heatmap THEN the Lumen System SHALL color-code cells based on risk severity (Red = Critical, Yellow = High/Medium, Green = No Risk)
3. WHEN a user hovers over a cell in the heatmap THEN the Lumen System SHALL display a tooltip with the risk description and contextual labels
4. WHEN the sheet is too large (>10,000 cells) THEN the Lumen System SHALL provide a zoomed or sampled view to maintain performance

### Requirement 14: Version Timeline for File History

**User Story:** As an FP&A manager performing monthly analysis, I want to see uploaded file history as a visual timeline, so that I can track model evolution over time and select versions for comparison.

#### Acceptance Criteria

1. WHEN files are uploaded THEN the Lumen System SHALL store metadata (filename, upload timestamp, health score) in session state
2. WHEN displaying file history THEN the Lumen System SHALL render a visual timeline (not just a list) showing upload dates and health scores
3. WHEN a user clicks on a timeline entry THEN the Lumen System SHALL allow selection of that version for comparison
4. WHEN two versions are selected from the timeline THEN the Lumen System SHALL automatically trigger Monthly Guardian diff analysis

### Requirement 15: Guardian Persona and UX

**User Story:** As an FP&A manager, I want the application to use encouraging and protective language with a professional Japanese business tone, so that I feel supported rather than criticized when issues are found.

#### Acceptance Criteria

1. WHEN displaying risk information THEN the Lumen System SHALL use the term "リスク" (Risk) or "注意" (Attention) instead of "エラー" (Error)
2. WHEN suggesting improvements THEN the Lumen System SHALL use the term "改善機会" (Optimization Opportunity) instead of "悪い実装" (Bad Practice)
3. WHEN communicating with the user THEN the Lumen System SHALL maintain a Guardian persona that is reliable, helpful, and protective
4. WHEN the application loads THEN the Lumen System SHALL display a wide layout with minimum 1280px width assumption
5. WHEN displaying the interface THEN the Lumen System SHALL show a sidebar containing file uploaders, configuration options, and AI settings

### Requirement 16: Performance and Caching

**User Story:** As an FP&A manager, I want the application to perform efficiently with caching, so that I don't have to wait for re-parsing when interacting with the interface.

#### Acceptance Criteria

1. WHEN the parse function is called THEN the Lumen System SHALL apply Streamlit cache_data decorator to the parsing operation
2. WHEN determining cache validity THEN the Lumen System SHALL use the uploaded file content as the cache key
3. WHEN a file is re-uploaded with identical content THEN the Lumen System SHALL retrieve results from cache without re-parsing
4. WHEN parsing is in progress THEN the Lumen System SHALL display a spinner with the message "Parsing Excel model... This may take a minute."

### Requirement 17: Graceful Error Handling (Robustness Priority)

**User Story:** As an FP&A manager, I want the application to handle file errors gracefully with specific, actionable messages, so that I receive clear guidance when something goes wrong rather than seeing a crash.

#### Acceptance Criteria

1. WHEN a corrupt file is uploaded THEN the Lumen System SHALL catch the parsing exception and display a specific error message with troubleshooting steps
2. WHEN parsing exceeds 60 seconds THEN the Lumen System SHALL timeout gracefully and display a message indicating the file is too complex with suggestions for simplification
3. WHEN a memory error occurs during parsing THEN the Lumen System SHALL catch the exception and inform the user the file is too large with file size recommendations
4. WHEN any file handling error occurs THEN the Lumen System SHALL prevent application crashes, log the error details, and maintain a functional interface
5. WHEN openpyxl encounters styling or formatting issues THEN the Lumen System SHALL skip problematic cells and continue parsing with a warning message

### Requirement 18: Fiscal Year Configuration

**User Story:** As an FP&A manager, I want to configure my fiscal year start month, so that timeline gap detection and monthly analysis align with my organization's fiscal calendar.

#### Acceptance Criteria

1. WHEN the application loads THEN the Lumen System SHALL display a fiscal year start month selector in the sidebar
2. WHEN the selector is displayed THEN the Lumen System SHALL offer months 1 through 12 as options
3. WHEN a fiscal year start month is selected THEN the Lumen System SHALL use it for all timeline-related analysis and Monthly Guardian comparisons



### Requirement 19: Model Maturity Scoring (Excel Rehab Gamification)

**User Story:** As an FP&A manager, I want to see my Excel model's maturity level and unlock advanced features by improving quality, so that I am motivated to fix issues through a gamified progression system.

#### Acceptance Criteria

1. WHEN the Lumen System analyzes a model THEN the Lumen System SHALL calculate a maturity level based on risk counts and types
2. WHEN a model contains more than 5 Hidden Hardcode risks in critical rows THEN the Lumen System SHALL classify the model as Level 1 (Critical Condition - Static Model) and display status as "🏥 Maturity Level 1: Static Model"
3. WHEN a model has fewer than 5 Hidden Hardcode risks but contains Circular References or high-severity risks THEN the Lumen System SHALL classify the model as Level 2 (Rehabilitating - Unstable Model) and display status as "🩹 Maturity Level 2: Unstable Model"
4. WHEN a model has no Critical risks and fewer than 3 High-severity risks THEN the Lumen System SHALL classify the model as Level 3 (Healthy Athlete - Strategic Model) and display status as "🏆 Maturity Level 3: Strategic Model"
5. WHEN displaying Level 1 or Level 2 status THEN the Lumen System SHALL show locked features (Goal Seek, Scenario Planning) with tooltips indicating requirements to unlock
6. WHEN displaying Level 3 status THEN the Lumen System SHALL unlock strategic features (Goal Seek, Scenario Planning) and display them as available
7. WHEN a user views a locked feature THEN the Lumen System SHALL display a tooltip message indicating "Unlock this feature by fixing X more hardcodes" where X is the number of issues remaining
8. WHEN the AI generates suggestions for Level 1 models THEN the Lumen System SHALL adjust the AI persona to act as a "Coach" focused on decomposition and variable creation rather than error correction
9. WHEN the AI generates suggestions for Level 2 models THEN the Lumen System SHALL adjust the AI persona to focus on stability improvements and error fixes
10. WHEN the AI generates suggestions for Level 3 models THEN the Lumen System SHALL adjust the AI persona to focus on strategic optimization and scenario planning capabilities
11. WHEN displaying the maturity level THEN the Lumen System SHALL show a progress indicator (progress bar or badge) visualizing the current level and progress toward the next level
12. WHEN a user improves their model and re-uploads THEN the Lumen System SHALL recalculate the maturity level and display level-up notifications if the level increased

### Requirement 20: 3-Tier Risk Triage System

**User Story:** As an FP&A manager, I want risks organized by business impact rather than technical severity, so that I can prioritize "must fix" issues that break calculations over "should fix" maintenance issues.

#### Acceptance Criteria

1. WHEN displaying detected risks THEN the Lumen System SHALL organize risks into three tabs based on business impact classification
2. WHEN a risk is a Circular Reference THEN the Lumen System SHALL classify it as Fatal Error (Tab 1) because the model is uncomputable
3. WHEN a risk is a Phantom Link (external reference) THEN the Lumen System SHALL classify it as Fatal Error (Tab 1) because the model cannot be evaluated independently
4. WHEN a risk is a formula error (#REF!, #VALUE!, #DIV/0!) THEN the Lumen System SHALL classify it as Fatal Error (Tab 1) because calculations are broken
5. WHEN a risk is an Inconsistent Formula (row pattern break) THEN the Lumen System SHALL classify it as Integrity Risk (Tab 2) because logic may be incorrect
6. WHEN a risk is an Inconsistent Value (same label with different hardcoded values) THEN the Lumen System SHALL classify it as Integrity Risk (Tab 2) because it indicates potential update omission
7. WHEN a risk is a Logic Alert from the Logic Translator THEN the Lumen System SHALL classify it as Integrity Risk (Tab 2) because semantic oddities suggest errors
8. WHEN a risk is a Hidden Hardcode with consistent values THEN the Lumen System SHALL classify it as Structural Debt (Tab 3) because it works correctly but is hard to maintain
9. WHEN a risk is a Merged Cell THEN the Lumen System SHALL classify it as Structural Debt (Tab 3) because it works correctly but creates maintenance issues
10. WHEN displaying Tab 1 (Fatal Errors) THEN the Lumen System SHALL use red color coding and critical severity indicators
11. WHEN displaying Tab 2 (Integrity Risks) THEN the Lumen System SHALL use orange/yellow color coding and make this tab visually prominent as it contains hidden bugs
12. WHEN displaying Tab 3 (Structural Debt) THEN the Lumen System SHALL use blue/gray color coding to indicate lower priority maintenance issues
13. WHEN a user switches between tabs THEN the Lumen System SHALL display risk counts in tab labels (e.g., "Fatal Errors (3)", "Integrity Risks (7)", "Structural Debt (12)")
14. WHEN displaying risks within each tab THEN the Lumen System SHALL show cell address, sheet name, contextual labels, and risk description in a clear table format

### Requirement 21: Professional Minimalism & Master-Detail Layout ("The Cockpit")

**User Story:** As a finance professional, I want a Bloomberg Terminal-style master-detail interface with high data density and minimal decoration, so that I can quickly scan risks and inspect details without excessive scrolling or clicking.

#### Acceptance Criteria

1. WHEN the application loads THEN the Lumen System SHALL display a split-view layout with 60% width for the master panel and 40% width for the detail panel
2. WHEN displaying the master panel THEN the Lumen System SHALL render an interactive risk table using st.dataframe with single-row selection mode enabled
3. WHEN displaying the risk table THEN the Lumen System SHALL include columns for Location, Context, Risk Type, and Value with compact row height
4. WHEN displaying the risk table THEN the Lumen System SHALL remove all emojis and icons from data cells to maximize information density
5. WHEN displaying the risk table THEN the Lumen System SHALL apply color coding only for danger signals using bold red text or light red background for Critical/High severity risks
6. WHEN displaying the risk table THEN the Lumen System SHALL use default black/gray text for Medium/Low severity risks
7. WHEN displaying the risk table THEN the Lumen System SHALL sort risks by severity descending then by impact count descending with the most dangerous item at the top
8. WHEN a user selects a row in the risk table THEN the Lumen System SHALL display detailed information in the detail panel
9. WHEN displaying the detail panel with a selected risk THEN the Lumen System SHALL show Section A (Logic X-Ray) with the dependency trace in simple text format
10. WHEN displaying the detail panel with a selected risk THEN the Lumen System SHALL show Section B (The Cure) with the AI suggestion and refactoring recipe
11. WHEN no row is selected THEN the Lumen System SHALL display instructions in the detail panel prompting the user to select a risk
12. WHEN rendering the interface THEN the Lumen System SHALL use compact spacing and minimal padding to show maximum rows above the fold
13. WHEN rendering the interface THEN the Lumen System SHALL use a professional financial statement aesthetic with clean typography and no decorative elements

### Requirement 22: Risk Review System with Session-Based Tracking

**User Story:** As an FP&A manager, I want to mark risks as reviewed with checkboxes and see my progress in real-time, so that I can systematically work through issues and track completion without losing state during my session.

#### Acceptance Criteria

1. WHEN displaying the risk table THEN the Lumen System SHALL add a "確認" (Review) checkbox column as the leftmost column
2. WHEN a user checks a risk checkbox THEN the Lumen System SHALL store the review state in session_state and update the display immediately
3. WHEN a risk is marked as reviewed THEN the Lumen System SHALL apply visual feedback by graying out the row and reducing opacity to 0.6
4. WHEN calculating the health score THEN the Lumen System SHALL display both initial score and current score based on unreviewed risks only
5. WHEN displaying the health score THEN the Lumen System SHALL show review progress as "確認済み: X/Y (Z%)" where X is reviewed count, Y is total count, and Z is percentage
6. WHEN a user exports to CSV THEN the Lumen System SHALL include a "確認済み" column with TRUE/FALSE values and a timestamp column showing when the export was generated
7. WHEN displaying the risk table THEN the Lumen System SHALL provide filter options: "すべて" (All), "未確認のみ" (Unreviewed Only), "確認済みのみ" (Reviewed Only)
8. WHEN the filter is set to "未確認のみ" THEN the Lumen System SHALL display only risks where the checkbox is unchecked
9. WHEN the filter is set to "確認済みのみ" THEN the Lumen System SHALL display only risks where the checkbox is checked
10. WHEN the session ends THEN the Lumen System SHALL clear all review states (no persistence across sessions)
11. WHEN calculating the current health score THEN the Lumen System SHALL use the formula: 100 - (Unreviewed_Critical×10) - (Unreviewed_High×5) - (Unreviewed_Medium×2)
12. WHEN displaying the health score section THEN the Lumen System SHALL show initial score, current score, and improvement delta with color coding (green for improvement)
