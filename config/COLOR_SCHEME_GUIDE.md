# Nexa Color Scheme Guide

## Overview

This guide explains the centralized color scheme used across all Nexa dashboards and charts. The color scheme ensures visual consistency and improves user experience by using the same colors for the same data categories across all visualizations.

## Color Configuration

All colors are defined in `config/color_scheme.py` and should be imported and used consistently across all dashboard components.

## Category Colors

These colors represent the main data categories in the system:

| Category | Color | Hex Code | Usage |
|----------|-------|----------|-------|
| **LEAVE** | Red | `#DC2626` | Leave/vacation days, time off |
| **INTERNAL** | Blue | `#2563EB` | Internal project work, company projects |
| **OTHER** | Gray | `#6B7280` | Other/uncategorized work |
| **TOTAL** | Green | `#059669` | Total days, overall metrics |
| **EMPLOYEE_COUNT** | Green | `#10B981` | Employee count metrics |

## Chart Element Colors

These colors are used for chart elements and reference lines:

| Element | Color | Hex Code | Usage |
|---------|-------|----------|-------|
| **MEAN_LINE** | Green | `#10B981` | Mean/average reference lines |
| **MEDIAN_LINE** | Orange | `#F59E0B` | Median reference lines |
| **UPPER_BOUND** | Red | `#DC2626` | Upper bound reference lines |
| **LOWER_BOUND** | Red | `#DC2626` | Lower bound reference lines |
| **OUTLIER_MARKER** | Yellow | `#FCD34D` | Outlier data points |
| **OUTLIER_BORDER** | Black | `#000000` | Outlier marker borders |
| **DISTRIBUTION** | Light Blue | `#93C5FD` | Distribution histograms |
| **TREND_LINE** | Orange | `#F59E0B` | Trend lines |

## Status Colors

These colors represent different status indicators:

| Status | Color | Hex Code | Usage |
|--------|-------|----------|-------|
| **SUCCESS** | Green | `#10B981` | Success states, positive indicators |
| **WARNING** | Orange | `#F59E0B` | Warning states, caution indicators |
| **ERROR** | Red | `#DC2626` | Error states, negative indicators |
| **INFO** | Blue | `#3B82F6` | Information states, neutral indicators |

## Usage Examples

### Basic Color Functions

```python
from config.color_scheme import get_category_color, get_chart_color

# Get category colors
leave_color = get_category_color('LEAVE')        # Returns: #DC2626
internal_color = get_category_color('INTERNAL')  # Returns: #2563EB
other_color = get_category_color('OTHER')        # Returns: #6B7280

# Get chart element colors
mean_color = get_chart_color('MEAN_LINE')        # Returns: #10B981
upper_bound_color = get_chart_color('UPPER_BOUND') # Returns: #DC2626
```

### Plotly Integration

```python
from config.color_scheme import get_plotly_marker_config, get_plotly_line_config

# For Plotly markers
marker_config = get_plotly_marker_config('LEAVE', size=10)
# Returns: {'size': 10, 'color': '#DC2626'}

# For Plotly lines
line_config = get_plotly_line_config('INTERNAL', width=3)
# Returns: {'color': '#2563EB', 'width': 3}
```

### Complete Plotly Chart Example

```python
import plotly.graph_objects as go
from config.color_scheme import get_category_color, get_chart_color

# Create a bar chart with consistent colors
fig = go.Figure()

# LEAVE data
fig.add_trace(go.Bar(
    x=months,
    y=leave_days,
    name='LEAVE Days',
    marker_color=get_category_color('LEAVE')  # Red
))

# INTERNAL data
fig.add_trace(go.Bar(
    x=months,
    y=internal_days,
    name='Internal Days',
    marker_color=get_category_color('INTERNAL')  # Blue
))

# Add reference lines
fig.add_hline(
    y=upper_bound,
    line_dash="dash",
    line_color=get_chart_color('UPPER_BOUND')  # Red
)
```

## Color Palette

For cases where you need multiple different colors, use the predefined palette:

```python
from config.color_scheme import get_palette_color

# Get colors from the palette
color1 = get_palette_color(0)  # Red
color2 = get_palette_color(1)  # Blue
color3 = get_palette_color(2)  # Green
# ... and so on
```

## Best Practices

1. **Always use the centralized color functions** - Never hardcode colors
2. **Be consistent** - Use the same color for the same category across all dashboards
3. **Use semantic names** - Use `get_category_color('LEAVE')` instead of `get_palette_color(0)`
4. **Test color consistency** - Run the color consistency test to verify all colors work correctly

## Testing

Run the color consistency test to verify all colors are working correctly:

```bash
python src/unit_testing/test_color_consistency.py
```

## Adding New Colors

To add new colors to the scheme:

1. Add the color definition to the appropriate dictionary in `config/color_scheme.py`
2. Add a corresponding getter function if needed
3. Update this documentation
4. Test the new color with the consistency test

## Migration Guide

If you're updating existing code to use the centralized color scheme:

1. Replace hardcoded colors with function calls
2. Import the color scheme functions
3. Test that the colors display correctly
4. Verify consistency across all dashboards

Example migration:

```python
# Before (hardcoded)
marker_color='red'

# After (centralized)
marker_color=get_category_color('LEAVE')
```

## Accessibility

The color scheme has been designed with accessibility in mind:

- High contrast ratios for text readability
- Color-blind friendly palette
- Consistent use of colors reduces cognitive load
- Clear visual hierarchy through color coding

## Support

For questions about the color scheme or to request new colors, please refer to the project documentation or contact the development team.
