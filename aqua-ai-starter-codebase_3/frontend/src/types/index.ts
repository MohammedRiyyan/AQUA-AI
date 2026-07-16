export interface DailySummary {
  date: string;
  consumed_ml: number;
  goal_ml: number;
  remaining_ml: number;
  hydration_percentage: number;
  hydration_score: "great" | "good" | "low" | "needs_water";
}

export interface Container {
  id: string;
  name: string;
  capacity_ml: number;
  icon: string | null;
  color: string | null;
  is_estimated: boolean;
}

export interface SourceCitation {
  title: string;
  document_id: string | null;
  relevance_score: number;
}

export interface AIAnswer {
  text: string;
  confidence: number;
  reasoning: string;
  sources: SourceCitation[];
  model_version: string | null;
  is_in_domain: boolean;
}

export interface Achievement {
  key: string;
  name: string;
  description: string;
  icon: string | null;
  unlocked: boolean;
}

export type ContainerShape = "cylinder" | "cone" | "rounded" | "square";
