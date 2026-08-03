import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { AuthProvider } from "@/auth/AuthContext";
import { AuthGuard, GuestGuard } from "@/auth/AuthGuard";
import { DashboardPage } from "@/pages/DashboardPage";
import { DocumentsPage } from "@/pages/DocumentsPage";
import { LoginPage } from "@/pages/LoginPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { StudyPlanDetailPage } from "@/pages/StudyPlanDetailPage";
import { StudyPlansPage } from "@/pages/StudyPlansPage";
import { WorkspacePage } from "@/pages/WorkspacePage";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 30_000,
      retry: 1,
    },
  },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route element={<GuestGuard />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
            </Route>

            <Route element={<AuthGuard />}>
              <Route path="/" element={<DashboardPage />} />
              <Route path="/documents" element={<DocumentsPage />} />
              <Route path="/workspace" element={<WorkspacePage />} />
              <Route path="/workspace/:chatId" element={<WorkspacePage />} />
              <Route path="/plans" element={<StudyPlansPage />} />
              <Route path="/plans/:planId" element={<StudyPlanDetailPage />} />
            </Route>

            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
