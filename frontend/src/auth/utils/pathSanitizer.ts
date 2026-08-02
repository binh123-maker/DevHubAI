/**
 * Validates and sanitizes a post-login redirect path to prevent Open Redirect vulnerabilities.
 * Ensures the target path is a safe relative path starting with '/' and not '//' or external protocol.
 */
export function sanitizeRedirectPath(path: unknown, fallbackPath = "/workspaces"): string {
  if (typeof path !== "string" || !path) {
    return fallbackPath
  }

  // Trim whitespace
  const trimmed = path.trim()

  // Prevent protocol-relative URLs (e.g. //evil.com) and external URLs (e.g. https://evil.com)
  if (
    !trimmed.startsWith("/") ||
    trimmed.startsWith("//") ||
    trimmed.includes(":") ||
    trimmed.includes("\\")
  ) {
    return fallbackPath
  }

  return trimmed
}
