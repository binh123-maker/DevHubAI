import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"

import { AppLayout } from "@/components/layout/AppLayout"
import { AuthLayout } from "@/components/layout/AuthLayout"
import { ProtectedRoute, PublicOnlyRoute } from "@/components/routing/ProtectedRoute"
import ChatHistoryPage from "@/pages/ChatHistoryPage"
import DocumentViewerPage from "@/pages/DocumentViewerPage"
import LandingPage from "@/pages/LandingPage"
import LoginPage from "@/pages/LoginPage"
import ProfilePage from "@/pages/ProfilePage"
import RegisterPage from "@/pages/RegisterPage"
import WorkspaceDetailPage from "@/pages/WorkspaceDetailPage"
import WorkspaceListPage from "@/pages/WorkspaceListPage"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />

        <Route element={<PublicOnlyRoute />}>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/workspaces" element={<WorkspaceListPage />} />
            <Route path="/workspaces/:id" element={<WorkspaceDetailPage />} />
            <Route path="/documents/:id" element={<DocumentViewerPage />} />
            <Route path="/history/:chatId?" element={<ChatHistoryPage />} />
            <Route path="/profile" element={<ProfilePage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
