#!/usr/bin/env python3
"""
Style Humanizer and Prose Cadence Checker for Master's Thesis.
Adapted from ARMS (House-Style) to ensure human-grade academic prose,
prevent repetitive AI tics, and maintain proper sentence length distribution.
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Any

# Common AI markers and hollow buzzwords that make academic writing feel synthetic
AI_MARKER_PATTERNS = [
    r"\bdelves? into\b",
    r"\ba testament to\b",
    r"\bfurthermore\b",
    r"\bmoreover\b",
    r"\bcrucial role\b",
    r"\bpivotal role\b",
    r"\bgame[ -]changer\b",
    r"\bbustling\b",
    r"\btapestry\b",
    r"\bbeacon\b",
    r"\bin conclusion\b",
    r"\bit is worth noting that\b",
    r"\bit should be emphasized that\b",
    r"\bcomprehensive exploration\b",
    r"\bharnessing the power of\b",
    r"\bseamlessly integrates?\b"
]

def clean_latex_prose(text: str) -> str:
    """Strips LaTeX comments, environments, equations, and commands to isolate readable prose."""
    # Remove comments
    text = re.sub(r"%.*$", "", text, flags=re.MULTILINE)
    # Remove math environments
    text = re.sub(r"\\begin\{equation\}.*?\\end\{equation\}", "", text, flags=re.DOTALL)
    text = re.sub(r"\\begin\{align\}.*?\\end\{align\}", "", text, flags=re.DOTALL)
    text = re.sub(r"\$\$.*?\$\$", "", text, flags=re.DOTALL)
    text = re.sub(r"\$.*?\$", "", text)
    # Remove tables and figures
    text = re.sub(r"\\begin\{table\}.*?\\end\{table\}", "", text, flags=re.DOTALL)
    text = re.sub(r"\\begin\{figure\}.*?\\end\{figure\}", "", text, flags=re.DOTALL)
    # Remove cite, ref, label
    text = re.sub(r"\\cite\{.*?\}", "[REF]", text)
    text = re.sub(r"\\ref\{.*?\}", "[FIG/SEC]", text)
    text = re.sub(r"\\label\{.*?\}", "", text)
    # Remove common commands like \gls{...}, \texttt{...}, \textbf{...}
    text = re.sub(r"\\[a-zA-Z]+\{(.*?)\}", r"\1", text)
    return text.strip()

def analyze_prose(file_path: Path) -> Dict[str, Any]:
    with open(file_path, "r", encoding="utf-8") as f:
        raw_text = f.read()

    prose = clean_latex_prose(raw_text)
    paragraphs = [p.strip() for p in prose.split("\n\n") if p.strip()]
    sentences = []
    for p in paragraphs:
        # Split sentences roughly
        s_list = re.split(r"(?<=[.!?])\s+", p)
        sentences.extend([s.strip() for s in s_list if len(s.strip().split()) > 2])

    if not sentences:
        return {"error": "No prose sentences found."}

    word_counts = [len(s.split()) for s in sentences]
    mean_len = sum(word_counts) / len(word_counts)
    long_sentences = [s for s, w in zip(sentences, word_counts) if w > 40]
    short_sentences = [s for s, w in zip(sentences, word_counts) if w < 6]

    # Check AI markers
    found_markers = []
    for pattern in AI_MARKER_PATTERNS:
        matches = re.findall(pattern, prose, flags=re.IGNORECASE)
        if matches:
            found_markers.append((pattern.replace(r"\b", "").replace(r"\?", ""), len(matches)))

    return {
        "file": file_path.name,
        "total_paragraphs": len(paragraphs),
        "total_sentences": len(sentences),
        "mean_sentence_length": round(mean_len, 1),
        "target_range": "18.0 - 24.0 words",
        "long_sentences_count (>40 words)": len(long_sentences),
        "short_sentences_count (<6 words)": len(short_sentences),
        "ai_marker_flags": found_markers,
        "sample_long_sentences": long_sentences[:3]
    }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python style_humanizer.py <path_to_tex_file>")
        sys.exit(1)

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"Error: File {path} does not exist.")
        sys.exit(1)

    report = analyze_prose(path)
    print("\n" + "="*50)
    print(f"  Prose Style & Humanization Report: {report.get('file')}")
    print("="*50)
    for k, v in report.items():
        if k != "sample_long_sentences":
            print(f" • {k}: {v}")
    if report.get("sample_long_sentences"):
        print("\nFlagged Long Sentences (>40 words):")
        for s in report["sample_long_sentences"]:
            print(f"   - \"{s}\"\n")
