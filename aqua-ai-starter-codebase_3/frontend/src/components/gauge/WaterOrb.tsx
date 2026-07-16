"use client";

import { useEffect, useRef } from "react";

interface WaterOrbProps {
  consumedMl: number;
  goalMl: number;
}

/**
 * The Aqua Orb: a physically-animated liquid gauge (dual sine-wave surface +
 * rising bubbles + glass specular highlight) rather than a generic circular
 * progress ring. This is the app's signature visual element.
 */
export function WaterOrb({ consumedMl, goalMl }: WaterOrbProps) {
  const backRef = useRef<SVGPathElement>(null);
  const frontRef = useRef<SVGPathElement>(null);
  const bubblesRef = useRef<SVGGElement>(null);
  const offsetRef = useRef(0);
  const rafRef = useRef<number>();

  const pct = Math.max(0, Math.min(1, goalMl > 0 ? consumedMl / goalMl : 0));

  useEffect(() => {
    function tick() {
      offsetRef.current += 0.6;
      const y = 200 - pct * 190 - 5;
      const a1 = Math.sin(offsetRef.current / 18) * 4;
      const a2 = Math.sin(offsetRef.current / 14 + 1.4) * 5;

      backRef.current?.setAttribute(
        "d",
        `M0 ${y + a1} Q 25 ${y - 8 + a1} 50 ${y + a1} T 100 ${y + a1} T 150 ${y + a1} T 200 ${y + a1} V200 H0 Z`
      );
      frontRef.current?.setAttribute(
        "d",
        `M0 ${y + 8 + a2} Q 25 ${y + 16 + a2} 50 ${y + 8 + a2} T 100 ${y + 8 + a2} T 150 ${y + 8 + a2} T 200 ${
          y + 8 + a2
        } V200 H0 Z`
      );
      rafRef.current = requestAnimationFrame(tick);
    }
    rafRef.current = requestAnimationFrame(tick);
    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
    };
  }, [pct]);

  useEffect(() => {
    const g = bubblesRef.current;
    if (!g) return;
    g.innerHTML = "";
    const count = Math.round(3 + Math.max(0.08, pct) * 5);
    for (let i = 0; i < count; i++) {
      const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
      const r = 1.2 + Math.random() * 2;
      const x = 15 + Math.random() * 170;
      c.setAttribute("r", String(r));
      c.setAttribute("cx", String(x));
      c.setAttribute("cy", "195");
      c.setAttribute("fill", "rgba(255,255,255,0.55)");
      const dur = 4 + Math.random() * 4;
      const delay = Math.random() * 4;
      c.style.animation = `bubbleRise ${dur}s ${delay}s linear infinite`;
      g.appendChild(c);
    }
  }, [pct]);

  const scoreLabel = pct >= 0.9 ? "Great" : pct >= 0.6 ? "Good" : pct >= 0.3 ? "Low" : "Needs water";

  return (
    <div className="glass rounded-xl2 flex flex-col items-center gap-1.5 px-5 pb-5 pt-7">
      <div className="relative h-[236px] w-[236px]">
        <div className="animate-pulseGlow absolute -inset-8 rounded-full bg-aqua/30 blur-md" />
        <div className="shadow-orb relative h-full w-full overflow-hidden rounded-full ring-1 ring-white/20">
          <svg viewBox="0 0 200 200" className="block h-full w-full">
            <defs>
              <clipPath id="orbClip">
                <circle cx="100" cy="100" r="100" />
              </clipPath>
              <linearGradient id="waterGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#3EE8FF" />
                <stop offset="100%" stopColor="#0A6FA8" />
              </linearGradient>
              <radialGradient id="orbSheen" cx="30%" cy="20%" r="70%">
                <stop offset="0%" stopColor="rgba(255,255,255,0.55)" />
                <stop offset="45%" stopColor="rgba(255,255,255,0.05)" />
                <stop offset="100%" stopColor="rgba(255,255,255,0)" />
              </radialGradient>
            </defs>
            <rect width="200" height="200" fill="rgba(255,255,255,0.02)" />
            <g clipPath="url(#orbClip)">
              <path ref={backRef} fill="rgba(62,232,255,0.35)" />
              <path ref={frontRef} fill="url(#waterGrad)" />
              <g ref={bubblesRef} opacity={0.55} />
            </g>
            <circle cx="100" cy="100" r="99" fill="url(#orbSheen)" />
          </svg>
        </div>
        <div className="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
          <div className="font-mono text-4xl font-bold">{Math.round(pct * 100)}%</div>
          <div className="mt-0.5 text-center text-[11px] text-foam/60">
            {pct >= 1 ? "goal reached today" : "of today's goal"}
          </div>
        </div>
      </div>

      <div className="mt-2 text-[12.5px] text-foam/70">
        <b className="font-semibold text-foam">{Math.round(consumedMl)}</b> ml consumed ·{" "}
        {Math.max(0, Math.round(goalMl - consumedMl))} ml to go
      </div>

      <div className="mt-4 flex w-full gap-2.5">
        <MiniStat label="Hydration" value={scoreLabel} />
        <MiniStat label="Day streak" value="—" />
        <MiniStat label="ML goal" value={String(Math.round(goalMl))} />
      </div>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex-1 rounded-xl border border-white/10 bg-white/[0.06] px-1.5 py-2.5 text-center">
      <div className="font-mono text-[15px] font-semibold">{value}</div>
      <div className="mt-0.5 text-[9.5px] uppercase tracking-wide text-foam/40">{label}</div>
    </div>
  );
}
