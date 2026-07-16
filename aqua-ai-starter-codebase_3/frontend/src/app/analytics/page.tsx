"use client";

import { useEffect, useState } from "react";
import { BlobField } from "@/components/layout/BlobField";
import { Dock } from "@/components/layout/Dock";
import { WeeklyChart } from "@/components/analytics/WeeklyChart";
import { api } from "@/lib/api";
import type { DailySummary } from "@/types";

const DEMO_WEEK: DailySummary[] = [1900, 2400, 1750, 2650, 2100, 2300, 1350].map((ml, i) => ({
  date: `day-${i}`,
  consumed_ml: ml,
  goal_ml: 2600,
  remaining_ml: Math.max(0, 2600 - ml),
  hydration_percentage: Math.round((ml / 2600) * 100),
  hydration_score: ml / 2600 >= 0.9 ? "great" : ml / 2600 >= 0.6 ? "good" : ml / 2600 >= 0.3 ? "low" : "needs_water",
}));

export default function AnalyticsPage() {
  const [week, setWeek] = useState<DailySummary[]>(DEMO_WEEK);

  useEffect(() => {
    api.weeklySummary().then((w) => w.length && setWeek(w)).catch(() => {});
  }, []);

  const avg = Math.round(week.reduce((s, d) => s + d.consumed_ml, 0) / week.length);
  const best = week.reduce((a, b) => (b.consumed_ml > a.consumed_ml ? b : a));
  const worst = week.reduce((a, b) => (b.consumed_ml < a.consumed_ml ? b : a));

  return (
    <>
      <BlobField />
      <main className="relative z-[1] mx-auto flex min-h-screen max-w-[430px] flex-col gap-[18px] px-[18px] pb-[110px] pt-[18px]">
        <h1 className="font-display text-xl font-bold">Analytics</h1>

        <WeeklyChart days={week} />

        <div className="glass rounded-lg2 grid grid-cols-3 gap-2.5 p-4">
          <Stat label="7-day avg" value={`${avg}ml`} />
          <Stat label="Best day" value={`${Math.round(best.consumed_ml)}ml`} />
          <Stat label="Lowest day" value={`${Math.round(worst.consumed_ml)}ml`} />
        </div>

        <div className="glass rounded-lg2 p-4 text-[12.5px] text-foam/60">
          Monthly and yearly views, plus longest-streak tracking, plug into the same{" "}
          <code className="text-aqua-soft">/water-logs</code> aggregation endpoints — extend{" "}
          <code className="text-aqua-soft">backend/app/api/routers/water_logs.py</code> with{" "}
          <code className="text-aqua-soft">/monthly</code> and <code className="text-aqua-soft">/yearly</code> routes
          following the same pattern as <code className="text-aqua-soft">/weekly</code>.
        </div>
      </main>
      <Dock />
    </>
  );
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="text-center">
      <div className="font-mono text-base font-semibold">{value}</div>
      <div className="mt-0.5 text-[9.5px] uppercase tracking-wide text-foam/40">{label}</div>
    </div>
  );
}
