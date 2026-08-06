import { useNavigate } from "react-router-dom";
import { ArrowRight, AlertTriangle, FileCode, Layers } from "lucide-react";

const kpis = [
  { icon: AlertTriangle, value: "167", label: "Patterns", desc: "Detectable v1 patterns" },
  { icon: Layers, value: "7", label: "Rule Modules", desc: "Syntax, safety, style, dead code & more" },
  { icon: FileCode, value: "95,651", label: "Issues Detected", desc: "Across 676 scripts (189K LOC)" },
];

export default function DashboardPage() {
  const navigate = useNavigate();

  return (
    <div className="space-y-12">
      <div className="text-center py-12">
        <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-amber-500/10 mb-6">
          <FileCode className="h-8 w-8 text-amber-500" />
        </div>
        <h1 className="text-4xl font-bold text-zinc-100 mb-3">ahk-lint</h1>
        <p className="text-xl text-zinc-400 max-w-2xl mx-auto">
          AutoHotkey v1&rarr;v2 Migration Linter
        </p>
        <p className="text-zinc-500 mt-3 max-w-xl mx-auto">
          Detects and repairs v1-to-v2 migration patterns across 167 rules.
          Zero false positive errors on production v2 scripts.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {kpis.map(({ icon: Icon, value, label, desc }) => (
          <div key={label} className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <div className="flex items-center gap-3 mb-3">
              <div className="w-10 h-10 rounded-lg bg-zinc-800 flex items-center justify-center">
                <Icon className="h-5 w-5 text-amber-500" />
              </div>
              <span className="text-2xl font-bold text-zinc-100">{value}</span>
            </div>
            <div className="text-sm font-medium text-zinc-300">{label}</div>
            <div className="text-xs text-zinc-500 mt-1">{desc}</div>
          </div>
        ))}
      </div>

      <div className="flex gap-4 justify-center">
        <button
          onClick={() => navigate("/lab")}
          className="flex items-center gap-2 px-6 py-3 bg-amber-500 hover:bg-amber-400 text-zinc-950 font-semibold rounded-xl transition-colors"
        >
          Try the Linter
          <ArrowRight className="h-4 w-4" />
        </button>
        <button
          onClick={() => navigate("/paper")}
          className="flex items-center gap-2 px-6 py-3 bg-zinc-800 hover:bg-zinc-700 text-zinc-100 font-semibold rounded-xl transition-colors border border-zinc-700"
        >
          Read the Paper
        </button>
      </div>
    </div>
  );
}
