from __future__ import annotations
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

def load_json(path: str | Path) -> Any:
    p = Path(path)
    if not p.is_absolute(): p = ROOT / p
    with p.open("r", encoding="utf-8-sig") as f: return json.load(f)

def write_text(path: str | Path, content: str) -> Path:
    p = Path(path)
    if not p.is_absolute(): p = ROOT / p
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8", newline="\n")
    return p

def synthetic_banner() -> str:
    return "[SYNTHETIC] All records, values, metrics, roles and policies are invented and illustrative."
