#!/usr/bin/env python3
"""Free-tier quickstart: walk a company's recent annual reports and print one section of each.

Deliberately stdlib-only — no `pip install`. A free key is enough to run this.

    export DATASINK_API_KEY=...          # https://datasink.ing
    python free_quickstart.py 600519.SS              # Moutai (China)
    python free_quickstart.py 7203.T --limit 2       # Toyota (Japan)
    python free_quickstart.py 005930.KS --section 경영  # Samsung (Korea), explicit keyword

Why this shape: a full annual report is often 200k+ characters, and an LLM that only needs the
MD&A should not be fed the whole thing. `list_sections` -> `get_section` is the cheap path, and
this script is the smallest complete example of it.

Section keywords are matched against the report's *own* headings, in the report's *own* language.
The candidate lists below are best-effort for each market — if none of them hit, the script prints
the headings the report actually has, so you can pass one with --section. Trust the report, not
this table.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "https://api.datasink.ing"

# Best-effort MD&A-ish heading keywords per exchange suffix. First hit wins; a miss is not fatal.
CANDIDATES = {
    ".SS": ["管理层讨论与分析", "经营情况讨论与分析", "董事会报告"],
    ".SZ": ["管理层讨论与分析", "经营情况讨论与分析", "董事会报告"],
    ".BJ": ["管理层讨论与分析", "经营情况讨论与分析"],
    ".T":  ["経営成績", "事業の状況", "経営に関する分析"],
    ".KS": ["경영진의 논의", "사업의 내용", "이사의 경영진단"],
    ".KQ": ["경영진의 논의", "사업의 내용", "이사의 경영진단"],
    ".KN": ["경영진의 논의", "사업의 내용"],
    ".TW": ["營運概況", "經營狀況", "營運之檢討與分析"],
    ".TWO": ["營運概況", "經營狀況", "營運之檢討與分析"],
}


def get(path, key, **params):
    """GET an API path, raising a readable error instead of a traceback."""
    params["apikey"] = key
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", "replace")[:300]
        if e.code == 401:
            sys.exit("401 Missing or invalid API key. Set DATASINK_API_KEY (free at https://datasink.ing).")
        if e.code == 429:
            sys.exit(f"429 Quota exhausted — 8,191 documents per rolling 7 days. {detail}")
        sys.exit(f"HTTP {e.code} on {path}: {detail}")


def pick_section(sections, keyword, suffix):
    """Return the first heading containing `keyword`, or the first candidate that hits."""
    if keyword:
        hits = [s for s in sections if keyword in s]
        return hits[0] if hits else None
    for cand in CANDIDATES.get(suffix, []):
        hits = [s for s in sections if cand in s]
        if hits:
            return hits[0]
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("symbol", help="FMP-style symbol, e.g. 600519.SS / 7203.T / 2330.TW")
    ap.add_argument("--limit", type=int, default=2, help="how many annual reports to walk (default 2)")
    ap.add_argument("--section", help="explicit heading keyword, overrides the built-in candidates")
    args = ap.parse_args()

    key = os.environ.get("DATASINK_API_KEY")
    if not key:
        sys.exit("Set DATASINK_API_KEY first (free key: https://datasink.ing).")

    suffix = "." + args.symbol.rsplit(".", 1)[-1]

    reports = get("/documents", key, symbol=args.symbol, doc_type="annual",
                  order="desc", size=args.limit)
    items = reports.get("items", reports if isinstance(reports, list) else [])
    if not items:
        sys.exit(f"No annual reports found for {args.symbol}. Check the symbol, or try 7203.T.")

    total_full = total_section = 0
    for rep in items:
        doc_id, period = rep["id"], rep.get("report_period", "?")
        sections = get(f"/documents/{doc_id}/sections", key)["sections"]
        heading = pick_section(sections, args.section, suffix)

        print(f"\n=== {args.symbol} · {period} · doc {doc_id} ===")
        if heading is None:
            print(f"  No section matched. This report has {len(sections)} headings:")
            for s in sections[:15]:
                print(f"    - {s}")
            print("  Re-run with --section <one of the above>.")
            continue

        sect = get(f"/documents/{doc_id}", key, section=heading)["content"]
        full = get(f"/documents/{doc_id}", key)["content"]  # costs 2 documents total for this demo
        total_full += len(full)
        total_section += len(sect)
        print(f"  section : {heading!r} — {len(sect):,} chars")
        print(f"  full    : {len(full):,} chars  ({100 * len(sect) / max(len(full), 1):.1f}% of the report)")
        print("  ---")
        print("\n".join(f"  {line}" for line in sect[:700].splitlines()))
        if len(sect) > 700:
            print(f"  … [{len(sect) - 700:,} more chars]")

    if total_full:
        saved = 100 * total_section / total_full
        print(f"\nSections were {saved:.1f}% of the full text — that is the context you bought back.")


if __name__ == "__main__":
    main()
