# Configuration Setup

## Quick Start

1. Copy the configuration template:
   ```bash
   cp config/config.template.py config/config.py
   ```

2. Edit `config/config.py` with your actual credentials:
   - ElapseIT API credentials
   - Xero API credentials  
   - Vision database credentials

3. Run the OAuth2 setup for Xero:
   ```bash
   python src/xero_oauth_server.py
   ```

## Configuration Files

- `config.template.py` - Template with placeholder values
- `config.py` - Your actual configuration (not tracked in git)
- `field_mappings.xlsx` - Field mapping configuration
- `Mapper.xlsx` - Client mapping file
- `pl_account_order.json` - Account order configuration

## Security Note

The `config.py` file contains sensitive credentials and is excluded from version control. Always use the template file as a starting point.
