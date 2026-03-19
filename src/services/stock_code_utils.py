# -*- coding: utf-8 -*-
"""
Shared stock code utilities.
"""

from __future__ import annotations

import re
from typing import Optional


# Known exchange prefixes (case-insensitive) and the digit lengths they accept.
# e.g. SH600519 -> 600519, HK00700 -> 00700
_PREFIX_DIGIT_LENS: dict = {
    "SH": (6,),
    "SZ": (6,),
    "SS": (6,),
    "HK": (5,),
}


def _strip_exchange_prefix(text: str) -> Optional[str]:
    """Strip leading exchange prefix (SH/SZ/HK etc.) and return the bare digits, or None."""
    for prefix, digit_lens in _PREFIX_DIGIT_LENS.items():
        if text.startswith(prefix):
            base = text[len(prefix):]
            if base.isdigit() and len(base) in digit_lens:
                return base
    return None


def is_code_like(value: str) -> bool:
    """Check if string looks like a stock code (5-6 digits, 1-5 letters, or prefixed code)."""
    text = value.strip().upper()
    if not text:
        return False
    if text.isdigit() and len(text) in (5, 6):
        return True
    
    # 新增：支援台股代碼 (例如 0050.TW, 2330.TW, 0050.TWO)
    if text.endswith(".TW") or text.endswith(".TWO"):
        return True
        
    for suffix in (".SH", ".SZ", ".SS"):
        if text.endswith(suffix):
            base = text[: -len(suffix)].strip()
            if base.isdigit() and len(base) in (5, 6):
                return True
    if re.match(r"^[A-Z]{1,5}(\.[A-Z])?$", text):
        return True
    # Support exchange-prefixed codes: SH600519, SZ000001, HK00700
    if _strip_exchange_prefix(text) is not None:
        return True
    return False


def normalize_code(raw: str) -> Optional[str]:
    """Normalize and validate a single stock code.

    Supports:
    - Plain digit codes: 600519, 00700
    - Suffix format: 600519.SH, 600519.SZ
    - Prefix format: SH600519, SZ000001, HK00700 (case-insensitive)
    - US ticker symbols: AAPL, TSLA
    - TW ticker symbols: 0050.TW, 2330.TW
    """
    text = raw.strip().upper()
    if not text:
        return None
    if text.isdigit() and len(text) in (5, 6):
        return text
        
    # 新增：如果是台股，直接回傳帶有後綴的完整代碼給 YFinance 處理
    if text.endswith(".TW") or text.endswith(".TWO"):
        return text
        
    if re.match(r"^[A-Z]{1,5}(\.[A-Z])?$", text):
        return text
    for suffix in (".SH", ".SZ", ".SS"):
        if text.endswith(suffix):
            base = text[: -len(suffix)].strip()
            if base.isdigit() and len(base) in (5, 6):
                return base
    # Support exchange-prefixed codes: SH600519 -> 600519, HK00700 -> 00700
    stripped = _strip_exchange_prefix(text)
    if stripped is not None:
        return stripped
    return None
