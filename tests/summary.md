# Phase 4 — Corpus Test Results

## Test: v1 Scripts (before migration)

**Source:** `autohotkey-test/scriptlets/v1/` (7 archived pre-migration scripts)

| Script | Issues | Errors | Warnings | Top Rules |
|--------|--------|--------|----------|-----------|
| classic_pranks.ahk | 170 | 110 | 60 | P001, W001, W003, W007, W008 |
| dev_context_music.ahk | 65 | 47 | 18 | P001, W001, W006, W007, W008 |
| eliza.ahk | 53 | 12 | 41 | P001, W001, W003, W008, S005 |
| fun_games.ahk | 37 | 14 | 23 | P001, W008, S005, S011, S012 |
| clipboard_manager.ahk | 11 | 4 | 7 | P001, W008, S005, S011 |
| media_controls.ahk | 5 | 3 | 2 | P001, W008, S005, S021 |
| ide_shortcuts.ahk | 2 | 1 | 1 | P001, S005 |
| **Total** | **343** | **191** | **152** | |
| **Average per file** | **49.0** | | | |

**Most common violations:**
- W008 (%var% → var): 50+ occurrences
- W001 (Random, var → var := Random()): 30+  
- W003 (Gui, Add → gui.Add()): 25+
- S005 (Missing #Requires/#SingleInstance): 7/7 scripts
- W007 (Gosub → function call): 15+

## Test: v2 Scripts (current fleet)

**Source:** `autohotkey-test/scriptlets/` (80+ production v2 scripts)

| Metric | Value |
|--------|-------|
| Total files | 80+ |
| Total issues | 0 |
| Clean scripts | 100% |

## Key Metrics for Paper

| Metric | Value |
|--------|-------|
| Detection rate | 343 issues in 7 v1 scripts |
| Auto-fix coverage | 7/10 v1→v2 patterns have auto-fix |
| False positives | Minimal (style/suggestion only) |
| Fleet v2 migration result | 80+ scripts, zero remaining issues |
| Rule categories | 50+ across 4 check modules |
