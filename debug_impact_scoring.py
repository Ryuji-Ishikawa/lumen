"""
Debug script to analyze why 201.26 isn't ranked as highest risk.

This script will:
1. Parse the CSV export
2. Calculate impact scores for each hardcoded value
3. Show the ranking logic
"""

import csv
from collections import defaultdict

# Read the CSV export
risks_by_value = defaultdict(list)

with open('2025-12-03T06-08_export.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['Risk Type'] == 'Hidden Hardcode':
            # Extract hardcoded value from description
            desc = row['Description']
            
            # Parse "Hardcoded value 'X' (N instances)"
            if "Hardcoded value '" in desc:
                value_part = desc.split("Hardcoded value '")[1]
                value = value_part.split("'")[0]
                
                # Parse instance count
                instance_part = desc.split('(')[1].split(' instances')[0]
                instance_count = int(instance_part)
                
                risks_by_value[value].append({
                    'sheet': row['Location'].split('!')[0],
                    'location': row['Location'],
                    'context': row['Context'],
                    'instances': instance_count,
                    'severity': row['Severity']
                })

# Calculate total diffusion for each value
print("=" * 80)
print("IMPACT ANALYSIS: Hardcoded Values by Diffusion")
print("=" * 80)

value_stats = []
for value, risk_list in risks_by_value.items():
    total_diffusion = sum(r['instances'] for r in risk_list)
    num_locations = len(risk_list)
    
    value_stats.append({
        'value': value,
        'total_diffusion': total_diffusion,
        'num_locations': num_locations,
        'risks': risk_list
    })

# Sort by total diffusion (descending)
value_stats.sort(key=lambda x: x['total_diffusion'], reverse=True)

# Display top 10
print("\nTop 10 Hardcoded Values by Diffusion (Total Occurrences):\n")
for idx, stat in enumerate(value_stats[:10], 1):
    print(f"{idx}. Value: {stat['value']}")
    print(f"   Total Diffusion: {stat['total_diffusion']} occurrences")
    print(f"   Appears in: {stat['num_locations']} different locations")
    print(f"   Locations:")
    for risk in stat['risks']:
        print(f"     - {risk['location']}: {risk['instances']} instances ({risk['context']})")
    print()

# Find 201.26 specifically
print("=" * 80)
print("SPECIFIC ANALYSIS: Value 201.26")
print("=" * 80)

if '201.26' in risks_by_value:
    stat_201 = next(s for s in value_stats if s['value'] == '201.26')
    rank = value_stats.index(stat_201) + 1
    
    print(f"\nRank: #{rank} out of {len(value_stats)} unique values")
    print(f"Total Diffusion: {stat_201['total_diffusion']} occurrences")
    print(f"Appears in: {stat_201['num_locations']} different locations")
    print(f"\nDetailed breakdown:")
    for risk in stat_201['risks']:
        print(f"  - {risk['location']}")
        print(f"    Context: {risk['context']}")
        print(f"    Instances: {risk['instances']}")
        print()
else:
    print("\n⚠️ Value 201.26 NOT FOUND in CSV export!")

# Analyze what's ranking higher
print("=" * 80)
print("WHY IS 201.26 NOT #1?")
print("=" * 80)

if '201.26' in risks_by_value:
    stat_201 = next(s for s in value_stats if s['value'] == '201.26')
    rank = value_stats.index(stat_201) + 1
    
    if rank > 1:
        print(f"\n201.26 is ranked #{rank}. Here's what's ranking higher:\n")
        for idx, stat in enumerate(value_stats[:rank-1], 1):
            print(f"#{idx}: Value '{stat['value']}' - {stat['total_diffusion']} occurrences")
            print(f"     Appears in {stat['num_locations']} locations")
    else:
        print("\n✓ 201.26 IS ranked #1!")
