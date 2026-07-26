import { useEffect } from "react"

export function useKeyboardShortcut(
  targetKey: string,
  onTrigger: () => void,
  options: { ctrlKey?: boolean; metaKey?: boolean } = {}
) {
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      const isCtrlOrMeta = options.ctrlKey || options.metaKey
        ? (e.ctrlKey || e.metaKey)
        : true

      if (isCtrlOrMeta && e.key.toLowerCase() === targetKey.toLowerCase()) {
        e.preventDefault()
        onTrigger()
      }
    }

    window.addEventListener("keydown", handleKeyDown)
    return () => window.removeEventListener("keydown", handleKeyDown)
  }, [targetKey, onTrigger, options])
}
