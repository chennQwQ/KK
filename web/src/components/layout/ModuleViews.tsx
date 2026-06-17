"use client";

import { FiRefreshCw, FiUploadCloud } from "react-icons/fi";
import type { StudioState } from "@/hooks/useStudioState";
import type { NavItem } from "@/types/studio";

export function NewObjectModule({ state }: { state: StudioState }) {
  return (
    <main className="module-canvas">
      <section className="module-hero">
        <span>Object Builder</span>
        <h1>新建对象</h1>
        <p>当前阶段只验证 KK 单对象完整流程。对象创建会在知识库、文档入库和持久化稳定后接入。</p>
      </section>

      <div className="builder-grid">
        <section className="builder-panel">
          <h2>当前真实对象</h2>
          <label>
            对象名称
            <input value={state.activeObject.name} readOnly />
          </label>
          <label>
            领域
            <input value={state.activeObject.domain} readOnly />
          </label>
          <label>
            说明
            <textarea value={state.activeObject.description} readOnly />
          </label>
        </section>

        <section className="builder-panel">
          <h2>知识库来源</h2>
          <div className="upload-shell">
            <FiUploadCloud aria-hidden="true" />
            <strong>上传入口开发中</strong>
            <span>当前先使用项目 data/ 目录中的 KK 文档完成整体流程测试。</span>
          </div>
          <div className="kb-chips large">
            {state.activeObject.knowledgeBases.map((item) => (
              <span key={item}>{item}</span>
            ))}
          </div>
        </section>
      </div>
    </main>
  );
}

export function KnowledgeBaseModule({ state }: { state: StudioState }) {
  const status = state.knowledgeBaseStatus;
  const documents = status?.document_count ?? state.activeObject.documents;
  const sourceFiles = status?.source_files ?? [];
  const isRegenerating = state.manifestState === "sending";
  const isRebuildingIndex = state.indexRebuildState === "sending";

  return (
    <main className="module-canvas">
      <section className="module-hero">
        <span>Knowledge Base</span>
        <h1>KK 本地知识库</h1>
        <p>当前只接入 data/ 目录中的 KK 文档，用它验证对象、知识库、索引状态和问答链路。</p>
      </section>

      <div className="kb-board">
        <section className="kb-row is-active">
          <div className="object-avatar">{state.activeObject.icon}</div>
          <div>
            <h2>{status?.knowledge_base_name ?? "KK 本地文档"}</h2>
            <p>{state.activeObject.description}</p>
            <div className="kb-chips">
              <span>状态: {status?.status ?? state.activeObject.status}</span>
              <span>Manifest: {status?.manifest_exists ? "已生成" : "未生成"}</span>
              <span>索引: {status?.index_exists ? "已存在" : "待重建"}</span>
              <span>Manifest 当前: {status?.manifest_current ? "是" : "否"}</span>
            </div>
            {sourceFiles.length > 0 && (
              <div className="kb-chips">
                {sourceFiles.map((file) => (
                  <span key={file}>{file}</span>
                ))}
              </div>
            )}
          </div>
          <strong>{documents} 文档</strong>
        </section>

        <section className="builder-panel">
          <div className="module-action-row">
            <div>
              <h2>Structured manifests</h2>
              <p>重新解析 data/ 中的 KK PDF，生成知识库入库和引用使用的结构化 manifest。</p>
            </div>
            <button
              className="secondary-action"
              disabled={isRegenerating}
              onClick={state.handleRegenerateManifests}
              type="button"
            >
              <FiRefreshCw aria-hidden="true" />
              {isRegenerating ? "解析中" : "重新解析文档"}
            </button>
          </div>

          <div className="manifest-list">
            {state.manifestItems.length > 0 ? (
              state.manifestItems.map((item) => (
                <div className="manifest-item" key={item.manifest_path}>
                  <div>
                    <strong>{item.source_file}</strong>
                    <span>{item.manifest_path}</span>
                  </div>
                  <div className="kb-chips">
                    <span>{item.source_type}</span>
                    <span>{item.parse_status}</span>
                    <span>{item.pages} pages</span>
                    <span>{item.items} items</span>
                    <span>{item.chapters} chapters</span>
                  </div>
                </div>
              ))
            ) : (
              <div className="manifest-empty">
                {state.manifestState === "offline" ? "Manifest 解析请求失败，请检查后端服务。" : "尚未执行本次解析。"}
              </div>
            )}
          </div>
        </section>

        <section className="builder-panel">
          <div className="module-action-row">
            <div>
              <h2>Chroma index</h2>
              <p>仅重建向量索引，不重新解析 PDF manifest。用于 structured manifest 已确认后刷新 RAG 检索库。</p>
            </div>
            <button
              className="secondary-action"
              disabled={isRebuildingIndex}
              onClick={state.handleRebuildIndex}
              type="button"
            >
              <FiRefreshCw aria-hidden="true" />
              {isRebuildingIndex ? "重建中" : "重建 Chroma 索引"}
            </button>
          </div>

          <div className="manifest-list">
            {state.indexRebuildResult ? (
              <div className="manifest-item">
                <div>
                  <strong>{state.indexRebuildResult.status}</strong>
                  <span>
                    chunks: {state.indexRebuildResult.chunks} · elapsed: {state.indexRebuildResult.elapsed_ms} ms
                  </span>
                </div>
                <div className="kb-chips">
                  <span>{state.indexRebuildState}</span>
                  {state.indexRebuildResult.error && <span>{state.indexRebuildResult.error}</span>}
                </div>
              </div>
            ) : (
              <div className="manifest-empty">尚未执行本次 Chroma 索引重建。</div>
            )}
          </div>
        </section>
      </div>
    </main>
  );
}

export function PlaceholderModule({ activeModule }: { activeModule: NavItem }) {
  const Icon = activeModule.icon;

  return (
    <main className="module-canvas placeholder-canvas">
      <section className="placeholder-panel">
        <div className="placeholder-icon">
          <Icon aria-hidden="true" />
        </div>
        <span>{activeModule.label}</span>
        <h1>{activeModule.emptyState}</h1>
        <p>该模块尚未接入真实数据。当前优先完成 KK 单对象、KK 本地知识库和问答链路。</p>
      </section>
    </main>
  );
}
