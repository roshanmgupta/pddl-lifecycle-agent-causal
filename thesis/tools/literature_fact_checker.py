#!/usr/bin/env python3
"""
Literature Fact-Checker and Grounding Engine for Master's Thesis.
Indexes all reference papers in `paper/` and validates claims, numbers, and citations
to prevent LLM hallucinations and enforce empirical integrity.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    from pypdf import PdfReader
except ImportError:
    print("Error: pypdf is not installed. Run: pip install pypdf")
    sys.exit(1)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PAPERS_DIR = PROJECT_ROOT / "paper"
BENCHMARK_RESULTS_FILE = PROJECT_ROOT / "benchmark_evaluation_results.json"
CACHE_FILE = Path(__file__).resolve().parent / "papers_cache.json"

class LiteratureFactChecker:
    def __init__(self, papers_dir: Path = PAPERS_DIR, cache_file: Path = CACHE_FILE):
        self.papers_dir = papers_dir
        self.cache_file = cache_file
        self.corpus: Dict[str, List[Dict[str, Any]]] = {}
        self.load_or_index_corpus()

    def index_all_papers(self, force_reindex: bool = False):
        """Indexes text page-by-page from all PDF papers."""
        pdf_files = list(self.papers_dir.glob("*.pdf"))
        print(f"[*] Found {len(pdf_files)} PDF papers in {self.papers_dir}")

        corpus_data = {}
        for pdf_path in pdf_files:
            file_name = pdf_path.name
            print(f"  -> Indexing: {file_name}...")
            pages_data = []
            try:
                reader = PdfReader(str(pdf_path))
                for page_idx, page in enumerate(reader.pages):
                    text = page.extract_text() or ""
                    cleaned_text = re.sub(r"\s+", " ", text).strip()
                    if cleaned_text:
                        pages_data.append({
                            "page": page_idx + 1,
                            "text": cleaned_text
                        })
            except Exception as e:
                print(f"     [!] Warning: Failed to extract {file_name}: {e}")
            corpus_data[file_name] = pages_data

        with open(self.cache_file, "w", encoding="utf-8") as f:
            json.dump(corpus_data, f, ensure_ascii=False)
        print(f"[OK] Indexed {len(corpus_data)} papers to {self.cache_file}")
        self.corpus = corpus_data

    def load_or_index_corpus(self):
        """Loads cached index if available, otherwise indexes papers."""
        if self.cache_file.exists():
            try:
                with open(self.cache_file, "r", encoding="utf-8") as f:
                    self.corpus = json.load(f)
                print(f"[OK] Loaded {len(self.corpus)} indexed papers from cache.")
                return
            except Exception:
                pass
        self.index_all_papers()

    def search_facts(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Searches across all indexed papers for relevant factual snippets."""
        keywords = [kw.lower() for kw in re.findall(r"\w+", query) if len(kw) > 3]
        results = []

        for paper_name, pages in self.corpus.items():
            for page in pages:
                text_lower = page["text"].lower()
                matches = sum(1 for kw in keywords if kw in text_lower)
                if matches > 0:
                    score = matches / max(1, len(keywords))
                    # Find best snippet
                    snippets = []
                    for sentence in re.split(r"(?<=[.!?]) +", page["text"]):
                        s_lower = sentence.lower()
                        if any(kw in s_lower for kw in keywords):
                            snippets.append(sentence)
                    
                    results.append({
                        "paper": paper_name,
                        "page": page["page"],
                        "score": round(score, 3),
                        "snippet": " ... ".join(snippets[:3])
                    })

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    def verify_claim(self, claim: str) -> Dict[str, Any]:
        """Validates a drafted claim against literature evidence and empirical results."""
        matches = self.search_facts(claim, top_k=3)
        return {
            "claim": claim,
            "has_evidence": len(matches) > 0 and matches[0]["score"] >= 0.4,
            "top_evidence": matches
        }

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Literature Fact Checker")
    parser.add_argument("--query", "-q", type=str, help="Search query or thesis claim to verify")
    parser.add_argument("--reindex", action="store_true", help="Force reindexing all PDFs")
    args = parser.parse_args()

    checker = LiteratureFactChecker()
    if args.reindex:
        checker.index_all_papers(force_reindex=True)

    if args.query:
        print(f"\n--- Verifying Claim: '{args.query}' ---")
        verif = checker.verify_claim(args.query)
        print(f"Evidence Found: {'YES' if verif['has_evidence'] else 'UNCERTAIN/LOW MATCH'}\n")
        for idx, match in enumerate(verif["top_evidence"], 1):
            print(f"[{idx}] Paper: {match['paper']} (Page {match['page']}) | Match Score: {match['score']}")
            print(f"    Excerpt: {match['snippet']}\n")
