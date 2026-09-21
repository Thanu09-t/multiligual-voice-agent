export type AgentStatusType =
  | "IDLE"
  | "LISTENING"
  | "THINKING"
  | "USING_TOOL"
  | "GENERATING"
  | "SPEAKING"
  | "INTERRUPTED"
  | "ERROR";

export interface MessageItem {
  id: string;
  sender: "user" | "agent" | "system";
  content: string;
  spokenContent?: string;
  toolCall?: {
    tool: string;
    status: "running" | "completed" | "failed";
    message?: string;
  };
  createdAt: string;
}

export interface ConversationItem {
  id: string;
  title: string;
  updatedAt: string;
}
