#!/usr/bin/env python3
"""
Clean LaTeX Compiler for Master's Thesis.
Runs latexmk from the thesis/ directory to generate a clean PDF.
"""

import subprocess
import sys
from pathlib import Path

THESIS_DIR = Path(__file__).resolve().parent.parent
MAIN_TEX = THESIS_DIR / "main.tex"

def compile_thesis(engine="lualatex", clean=False):
    if clean:
        print("[*] Cleaning temporary auxiliary files...")
        subprocess.run(["latexmk", "-C"], cwd=THESIS_DIR)
        return

    print(f"[*] Compiling thesis with latexmk ({engine})...")
    cmd = ["latexmk", f"-{engine}", "-bibtex", "-interaction=nonstopmode", "main.tex"]
    res = subprocess.run(cmd, cwd=THESIS_DIR)

    pdf_file = THESIS_DIR / "main.pdf"
    if pdf_file.exists():
        print(f"\n[OK] Thesis successfully compiled: {pdf_file} ({pdf_file.stat().st_size // 1024} KB)")
    else:
        print("\n[!] Compilation finished with warnings/errors. Check main.log.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Thesis Compiler")
    parser.add_argument("--clean", action="store_true", help="Clean auxiliary files")
    parser.add_argument("--engine", choices=["lualatex", "pdflatex", "xelatex"], default="lualatex", help="LaTeX engine")
    args = parser.parse_args()

    compile_thesis(engine=args.engine, clean=args.clean)
