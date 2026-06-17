"use client";

import { navItems } from "@/lib/studio-data";
import { useStudioState } from "@/hooks/useStudioState";
import { KnowledgeBaseModule, NewObjectModule, PlaceholderModule } from "@/components/layout/ModuleViews";
import { ObjectSidebar } from "@/components/layout/ObjectSidebar";
import { PrimaryRail } from "@/components/layout/PrimaryRail";
import { Workspace } from "@/components/layout/Workspace";

export function RagStudioShell() {
  const state = useStudioState();
  const activeModule = navItems.find((item) => item.id === state.activeNav) ?? navItems[0];

  return (
    <div className="app-shell">
      <PrimaryRail state={state} />
      {activeModule.status === "pending" ? (
        <PlaceholderModule activeModule={activeModule} />
      ) : (
        <ReadyModule activeNav={state.activeNav} state={state} />
      )}
    </div>
  );
}

function ReadyModule({ activeNav, state }: { activeNav: string; state: ReturnType<typeof useStudioState> }) {
  if (activeNav === "new") {
    return <NewObjectModule state={state} />;
  }

  if (activeNav === "kb") {
    return <KnowledgeBaseModule state={state} />;
  }

  return (
    <>
      <ObjectSidebar state={state} />
      <Workspace mode={activeNav === "history" ? "history" : "console"} state={state} />
    </>
  );
}
