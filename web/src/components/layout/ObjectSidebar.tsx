"use client";

import { FiChevronLeft, FiFilter, FiSearch } from "react-icons/fi";
import type { StudioState } from "@/hooks/useStudioState";

interface ObjectSidebarProps {
  state: StudioState;
}

export function ObjectSidebar({ state }: ObjectSidebarProps) {
  return (
    <aside className={state.historyDrawerOpen ? "history-panel drawer-open" : "history-panel"}>
      <div className="panel-heading">
        <div>
          <span>Workspace</span>
          <h1>对象会话</h1>
        </div>
        <button type="button" title="收起对象栏" onClick={() => state.setHistoryDrawerOpen(false)}>
          <FiChevronLeft aria-hidden="true" />
        </button>
      </div>

      <div className="object-switcher" aria-label="对象列表">
        {state.objects.map((item) => (
          <button
            className={state.activeObjectId === item.id ? "object-card is-active" : "object-card"}
            key={item.id}
            onClick={() => state.selectObject(item.id)}
            type="button"
          >
            <span className="object-avatar">{item.icon}</span>
            <span>
              <strong>{item.name}</strong>
              <small>
                {item.type} · {item.status}
              </small>
            </span>
          </button>
        ))}
      </div>

      <div className="search-row">
        <FiSearch aria-hidden="true" />
        <input
          aria-label="搜索对象会话"
          onChange={(event) => state.setQuery(event.target.value)}
          placeholder="搜索对象、问题、知识库"
          value={state.query}
        />
        <button type="button" title="筛选">
          <FiFilter aria-hidden="true" />
        </button>
      </div>

      <div className="history-list">
        {state.filteredSections.map((section) => (
          <section key={section.label}>
            <h2>{section.label}</h2>
            {section.items.map((item) => (
              <button
                className={state.selectedChat.id === item.id ? "history-item is-active" : "history-item"}
                key={item.id}
                onClick={() => state.selectChat(item)}
                type="button"
              >
                <span className="history-title">{item.title}</span>
                <span className="history-summary">{item.summary}</span>
                {item.inheritsFrom && <span className="inherit-badge">继承上文</span>}
                <span className="history-time">{item.time}</span>
              </button>
            ))}
          </section>
        ))}
      </div>
    </aside>
  );
}
