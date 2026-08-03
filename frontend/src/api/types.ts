export interface User {
  id: string;
  username: string;
  email: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface Document {
  id: string;
  file_name: string;
  status: string;
  chunk_count: number | null;
  error_message: string | null;
  index_name: string;
  uploaded_at: string;
}

export interface DocumentListResponse {
  documents: Document[];
}

export interface UploadResponse {
  task_id: string;
  detail: string;
  files_uploaded: number;
  document_ids: string[];
  status: string;
}

export interface TaskStatusResponse {
  task_id: string;
  status: string;
  result: Record<string, unknown> | null;
  error: string | null;
}

export interface ChatSummary {
  chat_id: string;
  message_count: number;
  updated_at: string | null;
}

export interface ChatListResponse {
  chats: ChatSummary[];
}

export interface ChatResponse {
  chat_id: string;
  messages: Array<Record<string, unknown>>;
  updated_at: string | null;
}

export interface NewChatResponse {
  chat_id: string;
}

export interface GenerateRequest {
  query: string;
  chat_id: string;
}

export interface GenerateResponse {
  task_id: string;
  status: string;
  message: string;
}

export interface StudyPlan {
  id: string;
  topic: string;
  study_topics: string[];
  notes: Record<string, unknown> | null;
  test: Record<string, unknown> | null;
  created_at: string;
  updated_at: string;
}

export interface StudyPlanListResponse {
  plans: StudyPlan[];
}

export interface ApiError {
  detail: string;
  request_id?: string | null;
}
