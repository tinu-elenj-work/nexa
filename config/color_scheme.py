"""
Centralized Color Scheme Configuration for Nexa Dashboards

This module defines consistent colors across all dashboards and charts in the Nexa system.
All dashboard components should import and use these color definitions to ensure consistency.
"""

# Category Colors - Main data categories
CATEGORY_COLORS = {
    'LEAVE': '#DC2626',      # Red - Leave/vacation days
    'INTERNAL': '#2563EB',   # Blue - Internal project work
    'OTHER': '#6B7280',      # Gray - Other/uncategorized work
    'TOTAL': '#059669',      # Green - Total days/overall metrics
    'EMPLOYEE_COUNT': '#10B981',  # Green - Employee count metrics
}

# Chart Element Colors - UI elements and reference lines
CHART_COLORS = {
    'MEAN_LINE': '#10B981',      # Green - Mean/average reference lines
    'MEDIAN_LINE': '#F59E0B',    # Orange - Median reference lines
    'UPPER_BOUND': '#DC2626',    # Red - Upper bound reference lines
    'LOWER_BOUND': '#DC2626',    # Red - Lower bound reference lines
    'OUTLIER_MARKER': '#FCD34D', # Yellow - Outlier data points
    'OUTLIER_BORDER': '#000000', # Black - Outlier marker borders
    'DISTRIBUTION': '#93C5FD',   # Light blue - Distribution histograms
    'TREND_LINE': '#F59E0B',     # Orange - Trend lines
}

# Status Colors - Data status indicators
STATUS_COLORS = {
    'SUCCESS': '#10B981',        # Green - Success states
    'WARNING': '#F59E0B',        # Orange - Warning states
    'ERROR': '#DC2626',          # Red - Error states
    'INFO': '#3B82F6',           # Blue - Information states
}

# Chart Background and Layout Colors
LAYOUT_COLORS = {
    'BACKGROUND': '#FFFFFF',     # White - Chart background
    'GRID': '#E5E7EB',          # Light gray - Grid lines
    'TEXT': '#374151',          # Dark gray - Text color
    'TITLE': '#111827',         # Black - Chart titles
}

# Color Palette for Multiple Series (when you need many different colors)
PALETTE = [
    '#DC2626',  # Red
    '#2563EB',  # Blue
    '#059669',  # Green
    '#7C3AED',  # Purple
    '#EA580C',  # Orange
    '#0891B2',  # Cyan
    '#BE185D',  # Pink
    '#65A30D',  # Lime
    '#CA8A04',  # Yellow
    '#6B7280',  # Gray
]

def get_category_color(category: str) -> str:
    """
    Get the color for a specific category.
    
    Args:
        category: The category name (LEAVE, INTERNAL, OTHER, etc.)
        
    Returns:
        Hex color code for the category
    """
    return CATEGORY_COLORS.get(category.upper(), PALETTE[0])

def get_chart_color(element: str) -> str:
    """
    Get the color for a specific chart element.
    
    Args:
        element: The chart element (MEAN_LINE, UPPER_BOUND, etc.)
        
    Returns:
        Hex color code for the chart element
    """
    return CHART_COLORS.get(element.upper(), PALETTE[0])

def get_status_color(status: str) -> str:
    """
    Get the color for a specific status.
    
    Args:
        status: The status (SUCCESS, WARNING, ERROR, INFO)
        
    Returns:
        Hex color code for the status
    """
    return STATUS_COLORS.get(status.upper(), PALETTE[0])

def get_palette_color(index: int) -> str:
    """
    Get a color from the palette by index.
    
    Args:
        index: The index in the palette (0-based)
        
    Returns:
        Hex color code from the palette
    """
    return PALETTE[index % len(PALETTE)]

# Plotly-compatible color dictionaries
def get_plotly_marker_color(category: str) -> dict:
    """Get Plotly marker color dict for a category."""
    return {'color': get_category_color(category)}

def get_plotly_line_color(category: str) -> dict:
    """Get Plotly line color dict for a category."""
    return {'color': get_category_color(category)}

def get_plotly_marker_config(category: str, size: int = 8) -> dict:
    """Get complete Plotly marker config for a category or chart element."""
    # Check if it's a category first, otherwise treat as chart element
    if category.upper() in CATEGORY_COLORS:
        color = get_category_color(category)
    else:
        color = get_chart_color(category)
    return {
        'size': size,
        'color': color
    }

def get_plotly_line_config(category: str, width: int = 3) -> dict:
    """Get complete Plotly line config for a category or chart element."""
    # Check if it's a category first, otherwise treat as chart element
    if category.upper() in CATEGORY_COLORS:
        color = get_category_color(category)
    else:
        color = get_chart_color(category)
    return {
        'color': color,
        'width': width
    }
