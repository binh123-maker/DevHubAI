import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { StrictMode } from "react"
import { createRoot } from "react-dom/client"

import App from "./App"
import { AuthProvider } from "./contexts/AuthContext"
import { ThemeProvider } from "./contexts/ThemeContext"
import { NavigationProvider } from "./contexts/NavigationContext"
import { GlobalSearchProvider } from "./contexts/GlobalSearchContext"
import "./index.css"

const queryClient = new QueryClient()

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <NavigationProvider>
          <GlobalSearchProvider>
            <AuthProvider>
              <App />
            </AuthProvider>
          </GlobalSearchProvider>
        </NavigationProvider>
      </ThemeProvider>
    </QueryClientProvider>
  </StrictMode>,
)
