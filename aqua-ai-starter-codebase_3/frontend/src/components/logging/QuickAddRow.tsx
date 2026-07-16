"use client";

import type { Container } from "@/types";

interface QuickAddRowProps {
  containers: Container[];
  onAdd: (amountMl: number, label: string) => void;
  onOpenBuilder: () => void;
}

export function QuickAddRow({ containers, onAdd, onOpenBuilder }: QuickAddRowProps) {
  return (
    <div>
      <div className="flex items-center justify-between px-0.5 pb-2 text-[11px] font-semibold uppercase tracking-wide text-foam/40">
        <span>Quick Add</span>
        <button onClick={onOpenBuilder} className="text-[11px] font-normal tracking-normal text-aqua-soft">
          + New container
        </button>
      </div>
      <div className="scrollbar-none flex gap-2.5 overflow-x-auto pb-1.5">
        {containers.map((c) => (
          <button
            key={c.id}
            onClick={() => onAdd(c.capacity_ml, c.name)}
            className="glass flex h-[72px] w-16 flex-shrink-0 flex-col items-center justify-center gap-1 rounded-[18px] transition-transform active:scale-90"
          >
            <DropIcon />
            <div className="font-mono text-[12.5px] font-semibold">{Math.round(c.capacity_ml)}</div>
            <div className="text-[8.5px] text-foam/40">ml</div>
          </button>
        ))}
        <button
          onClick={onOpenBuilder}
          className="flex h-[72px] w-16 flex-shrink-0 flex-col items-center justify-center gap-1 rounded-[18px] border border-aqua/30 bg-gradient-to-br from-aqua/20 to-teal/10"
        >
          <div className="text-lg leading-none">+</div>
          <div className="text-[8.5px] text-foam/40">Custom</div>
        </button>
      </div>
    </div>
  );
}

function DropIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 2C12 2 5 11 5 15.5C5 19.09 8.13 22 12 22C15.87 22 19 19.09 19 15.5C19 11 12 2 12 2Z" />
    </svg>
  );
}
