import { Outlet, useLocation } from "react-router-dom"

import { Sidebar } from "./Sidebar"
import { AppHeader } from "./AppHeader"
import { MobileDrawer } from "./MobileDrawer"
import { GlobalSearchModal } from "./GlobalSearchModal"
import { BackToTop } from "./BackToTop"

export function AppLayout() {
  const location = useLocation()
  const isChatRoute = location.pathname.startsWith("/history")

  return (
    <div className="flex h-screen h-[100dvh] w-full overflow-hidden bg-background text-foreground antialiased">
      {/* Sticky Desktop Sidebar */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col min-w-0 h-full overflow-hidden">
        {/* Sticky Top Header */}
        <AppHeader />

        {/* Page View Body */}
        <main
          className={
            isChatRoute
              ? "flex-1 min-h-0 w-full p-0 overflow-hidden flex flex-col"
              : "flex-1 p-4 md:p-8 max-w-7xl w-full mx-auto overflow-y-auto"
          }
        >
          <Outlet />
        </main>
      </div>

      {/* Global Modals & Utilities */}
      <MobileDrawer />
      <GlobalSearchModal />
      {!isChatRoute && <BackToTop />}
    </div>
  )
}
