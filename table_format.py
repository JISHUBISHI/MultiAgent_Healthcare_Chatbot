"""
Parse agent markdown into table segments for Streamlit display and summary export.
"""

from __future__ import annotations

import re
from typing import Literal

Segment = tuple[
    Literal["table"],
    list[str],
    list[list[str]],
] | tuple[
    Literal["text"],
    str,
]


def _parse_table_lines(table_lines: list[str]) -> tuple[list[str], list[list[str]]]:
    headers: list[str] = []
    rows: list[list[str]] = []
    for line in table_lines:
        if not line.strip().startswith("|"):
            continue
        if re.match(r"^\s*\|[\s\-|:\s]+\|\s*$", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if not headers:
            headers = cells
        else:
            rows.append(cells)
    return headers, rows


def segment_markdown_content(content: str) -> list[Segment]:
    """Split markdown into ordered table blocks and text blocks."""
    lines = content.split("\n")
    segments: list[Segment] = []
    i = 0
    text_buffer: list[str] = []

    def flush_text() -> None:
        nonlocal text_buffer
        if text_buffer:
            t = "\n".join(text_buffer).strip()
            if t:
                segments.append(("text", t))
            text_buffer = []

    while i < len(lines):
        line = lines[i]
        is_table_start = line.strip().startswith("|") and i + 1 < len(lines) and re.match(
            r"^\s*\|[\s\-|:\s]+\|\s*$", lines[i + 1]
        )
        if is_table_start:
            flush_text()
            tbl: list[str] = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                tbl.append(lines[i])
                i += 1
            headers, rows = _parse_table_lines(tbl)
            if headers:
                segments.append(("table", headers, rows))
            continue
        text_buffer.append(line)
        i += 1
    flush_text()
    return segments


def build_master_recommendation_rows(
    results: dict,
    sections: list[tuple[str, str]],
) -> list[dict[str, str]]:
    """
    Flatten every table row and notable text line into one row per recommendation.
    sections: list of (results_key, display_label)
    """
    out: list[dict[str, str]] = []
    for key, label in sections:
        raw = results.get(key) or ""
        content = str(raw).strip()
        if not content or content.startswith("Error"):
            continue

        for seg in segment_markdown_content(content):
            if seg[0] == "table":
                _, headers, rows = seg
                for row in rows:
                    parts = []
                    for ci, h in enumerate(headers):
                        cell = row[ci] if ci < len(row) else ""
                        parts.append(f"{h}: {cell}")
                    out.append(
                        {
                            "Section": label,
                            "Format": "Table row",
                            "Recommendation": " | ".join(parts),
                        }
                    )
            else:
                _, text = seg
                for line in text.split("\n"):
                    line_stripped = line.strip()
                    if not line_stripped:
                        continue
                    if re.match(r"^#{1,6}\s+", line_stripped):
                        out.append(
                            {
                                "Section": label,
                                "Format": "Heading",
                                "Recommendation": re.sub(r"^#{1,6}\s+", "", line_stripped),
                            }
                        )
                    elif re.match(r"^[\-*•]\s+", line_stripped):
                        body = re.sub(r"^[\-*•]\s+", "", line_stripped)
                        body = re.sub(r"^\*\*(.*)\*\*$", r"\1", body)
                        out.append(
                            {
                                "Section": label,
                                "Format": "Bullet",
                                "Recommendation": body,
                            }
                        )
                    elif re.match(r"^\d+\.\s+", line_stripped):
                        body = re.sub(r"^\d+\.\s+", "", line_stripped)
                        out.append(
                            {
                                "Section": label,
                                "Format": "Numbered",
                                "Recommendation": body,
                            }
                        )
                    else:
                        # Paragraph / other — skip very short noise
                        cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", line_stripped)
                        if len(cleaned) > 2:
                            out.append(
                                {
                                    "Section": label,
                                    "Format": "Text",
                                    "Recommendation": cleaned,
                                }
                            )
    return out
