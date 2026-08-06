import { Routes, Route, NavLink } from "react-router-dom";
import { Home, BookOpen, FlaskConical } from "lucide-react";
import DashboardPage from "./pages/DashboardPage";
import PaperPage from "./pages/PaperPage";
import LabPage from "./pages/LabPage";

const navItems = [
  { to: "/", icon: Home, label: "Dashboard" },
  { to: "/paper", icon: BookOpen, label: "Paper" },
  { to: "/lab", icon: FlaskConical, label: "Lab" },
];

export default function App() {
  return (
    <div className="flex h-screen bg-zinc-950">
      <aside className="w-56 flex-shrink-0 bg-zinc-900 border-r border-zinc-800 flex flex-col">
        <div className="flex items-center gap-3 px-5 py-5 border-b border-zinc-800">
          <div className="w-8 h-8 rounded-lg bg-amber-500 flex items-center justify-center font-bold text-zinc-950 text-sm">AL</div>
          <div>
            <div className="text-zinc-100 font-semibold text-sm leading-tight">ahk-lint</div>
            <div className="text-zinc-500 text-xs">v2.0.0</div>
          </div>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map(({ to, icon: Icon, label }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-amber-500/10 text-amber-500"
                    : "text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800"
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="px-5 py-4 border-t border-zinc-800 text-xs text-zinc-600">
          AutoHotkey v2 Linter
        </div>
      </aside>
      <main className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto px-8 py-8">
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/paper" element={<PaperPage />} />
            <Route path="/lab" element={<LabPage />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
