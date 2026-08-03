import { apiFetch } from "./client";
import type {
  ChatListResponse,
  ChatResponse,
  DocumentListResponse,
  GenerateRequest,
  GenerateResponse,
  LoginRequest,
  NewChatResponse,
  RegisterRequest,
  StudyPlan,
  StudyPlanListResponse,
  TaskStatusResponse,
  TokenResponse,
  UploadResponse,
  User,
} from "./types";

export const authApi = {
  register: (data: RegisterRequest) =>
    apiFetch<User>("/v1/register", { method: "POST", body: JSON.stringify(data) }, false),

  login: (data: LoginRequest) =>
    apiFetch<TokenResponse>("/v1/login", { method: "POST", body: JSON.stringify(data) }, false),

  logout: (refreshToken: string) =>
    apiFetch<void>(
      "/v1/logout",
      { method: "POST", body: JSON.stringify({ refresh_token: refreshToken }) },
    ),

  me: () => apiFetch<User>("/v1/me"),
};

export const chatsApi = {
  list: () => apiFetch<ChatListResponse>("/v1/chats"),
  create: () => apiFetch<NewChatResponse>("/v1/chats", { method: "POST" }),
  get: (chatId: string) => apiFetch<ChatResponse>(`/v1/chats/${chatId}`),
};

export const documentsApi = {
  list: () => apiFetch<DocumentListResponse>("/v1/documents"),
  upload: (files: File[]) => {
    const form = new FormData();
    files.forEach((file) => form.append("files", file));
    return apiFetch<UploadResponse>("/v1/upload", { method: "POST", body: form });
  },
};

export const tasksApi = {
  get: (taskId: string) => apiFetch<TaskStatusResponse>(`/v1/tasks/${taskId}`),
};

export const generateApi = {
  create: (data: GenerateRequest) =>
    apiFetch<GenerateResponse>("/v1/generate", { method: "POST", body: JSON.stringify(data) }),
};

export const studyPlansApi = {
  list: () => apiFetch<StudyPlanListResponse>("/v1/study-plans"),
  get: (planId: string) => apiFetch<StudyPlan>(`/v1/study-plans/${planId}`),
};
