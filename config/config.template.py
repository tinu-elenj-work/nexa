# Nexa Configuration Template
# Copy this file to config.py and replace the placeholder values with your actual credentials

ELAPSEIT_CONFIG = {
    'domain': 'your-domain.com',  # Replace with your ElapseIT domain
    'username': 'your-username@domain.com',  # Replace with your API username
    'password': 'your-password',  # Replace with your password
    'timezone': 'Europe/London'  # Replace with your timezone
}

# Alternative domain to try if the first one doesn't work
ELAPSEIT_CONFIG_ALT = {
    'domain': 'your-company-id',  # Replace with your company ID
    'username': 'your-username@domain.com',  # Replace with your API username
    'password': 'your-password',  # Replace with your password
    'timezone': 'Europe/London'  # Replace with your timezone
}

# API Endpoints (usually don't need to change these)
API_ENDPOINTS = {
    'auth': 'https://auth.elapseit.net/oauth2/token',
    'projects': '/projects',
    'allocations': '/allocations',
    'clients': '/clients',
    'people': '/people'
}

# Export settings
EXPORT_SETTINGS = {
    'output_directory': 'api_exports',
    'file_format': 'csv',
    'encoding': 'utf-8'
}

# Request settings
REQUEST_SETTINGS = {
    'timeout': 30,
    'retry_attempts': 3,
    'retry_delay': 5
}

# Xero API Configuration
# Get these from your Xero app at https://developer.xero.com/app/manage
XERO_CONFIG = {
    'client_id': 'YOUR_XERO_CLIENT_ID',  # Replace with your Xero app client ID
    'client_secret': 'YOUR_XERO_CLIENT_SECRET',  # Replace with your Xero app client secret
    'access_token': 'YOUR_ACCESS_TOKEN',  # Replace with your OAuth2 access token
    'refresh_token': 'YOUR_REFRESH_TOKEN',  # Replace with your OAuth2 refresh token
    'scopes': [
        'accounting.transactions',
        'accounting.transactions.read',
        'accounting.reports.read',
        'accounting.contacts',
        'accounting.contacts.read',
        'accounting.settings.read',
        'projects',
        'projects.read',
        'offline_access'
    ]
}

# Vision Database Configuration
# Replace with your Vision PostgreSQL database credentials
VISION_DB_CONFIG = {
    'host': 'YOUR_VISION_DB_HOST',  # Replace with your Vision database host
    'port': 5432,  # Default PostgreSQL port
    'database': 'YOUR_VISION_DB_NAME',  # Replace with your Vision database name
    'user': 'YOUR_VISION_DB_USER',  # Replace with your Vision database username
    'password': 'YOUR_VISION_DB_PASSWORD'  # Replace with your Vision database password
}
