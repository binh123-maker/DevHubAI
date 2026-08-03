import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom"

import { AppLayout } from "@/components/layout/AppLayout"
import { AuthLayout } from "@/components/layout/AuthLayout"
import { ProtectedRoute, PublicOnlyRoute } from "@/components/routing/ProtectedRoute"
import ChatHistoryPage from "@/pages/ChatHistoryPage"
import DocumentViewerPage from "@/pages/DocumentViewerPage"
import ForgotPasswordPage from "@/pages/ForgotPasswordPage"
import LandingPage from "@/pages/LandingPage"
import LoginPage from "@/pages/LoginPage"
import OAuthCallbackPage from "@/pages/OAuthCallbackPage"
import ProfilePage from "@/pages/ProfilePage"
import RegisterPage from "@/pages/RegisterPage"
import SettingsPage from "@/pages/SettingsPage"
import WorkspaceDetailPage from "@/pages/WorkspaceDetailPage"
import WorkspaceListPage from "@/pages/WorkspaceListPage"

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<LandingPage />} />

        <Route path="/auth/callback/:provider" element={<OAuthCallbackPage />} />

        <Route element={<PublicOnlyRoute />}>
          <Route element={<AuthLayout />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          </Route>
        </Route>

        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route path="/workspaces" element={<WorkspaceListPage />} />
            <Route path="/workspaces/:id" element={<WorkspaceDetailPage />} />
            <Route path="/documents/:id" element={<DocumentViewerPage />} />
            <Route path="/history/:chatId?" element={<ChatHistoryPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Route>

        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  )
}
