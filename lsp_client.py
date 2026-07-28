"""Python LSP client for thqby's AutoHotkey v2 language server.

Communicates via JSON-RPC over stdin/stdout with the Node.js LSP server.
"""

import json
import logging
import os
import subprocess
from pathlib import Path

logger = logging.getLogger("ahk-lint-lsp")

LSP_SERVER_PATH = os.environ.get(
    "AHK_LSP_PATH",
    str(
        Path(__file__).resolve().parent.parent
        / "vscode-autohotkey2-lsp"
        / "server"
        / "cli"
        / "cli.js"
    ),
)


class LSPClient:
    """Manages a subprocess running thqby's AHK v2 LSP server."""

    def __init__(self, node_path: str = "node"):
        self.node_path = node_path
        self.proc: subprocess.Popen | None = None
        self.buffer = ""
        self.request_id = 0

    def start(self):
        if not Path(LSP_SERVER_PATH).exists():
            logger.warning(
                f"LSP server not found at {LSP_SERVER_PATH}. Install thqby's vscode-autohotkey2-lsp."
            )
            return False
        try:
            self.proc = subprocess.Popen(
                [self.node_path, LSP_SERVER_PATH, "--stdio"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            # Initialize LSP
            self._send_request(
                "initialize",
                {
                    "processId": None,
                    "capabilities": {},
                    "rootUri": "file:///",
                },
            )
            # Initialized notification
            self._send_notification("initialized", {})
            logger.info("LSP server started")
            return True
        except Exception as e:
            logger.warning(f"Failed to start LSP server: {e}")
            return False

    def stop(self):
        if self.proc:
            self._send_notification("exit", {})
            try:
                self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.proc.kill()
            self.proc = None

    def lint(self, source: str, file_path: str = "untitled.ahk") -> list[dict]:
        if not self.proc:
            return []
        # Open document
        self._send_notification(
            "textDocument/didOpen",
            {
                "textDocument": {
                    "uri": f"file:///{file_path}",
                    "languageId": "ahk2",
                    "version": 1,
                    "text": source,
                }
            },
        )
        # Request diagnostics
        result = self._send_request(
            "textDocument/diagnostic",
            {
                "textDocument": {"uri": f"file:///{file_path}"},
            },
        )
        # Parse diagnostics
        issues = []
        if result and "diagnosticCollection" in result:
            for diagnostic in result["diagnosticCollection"].get("diagnostics", []):
                issues.append(
                    {
                        "rule": "LSP",
                        "severity": self._severity(diagnostic.get("severity", 2)),
                        "message": diagnostic.get("message", ""),
                        "line": diagnostic.get("range", {}).get("start", {}).get("line", 0) + 1,
                        "col": diagnostic.get("range", {}).get("start", {}).get("character", 0) + 1,
                        "fixable": False,
                        "source": "LSP",
                    }
                )
        return issues

    def _send_request(self, method: str, params: dict) -> dict | None:
        if not self.proc or not self.proc.stdin:
            return None
        self.request_id += 1
        msg = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
            "params": params,
        }
        self._write_message(msg)
        return self._read_response()

    def _send_notification(self, method: str, params: dict):
        if not self.proc or not self.proc.stdin:
            return
        msg = {"jsonrpc": "2.0", "method": method, "params": params}
        self._write_message(msg)

    def _write_message(self, msg: dict):
        data = json.dumps(msg, ensure_ascii=False)
        header = f"Content-Length: {len(data)}\r\n\r\n"
        self.proc.stdin.write(header + data)
        self.proc.stdin.flush()

    def _read_response(self) -> dict | None:
        if not self.proc or not self.proc.stdout:
            return None
        # Read header
        while True:
            line = self.proc.stdout.readline()
            if not line:
                return None
            line = line.strip()
            if line.startswith("Content-Length:"):
                length = int(line.split(":")[1].strip())
            elif line == "" and length:
                break
        # Read body
        data = self.proc.stdout.read(length)
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _severity(lsp_severity: int) -> str:
        return {1: "error", 2: "warning", 3: "suggestion", 4: "suggestion"}.get(
            lsp_severity, "warning"
        )

    def __del__(self):
        self.stop()
