#!/usr/bin/env python3
"""
Remove emoji characters from extract_vision_data_enhanced.py to fix encoding issues
"""

import re

def remove_emojis_from_file(file_path):
    """Remove emoji characters from a file"""
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Remove emoji characters (Unicode ranges for emojis)
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags (iOS)
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"  # enclosed characters
        "]+", 
        flags=re.UNICODE
    )
    
    # Replace emojis with simple text equivalents
    replacements = {
        "🎭": "[MASK]",
        "🔍": "[DETECT]",
        "📊": "[DATA]",
        "📈": "[CHART]",
        "📋": "[LIST]",
        "✅": "[OK]",
        "❌": "[ERROR]",
        "⚠️": "[WARNING]",
        "🗄️": "[DB]",
        "⏭️": "[SKIP]",
        "🎯": "[TARGET]"
    }
    
    # Apply specific replacements first
    for emoji, replacement in replacements.items():
        content = content.replace(emoji, replacement)
    
    # Remove any remaining emojis
    content = emoji_pattern.sub('', content)
    
    # Write back to file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Removed emojis from {file_path}")

if __name__ == "__main__":
    remove_emojis_from_file("../extract_vision_data_enhanced.py")
