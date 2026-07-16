"use client";

import { useEffect, useState } from "react";
import { BlobField } from "@/components/layout/BlobField";
import { Dock } from "@/components/layout/Dock";
import { WaterOrb } from "@/components/gauge/WaterOrb";
import { QuickAddRow } from "@/components/logging/QuickAddRow";
import { AIAdvicePanel } from "@/components/ai/AIAdvicePanel";
import { ContainerBuilderModal } from "@/components/logging/ContainerBuilderModal";
import { api } from "@/lib/api";
import type { AIAnswer, Container, DailySummary } from "@/types";

// Fallback demo data so the dashboard renders meaningfully before a backend
// is running / a user is authenticated — replace with real loading/auth states.
const DEMO_CONTAINERS: Container[] = [
  { id: "150", name: "150", capacity_ml: 150, icon: "glass", color: null, is_estimated: false },
  { id: "200", name: "200", capacity_ml: 200, icon: "glass", color: null, is_estimated: false },
  { id: "250", name: "250", capacity_ml: 250, icon: "glass", color: null, is_estimated: false },
  { id: "500", name: "500", capacity_ml: 500, icon: "bottle", color: null, is_estimated: false },
  { id: "750", name: "750", capacity_ml: 750, icon: "bottle", color: null, is_estimated: false },
  { id: "1000", name: "1L", capacity_ml: 1000, icon: "bottle", color: null, is_estimated: false },
];
const DEMO_SUMMARY: DailySummary = {
  date: new Date().toISOString().slice(0, 10),
  consumed_ml: 1350,
  goal_ml: 2600,
  remaining_ml: 1250,
  hydration_percentage: 52,
  hydration_score: "good",
};
const DEMO_ADVICE: AIAnswer = {
  text: "You've had 1350ml today. Based on today's weather and a moderate activity level, aim for another 1250ml over the next few hours, spaced in ~250ml increments.",
  confidence: 0.92,
  reasoning: "Retrieved 3 passages from the hydration knowledge base and grounded the answer in the user's profile.",
  sources: [{ title: "WHO Hydration Guidelines, 2023", document_id: null, relevance_score: 0.91 }],
  model_version: "aqua-hydration-llm-v0.1",
  is_in_domain: true,
};

export default function HomePage() {
  const [summary, setSummary] = useState<DailySummary>(DEMO_SUMMARY);
  const [containers, setContainers] = useState<Container[]>(DEMO_CONTAINERS);
  const [advice, setAdvice] = useState<AIAnswer | null>(DEMO_ADVICE);
  const [theme, setTheme] = useState<"dark" | "light">("dark");
  const [builderOpen, setBuilderOpen] = useState(false);

  useEffect(() => {
    // Best-effort live data load; silently keep demo data if unauthenticated
    // or the backend isn't reachable yet (e.g. first-run local dev).
    api.dailySummary().then(setSummary).catch(() => {});
    api.containers().then((c) => c.length && setContainers(c)).catch(() => {});
    api.dailyAdvice().then(setAdvice).catch(() => {});
  }, []);

  async function handleAdd(amountMl: number, label: string) {
    setSummary((s) => ({
      ...s,
      consumed_ml: s.consumed_ml + amountMl,
      remaining_ml: Math.max(0, s.remaining_ml - amountMl),
      hydration_percentage: Math.min(100, Math.round(((s.consumed_ml + amountMl) / s.goal_ml) * 100),),
    }));
    api.logWater(amountMl).catch(() => {});
  }

  function toggleTheme() {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    document.documentElement.setAttribute("data-theme", next);
  }

  return (
    <>
      <BlobField />
      <main className="relative z-[1] mx-auto flex min-h-screen max-w-[430px] flex-col gap-[18px] px-[18px] pb-[110px] pt-[6px]">
        <header className="flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="flex h-[38px] w-[38px] items-center justify-center rounded-xl bg-gradient-to-br from-aqua-soft to-teal shadow-[0_4px_18px_rgba(23,211,255,0.35)]">
              <svg width="19" height="19" viewBox="0 0 24 24" fill="none">
                <path d="M12 2C12 2 5 11 5 15.5C5 19.09 8.13 22 12 22C15.87 22 19 19.09 19 15.5C19 11 12 2 12 2Z" fill="#04151c" />
              </svg>
            </div>
            <div>
              <div className="font-display text-[17px] font-bold tracking-tight">Aqua AI</div>
              <div className="-mt-0.5 text-[10.5px] tracking-wide text-foam/40">EVERY DROP COUNTS</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="glass flex items-center gap-1.5 rounded-full py-1.5 pl-2 pr-3 text-[11.5px] text-foam/70">
              <SunIcon />
              <span>24°C · Rotterdam</span>
            </div>
            <button onClick={toggleTheme} className="glass flex h-[38px] w-[38px] items-center justify-center rounded-full">
              <MoonIcon />
            </button>
          </div>
        </header>

        <WaterOrb consumedMl={summary.consumed_ml} goalMl={summary.goal_ml} />

        <QuickAddRow containers={containers} onAdd={handleAdd} onOpenBuilder={() => setBuilderOpen(true)} />

        <AIAdvicePanel initialAdvice={advice} />
      </main>
      <Dock />

      <ContainerBuilderModal
        open={builderOpen}
        onClose={() => setBuilderOpen(false)}
        onCreated={() => api.containers().then(setContainers).catch(() => {})}
      />
    </>
  );
}

function SunIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#7FE8FF" strokeWidth={2} strokeLinecap="round">
      <path d="M12 2v2M4.9 4.9l1.4 1.4M2 12h2M4.9 19.1l1.4-1.4M12 20v2M17.7 17.7l1.4 1.4M20 12h2M17.7 6.3l1.4-1.4" />
      <circle cx="12" cy="12" r="4" />
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79Z" />
    </svg>
  );
}
