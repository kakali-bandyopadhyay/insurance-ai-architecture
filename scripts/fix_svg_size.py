from __future__ import annotations

import argparse
import math
import re
import xml.etree.ElementTree as ET
from pathlib import Path


def _pixels(value: str) -> str:
    number = float(value)
    if not math.isfinite(number) or number <= 0:
        raise ValueError("SVG viewBox dimensions must be positive finite numbers")
    return f"{number:g}px"


def fix_svg_size(svg_path: str | Path) -> Path:
    path = Path(svg_path)
    tree = ET.parse(path)
    root = tree.getroot()
    if not root.tag.endswith("svg"):
        raise ValueError("The document root must be an SVG element")

    view_box = root.get("viewBox") or root.get("viewbox")
    if not view_box:
        raise ValueError("SVG root must have a viewBox")
    dimensions = re.split(r"[\s,]+", view_box.strip())
    if len(dimensions) != 4:
        raise ValueError("SVG viewBox must contain four numbers")

    root.set("width", _pixels(dimensions[2]))
    root.set("height", _pixels(dimensions[3]))

    style = root.get("style")
    if style:
        declarations = [part.strip() for part in style.split(";") if part.strip()]
        declarations = [part for part in declarations
                        if part.split(":", 1)[0].strip().lower() != "max-width"]
        if declarations:
            root.set("style", "; ".join(declarations))
        else:
            root.attrib.pop("style", None)

    namespace = re.match(r"\{([^}]+)\}", root.tag)
    if namespace:
        ET.register_namespace("", namespace.group(1))
    tree.write(path, encoding="utf-8", xml_declaration=True)
    return path


def main() -> None:
    parser = argparse.ArgumentParser(description="Set SVG pixel dimensions from its viewBox.")
    parser.add_argument("svg_path", type=Path, help="SVG file to update in place")
    args = parser.parse_args()
    fix_svg_size(args.svg_path)


if __name__ == "__main__":
    main()
