import re
import string

def remove_urls(text: str) -> str:
    """Remove URLs from text."""
    url_pattern = re.compile(r'https?://\S+|www\.\S+')
    return url_pattern.sub(r'', text)

def remove_emojis(text: str) -> str:
    """Remove emojis from text. (Simple approach for emojis and non-ascii)"""
    return text.encode('ascii', 'ignore').decode('ascii')

def clean_reddit_text(text: str) -> str:
    """
    Main function to run the full text cleaning pipeline.
    Note: We DO NOT remove stopwords or punctuation here because 
    modern sentence transformers rely on natural sentence structure.
    """
    if not text:
        return ""
    
    text = remove_urls(text)
    text = remove_emojis(text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text
