import { apiClient } from "./client";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export interface ChatConversation {
  id: string;
  title: string | null;
  session_id: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  messages: ChatMessage[];
}

export interface ChatMessageCreate {
  message: string;
  conversation_id?: string;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  session_id: string;
  metadata?: Record<string, any>;
}

/**
 * Send a chat message
 */
export async function sendChatMessage(
  data: ChatMessageCreate
): Promise<ChatResponse> {
  return apiClient.post<ChatResponse>("/chat/message", data);
}

/**
 * Get all conversations for the current user
 */
export async function getConversations(): Promise<ChatConversation[]> {
  return apiClient.get<ChatConversation[]>("/chat/conversations");
}

/**
 * Get a specific conversation with all messages
 */
export async function getConversation(
  conversationId: string
): Promise<ChatConversation> {
  return apiClient.get<ChatConversation>(
    `/chat/conversations/${conversationId}`
  );
}

/**
 * Delete a conversation
 */
export async function deleteConversation(
  conversationId: string
): Promise<void> {
  return apiClient.delete(`/chat/conversations/${conversationId}`);
}

