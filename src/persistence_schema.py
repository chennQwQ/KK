"""Persistence schema planning contract.

This module is an inventory for future PostgreSQL/SQLite migrations,
not an executable migration or live database schema.
"""

TABLES: dict[str, tuple[str, ...]] = {
    "users": ("id", "email", "display_name", "created_at"),
    "knowledge_bases": ("id", "owner_id", "name", "visibility", "created_at"),
    "documents": ("id", "knowledge_base_id", "source_type", "file_name", "checksum", "status", "created_at"),
    "ingestion_manifests": ("id", "document_id", "parser_version", "chunk_size", "chunk_overlap", "embedding_model", "created_at"),
    "chat_categories": ("id", "user_id", "name", "parent_id", "sort_order"),
    "chat_tags": ("id", "user_id", "name"),
    "chat_tag_links": ("chat_id", "tag_id"),
    "virtual_agents": ("id", "owner_id", "name", "system_prompt", "style_prompt", "retrieval_policy_id", "memory_policy_id", "is_public", "created_at"),
    "chats": ("id", "user_id", "agent_id", "knowledge_base_id", "category_id", "category_source", "title", "summary", "created_at", "updated_at"),
    "chat_participants": ("chat_id", "participant_type", "participant_id", "display_name"),
    "messages": ("id", "chat_id", "sender_type", "sender_id", "role", "content", "model_name", "token_usage", "created_at"),
    "citations": ("id", "message_id", "document_id", "page", "chunk_id", "source_preview"),
    "memory_items": ("id", "user_id", "agent_id", "chat_id", "knowledge_base_id", "scope", "content", "importance", "created_at"),
    "jobs": ("id", "user_id", "job_type", "status", "progress", "error_summary", "created_at", "updated_at"),
    "module_settings": ("id", "user_id", "knowledge_base_id", "module_name", "settings_json"),
}


def required_tables() -> set[str]:
    return set(TABLES)
