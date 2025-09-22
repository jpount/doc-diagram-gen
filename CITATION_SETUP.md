# Citation System Setup Guide

## CORRECT WORKFLOW ORDER (IMPORTANT!)

### Step 1: Run Repomix FIRST
```bash
# This MUST be done before anything else
repomix --config .repomix.config.json codebase/daytrader/
```
This creates `output/reports/repomix-summary.md` (required for citations)

### Step 2: Extract Citations
```bash
# Run the citation extraction on the repomix output
python3 framework/scripts/extract_citations.py
```
This creates `output/context/codebase-citations.json` from the repomix summary

### Step 3: Run Setup
```bash
# Now run setup which will detect the citations
python3 setup.py
```
Setup will check if citations exist and offer to extract them if missing

### Step 4: Run Agents
```bash
# Finally run your analysis
python3 run_analysis.py
```

## Full Pipeline Summary

```bash
# Complete order:
1. repomix --config .repomix.config.json codebase/daytrader/  # MUST BE FIRST
2. python3 framework/scripts/extract_citations.py              # Extract citations
3. python3 setup.py                                           # Configure agents
4. python3 run_analysis.py                                    # Run analysis
```

## What Each Step Does

1. **Repomix**: Compresses the codebase into a single markdown file
2. **Extract Citations**: Parses the repomix file to extract all classes, methods, etc. into a JSON index
3. **Setup**: Configures which agents to run (now also checks for citations)
4. **Run Analysis**: Executes the selected agents (they can lookup citations)

## Testing the Citation Scripts

### Test just the parser:
```bash
python3 framework/scripts/repomix_parser.py
```

### Test just the citation manager:
```bash
python3 framework/scripts/citation_manager.py
```

### Test the full extraction:
```bash
python3 framework/scripts/extract_citations.py --validate
```

## Files Created

- `framework/scripts/repomix_parser.py` - Parses repomix-summary.md
- `framework/scripts/citation_manager.py` - Manages citations and REF-XXX IDs
- `framework/scripts/extract_citations.py` - Main extraction script
- `output/context/codebase-citations.json` - Extracted citations index
- `output/citations/{agent-name}-citations.md` - Per-agent citation references

## Key Point
The repomix-summary.md file MUST exist before citations can be extracted!