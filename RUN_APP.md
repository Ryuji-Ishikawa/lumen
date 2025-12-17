# Running Project Lumen - Debug Dashboard

## Quick Start

### 1. Start the Streamlit App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### 2. Upload Your Excel Files

**Sidebar → File Upload:**
- **Single File Analysis:** Upload one file to analyze
- **Differential Analysis:** Upload both "Reference (Old)" and "Target (New)" files to compare

**Supported:**
- File format: `.xlsx` only
- Max file size: 50MB
- Japanese Excel files fully supported

### 3. View Debug Dashboard

The app now includes comprehensive debugging features:

#### **Performance Timer**
- Shows parse time for each file
- Displayed in success message and Debug Log tab

#### **Debug Log Tab**
- Click the "Debug Log" tab to see detailed parsing information
- Logs include:
  - File size
  - Parse time
  - Number of sheets, cells, merged ranges
  - Any errors or warnings

#### **Error Handling**
- If parsing fails, the app will NOT crash
- Instead, you'll see:
  - Clear error message
  - Debug log with details
  - Suggestions for fixing the issue

### 4. Features Available

**Dashboard Tab:**
- Health score
- Risk summary
- File statistics

**All Risks Tab:**
- Complete list of detected risks
- Sortable table

**By Severity Tab:**
- Risks grouped by severity
- Expandable sections

**Dependency Tree Tab:**
- Interactive graph visualization
- Filter by sheet
- Adjustable node limit

**Debug Log Tab:** ⭐ NEW
- Parse timing
- Detailed logs
- Error diagnostics

## Debug Features

### What Gets Logged

1. **File Upload**
   - Filename
   - File size in MB
   - Start time

2. **Parsing**
   - Parse duration
   - Number of sheets
   - Number of cells
   - Number of merged ranges

3. **Errors**
   - Error type
   - Error message
   - Detailed context

### Log Levels

- ℹ️ **INFO:** General information
- ✅ **SUCCESS:** Successful operations
- ⚠️ **WARNING:** Non-critical issues
- ❌ **ERROR:** Critical failures

### Example Debug Log

```
✅ [10:52:15] Parsed Sample_Business Plan.xlsx in 2.34s
   {
     "sheets": 3,
     "cells": 1245,
     "merged_ranges": 47
   }

ℹ️ [10:52:13] File size: 2.45 MB

ℹ️ [10:52:13] Starting parse of Sample_Business Plan.xlsx
```

## Troubleshooting

### App Won't Start

```bash
# Install dependencies
pip install -r requirements.txt

# Verify Streamlit is installed
streamlit --version
```

### File Upload Fails

**Check:**
1. File is `.xlsx` format (not `.xls`)
2. File is not password-protected
3. File size is under 50MB

**Debug:**
- Check the Debug Log tab for specific error details
- Look for error messages in the expandable "Show Debug Log" section

### Parsing Takes Too Long

**For large files (>10MB):**
- Parsing may take 30-60 seconds
- Watch the spinner for progress
- Check Debug Log for timing details

**If it times out:**
- Try analyzing one sheet at a time
- Reduce file complexity
- Check for circular references

## Performance Expectations

| File Size | Cells | Expected Parse Time |
|-----------|-------|---------------------|
| < 1MB     | < 1,000 | < 1s |
| 1-5MB     | 1,000-10,000 | 1-5s |
| 5-20MB    | 10,000-50,000 | 5-30s |
| 20-50MB   | 50,000+ | 30-60s |

## UAT Testing Checklist

- [ ] App starts without errors
- [ ] File upload works
- [ ] Parse time is displayed
- [ ] Debug Log tab shows detailed information
- [ ] Errors are caught and displayed (not crashed)
- [ ] Large files (>10MB) parse successfully
- [ ] Japanese text displays correctly
- [ ] Merged cells are handled correctly

## Next Steps

After UAT validation:
1. Test with real confidential Excel files
2. Verify all Japanese patterns are handled
3. Check performance with large files
4. Validate error messages are helpful
5. Proceed to Phase 5 (AI Integration)

---

**Ready for UAT!** 🚀

The Debug Dashboard is operational and ready to reveal the truth about your data.
