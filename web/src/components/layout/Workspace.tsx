"use client";

import {
  FiCheckCircle,
  FiChevronDown,
  FiChevronLeft,
  FiChevronRight,
  FiCopy,
  FiCpu,
  FiFileText,
  FiRefreshCw,
  FiSend,
  FiSliders,
  FiThumbsDown,
  FiThumbsUp,
} from "react-icons/fi";
import { models } from "@/lib/studio-data";
import type { StudioState } from "@/hooks/useStudioState";
import { getObjectQuestionPlaceholder } from "@/utils/studio";

interface WorkspaceProps {
  mode: "console" | "history";
  state: StudioState;
}

export function Workspace({ mode, state }: WorkspaceProps) {
  return (
    <main className="workspace">
      <TopMetrics state={state} />
      <div className={mode === "history" ? "content-grid history-focus" : "content-grid"}>
        <ChatThread state={state} />
        <EvidencePanel state={state} />
      </div>
    </main>
  );
}

function TopMetrics({ state }: { state: StudioState }) {
  return (
    <header className="top-metrics">
      <div className="panel-toggle-group">
        <button onClick={() => state.setHistoryDrawerOpen(true)} type="button" title="打开对象会话">
          <FiChevronRight aria-hidden="true" />
        </button>
      </div>
      <div className="status-cluster">
        <div className="status-dot" />
        <div>
          <span>当前对象</span>
          <strong>{state.activeObject.name}</strong>
        </div>
      </div>
      <div className="metric">
        <span>领域</span>
        <strong>{state.activeObject.domain}</strong>
      </div>
      <div className="metric">
        <span>文档</span>
        <strong>{state.activeObject.documents}</strong>
      </div>
      <div className="metric">
        <span>Chunks</span>
        <strong>{state.activeObject.chunks}</strong>
      </div>
      <div className="metric">
        <span>索引更新</span>
        <strong>{state.activeObject.updatedAt}</strong>
      </div>
      <label className="model-picker">
        <FiCpu aria-hidden="true" />
        <select
          aria-label="选择模型"
          onChange={(event) => state.setSelectedModel(event.target.value)}
          value={state.selectedModel}
        >
          {models.map((model) => (
            <option key={model}>{model}</option>
          ))}
        </select>
        <FiChevronDown aria-hidden="true" />
      </label>
      <div className="panel-toggle-group evidence-toggle">
        <button onClick={() => state.setEvidenceDrawerOpen(true)} type="button" title="打开来源证据">
          <FiChevronLeft aria-hidden="true" />
        </button>
      </div>
    </header>
  );
}

function ChatThread({ state }: { state: StudioState }) {
  return (
    <section className="thread-surface" aria-label="对象对话">
      <div className="thread-scroll">
        <div className="thread-header">
          <div>
            <span>{state.activeObject.type}</span>
            <h2>{state.selectedChat.title}</h2>
          </div>
          <button
            className="secondary-action"
            disabled={state.indexRebuildState === "sending"}
            onClick={state.handleRebuildIndex}
            type="button"
          >
            <FiRefreshCw aria-hidden="true" />
            {state.indexRebuildState === "sending" ? "重建中" : "重建 Chroma 索引"}
          </button>
        </div>

        <div className="object-summary">
          <div>
            <strong>{state.activeObject.name}</strong>
            <p>{state.activeObject.description}</p>
          </div>
          <div className="kb-chips">
            {state.activeObject.knowledgeBases.map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </div>

        <div className="message user-message">
          <div className="message-meta">你 · {state.selectedChat.time}</div>
          <p>{state.lastQuestion}</p>
        </div>

        <article className="answer-block">
          <div className="answer-header">
            <div>
              <span>{state.activeObject.name}</span>
              <strong>{state.answerText ? "真实 RAG 回答" : "Pending"}</strong>
            </div>
            <div className={`api-pill ${state.apiState}`}>
              <FiCheckCircle aria-hidden="true" />
              {state.apiState === "sending" ? "请求中" : state.apiState === "offline" ? "API 未连接" : "Ready"}
            </div>
          </div>

          {state.answerText ? (
            <p>{state.answerText}</p>
          ) : (
            <div className="manifest-empty">
              {state.apiState === "sending"
                ? "回答生成中，等待后端 RAG API 返回。"
                : state.apiState === "offline"
                  ? "问答 API 未连接或请求失败，当前不显示本地 demo 回答。"
                  : "尚未请求真实 RAG 回答，提交问题后这里会显示 API 返回内容。"}
            </div>
          )}

          <footer className="answer-actions">
            <button
              className={state.feedback === "up" ? "is-selected" : ""}
              onClick={() => state.setFeedback("up")}
              type="button"
              title="有帮助"
            >
              <FiThumbsUp aria-hidden="true" />
            </button>
            <button
              className={state.feedback === "down" ? "is-selected" : ""}
              onClick={() => state.setFeedback("down")}
              type="button"
              title="需要改进"
            >
              <FiThumbsDown aria-hidden="true" />
            </button>
            <button type="button" title="复制回答">
              <FiCopy aria-hidden="true" />
            </button>
          </footer>
        </article>
      </div>

      <form className="composer" onSubmit={state.handleSubmit}>
        <input
          aria-label="继续提问"
          onChange={(event) => state.setDraft(event.target.value)}
          placeholder={getObjectQuestionPlaceholder(state.activeObject.name)}
          value={state.draft}
        />
        <button type="submit" title="发送">
          <FiSend aria-hidden="true" />
        </button>
      </form>
    </section>
  );
}

function EvidencePanel({ state }: { state: StudioState }) {
  return (
    <aside className={state.evidenceDrawerOpen ? "evidence-panel drawer-open" : "evidence-panel"} aria-label="来源证据">
      <div className="evidence-header">
        <div>
          <span>来源证据</span>
          <h2>{state.displayedSources.length} 条引用</h2>
        </div>
        <button onClick={() => state.setEvidenceDrawerOpen(false)} type="button" title="关闭来源证据">
          <FiSliders aria-hidden="true" />
        </button>
      </div>

      <div className="source-tabs" role="tablist" aria-label="来源排序">
        <button
          className={state.sourceTab === "relevance" ? "is-active" : ""}
          onClick={() => state.setSourceTab("relevance")}
          type="button"
        >
          相关度排序
        </button>
        <button
          className={state.sourceTab === "citation" ? "is-active" : ""}
          onClick={() => state.setSourceTab("citation")}
          type="button"
        >
          引用顺序
        </button>
      </div>

      <div className="source-list">
        {state.displayedSources.length > 0 ? (
          state.displayedSources.map((source) => (
            <button
              className={state.activeSource === source.id ? "source-card is-active" : "source-card"}
              key={source.id}
              onClick={() => state.setActiveSource(source.id)}
              type="button"
            >
              <div className="source-topline">
                <span className="rank-badge">{source.rank}</span>
                <strong>{source.title}</strong>
                <span>{source.score}</span>
              </div>
              <p>{source.quote}</p>
              <div className="source-meta">
                <span>
                  <FiFileText aria-hidden="true" />
                  {source.page}
                </span>
                {source.tags.map((tag) => (
                  <span key={tag}>{tag}</span>
                ))}
              </div>
            </button>
          ))
        ) : (
          <div className="manifest-empty">
            {state.apiState === "sending" ? "来源检索中。" : "暂无真实 API 来源，提交问题后显示 citations。"}
          </div>
        )}
      </div>

      <button className="wide-action" type="button">
        查看全部来源
      </button>
    </aside>
  );
}
