"use client";

import { FormEvent, useEffect, useMemo, useState } from "react";
import { askQuestion } from "@/lib/api/chat";
import { citationsToSourceCards } from "@/lib/citations";
import { getKnowledgeBaseStatus, rebuildKnowledgeBaseIndex, regenerateKnowledgeBaseManifests } from "@/lib/api/knowledge-base";
import { getObjects } from "@/lib/api/objects";
import { historySections, models, studioObjects } from "@/lib/studio-data";
import type { IndexRebuildResponse, KnowledgeBaseStatusResponse, ManifestRegenerateItem } from "@/lib/api/types";
import type { ApiState, FeedbackValue, HistoryItem, SourceCard, SourceTab } from "@/types/studio";
import { findHistoryItem, getObjectThreads } from "@/utils/studio";

export function useStudioState() {
  const [activeNav, setActiveNav] = useState("console");
  const [activeHistory, setActiveHistory] = useState("kk-first-test");
  const [activeObjectId, setActiveObjectId] = useState("kk-advisor");
  const [activeSource, setActiveSource] = useState("s1");
  const [sourceTab, setSourceTab] = useState<SourceTab>("relevance");
  const [query, setQuery] = useState("");
  const [draft, setDraft] = useState("");
  const [selectedModel, setSelectedModel] = useState(models[0]);
  const [railCollapsed, setRailCollapsed] = useState(false);
  const [historyDrawerOpen, setHistoryDrawerOpen] = useState(false);
  const [evidenceDrawerOpen, setEvidenceDrawerOpen] = useState(false);
  const [feedback, setFeedback] = useState<FeedbackValue>(null);
  const [lastQuestion, setLastQuestion] = useState(findHistoryItem("kk-first-test")?.question ?? "");
  const [answerText, setAnswerText] = useState("");
  const [apiState, setApiState] = useState<ApiState>("ready");
  const [objects, setObjects] = useState(studioObjects);
  const [latestSources, setLatestSources] = useState<SourceCard[]>([]);
  const [knowledgeBaseStatus, setKnowledgeBaseStatus] = useState<KnowledgeBaseStatusResponse | null>(null);
  const [manifestItems, setManifestItems] = useState<ManifestRegenerateItem[]>([]);
  const [manifestState, setManifestState] = useState<ApiState>("ready");
  const [indexRebuildResult, setIndexRebuildResult] = useState<IndexRebuildResponse | null>(null);
  const [indexRebuildState, setIndexRebuildState] = useState<ApiState>("pending");

  useEffect(() => {
    let cancelled = false;

    getObjects()
      .then((nextObjects) => {
        if (!cancelled && nextObjects.length > 0) {
          setObjects(nextObjects);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setObjects(studioObjects);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;

    getKnowledgeBaseStatus()
      .then((status) => {
        if (!cancelled) {
          setKnowledgeBaseStatus(status);
        }
      })
      .catch(() => {
        if (!cancelled) {
          setKnowledgeBaseStatus(null);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const activeModule = useMemo(() => activeNav, [activeNav]);
  const selectedChat = findHistoryItem(activeHistory) ?? findHistoryItem("kk-first-test")!;
  const activeObject = objects.find((item) => item.id === activeObjectId) ?? objects[0] ?? studioObjects[0];

  const filteredSections = useMemo(() => {
    const activeObjectThreadIds = new Set(getObjectThreads(activeObjectId).map((item) => item.id));

    return historySections
      .map((section) => ({
        ...section,
        items: section.items.filter(
          (item) =>
            activeObjectThreadIds.has(item.id) &&
            `${item.title} ${item.summary}`.toLowerCase().includes(query.trim().toLowerCase()),
        ),
      }))
      .filter((section) => section.items.length > 0);
  }, [activeObjectId, query]);

  const displayedSources = useMemo(() => {
    if (sourceTab === "citation") {
      return [...latestSources].sort((left, right) => left.rank - right.rank);
    }

    return [...latestSources].sort((left, right) => Number(right.score) - Number(left.score));
  }, [latestSources, sourceTab]);

  function selectChat(item: HistoryItem) {
    setActiveHistory(item.id);
    setActiveObjectId(item.objectId);
    setLastQuestion(item.question);
    setAnswerText("");
    setLatestSources([]);
    setFeedback(null);
  }

  function selectObject(objectId: string) {
    const firstThread = getObjectThreads(objectId)[0];

    setActiveObjectId(objectId);
    if (firstThread) {
      setActiveHistory(firstThread.id);
      setLastQuestion(firstThread.question);
    }
    setAnswerText("");
    setLatestSources([]);
    setFeedback(null);
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const nextQuestion = draft.trim();

    if (!nextQuestion) {
      return;
    }

    setLastQuestion(nextQuestion);
    setDraft("");
    setApiState("sending");
    setAnswerText("");
    setLatestSources([]);

    try {
      const response = await askQuestion({ question: nextQuestion, chatId: activeHistory, objectId: activeObjectId });
      setAnswerText(response.answer);
      setLatestSources(response.citations.length > 0 ? citationsToSourceCards(response.citations) : []);
      setApiState("ready");
    } catch {
      setAnswerText("");
      setLatestSources([]);
      setApiState("offline");
    }
  }

  async function handleRegenerateManifests() {
    setManifestState("sending");

    try {
      const response = await regenerateKnowledgeBaseManifests();
      setManifestItems(response.generated);
      setManifestState("ready");
      const status = await getKnowledgeBaseStatus();
      setKnowledgeBaseStatus(status);
    } catch {
      setManifestState("offline");
    }
  }

  async function handleRebuildIndex() {
    setIndexRebuildState("sending");
    setIndexRebuildResult(null);

    try {
      const response = await rebuildKnowledgeBaseIndex();
      setIndexRebuildResult(response);
      setIndexRebuildState(response.status === "failed" ? "offline" : "ready");
      const status = await getKnowledgeBaseStatus();
      setKnowledgeBaseStatus(status);
    } catch {
      setIndexRebuildResult({
        status: "failed",
        chunks: 0,
        elapsed_ms: 0,
        error: "Index rebuild request failed.",
      });
      setIndexRebuildState("offline");
    }
  }

  return {
    activeModule,
    activeNav,
    activeObject,
    activeObjectId,
    activeSource,
    answerText,
    apiState,
    displayedSources,
    draft,
    evidenceDrawerOpen,
    feedback,
    filteredSections,
    historyDrawerOpen,
    lastQuestion,
    knowledgeBaseStatus,
    indexRebuildResult,
    indexRebuildState,
    manifestItems,
    manifestState,
    objects,
    query,
    railCollapsed,
    selectedChat,
    selectedModel,
    sourceTab,
    handleRebuildIndex,
    handleSubmit,
    handleRegenerateManifests,
    selectChat,
    selectObject,
    setActiveNav,
    setActiveObjectId,
    setActiveSource,
    setDraft,
    setEvidenceDrawerOpen,
    setFeedback,
    setHistoryDrawerOpen,
    setQuery,
    setRailCollapsed,
    setSelectedModel,
    setSourceTab,
  };
}

export type StudioState = ReturnType<typeof useStudioState>;
