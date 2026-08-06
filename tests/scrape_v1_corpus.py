#!/usr/bin/env python3
"""Scrape AHK v1 scripts from GitHub for corpus expansion.

Uses GitHub REST API. Set GITHUB_TOKEN env var for 5000 req/hr (vs 60/hr unauthenticated).

Queries:
  - \"#NoEnv\" language:autohotkey (v1-only directive, removed in v2)
  - \"#Requires AutoHotkey v1\" extension:ahk (explicit version marker)

Each hit is shallow-cloned (--depth 1 --filter=blob:none), then .ahk files
are extracted and filtered by v1 signature before saving.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from pathlib import Path

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUTPUT_DIR = Path(__file__).parent / "fixtures" / "v1_corpus_external"
MAX_REPOS = 50
PER_PAGE = 30
CLONE_TIMEOUT = 60
MIN_FILE_BYTES = 10
MAX_FILE_BYTES = 500_000

QUERIES = [
    ('"#NoEnv" language:autohotkey', "noenv"),
    ('"#Requires AutoHotkey v1" extension:ahk', "requires_v1"),
]

V1_SIGNATURES = ("#NoEnv", "Gosub", "StringSplit,", "MsgBox,", "Gui, Add",
                 "IfEqual", "SetTimer,", "%", "StringLeft,", "StringRight,")


def github_search(query: str, page: int = 1) -> list[dict]:
    encoded = urllib.parse.quote(query)
    url = f"https://api.github.com/search/code?q={encoded}&per_page={PER_PAGE}&page={page}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"token {GITHUB_TOKEN}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 403:
            print(f"  Rate limited. Set GITHUB_TOKEN env var for higher limits.", file=sys.stderr)
        return []
    except Exception as e:
        print(f"  Search error: {e}", file=sys.stderr)
        return []
    return data.get("items", [])


def clone_and_extract(repo_full_name: str) -> list[Path] | None:
    repo_dir = Path(tempfile.mkdtemp(prefix="ahk_corpus_"))
    clone_url = f"https://github.com/{repo_full_name}.git"
    try:
        subprocess.run(
            ["git", "clone", "--depth", "1", "--filter=blob:none",
             clone_url, str(repo_dir)],
            capture_output=True, timeout=CLONE_TIMEOUT, check=True,
        )
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
        shutil.rmtree(repo_dir, ignore_errors=True)
        return None

    ahk_files = list(repo_dir.glob("**/*.ahk"))
    return [repo_dir, ahk_files] if ahk_files else (shutil.rmtree(repo_dir, ignore_errors=True) or None)


if __name__ == "__main__":
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    seen_repos: set[str] = set()
    collected: list[Path] = []

    for query, label in QUERIES:
        print(f"\n=== Searching: {label} ===")
        for page in range(1, 4):
            items = github_search(query, page)
            if not items:
                break
            for item in items:
                repo = item["repository"]["full_name"]
                if repo in seen_repos:
                    continue
                seen_repos.add(repo)
                if len(seen_repos) > MAX_REPOS:
                    break

                result = clone_and_extract(repo)
                if result is None:
                    continue
                repo_dir, ahk_files = result

                for af in ahk_files:
                    size = af.stat().st_size
                    if size < MIN_FILE_BYTES or size > MAX_FILE_BYTES:
                        continue
                    try:
                        content = af.read_text(encoding="utf-8", errors="replace")
                    except Exception:
                        continue
                    if not any(sig in content for sig in V1_SIGNATURES):
                        continue
                    dest = OUTPUT_DIR / f"{repo.replace('/', '_')}_{af.name}"
                    dest.write_text(content, encoding="utf-8")
                    collected.append(dest)
                                        try:
                        print(f"    -> {dest.name} ({size} bytes) [{repo}]")
                    except UnicodeEncodeError:
                        print(f"    -> {dest.name} ({size} bytes) [repo name has unicode chars]")

                shutil.rmtree(repo_dir, ignore_errors=True)
                time.sleep(2)

            if len(seen_repos) > MAX_REPOS:
                break
        if len(seen_repos) > MAX_REPOS:
            break

    print(f"\n=== Collected {len(collected)} v1 scripts from {len(seen_repos)} repos ===")
