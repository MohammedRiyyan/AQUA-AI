"use client";

import { useState } from "react";
import type { ContainerShape } from "@/types";
import { api } from "@/lib/api";

interface ContainerBuilderModalProps {
  open: boolean;
  onClose: () => void;
  onCreated: () => void;
}

const SHAPES: ContainerShape[] = ["cylinder", "cone", "rounded", "square"];
const COLORS = ["#17D3FF", "#0BA5A0", "#3A6FF7", "#F5A623", "#F76E9C", "#8B5CF6"];

function estimateVolume(shape: ContainerShape, heightCm: number, diameterCm: number): number {
  const r = diameterCm / 2;
  switch (shape) {
    case "cylinder":
      return Math.PI * r * r * heightCm;
    case "cone":
      return (1 / 3) * Math.PI * r * r * heightCm;
    case "rounded":
      return Math.PI * r * r * heightCm * 0.92;
    case "square":
      return diameterCm * diameterCm * heightCm;
  }
}

export function ContainerBuilderModal({ open, onClose, onCreated }: ContainerBuilderModalProps) {
  const [tab, setTab] = useState<"manual" | "smart">("manual");
  const [name, setName] = useState("");
  const [capacity, setCapacity] = useState("");
  const [color, setColor] = useState(COLORS[0]);
  const [shape, setShape] = useState<ContainerShape>("cylinder");
  const [height, setHeight] = useState("");
  const [diameter, setDiameter] = useState("");

  if (!open) return null;

  const estimatedMl = height && diameter ? Math.round(estimateVolume(shape, parseFloat(height), parseFloat(diameter))) : null;

  async function saveManual() {
    const cap = parseFloat(capacity);
    if (!cap || cap <= 0) return;
    await api.createContainer({ name: name || "Custom Container", capacity_ml: cap, color }).catch(() => {});
    onCreated();
    onClose();
  }

  async function saveSmart() {
    if (!estimatedMl) return;
    await api
      .createContainer({ name: `Smart ${estimatedMl}`, shape, height_cm: parseFloat(height), diameter_cm: parseFloat(diameter) })
      .catch(() => {});
    onCreated();
    onClose();
  }

  return (
    <div className="fixed inset-0 z-20 flex items-end justify-center bg-black/55 backdrop-blur-sm" onClick={onClose}>
      <div
        className="max-h-[82vh] w-full max-w-[430px] overflow-y-auto rounded-t-[26px] border border-white/10 bg-deep p-5 pb-7 shadow-2xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mx-auto mb-4 h-1 w-9 rounded-full bg-white/15" />
        <div className="mb-3.5 flex items-center justify-between text-[16px] font-bold">
          New Container
          <button onClick={onClose} className="text-[13px] font-normal text-foam/40">
            Cancel
          </button>
        </div>

        <div className="mb-4 flex gap-1.5 rounded-[14px] bg-white/[0.09] p-1">
          <button
            onClick={() => setTab("manual")}
            className={`flex-1 rounded-[11px] py-2 text-[11.5px] font-semibold ${tab === "manual" ? "bg-deep-2" : "text-foam/40"}`}
          >
            Manual capacity
          </button>
          <button
            onClick={() => setTab("smart")}
            className={`flex-1 rounded-[11px] py-2 text-[11.5px] font-semibold ${tab === "smart" ? "bg-deep-2" : "text-foam/40"}`}
          >
            Smart glass measure
          </button>
        </div>

        {tab === "manual" ? (
          <div>
            <Field label="Name">
              <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Steel Bottle" className="input" />
            </Field>
            <Field label="Capacity (ml)">
              <input value={capacity} onChange={(e) => setCapacity(e.target.value)} type="number" placeholder="750" className="input" />
            </Field>
            <Field label="Color">
              <div className="flex gap-2">
                {COLORS.map((c) => (
                  <button
                    key={c}
                    onClick={() => setColor(c)}
                    className="h-[30px] w-[30px] rounded-full"
                    style={{ background: c, border: color === c ? "2px solid #fff" : "2px solid transparent" }}
                  />
                ))}
              </div>
            </Field>
            <button onClick={saveManual} className="primary-btn">
              Save container
            </button>
          </div>
        ) : (
          <div>
            <Field label="Shape">
              <div className="flex gap-2">
                {SHAPES.map((s) => (
                  <button
                    key={s}
                    onClick={() => setShape(s)}
                    className={`flex-1 rounded-xl border px-1 py-2.5 text-center text-[11px] capitalize ${
                      shape === s ? "border-aqua bg-aqua/10 text-aqua-soft" : "border-white/10 bg-white/[0.09] text-foam/60"
                    }`}
                  >
                    {s}
                  </button>
                ))}
              </div>
            </Field>
            <Field label="Height (cm)">
              <input value={height} onChange={(e) => setHeight(e.target.value)} type="number" placeholder="14" className="input" />
            </Field>
            <Field label="Diameter (cm)">
              <input value={diameter} onChange={(e) => setDiameter(e.target.value)} type="number" placeholder="7" className="input" />
            </Field>
            <div className="mb-2 rounded-xl border border-aqua/25 bg-aqua/[0.08] p-3 text-center text-[12.5px] text-aqua-soft">
              {estimatedMl ? `Estimated capacity: ${estimatedMl} ml (${shape})` : "Enter dimensions to estimate capacity"}
            </div>
            <button onClick={saveSmart} className="primary-btn">
              Save estimated container
            </button>
          </div>
        )}
      </div>

      <style jsx>{`
        .input {
          width: 100%;
          padding: 11px 13px;
          border-radius: 12px;
          background: rgba(255, 255, 255, 0.09);
          border: 1px solid rgba(255, 255, 255, 0.14);
          color: inherit;
          font-size: 13.5px;
          outline: none;
        }
        .primary-btn {
          width: 100%;
          padding: 14px;
          border-radius: 16px;
          background: linear-gradient(160deg, #17d3ff, #0ba5a0);
          color: #04151c;
          font-weight: 700;
          font-size: 14px;
          margin-top: 6px;
        }
      `}</style>
    </div>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-3">
      <label className="mb-1.5 block text-[11px] uppercase tracking-wide text-foam/40">{label}</label>
      {children}
    </div>
  );
}
