"""Load probing-strategy text from sibling `*.js` protocol files (single source of truth)."""

from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path

_CODE_DIR = Path(__file__).resolve().parent


def _extract_exported_template(js_source: str, export_name: str | None = None) -> str:
    if export_name:
        pattern = rf"export const {re.escape(export_name)}\s*=\s*`([\s\S]*?)`;"
        m = re.search(pattern, js_source)
        if not m:
            raise ValueError(f"Could not find export const {export_name} in probe JS")
        return m.group(1).strip()

    m = re.search(r"export const \w+\s*=\s*`([\s\S]*?)`\s*;\s*$", js_source.strip())
    if m:
        return m.group(1).strip()
    m = re.search(r"export const \w+\s*=\s*`([\s\S]*?)`\s*;", js_source)
    if not m:
        raise ValueError("Could not find export const … = `…` block in probe JS")
    return m.group(1).strip()


@lru_cache(maxsize=16)
def load_probe_js(relative_name: str, export_name: str | None = None) -> str:
    """Load the exported template literal body from a probe protocol ``*.js`` file."""
    path = _CODE_DIR / relative_name
    if not path.is_file():
        raise FileNotFoundError(f"Missing probe protocol file: {path}")
    return _extract_exported_template(path.read_text(encoding="utf-8"), export_name)


def descriptive_probe_external_text() -> str:
    return load_probe_js("01-descriptive.js", "descriptiveProbeExternal")


def descriptive_probe_internal_text() -> str:
    return load_probe_js("01-descriptive.js", "descriptiveProbeInternal")


def idiographic_probe_text() -> str:
    return load_probe_js("02-idiographic.js")


def clarifying_probe_text() -> str:
    return load_probe_js("03-clarifying.js")


def explanatory_probe_text() -> str:
    return load_probe_js("04-explanatory.js")
