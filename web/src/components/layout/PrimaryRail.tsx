"use client";

import { FiChevronLeft, FiChevronRight, FiLayers } from "react-icons/fi";
import { navItems, studioBrand } from "@/lib/studio-data";
import type { StudioState } from "@/hooks/useStudioState";

interface PrimaryRailProps {
  state: StudioState;
}

export function PrimaryRail({ state }: PrimaryRailProps) {
  return (
    <aside className={`primary-rail ${state.railCollapsed ? "is-collapsed" : ""}`}>
      <div className="brand-row">
        <div className="brand-mark">
          <FiLayers aria-hidden="true" />
        </div>
        {!state.railCollapsed && (
          <div>
            <strong>{studioBrand.name}</strong>
            <span>{studioBrand.subtitle}</span>
          </div>
        )}
      </div>

      <nav className="rail-nav" aria-label="主导航">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              className={state.activeNav === item.id ? "is-active" : ""}
              key={item.id}
              onClick={() => state.setActiveNav(item.id)}
              type="button"
              title={item.label}
            >
              <Icon aria-hidden="true" />
              {!state.railCollapsed && <span>{item.label}</span>}
            </button>
          );
        })}
      </nav>

      <div className="rail-footer">
        {!state.railCollapsed && (
          <div className="user-chip">
            <div className="avatar">R</div>
            <div>
              <strong>studio owner</strong>
              <span>对象构建者</span>
            </div>
          </div>
        )}
        <button
          className="collapse-button"
          onClick={() => state.setRailCollapsed((value) => !value)}
          type="button"
          title={state.railCollapsed ? "展开侧栏" : "收起侧栏"}
        >
          {state.railCollapsed ? <FiChevronRight aria-hidden="true" /> : <FiChevronLeft aria-hidden="true" />}
          {!state.railCollapsed && <span>收起</span>}
        </button>
      </div>
    </aside>
  );
}
