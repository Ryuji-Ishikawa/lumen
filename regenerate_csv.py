"""
Regenerate CSV export with date-only column filter fix
"""

import csv
from datetime import datetime
from pathlib import Path
from src.parser import parse_excel_file
from src.analyzer import ModelAnalyzer

def export_risks_to_csv(model, output_file):
    """Export risks to CSV file"""
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Write header
        writer.writerow(['Risk Type', 'Severity', 'Location', 'Context', 'Description'])
        
        # Write risks
        for risk in model.risks:
            writer.writerow([
                risk.risk_type,
                risk.severity,
                risk.get_location(),
                risk.get_context(),  # This now uses the fixed get_context() method
                risk.description
            ])
    
    print(f"✅ Exported {len(model.risks)} risks to {output_file}")

def main():
    # Load the sample file
    sample_file = Path("Sample_Business Plan.xlsx")
    
    if not sample_file.exists():
        print(f"❌ File not found: {sample_file}")
        return
    
    print(f"📂 Loading {sample_file}...")
    
    # Read file
    with open(sample_file, 'rb') as f:
        file_bytes = f.read()
    
    # Parse
    print("🔄 Parsing Excel file...")
    model = parse_excel_file(file_bytes, sample_file.name)
    
    # Analyze
    print("🔍 Analyzing risks...")
    analyzer = ModelAnalyzer()
    model = analyzer.analyze(model, fiscal_start_month=1, allowed_constants=[])
    
    # Export
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")
    output_file = f"{timestamp}_export.csv"
    
    print(f"💾 Exporting to {output_file}...")
    export_risks_to_csv(model, output_file)
    
    print(f"\n✅ Done! Health Score: {model.health_score}/100")
    print(f"📊 Total Risks: {len(model.risks)}")
    
    # Show sample of fixed contexts
    print("\n📋 Sample of context labels (first 10 risks):")
    for i, risk in enumerate(model.risks[:10], 1):
        context = risk.get_context()
        print(f"  {i}. {context}")

if __name__ == "__main__":
    main()
