"""Test to verify external link detection logic"""

# Test formulas
formula1 = '=Sheet2!A1'  # Internal cross-sheet
formula2 = '=[OtherFile.xlsx]Sheet1!A1'  # External workbook
formula3 = "='Sheet Name'!A1"  # Internal with space in name
formula4 = "='C:\\Users\\John\\[Data.xlsx]Sheet1'!A1"  # External with path

print('Formula 1 (internal cross-sheet):', formula1)
print('  Has brackets:', '[' in formula1 and ']' in formula1)
print('  Has path:', ':\\' in formula1 or '/' in formula1)
print('  Should flag: NO')
print()

print('Formula 2 (external workbook):', formula2)
print('  Has brackets:', '[' in formula2 and ']' in formula2)
print('  Has path:', ':\\' in formula2 or '/' in formula2)
print('  Should flag: YES')
print()

print('Formula 3 (internal with space):', formula3)
print('  Has brackets:', '[' in formula3 and ']' in formula3)
print('  Has path:', ':\\' in formula3 or '/' in formula3)
print('  Should flag: NO')
print()

print('Formula 4 (external with path):', formula4)
print('  Has brackets:', '[' in formula4 and ']' in formula4)
print('  Has path:', ':\\' in formula4 or '/' in formula4)
print('  Should flag: YES')
