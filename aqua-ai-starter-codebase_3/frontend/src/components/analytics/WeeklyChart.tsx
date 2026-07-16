"use client";

import type { DailySummary } from "@/types";

const DAY_LABELS = ["M", "T", "W", "T", "F", "S", "S"];

export function WeeklyChart({ days }: { days: DailySummary[] }) {
  const max = Math.max(...days.map((d) => Math.max(d.consumed_ml, d.goal_ml)), 1);

  return (
    <div className="glass rounded-lg2 p-[18px]">
      <div className="flex items-center justify-between px-0.5 text-[11px] font-semibold uppercase tracking-wide text-foam/40">
        <span>This Week</span>
      </div>
      <div className="mt-3.5 flex h-24 items-end gap-2 px-0.5">
        {days.map((d, i) => {
          const h = Math.max(6, Math.round((d.consumed_ml / max) * 90));
          const isToday = i === days.length - 1;
          return (
            <div key={d.date} className="flex h-full flex-1 flex-col items-center justify-end gap-1.5">
              <div
                className={`w-full max-w-[26px] rounded-t-lg rounded-b-[4px] transition-[height] duration-1000 ${
                  isToday ? "bg-gradient-to-b from-white to-aqua" : "bg-gradient-to-b from-aqua-soft to-teal"
                }`}
                style={{ height: `${h}px` }}
              />
              <span className="text-[9.5px] text-foam/40">{DAY_LABELS[i]}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
