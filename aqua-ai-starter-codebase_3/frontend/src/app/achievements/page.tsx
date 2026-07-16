"use client";

import { useEffect, useState } from "react";
import { BlobField } from "@/components/layout/BlobField";
import { Dock } from "@/components/layout/Dock";
import { api } from "@/lib/api";
import type { Achievement } from "@/types";

const DEMO: Achievement[] = [
  { key: "seven_day_streak", name: "7 Day Streak", description: "Hit your goal 7 days in a row.", icon: null, unlocked: false },
  { key: "hydration_master", name: "Hydration Master", description: "Hit your goal 30 days in a row.", icon: null, unlocked: true },
  { key: "ocean_level", name: "Ocean Level", description: "Logged 50 liters total.", icon: null, unlocked: true },
  { key: "aqua_legend", name: "Aqua Legend", description: "Hit your goal 100 days in a row.", icon: null, unlocked: false },
  { key: "100l_club", name: "100L Club", description: "Logged 100 liters total.", icon: null, unlocked: false },
  { key: "500l_club", name: "500L Club", description: "Logged 500 liters total.", icon: null, unlocked: false },
];

export default function AchievementsPage() {
  const [achievements, setAchievements] = useState<Achievement[]>(DEMO);

  useEffect(() => {
    api.achievements().then((a) => a.length && setAchievements(a)).catch(() => {});
  }, []);

  return (
    <>
      <BlobField />
      <main className="relative z-[1] mx-auto flex min-h-screen max-w-[430px] flex-col gap-[18px] px-[18px] pb-[110px] pt-[18px]">
        <h1 className="font-display text-xl font-bold">Achievements</h1>
        <div className="grid grid-cols-2 gap-3">
          {achievements.map((a) => (
            <div
              key={a.key}
              className={`rounded-2xl border p-4 text-center ${
                a.unlocked ? "border-aqua/30 bg-gradient-to-br from-aqua/15 to-teal/5" : "border-white/10 bg-white/[0.04] opacity-40"
              }`}
            >
              <div className="mx-auto mb-2 flex h-10 w-10 items-center justify-center rounded-xl bg-white/[0.09]">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#7FE8FF" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2l2.9 6.3 6.9.8-5 4.8 1.3 6.8L12 17.3 5.9 20.7l1.3-6.8-5-4.8 6.9-.8z" />
                </svg>
              </div>
              <div className="text-[12px] font-semibold">{a.name}</div>
              <div className="mt-1 text-[10px] leading-snug text-foam/50">{a.description}</div>
            </div>
          ))}
        </div>
      </main>
      <Dock />
    </>
  );
}
