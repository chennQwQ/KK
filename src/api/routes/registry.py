API_ROUTES = {
    "health": ("GET", "/health"),
    "objects": ("GET", "/objects"),
    "knowledge_base_status": ("GET", "/knowledge-base/status"),
    "knowledge_base_manifest_regenerate": ("POST", "/knowledge-base/manifests/regenerate"),
    "knowledge_base_index_rebuild": ("POST", "/knowledge-base/index/rebuild"),
    "chat": ("POST", "/chat"),
}
