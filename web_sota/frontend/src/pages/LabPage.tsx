import { useState } from "react";
import { AlertTriangle, CheckCircle, Loader2, Wrench } from "lucide-react";

interface Issue {
  rule: string;
  severity: string;
  message: string;
  line: number;
  col?: number;
  fixable?: boolean;
}

interface LintResult {
  issues: Issue[];
  total: number;
  by_severity: { errors: number; warnings: number };
  clean: boolean;
}

const SEVERITY_COLORS: Record<string, string> = {
  error: "bg-red-500/15 text-red-400 border-red-500/30",
  warning: "bg-amber-500/15 text-amber-400 border-amber-500/30",
  suggestion: "bg-blue-500/15 text-blue-400 border-blue-500/30",
};

const DEFAULT_CODE = `; Paste your AHK script here
#NoEnv
#SingleInstance Force

MsgBox Hello World
var = 42
StringSplit, arr, input, % ","

Gui, Add, Text,, Welcome
Gui, Show

Random, rand, 1, 100
ToolTip Random: %rand%

Gosub, Cleanup
return

Cleanup:
ExitApp
return
`;

export default function LabPage() {
  const [source, setSource] = useState(DEFAULT_CODE);
  const [result, setResult] = useState<LintResult | null>(null);
  const [fixedSource, setFixedSource] = useState<string | null>(null);
  const [linting, setLinting] = useState(false);
  const [fixing, setFixing] = useState(false);

  async function handleLint() {
    setLinting(true);
    setResult(null);
    setFixedSource(null);
    try {
      const r = await fetch("/api/lint", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source }),
      });
      const data = await r.json();
      setResult(data);
    } catch {
      setResult(null);
    } finally {
      setLinting(false);
    }
  }

  async function handleFix() {
    setFixing(true);
    try {
      const r = await fetch("/api/fix", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source }),
      });
      const data = await r.json();
      setFixedSource(data.source);
    } catch {
      setFixedSource(null);
    } finally {
      setFixing(false);
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-zinc-100">AHK Linter Lab</h1>
        <p className="text-zinc-400 text-sm mt-1">Paste AutoHotkey code below to lint it for v1&rarr;v2 migration issues.</p>
      </div>

      <div className="space-y-3">
        <textarea
          value={source}
          onChange={(e) => setSource(e.target.value)}
          rows={20}
          className="w-full bg-zinc-900 border border-zinc-700 rounded-xl p-4 text-sm font-mono text-zinc-200 placeholder-zinc-600 resize-y focus:outline-none focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500"
          placeholder="Paste your AHK code here..."
        />
        <div className="flex gap-3">
          <button
            onClick={handleLint}
            disabled={linting || !source.trim()}
            className="flex items-center gap-2 px-5 py-2.5 bg-amber-500 hover:bg-amber-400 disabled:bg-zinc-700 disabled:text-zinc-500 text-zinc-950 font-semibold rounded-xl transition-colors"
          >
            {linting ? <Loader2 className="h-4 w-4 animate-spin" /> : <AlertTriangle className="h-4 w-4" />}
            {linting ? "Analyzing..." : "Analyze"}
          </button>
        </div>
      </div>

      {result && (
        <div className="space-y-4">
          <div className={`flex items-center gap-3 px-5 py-3 rounded-xl border ${
            result.clean
              ? "bg-emerald-500/5 border-emerald-500/20"
              : "bg-red-500/5 border-red-500/20"
          }`}>
            {result.clean ? (
              <CheckCircle className="h-5 w-5 text-emerald-400" />
            ) : (
              <AlertTriangle className="h-5 w-5 text-red-400" />
            )}
            <span className={`font-semibold ${result.clean ? "text-emerald-300" : "text-red-300"}`}>
              {result.clean
                ? "No issues found"
                : `${result.total} issue${result.total !== 1 ? "s" : ""} found (${result.by_severity.errors} error${result.by_severity.errors !== 1 ? "s" : ""}, ${result.by_severity.warnings} warning${result.by_severity.warnings !== 1 ? "s" : ""})`
              }
            </span>
            {!result.clean && (
              <button
                onClick={handleFix}
                disabled={fixing}
                className="ml-auto flex items-center gap-2 px-4 py-1.5 bg-amber-500/10 hover:bg-amber-500/20 text-amber-400 rounded-lg text-sm font-medium transition-colors border border-amber-500/20 disabled:opacity-50"
              >
                {fixing ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Wrench className="h-3.5 w-3.5" />}
                {fixing ? "Fixing..." : "Auto-Fix"}
              </button>
            )}
          </div>

          {result.issues.length > 0 && (
            <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-zinc-800">
                    <th className="text-left px-4 py-3 text-zinc-500 font-medium text-xs uppercase tracking-wider w-16">Line</th>
                    <th className="text-left px-4 py-3 text-zinc-500 font-medium text-xs uppercase tracking-wider w-24">Severity</th>
                    <th className="text-left px-4 py-3 text-zinc-500 font-medium text-xs uppercase tracking-wider w-24">Rule</th>
                    <th className="text-left px-4 py-3 text-zinc-500 font-medium text-xs uppercase tracking-wider">Message</th>
                  </tr>
                </thead>
                <tbody>
                  {result.issues.map((issue, i) => (
                    <tr key={i} className="border-b border-zinc-800/50 last:border-0 hover:bg-zinc-800/30">
                      <td className="px-4 py-2.5 text-zinc-300 font-mono text-xs">{issue.line}</td>
                      <td className="px-4 py-2.5">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium border ${SEVERITY_COLORS[issue.severity] || "bg-zinc-800 text-zinc-400"}`}>
                          {issue.severity}
                        </span>
                      </td>
                      <td className="px-4 py-2.5">
                        <code className="text-xs font-mono text-amber-400/80">{issue.rule}</code>
                      </td>
                      <td className="px-4 py-2.5 text-zinc-300 text-xs">{issue.message}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {fixedSource && (
        <div className="space-y-3">
          <h2 className="text-sm font-semibold text-zinc-400 uppercase tracking-wider">Fixed Code</h2>
          <div className="bg-zinc-900 border border-emerald-500/20 rounded-xl overflow-hidden">
            <div className="bg-emerald-500/5 px-4 py-2 border-b border-emerald-500/10 flex items-center gap-2">
              <CheckCircle className="h-4 w-4 text-emerald-400" />
              <span className="text-sm text-emerald-300 font-medium">Auto-fix applied</span>
            </div>
            <pre className="p-4 text-sm font-mono text-zinc-200 overflow-x-auto whitespace-pre-wrap">{fixedSource}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
