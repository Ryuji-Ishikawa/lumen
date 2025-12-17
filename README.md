# Project Lumen - Excel Model Guardian 🛡️

A Streamlit-based web application for analyzing Excel financial models, detecting risks, and visualizing improvements.

## Features

- **Risk Detection**: Identify hidden hardcodes, circular references, merged cell risks, cross-sheet complexity, and timeline gaps
- **Health Scoring**: Quantify model quality with a 0-100 score
- **Differential Analysis**: Compare two versions to track improvements
- **AI Explanations**: Get business-focused explanations of complex formulas (OpenAI/Google)
- **Guardian Persona**: Supportive, protective language instead of critical error messages

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
streamlit run app.py
```

## Project Structure

```
project-lumen/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── src/
│   ├── models.py         # Data models
│   ├── parser.py         # Excel parser with Virtual Fill
│   ├── analyzer.py       # Risk detection and health scoring
│   ├── diff.py           # Model comparison engine
│   └── ai_explainer.py   # AI-powered formula explanations
└── tests/                # Test suite
```

## Development Status

🚧 **MVP in Development** - Following phased implementation approach

## License

Proprietary - Internal use only
