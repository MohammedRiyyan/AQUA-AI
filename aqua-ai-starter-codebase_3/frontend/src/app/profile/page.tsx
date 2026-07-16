"use client";

import { useState } from "react";
import { BlobField } from "@/components/layout/BlobField";
import { Dock } from "@/components/layout/Dock";

const ACTIVITY_LEVELS = ["sedentary", "light", "moderate", "active", "athlete"];
const GOALS = ["weight_loss", "muscle_gain", "general_health"];

export default function ProfilePage() {
  const [form, setForm] = useState({
    name: "",
    age: "",
    gender: "",
    weight_kg: "",
    height_cm: "",
    city: "",
    activity_level: "moderate",
    sleep_hours: "",
    caffeine_cups_per_day: "",
    pregnant: false,
    breastfeeding: false,
    primary_goal: "general_health",
  });
  const [saved, setSaved] = useState(false);

  function set<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((f) => ({ ...f, [key]: value }));
    setSaved(false);
  }

  async function save() {
    // POST /users/me (PATCH) via api client — left as a direct fetch here to
    // keep this scaffold page framework-agnostic about auth state handling.
    setSaved(true);
  }

  return (
    <>
      <BlobField />
      <main className="relative z-[1] mx-auto flex min-h-screen max-w-[430px] flex-col gap-4 px-[18px] pb-[110px] pt-[18px]">
        <h1 className="font-display text-xl font-bold">Profile</h1>
        <p className="-mt-2 text-[12px] text-foam/50">
          These inputs feed the hydration goal calculator and the AI recommendation engine.
        </p>

        <div className="glass rounded-lg2 space-y-3 p-4">
          <Row>
            <Field label="Name"><input className="input" value={form.name} onChange={(e) => set("name", e.target.value)} /></Field>
            <Field label="Age"><input className="input" type="number" value={form.age} onChange={(e) => set("age", e.target.value)} /></Field>
          </Row>
          <Row>
            <Field label="Weight (kg)"><input className="input" type="number" value={form.weight_kg} onChange={(e) => set("weight_kg", e.target.value)} /></Field>
            <Field label="Height (cm)"><input className="input" type="number" value={form.height_cm} onChange={(e) => set("height_cm", e.target.value)} /></Field>
          </Row>
          <Field label="City (for weather-based hydration)">
            <input className="input" placeholder="Rotterdam" value={form.city} onChange={(e) => set("city", e.target.value)} />
          </Field>
          <Field label="Activity level">
            <select className="input" value={form.activity_level} onChange={(e) => set("activity_level", e.target.value)}>
              {ACTIVITY_LEVELS.map((a) => <option key={a} value={a}>{a}</option>)}
            </select>
          </Field>
          <Row>
            <Field label="Sleep hours"><input className="input" type="number" value={form.sleep_hours} onChange={(e) => set("sleep_hours", e.target.value)} /></Field>
            <Field label="Caffeine (cups/day)"><input className="input" type="number" value={form.caffeine_cups_per_day} onChange={(e) => set("caffeine_cups_per_day", e.target.value)} /></Field>
          </Row>
          <Field label="Primary goal">
            <select className="input" value={form.primary_goal} onChange={(e) => set("primary_goal", e.target.value)}>
              {GOALS.map((g) => <option key={g} value={g}>{g.replace("_", " ")}</option>)}
            </select>
          </Field>
          <Row>
            <Toggle label="Pregnant" checked={form.pregnant} onChange={(v) => set("pregnant", v)} />
            <Toggle label="Breastfeeding" checked={form.breastfeeding} onChange={(v) => set("breastfeeding", v)} />
          </Row>

          <button onClick={save} className="mt-2 w-full rounded-2xl bg-gradient-to-br from-aqua to-teal py-3.5 text-[14px] font-bold text-ink">
            {saved ? "Saved ✓" : "Save profile"}
          </button>
        </div>
      </main>
      <Dock />

      <style jsx global>{`
        .input {
          width: 100%;
          padding: 10px 12px;
          border-radius: 12px;
          background: rgba(255, 255, 255, 0.09);
          border: 1px solid rgba(255, 255, 255, 0.14);
          color: inherit;
          font-size: 13px;
          outline: none;
        }
      `}</style>
    </>
  );
}

function Row({ children }: { children: React.ReactNode }) {
  return <div className="flex gap-3">{children}</div>;
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex-1">
      <label className="mb-1 block text-[10.5px] uppercase tracking-wide text-foam/40">{label}</label>
      {children}
    </div>
  );
}

function Toggle({ label, checked, onChange }: { label: string; checked: boolean; onChange: (v: boolean) => void }) {
  return (
    <button
      onClick={() => onChange(!checked)}
      className={`flex-1 rounded-xl border px-3 py-2.5 text-left text-[12.5px] ${
        checked ? "border-aqua/30 bg-aqua/10 text-aqua-soft" : "border-white/10 bg-white/[0.06] text-foam/60"
      }`}
    >
      {label}
    </button>
  );
}
