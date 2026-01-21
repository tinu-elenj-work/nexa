# Nexa - Complete Integration Suite

A comprehensive project mapping and financial analysis tool that integrates ElapseIT, Vision, and Xero systems for complete project lifecycle management and financial reporting.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Setup configuration
cp config/config.template.py config/config.py
# Edit config/config.py with your credentials

# Run main Nexa application (API mode)
python src/project_mapper_enhanced.py --api --month "August 2025"

# Extract Xero financial reports
python src/get_xero_reports.py "June 2025"

# Extract timesheet data
python src/timesheet_extractor.py
```

## 🌟 Key Features

### 🔄 **Multi-System Integration**
- **🌐 ElapseIT API Integration**: Real-time project allocation data
- **📊 Vision Database Integration**: Direct PostgreSQL database connectivity
- **💰 Xero Financial Integration**: Complete financial reporting suite
- **📈 Timesheet Extraction**: Comprehensive timesheet analysis

### 📊 **Advanced Analytics**
- **🔄 Bidirectional Matching**: Advanced composite key matching algorithm
- **📈 Comprehensive Analysis**: Multiple output sheets with detailed insights
- **⚙️ Configurable Mappings**: External Excel configuration for field mappings
- **🎯 Employee Filtering**: Option to analyze specific employees
- **📅 Month-based Analysis**: Focused analysis for specific time periods

### 💰 **Financial Reporting**
- **📋 Balance Sheet Reports**: Automated balance sheet generation
- **📊 Profit & Loss Reports**: P&L analysis with multi-currency support
- **🧾 Invoice Management**: Invoice tracking and analysis
- **📈 Trial Balance**: Complete trial balance reports
- **💱 Multi-Currency Support**: FX rate integration for consolidation

### 🔧 **Data Management**
- **🔄 Automatic Data Deduplication**: Built-in data quality improvements
- **📁 Archive Management**: Automatic archiving with timestamps
- **🔍 Data Validation**: Comprehensive data quality checks
- **📊 Export Formats**: Excel, CSV, and JSON output options

## 📁 Project Structure

```
nexa/
├── src/                         # Source code
│   ├── project_mapper_enhanced.py    # Main Nexa application (API + CSV support)
│   ├── elapseit_api_client.py       # ElapseIT API client
│   ├── data_transformer.py          # API data transformation logic
│   ├── xero_api_client.py           # Xero API client
│   ├── vision_db_client.py          # Vision database client
│   ├── timesheet_extractor.py       # Timesheet extraction utility
│   ├── get_xero_reports.py          # Xero financial reports extractor
│   ├── get_xero_reports_backup.py   # Backup Xero reports extractor
│   ├── fx_reader.py                 # Foreign exchange rate reader
│   ├── create_field_mappings.py     # Field mapping configuration utility
│   ├── archive_elapseit_data.py     # Data archiving utility
│   ├── xero_oauth_setup.py          # Xero OAuth2 setup utility
│   ├── xero_oauth_server.py         # Automated OAuth2 server
│   └── xero_oauth_manual.py         # Manual OAuth2 setup guide
├── config/                      # Configuration files
│   ├── __init__.py                  # Config package initialization
│   ├── config.py                    # Main configuration (with credentials)
│   ├── config.template.py           # Configuration template
│   ├── field_mappings.xlsx          # Field mapping configuration
│   ├── Mapper.xlsx                  # Client mapping file
│   └── pl_account_order.json        # Account order configuration
├── data/                        # Input data files (CSV fallbacks)
│   ├── elapseIT_data/               # ElapseIT CSV data files
│   │   ├── README.md                # Data structure documentation
│   │   └── archive/                 # Archived data files
│   ├── vision_data/                 # Vision CSV data files
│   │   ├── allocations.csv          # Project allocations
│   │   ├── clients.csv              # Client data
│   │   ├── employees.csv            # Employee data
│   │   └── projects.csv             # Project data
│   ├── xero_data/                   # Xero CSV data files
│   │   ├── README.md                # Data structure documentation
│   │   └── archive/                 # Archived data files
│   └── fx/                          # Foreign exchange data
│       └── FX.xlsx                  # Exchange rate data
├── output/                      # Generated output files
│   ├── elapseIT_data/               # Timesheet reports
│   │   └── timesheets_*.xlsx        # Generated timesheet files
│   ├── mapping_results/             # Project mapping analysis
│   │   └── mapping_analysis_*.xlsx  # Generated mapping reports
│   └── xero_data/                   # Financial reports
│       ├── balance_sheet_*.xlsx     # Balance sheet reports
│       ├── profit_and_loss_*.xlsx   # P&L reports
│       ├── trial_balance_*.xlsx     # Trial balance reports
│       ├── chart_of_accounts_*.xlsx # Chart of accounts
│       ├── invoices_ytd_*.xlsx      # Invoice reports
│       └── archive/                 # Archived output files
├── tests/                       # Unit tests
│   ├── __init__.py                 # Test package initialization
│   ├── conftest.py                 # Pytest configuration
│   ├── test_*.py                   # Individual test files
│   └── __pycache__/                # Python cache
├── requirements.txt             # Python dependencies
├── requirements-test.txt        # Testing dependencies
├── run_tests.py                 # Test runner script
├── TEST_SUMMARY.md              # Testing documentation
└── README.md                    # This file
```

## 🔧 Configuration

### 1. API Configuration
Copy the configuration template and edit with your credentials:
```bash
cp config/config.template.py config/config.py
```

Edit `config/config.py` with your API credentials:

#### ElapseIT Configuration
```python
ELAPSEIT_CONFIG = {
    'domain': 'your-domain.com',
    'username': 'your-username@domain.com', 
    'password': 'your-password',
    'timezone': 'Europe/London'
}
```

#### Xero Configuration
```python
XERO_CONFIG = {
    'client_id': 'YOUR_XERO_CLIENT_ID',
    'client_secret': 'YOUR_XERO_CLIENT_SECRET',
    'access_token': 'YOUR_ACCESS_TOKEN',
    'refresh_token': 'YOUR_REFRESH_TOKEN',
    'scopes': [
        'accounting.transactions',
        'accounting.reports.read',
        'accounting.contacts',
        'projects',
        'offline_access'
    ]
}
```

#### Vision Database Configuration
```python
VISION_DB_CONFIG = {
    'host': 'YOUR_VISION_DB_HOST',
    'port': 5432,
    'database': 'YOUR_VISION_DB_NAME',
    'user': 'YOUR_VISION_DB_USER',
    'password': 'YOUR_VISION_DB_PASSWORD'
}
```

### 2. OAuth2 Setup (Xero)
For Xero API access, you need to complete OAuth2 authentication:

#### Automated OAuth2 Setup (Recommended)
```bash
python src/xero_oauth_server.py
```
This will:
- Start a local server on port 8080
- Open your browser for authorization
- Automatically capture the authorization code
- Exchange it for access/refresh tokens
- Update your config file

#### Manual OAuth2 Setup
```bash
python src/xero_oauth_manual.py
```
This provides step-by-step instructions for manual token setup.

### 3. Field Mappings
Run the field mapping utility to generate configuration files:
```bash
python src/create_field_mappings.py
```

## 📊 Usage Examples

### 🔄 Nexa Project Analysis

#### Basic API Analysis
```bash
python src/project_mapper_enhanced.py --api --month "August 2025"
```

#### Employee-Specific Analysis
```bash
python src/project_mapper_enhanced.py --api --month "August 2025" --employee "John Smith"
```

#### Debug Mode (no Excel output)
```bash
python src/project_mapper_enhanced.py --api --month "August 2025" --debug
```

#### Fallback to CSV Files
```bash
python src/project_mapper_enhanced.py --month "August 2025"
```

### 💰 Xero Financial Reports

#### Extract Reports for Specific Date
```bash
python src/get_xero_reports.py "June 2025"
python src/get_xero_reports.py "2025-06-30"
python src/get_xero_reports.py "31 December 2024"
```

#### Extract Reports for Today
```bash
python src/get_xero_reports.py
```

#### Available Report Types
- **Balance Sheet**: Complete balance sheet with multi-currency support
- **Profit & Loss**: P&L statement with detailed breakdowns
- **Trial Balance**: Full trial balance report
- **Chart of Accounts**: Complete account structure
- **Invoices**: Invoice tracking and analysis

### 📈 Timesheet Extraction

#### Extract Timesheet Data
```bash
python src/timesheet_extractor.py
```

#### Features
- Dynamic date range specification
- Excel output with multiple sheets:
  - Grouping by Client → Allocation → Resource (by month)
  - Grouping by Resource → Client → Allocation (by month)

### 🔄 Data Archiving

#### Archive ElapseIT Data
```bash
python src/archive_elapseit_data.py
```

## 📈 Output Files

### Nexa Analysis Reports (`output/mapping_results/`)
- **`bidirectional_matches`** - Perfect matches between systems
- **`elapseit_no_matches`** - ElapseIT entries without Vision matches
- **`vision_no_matches`** - Vision entries without ElapseIT matches
- **`missing_employees`** - Employee discrepancies between systems
- **`missing_clients`** - Client discrepancies between systems
- **`missing_projects`** - Project discrepancies between systems
- **`combined_allocations`** - Complete allocation data from both systems

### Xero Financial Reports (`output/xero_data/`)
- **`balance_sheet_{date}_{time}_{fyend}.xlsx`** - Balance sheet reports
- **`profit_and_loss_{date}_{time}_{fyend}.xlsx`** - P&L reports
- **`trial_balance_{date}_{time}_{fyend}.xlsx`** - Trial balance reports
- **`chart_of_accounts_{date}_{time}_{fyend}.xlsx`** - Chart of accounts
- **`invoices_ytd_{date}_{time}_{fyend}.xlsx`** - Invoice reports

### Timesheet Reports (`output/elapseIT_data/`)
- **`timesheets_{start_date}_to_{end_date}_{timestamp}.xlsx`** - Timesheet data

## 🔄 Data Flow

### Nexa Project Analysis Flow
1. **API Data Retrieval**: Fetch live data from ElapseIT API
2. **Data Transformation**: Convert API responses to standardized format
3. **Vision Data Loading**: Read Vision CSV files or database
4. **Data Processing**: Apply filtering and business logic
5. **Matching Analysis**: Perform bidirectional composite key matching
6. **Report Generation**: Create comprehensive Excel analysis

### Xero Financial Flow
1. **Authentication**: OAuth2 token management
2. **Report Generation**: Generate financial reports via API
3. **Multi-Currency Processing**: Apply FX rates for consolidation
4. **Data Transformation**: Convert to standardized format
5. **Archive Management**: Automatic timestamping and archiving
6. **Excel Export**: Generate formatted Excel reports

### Timesheet Extraction Flow
1. **Date Range Processing**: Parse and validate date inputs
2. **API Data Retrieval**: Fetch timesheet data from ElapseIT
3. **Data Aggregation**: Group by various dimensions
4. **Excel Generation**: Create multi-sheet Excel reports
5. **Archive Management**: Automatic file archiving

## 🧪 Testing

The project includes comprehensive testing capabilities:

### Running Tests
```bash
# Run all tests
python run_tests.py

# Run specific test categories
pytest tests/test_api_clients.py
pytest tests/test_data_transformers.py
pytest tests/test_main_applications.py
```

### Test Coverage
- **API Integration Tests**: Test all API connections (ElapseIT, Xero, Vision)
- **Data Processing Tests**: Validate data transformation logic
- **Report Generation Tests**: Verify output file generation
- **Error Handling Tests**: Test error scenarios and recovery
- **Configuration Tests**: Validate configuration loading and validation
- **Utility Tests**: Test helper functions and utilities

### Test Structure
```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── test_api_clients.py            # API client tests
├── test_data_transformers.py      # Data transformation tests
├── test_main_applications.py      # Main application tests
├── test_utilities.py              # Utility function tests
└── test_config.py                 # Configuration tests
```

See `TEST_SUMMARY.md` for detailed testing documentation.

## 📚 Additional Documentation

- **`README_TIMESHEET_EXTRACTOR.md`** - Detailed timesheet extraction guide
- **`DEPLOYMENT.md`** - Complete deployment guide
- **`config/config.template.py`** - Configuration template with examples

## 🆕 What's New in Enhanced Version

### API Integration
- ✅ Real-time data access (no CSV exports needed)
- ✅ Automatic duplicate removal (31 duplicates eliminated)
- ✅ Better data quality and consistency
- ✅ Same analysis accuracy (identical matching results)
- ✅ Future-proof architecture

### Financial Integration
- ✅ Complete Xero API integration
- ✅ Multi-currency support with FX rates
- ✅ Automated financial report generation
- ✅ Multi-company consolidation
- ✅ Automatic archiving with timestamps

### Data Management
- ✅ Vision database integration
- ✅ Comprehensive timesheet extraction
- ✅ Advanced data validation
- ✅ Flexible export formats

## 🔒 Security

- **API Credentials**: Stored in `config/config.py` (excluded from version control)
- **Token Management**: JWT token management with automatic refresh
- **Secure Connections**: HTTPS connections to all APIs
- **Configuration Template**: Use `config/config.template.py` as setup guide
- **Environment Variables**: Support for environment variable configuration

## 🚀 Deployment

This project is ready for deployment to Bitbucket:

### Prerequisites
- Python 3.8 or higher
- Git
- Bitbucket account
- API credentials for all integrated systems

### Deployment Steps
1. **Clone the repository**
2. **Install dependencies**: `pip install -r requirements.txt`
3. **Setup configuration**: Copy `config/config.template.py` to `config/config.py` and configure
4. **Test connections**: Run individual modules to verify API connections
5. **Run the application**: `python src/project_mapper_enhanced.py --api --month "August 2025"`

### Environment Setup
```bash
# Initialize Git repository
git init
git add .
git commit -m "Initial commit: Complete integration suite"

# Add Bitbucket remote
git remote add origin https://bitbucket.org/your-username/nexa.git
git push -u origin main
```

## 📞 Support

For issues or questions:
1. Check the documentation in the `README_*.md` files
2. Review the source code in the `src/` directory
3. Examine logs and debug output for troubleshooting
4. Check configuration files for proper setup

## 🔧 Troubleshooting

### Common Issues

#### API Authentication Errors
- Verify credentials in `config/config.py`
- Check API endpoint availability
- Verify timezone settings
- Test individual API connections

#### Data Processing Errors
- Check data file formats
- Verify field mappings
- Review data quality
- Check database connections

#### Output Generation Issues
- Ensure output directory exists
- Check file permissions
- Verify Excel file dependencies
- Review error logs

### Performance Optimization
- Use API mode for real-time data
- Implement data caching for large datasets
- Optimize database queries
- Use parallel processing for large reports

---

**Note**: This project provides a complete integration suite for ElapseIT, Vision, and Xero systems with comprehensive project mapping, financial reporting, and timesheet analysis capabilities.