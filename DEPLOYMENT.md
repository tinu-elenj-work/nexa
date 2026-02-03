# Nexa - Deployment Guide

## 🚀 Quick Deployment

### Prerequisites
- Python 3.8 or higher
- Git
- Bitbucket account
- API credentials for all integrated systems

**IMPORTANT**: This system uses an externally managed Python environment (PEP 668). Always use the virtual environment for all operations.

### 1. Clone the Repository
```bash
git clone https://bitbucket.org/elenj/workspace/projects/ESBUS/nexa.git
cd nexa
```

### 2. Create Virtual Environment
```bash
python3 -m venv venv
```

### 3. Install Dependencies
```bash
venv/bin/pip install -r requirements.txt
```

### 4. Setup Configuration
```bash
# Copy configuration template
cp config/config.template.py config/config.py

# Edit with your credentials
# Edit config/config.py with your actual API credentials
```

### 5. Setup Xero OAuth2 (Required)
```bash
# Run automated OAuth2 setup
venv/bin/python src/xero_oauth_server.py
```

### 6. Test the System
```bash
# Test ElapseIT integration with date range
venv/bin/python src/timesheet_extractor.py --start-date 2025-03-01 --end-date 2026-01-31

# Test Xero integration
venv/bin/python src/get_xero_reports.py "June 2025"

# Test main analysis
venv/bin/python src/project_mapper_enhanced.py --api --month "August 2025"
```

## 🔧 Configuration

### ElapseIT Configuration
Edit `config/config.py`:
```python
ELAPSEIT_CONFIG = {
    'domain': 'your-domain.com',
    'username': 'your-username@domain.com',
    'password': 'your-password',
    'timezone': 'Europe/London'
}
```

### Xero Configuration
After running OAuth2 setup, your tokens will be automatically added to `config/config.py`:
```python
XERO_CONFIG = {
    'client_id': 'YOUR_XERO_CLIENT_ID',
    'client_secret': 'YOUR_XERO_CLIENT_SECRET',
    'access_token': 'AUTO_GENERATED_TOKEN',
    'refresh_token': 'AUTO_GENERATED_TOKEN',
    'scopes': [...]
}
```

### Vision Database Configuration
```python
VISION_DB_CONFIG = {
    'host': 'your-db-host',
    'port': 5432,
    'database': 'your-database',
    'user': 'your-username',
    'password': 'your-password'
}
```

## 📊 Usage

### Generate Project Mapping Analysis
```bash
venv/bin/python src/project_mapper_enhanced.py --api --month "August 2025"
```

### Extract Timesheet Data
```bash
# With date range
venv/bin/python src/timesheet_extractor.py --start-date 2025-03-01 --end-date 2026-01-31

# Interactive mode
venv/bin/python src/timesheet_extractor.py --interactive
```

### Generate Xero Financial Reports
```bash
venv/bin/python src/get_xero_reports.py "June 2025"
```

## 🧪 Testing

### Run Integration Tests
```bash
venv/bin/pytest tests/test_integration_with_real_data.py -v
```

### Run All Tests
```bash
venv/bin/python run_tests.py

# Run with coverage
venv/bin/python run_tests.py --coverage
```

## 📁 Output Files

All generated files are saved to the `output/` directory:
- `output/mapping_results/` - Project mapping analysis
- `output/elapseIT_data/` - Timesheet reports
- `output/xero_data/` - Financial reports

## 🔒 Security

- Never commit `config/config.py` (contains sensitive credentials)
- Use `config/config.template.py` as a template
- Keep API credentials secure
- Use environment variables in production if needed

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure you're in the project root directory
2. **API Authentication**: Verify credentials in `config/config.py`
3. **Database Connection**: Check Vision database credentials and network access
4. **OAuth2 Issues**: Re-run `venv/bin/python src/xero_oauth_server.py`
5. **Virtual Environment**: Always use `venv/bin/python` for all commands

### Getting Help

1. Check the main README.md for detailed documentation
2. Review error messages in the console output
3. Verify all configuration files are properly set up
4. Test individual components before running full analysis

## 📈 Production Deployment

### Environment Setup
1. Use a dedicated server or cloud instance
2. Set up proper file permissions
3. Configure automated backups for output files
4. Set up monitoring for API rate limits

### Scheduled Execution
Consider setting up cron jobs or scheduled tasks for regular data extraction:
```bash
# Example cron job (runs daily at 2 AM)
0 2 * * * cd /path/to/nexa && python src/project_mapper_enhanced.py --api --month "$(date +'%B %Y')"
```

---

**Repository**: https://bitbucket.org/elenj/workspace/projects/ESBUS/nexa  
**Documentation**: See README.md for complete feature documentation
