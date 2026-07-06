# ahk-lint — AutoHotkey v2 Linter

AST-based analysis, auto-fix, config file, SARIF output.

## Quick Start

```bash
pip install ahk-lint
ahk-lint script.ahk
ahk-lint .\scripts\ --fix          # Auto-fix with .bak backup
ahk-lint . --format sarif > out.sarif  # GitHub code scanning
```

## Checks

| ID | Check | Severity | Auto-fix |
|----|-------|----------|----------|
| W001 | `Random, var` → `var := Random()` | error | ✅ |
| W002 | `StringSplit` → `StrSplit()` | error | ✅ |
| W003 | `Gui, Add` → `gui.Add()` | error | ✅ |
| W004 | `IfEqual` → `if ( = )` | error | ✅ |
| W005 | `FileRead, var` → `var := FileRead()` | error | ✅ |
| W006 | `FormatTime, var` → `var := FormatTime()` | error | ✅ |
| W007 | `Gosub` → function call | warning | ❌ |
| W008 | `%var%` → `var` | error | ✅ |
| W009 | `Menu, Tray` → `A_TrayMenu` | error | ✅ |
| W010 | `SetTimer, Label` → `SetTimer(Func)` | warning | ✅ |
| S003 | I/O without try/catch | error | ❌ |
| S005 | Missing `#Requires`/`#SingleInstance` | warning | ❌ |
| S010 | Tab characters | suggestion | ❌ |
| S011 | Trailing whitespace | suggestion | ❌ |
| S012 | Line too long | suggestion | ❌ |
| S020 | Unused variable | warning | ❌ |
| S021 | Unreachable code | warning | ❌ |

## Configuration

```toml
# .ahklintrc
[checks]
v1_syntax = "error"
style = "warning"

[suppressions]
"tests/" = ["style"]
"legacy/" = "all"

[fix]
enabled = true
backup = true
```

## Per-line Suppression

```autohotkey
; @ahk-lint-disable-next-line W001
Random, var, 1, 10  ; intentional v1 compat
```

## Output Formats

```bash
ahk-lint src/                        # Terminal (default)
ahk-lint src/ --format json           # JSON
ahk-lint src/ --format sarif          # GitHub code scanning
```

## License

MIT
