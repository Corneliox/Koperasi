import sys
import re

# Windows Version Detection
is_win7 = False
if sys.platform == 'win32' and hasattr(sys, 'getwindowsversion'):
    try:
        ver = sys.getwindowsversion()
        is_win7 = (ver.major == 6 and ver.minor == 1)
    except Exception:
        is_win7 = False

# Functional icons that should be replaced with words instead of just stripped
CRITICAL_FALLBACKS = {
    "✏️": "Edit",
    "🗑️": "Hapus",
    "🛒": "Beli",
    "👁": "Lihat",
    "💵": "Bayar",
    "🔄": "Reload",
    "➕": "Tambah",
    "↩️": "Retur",
    "📥": "Import",
    "📊": "Report",
    "📄": "PDF",
    "💾": "Simpan",
    "❌": "Batal",
    "✅": "OK",
    "⚠️": "!",
    "●": "*",
    "🏛️": "Koperasi",
    "🏛": "Koperasi",
    "←": "<-",
    "→": "->",
    "↑": "^",
    "↓": "v",
}

def fix_emoji(text: str) -> str:
    """
    Cleaner Windows 7 fix: 
    1. Replace functional emojis with short words.
    2. Strip all other emojis/non-ASCII characters.
    """
    if not is_win7 or not isinstance(text, str) or not text:
        return text
    
    # Handle critical functional icons first
    # If the text is ONLY the emoji, return the word
    if text in CRITICAL_FALLBACKS:
        return CRITICAL_FALLBACKS[text]
    
    # If emoji is part of a string, replace it with the word or empty
    result = text
    for emoji, word in CRITICAL_FALLBACKS.items():
        if emoji in result:
            # If it's a decorative emoji in a string (like "🏠 Dashboard"), 
            # we usually just want it gone.
            result = result.replace(emoji, "")

    # Regex to strip all remaining non-ASCII (emojis, etc)
    result = re.sub(r'[^\x00-\x7F]+', '', result)
    
    # Clean up multiple spaces and return
    return " ".join(result.split()).strip()
