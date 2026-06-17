import type { IconType } from "react-icons";

export type NavStatus = "ready" | "pending";

export interface StudioBrand {
  name: string;
  subtitle: string;
}

export interface LayoutPolicy {
  mainOnlyBelowPx: number;
  narrowMode: "hide-sidebars";
}

export interface NavItem {
  id: string;
  label: string;
  icon: IconType;
  status: NavStatus;
  emptyState?: string;
}

export interface StudioObject {
  id: string;
  name: string;
  type: string;
  domain: string;
  status: string;
  icon: string;
  description: string;
  knowledgeBases: string[];
  documents: number;
  chunks: string;
  updatedAt: string;
}

export interface HistoryItem {
  id: string;
  objectId: string;
  title: string;
  time: string;
  summary: string;
  question: string;
  inheritsFrom?: string;
}

export interface HistorySection {
  label: string;
  items: HistoryItem[];
}

export interface SourceCard {
  id: string;
  rank: number;
  title: string;
  page: string;
  score: string;
  quote: string;
  tags: string[];
}

export type ApiState = "pending" | "ready" | "sending" | "offline";
export type SourceTab = "relevance" | "citation";
export type FeedbackValue = "up" | "down" | null;
