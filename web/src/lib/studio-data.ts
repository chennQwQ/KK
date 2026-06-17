import {
  FiArchive,
  FiBarChart2,
  FiBookOpen,
  FiClock,
  FiCpu,
  FiDatabase,
  FiLayers,
  FiMessageSquare,
  FiPlus,
  FiSettings,
} from "react-icons/fi";
import type { HistorySection, LayoutPolicy, NavItem, SourceCard, StudioBrand, StudioObject } from "@/types/studio";

export const studioBrand: StudioBrand = {
  name: "RAG Studio",
  subtitle: "KK Object Console",
};

export const layoutPolicy: LayoutPolicy = {
  mainOnlyBelowPx: 1180,
  narrowMode: "hide-sidebars",
};

const pendingCopy = "开发中，尚未接入真实数据。";

export const navItems: NavItem[] = [
  { id: "console", label: "对象工作台", icon: FiBookOpen, status: "ready" },
  { id: "new", label: "新建对象", icon: FiPlus, status: "pending", emptyState: pendingCopy },
  { id: "history", label: "对话记录", icon: FiClock, status: "ready" },
  { id: "kb", label: "知识库", icon: FiDatabase, status: "ready" },
  { id: "datasets", label: "数据源", icon: FiArchive, status: "pending", emptyState: pendingCopy },
  { id: "retrieval", label: "检索策略", icon: FiLayers, status: "pending", emptyState: pendingCopy },
  { id: "prompts", label: "提示词", icon: FiMessageSquare, status: "pending", emptyState: pendingCopy },
  { id: "eval", label: "评估中心", icon: FiBarChart2, status: "pending", emptyState: pendingCopy },
  { id: "models", label: "模型管理", icon: FiCpu, status: "pending", emptyState: pendingCopy },
  { id: "settings", label: "设置", icon: FiSettings, status: "pending", emptyState: pendingCopy },
];

export const studioObjects: StudioObject[] = [
  {
    id: "kk-advisor",
    name: "KK 投研助手",
    type: "已构建对象",
    domain: "KK 文档问答",
    status: "可测试",
    icon: "K",
    description: "基于当前 data/ 目录中的 KK 相关文档构建的第一个真实 RAG 对象。",
    knowledgeBases: ["KK 本地文档"],
    documents: 3,
    chunks: "待索引统计",
    updatedAt: "本地数据",
  },
];

export const historySections: HistorySection[] = [
  {
    label: "本地测试",
    items: [
      {
        id: "kk-first-test",
        objectId: "kk-advisor",
        title: "KK 文档问答测试",
        time: "现在",
        summary: "使用 data/ 下现有 KK 文档完成端到端问答验证",
        question: "请基于当前 KK 文档，总结其中最核心的观点。",
      },
      {
        id: "kk-index-test",
        objectId: "kk-advisor",
        title: "KK 知识库索引检查",
        time: "本地",
        summary: "检查 manifest、文档数量和索引状态是否与本地数据一致",
        question: "当前 KK 知识库有哪些本地文档？索引状态是否可用？",
      },
    ],
  },
];

export const sourceCards: SourceCard[] = [];

export const models = ["deepseek-chat"];
