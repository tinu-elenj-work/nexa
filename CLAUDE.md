# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Nexa is a comprehensive integration suite that connects three business systems:
- **ElapseIT**: Time tracking and project management (REST API integration)
- **Vision**: Project management database (PostgreSQL direct connection)
- **Xero**: Accounting and financial management (REST API integration with OAuth2)

The system performs bidirectional data matching, financial analysis, and automated Excel report generation.

## Key Commands

### Setup
```bash
# IMPORTANT: The system uses an externally managed environment (PEP 668)
# Always check for and use the existing virtual environment

# Check if virtual environment exists
ls -la | grep -E "venv|\.venv|env"

# If venv exists, use it for all Python commands
# If venv doesn't exist, create it first:
python3 -m venv venv

# Install dependencies using the virtual environment
venv/bin/pip install -r requirements.txt

# Setup configuration (first time only)
cp config/config.template.py config/config.py
# Edit config/config.py with actual credentials

# Setup Xero OAuth2 authentication
venv/bin/python src/xero_oauth_server.py
```

### Main Operations
```bash
# Run project mapping analysis (primary application)
venv/bin/python src/project_mapper_enhanced.py --api --month "August 2025"

# Employee-specific analysis
venv/bin/python src/project_mapper_enhanced.py --api --month "August 2025" --employee "John Smith"

# Debug mode (no Excel output)
venv/bin/python src/project_mapper_enhanced.py --api --month "August 2025" --debug

# Extract Xero financial reports
venv/bin/python src/get_xero_reports.py "June 2025"
venv/bin/python src/get_xero_reports.py "2025-06-30"
venv/bin/python src/get_xero_reports.py  # Uses today's date

# Extract timesheet data (with date range)
venv/bin/python src/timesheet_extractor.py --start-date 2025-03-01 --end-date 2026-01-31

# Archive old ElapseIT data
venv/bin/python src/archive_elapseit_data.py

# Extract Vision database data
venv/bin/python src/extract_vision_data_enhanced.py --mask
venv/bin/python src/extract_vision_data_enhanced.py  # Extract without masking
```

### Testing
```bash
# Run all tests
venv/bin/python run_tests.py

# Run with coverage
venv/bin/python run_tests.py --coverage

# Run specific test file
venv/bin/python run_tests.py --specific test_api_clients.py

# Individual test with pytest
venv/bin/pytest tests/test_elapseit_api_client.py -v
```

## Architecture Overview

### Data Flow Pattern
1. **API Data Retrieval** → API clients authenticate and fetch raw JSON data
2. **Data Transformation** → Transform API responses to standardized pandas DataFrames
3. **Data Processing** → Apply filtering, deduplication, and business logic
4. **Matching Analysis** → Bidirectional composite key matching algorithm
5. **Report Generation** → Multi-sheet Excel reports with formatting and archiving

### Core Components

**API Clients** (`src/*_api_client.py`):
- Handle authentication (OAuth2, JWT tokens)
- Implement retry logic and error handling
- Return raw JSON data from APIs

**Data Transformers** (`src/data_transformer.py`):
- Convert API responses to standardized DataFrame format
- Handle data validation and type conversion
- Normalize field names for consistency

**Main Application** (`src/project_mapper_enhanced.py`):
- Orchestrates entire analysis pipeline
- Supports both API mode (real-time) and CSV fallback mode
- Implements bidirectional matching algorithm
- Generates multi-sheet Excel reports with detailed analysis

**Database Client** (`src/vision_db_client.py`):
- PostgreSQL connection pooling
- Efficient query execution for large datasets
- Read-only access for security

### Configuration Architecture
- `config/config.py`: Main configuration with credentials (git-ignored in production)
- `config/config.template.py`: Template for setup
- `config/field_mappings.xlsx`: Field mapping configuration for data transformation
- `config/color_scheme.py`: Centralized color definitions for dashboards

## Critical Implementation Patterns

### Import Rules - CRITICAL
**NEVER use relative imports in src/ files**:
```python
# ❌ WRONG - will cause ModuleNotFoundError
from .elapseit_api_client import ElapseITAPIClient

# ✅ CORRECT - use absolute imports
from elapseit_api_client import ElapseITAPIClient
```

For files in `src/unit_testing/`, add sys.path manipulation:
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from elapseit_api_client import ElapseITAPIClient
```

### ElapseIT API Client Initialization - CRITICAL
**Always extract config values, never pass dict directly**:
```python
# ❌ WRONG - will cause TypeError
client = ElapseITAPIClient(ELAPSEIT_CONFIG)

# ✅ CORRECT - extract individual config values
client = ElapseITAPIClient(
    domain=ELAPSEIT_CONFIG['domain'],
    username=ELAPSEIT_CONFIG['username'],
    password=ELAPSEIT_CONFIG['password'],
    timezone=ELAPSEIT_CONFIG['timezone']
)
```

### Excel Output Requirements - CRITICAL
**ALL Excel output files MUST have auto-sized columns**:
```python
# Required pattern for all Excel outputs
for column in worksheet.columns:
    max_length = 0
    column_letter = column[0].column_letter
    for cell in column:
        try:
            if len(str(cell.value)) > max_length:
                max_length = len(str(cell.value))
        except:
            pass
    adjusted_width = min(max_length + 2, 50)  # Cap at 50 characters
    worksheet.column_dimensions[column_letter].width = adjusted_width

# Format header row
for cell in worksheet[1]:
    cell.font = Font(bold=True)
```

### Color Scheme Consistency - CRITICAL
**Always use centralized color definitions**:
```python
# ✅ CORRECT - use centralized colors
from config.color_scheme import get_category_color, get_chart_color
marker_color = get_category_color('LEAVE')  # Red
line_color = get_chart_color('UPPER_BOUND')  # Red

# ❌ WRONG - never hardcode colors
marker_color = 'red'
line_color = '#DC2626'
```

Test color consistency:
```bash
venv/bin/python src/unit_testing/test_color_consistency.py
```

## Data Analysis Guidelines

### Code Analysis Rules - CRITICAL
**NEVER make assumptions about code logic**:
1. Always read the actual source code using Read tool
2. Trace execution paths through actual code
3. Verify function calls and parameters
4. Never guess what code "should" do without examining it

### Data Analysis Rules - CRITICAL
**NEVER create fictional data or make assumptions**:
1. Always fetch actual data from APIs, database, or files
2. Verify calculations against raw data
3. State clearly if data is not available
4. Show data sources in all analysis

## Testing Structure

### Regression Tests (`tests/`)
- Production test suite using pytest
- Comprehensive mocking of external dependencies
- Test all API integrations, data transformers, and main applications
- Target: 90%+ code coverage

### Debug/Unit Tests (`src/unit_testing/`)
- Development and debugging scripts (not production tests)
- Single-purpose investigation scripts for specific scenarios
- Files in this directory ARE tracked in git (unlike typical debug directories)
- Used for data validation, column checks, and ad-hoc analysis
- Examples: check_vision_tables.py, verify_cost_to_company_masking.py

## Output Files Structure

```
output/
├── mapping_results/         # Project mapping analysis
│   └── mapping_analysis_*.xlsx
├── elapseIT_data/          # Timesheet reports
│   ├── timesheets_*.xlsx
│   └── archive/            # Archived timesheets
├── vision_data/            # Vision database exports
│   └── vision_extract_*.xlsx
└── xero_data/              # Financial reports
    ├── balance_sheet_*.xlsx
    ├── profit_and_loss_*.xlsx
    ├── trial_balance_*.xlsx
    ├── chart_of_accounts_*.xlsx
    ├── invoices_ytd_*.xlsx
    └── archive/            # Archived reports
```

### Output Naming Convention
- Timestamp format: `YYYYMMDD_HHMMSS`
- Financial year end suffix: `_FEB26`, `_MAR25`, etc.
- Example: `profit_and_loss_2025_06_30_193626_FEB26.xlsx`

## Common Pitfalls

### File Paths
- Always use absolute imports from project root when in `src/` directory
- Use `Path` from `pathlib` for cross-platform compatibility
- Project assumes execution from repository root directory

### API Authentication
- Xero tokens expire; use `src/xero_oauth_server.py` to refresh
- ElapseIT uses OAuth2 with JWT tokens that auto-refresh
- Always check authentication before making API calls

### Data Processing
- ElapseIT API can return duplicates; always deduplicate after retrieval
- Handle timezone conversions explicitly (ElapseIT uses configurable timezone)
- Validate data completeness before matching operations

### Excel Generation
- Files may fail to write if open in Excel (handle PermissionError)
- Always implement auto-sizing for all columns
- Use `xlsxwriter` for formatting, `openpyxl` for reading
- Archive old files before generating new ones to prevent conflicts

## Repository Context

- **Main branch**: `main`
- **Git hosting**: GitHub (git@github.com:tinu-elenj-work/nexa.git)
- **Python version**: 3.8+ (tested with 3.13)
- **Development OS**: Windows (WSL2) - note for path handling
