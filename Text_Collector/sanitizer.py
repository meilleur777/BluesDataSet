"""
Sanitizer module for the Blues Artist Data Collector.

This module provides centralized functions for sanitizing text content and filenames
across all collector modules. This ensures consistent text processing and filename
handling throughout the application.
"""

import re
import unicodedata


def sanitize_text(text):
    """
    Clean up text content by removing or replacing problematic characters.
    
    Args:
        text (str): The text content to sanitize
        
    Returns:
        str: The sanitized text
    """
    if not text:
        return ""
    
    # Convert None to empty string
    if text is None:
        return ""
        
    # Replace non-breaking spaces with regular spaces
    text = text.replace('\xa0', ' ')
    
    # Replace other Unicode whitespace characters
    text = text.replace('\u2003', ' ')  # em space
    text = text.replace('\u2002', ' ')  # en space
    text = text.replace('\u2005', ' ')  # four-per-em space
    text = text.replace('\u2007', ' ')  # figure space
    text = text.replace('\u2008', ' ')  # punctuation space
    text = text.replace('\u2009', ' ')  # thin space
    text = text.replace('\u200a', ' ')  # hair space
    
    # Remove invisible formatting characters
    text = text.replace('\u200b', '')  # zero-width space
    text = text.replace('\u200c', '')  # zero-width non-joiner
    text = text.replace('\u200d', '')  # zero-width joiner
    text = text.replace('\u2060', '')  # word joiner
    text = text.replace('\ufeff', '')  # byte order mark
    
    # Replace control characters
    control_chars = ''.join(chr(c) for c in range(32) if c not in [9, 10, 13])
    text = re.sub(f'[{re.escape(control_chars)}]', '', text)
    
    # Normalize Unicode characters
    text = unicodedata.normalize('NFC', text)
    
    # Replace multiple consecutive spaces with a single space
    text = re.sub(r' +', ' ', text)
    
    # Normalize line endings
    text = text.replace('\r\n', '\n')
    text = text.replace('\r', '\n')
    
    # Replace multiple newlines with at most two
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Remove trailing spaces at the end of lines
    text = re.sub(r' +\n', '\n', text)
    
    # Strip leading and trailing whitespace
    text = text.strip()
    
    return text


def sanitize_filename(name):
    """
    Sanitize a string to be used as a filename or directory name.
    Removes or replaces invalid characters.
    
    Args:
        name (str): The filename to sanitize
        
    Returns:
        str: The sanitized filename
    """
    if not name:
        return "unnamed"
    
    # First, clean the text content
    name = sanitize_text(name)
    
    # Convert to ASCII where possible (remove accents, etc.)
    try:
        # For simple accented characters, normalize to separate base and combining character
        name = unicodedata.normalize('NFKD', name)
        # Remove combining characters (accents)
        name = ''.join([c for c in name if not unicodedata.combining(c)])
    except:
        # If that fails, just continue with the original
        pass
    
    # Replace problematic characters with underscores
    invalid_chars = r'[<>:"/\\|?*\']'
    sanitized = re.sub(invalid_chars, '_', name)
    
    # Replace characters that might be confusion at beginning/end
    sanitized = sanitized.strip('.')
    sanitized = sanitized.strip()
    
    # Replace multiple consecutive underscores with a single one
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Replace whitespace with underscores
    sanitized = sanitized.replace(' ', '_')
    
    # Limit length (Windows has a 255 character path limit)
    max_length = 100
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    # Ensure we don't end with an underscore or dot
    sanitized = sanitized.rstrip('_.')
    
    # If empty after sanitization, provide a default
    if not sanitized:
        return "unnamed"
    
    return sanitized


def sanitize_file_content(content, remove_html=True):
    """
    Sanitize content that will be written to a file.
    
    Args:
        content (str): The content to sanitize
        remove_html (bool): Whether to attempt to remove HTML tags
        
    Returns:
        str: The sanitized content
    """
    if not content:
        return ""
    
    # Basic text sanitization
    content = sanitize_text(content)
    
    # Optionally remove HTML tags
    if remove_html:
        content = re.sub(r'<[^>]+>', '', content)
    
    return content
