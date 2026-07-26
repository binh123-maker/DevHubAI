export interface SavedScopeMemory {
  chatMode: "global" | "workspace" | "folder" | "documents"
  workspaceId?: string
  folderId?: string
  modelId?: string
}

const SCOPE_MEMORY_KEY = "devhub-last-scope"

export function saveScopeMemory(memory: SavedScopeMemory) {
  try {
    localStorage.setItem(SCOPE_MEMORY_KEY, JSON.stringify(memory))
  } catch (e) {
    console.error("Failed to save scope memory:", e)
  }
}

export function loadScopeMemory(): SavedScopeMemory {
  try {
    const saved = localStorage.getItem(SCOPE_MEMORY_KEY)
    if (saved) {
      return JSON.parse(saved)
    }
  } catch (e) {
    console.error("Failed to load scope memory:", e)
  }
  return { chatMode: "global" }
}
