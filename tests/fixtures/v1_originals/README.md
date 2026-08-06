# V1 Test Corpus

7 legacy AutoHotkey v1 scripts from a fleet migration archive (autohotkey-test depot).
Pre-migration, pre-fix. Each script contains known v1 patterns.

| Script | LOC | Category |
|---|---|---|
| classic_pranks.ahk | ~400 | GUI automation, hotkeys, timers |
| dev_context_music.ahk | ~200 | File I/O, hotkeys, GUI |
| eliza.ahk | ~250 | String manipulation, chatbot |
| fun_games.ahk | ~150 | Mouse input, timers, pixel search |
| clipboard_manager.ahk | ~80 | Clipboard, GUI |
| media_controls.ahk | ~40 | Media keys, hotkeys |
| ide_shortcuts.ahk | ~30 | IDE hotkeys, key remapping |

Usage: `python tests/phase4_corpus_test.py`
