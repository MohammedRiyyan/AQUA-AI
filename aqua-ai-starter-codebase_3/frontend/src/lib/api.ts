import type { AIAnswer, Achievement, Container, DailySummary } from "@/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = typeof window !== "undefined" ? localStorage.getItem("aqua_token") : null;
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed: ${res.status}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  dailySummary: () => request<DailySummary>("/water-logs/summary"),
  weeklySummary: () => request<DailySummary[]>("/water-logs/weekly"),
  logWater: (amount_ml: number, container_id?: string) =>
    request("/water-logs", { method: "POST", body: JSON.stringify({ amount_ml, container_id }) }),
  containers: () => request<Container[]>("/containers"),
  createContainer: (payload: Record<string, unknown>) =>
    request<Container>("/containers", { method: "POST", body: JSON.stringify(payload) }),
  dailyAdvice: () => request<AIAnswer>("/ai/daily-advice"),
  askAI: (question: string) => request<AIAnswer>("/ai/chat", { method: "POST", body: JSON.stringify({ question }) }),
  achievements: () => request<Achievement[]>("/achievements"),
  recalculateGoal: (lat: number, lon: number) =>
    request(`/goals/recalculate?lat=${lat}&lon=${lon}`, { method: "POST" }),
};
