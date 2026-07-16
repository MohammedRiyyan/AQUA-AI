"use client";

import { useState } from "react";
import type { AIAnswer } from "@/types";
import { api } from "@/lib/api";

interface AIAdvicePanelProps {
  initialAdvice: AIAnswer | null;
}

export function AIAdvicePanel({ initialAdvice }: AIAdvicePanelProps) {
  const [answer, setAnswer] = useState<AIAnswer | null>(initialAdvice);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleAsk() {
    const q = question.trim();
    if (!q || loading) return;
    setLoading(true);
    try {
      const res = await api.askAI(q);
      setAnswer(res);
      setQuestion("");
    } catch {
      setAnswer({
        text: "I couldn't reach the hydration model just now — please try again in a moment.",
        confidence: 0,
        reasoning: "Request failed",
        sources: [],
        model_version: null,
        is_in_domain: true,
      });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="glass rounded-lg2 p-4.5 p-[18px]">
      <div className="mb-2.5 flex items-center gap-2.5">
        <div className="flex h-[30px] w-[30px] flex-shrink-0 items-center justify-center rounded-[10px] bg-gradient-to-br from-aqua to-teal">
          <DropIcon className="h-[15px] w-[15px] stroke-ink" />
        </div>
        <div className="text-[13px] font-semibold">
          Hydration Coach
          <span className="mt-0.5 block text-[10px] font-normal text-foam/40">Custom RAG model · hydration-only</span>
        </div>
      </div>

      <p className="mb-2.5 text-[13.5px] leading-relaxed">
        {answer?.text ?? "Loading today's advice…"}
      </p>

      {answer && (
        <div className="mb-3 flex flex-wrap gap-1.5">
          {answer.is_in_domain && (
            <span className="rounded-full border border-aqua/25 bg-white/[0.09] px-2.5 py-1 text-[9.5px] text-aqua-soft">
              {Math.round(answer.confidence * 100)}% confidence
            </span>
          )}
          {answer.sources.map((s, i) => (
            <span key={i} className="rounded-full border border-white/10 bg-white/[0.09] px-2.5 py-1 text-[9.5px] text-foam/60">
              Source: {s.title}
            </span>
          ))}
        </div>
      )}

      <div className="flex gap-2">
        <input
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAsk()}
          placeholder="Ask about hydration, e.g. 'is coffee dehydrating?'"
          className="flex-1 rounded-[14px] border border-white/10 bg-white/[0.09] px-3 py-2.5 text-[12.5px] outline-none placeholder:text-foam/40"
        />
        <button
          onClick={handleAsk}
          disabled={loading}
          className="flex h-[38px] w-[38px] flex-shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-aqua to-teal disabled:opacity-50"
        >
          <SendIcon className="h-4 w-4 stroke-ink" />
        </button>
      </div>
    </div>
  );
}

function DropIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" strokeWidth={2.4} strokeLinecap="round" className={className}>
      <path d="M12 2C12 2 5 11 5 15.5C5 19.09 8.13 22 12 22C15.87 22 19 19.09 19 15.5C19 11 12 2 12 2Z" />
    </svg>
  );
}

function SendIcon({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 24 24" fill="none" strokeWidth={2.4} strokeLinecap="round" strokeLinejoin="round" className={className}>
      <path d="M22 2 11 13" />
      <path d="M22 2 15 22l-4-9-9-4 20-7Z" />
    </svg>
  );
}
