# Unit Testing and Debugging Directory

This directory is specifically for **debugging and unitary test scripts** that are used during development and troubleshooting.

## Purpose

- **Debugging Scripts**: Quick scripts to test specific functionality or debug issues
- **Unitary Tests**: Individual component tests that don't fit into the main regression test suite
- **Development Tools**: Scripts for data exploration, API testing, and validation

## Naming Conventions

- **Debug scripts**: `debug_*.py` (e.g., `debug_aaisha_leave_calculation.py`)
- **Unitary tests**: `test_*.py` (e.g., `test_vacation_api_response.py`)
- **Exploration scripts**: `explore_*.py` (e.g., `explore_elapseit_data_structure.py`)

## Examples

### Debug Scripts
```python
# debug_aaisha_leave_calculation.py
"""Debug script to investigate Aaisha Dout's leave calculation issue"""

from src.timesheet_extractor import ElapseITTimesheetExtractor
from config.config import ELAPSEIT_CONFIG

def debug_aaisha_leave():
    # Debug logic here
    pass

if __name__ == "__main__":
    debug_aaisha_leave()
```

### Unitary Tests
```python
# test_vacation_api_response.py
"""Test script to validate vacation API response structure"""

import requests
from config.config import ELAPSEIT_CONFIG

def test_vacation_api_structure():
    # Test specific API response structure
    pass

if __name__ == "__main__":
    test_vacation_api_structure()
```

## Important Notes

- **Not for Production**: These scripts are for development and debugging only
- **Temporary**: Scripts can be deleted after debugging is complete
- **Isolated**: Each script should be self-contained and not depend on other scripts
- **Documented**: Include clear comments explaining the purpose and usage

## Relationship to Main Test Suite

- **Main Test Suite**: Located in `tests/` directory for regression testing
- **This Directory**: For ad-hoc debugging and development testing
- **No Conflicts**: Scripts here don't interfere with the main test suite

## Cleanup

- Remove scripts that are no longer needed
- Keep only active debugging scripts
- Archive important findings in comments or documentation
