"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { VoiceOrb } from "@/components/VoiceOrb";
import { WaveformVisualizer } from "@/components/WaveformVisualizer";
import { TranscriptView } from "@/components/TranscriptView";
import { Sidebar } from "@/components/Sidebar";
import { MultimodalInput } from "@/components/MultimodalInput";
import { MemoryDrawer } from "@/components/MemoryDrawer";
import { DocumentPanel } from "@/components/DocumentPanel";
import { SettingsModal } from "@/components/SettingsModal";
import { ToolsModal } from "@/components/ToolsModal";
import { MessageItem, ConversationItem } from "@/types/agent";
import { useVoiceAgent } from "@/hooks/useVoiceAgent";
import { API_BASE_URL, WS_BASE_URL } from "@/lib/config";
import { Shield, FileCode2, Globe } from "lucide-react";

export default function NovaHome() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [memoryDrawerOpen, setMemoryDrawerOpen] = useState(false);
  const [documentPanelOpen, setDocumentPanelOpen] = useState(false);
  const [settingsModalOpen, setSettingsModalOpen] = useState(false);
  const [toolsModalOpen, setToolsModalOpen] = useState(false);
  const [conversations, setConversations] = useState<ConversationItem[]>([]);
  const [activeConversationId, setActiveConversationId] = useState<string | null>(null);
  const [messages, setMessages] = useState<MessageItem[]>([]);

  // Load and select conversation messages
  const handleSelectConversation = async (id: string) => {
    setActiveConversationId(id);
    try {
      const res = await fetch(`${API_BASE_URL}/api/conversations/${id}`);
      if (res.ok) {
        const data = await res.json();
        if (data && Array.isArray(data.messages)) {
          const loaded: MessageItem[] = data.messages.map((m: any) => ({
            id: m.id,
            sender: m.sender,
            content: m.content,
            spokenContent: m.spoken_content,
            createdAt: m.created_at,
          }));
          setMessages(loaded);
        }
      }
    } catch (err) {
      console.error("Failed to load conversation messages:", err);
    }
  };

  const refreshConversations = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/conversations`);
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) setConversations(data);
      }
    } catch (err) {}
  };

  const handleDeleteConversation = async (id: string) => {
    try {
      await fetch(`${API_BASE_URL}/api/conversations/${id}`, { method: "DELETE" });
      setConversations((prev) => prev.filter((c) => c.id !== id));
      if (activeConversationId === id) {
        handleNewConversation();
      }
    } catch (err) {
      console.error("Failed to delete conversation:", err);
    }
  };

  // Wire in real-time WebSocket voice agent with client VAD, instant barge-in, and multilingual TTS
  const {
    status,
    audioLevel,
    isListening,
    analyserNode,
    startListening,
    stopListening,
    sendTextMessage,
  } = useVoiceAgent({
    serverUrl: `${WS_BASE_URL}/api/voice`,
    conversationId: activeConversationId,
    userId: "user-default",
    onMessageReceived: (message) => {
      setMessages((prev) => [...prev, message]);
    },
    onConversationUpdate: (newConvId) => {
      if (newConvId && newConvId !== activeConversationId) {
        setActiveConversationId(newConvId);
      }
      refreshConversations();
    },
  });

  // Load conversation history on initial mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/conversations`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) {
          setConversations(data);
        }
      })
      .catch(() => {});
  }, []);

  const toggleRecording = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  const handleNewConversation = () => {
    setActiveConversationId(null);
    setMessages([]);
  };

  const handleAttachFile = async (file: File) => {
    setDocumentPanelOpen(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", "user-default");
    try {
      await fetch(`${API_BASE_URL}/api/documents/upload`, {
        method: "POST",
        body: formData,
      });
    } catch (err) {
      console.error("Upload error:", err);
    }
  };

  return (
    <div className="flex h-screen bg-[#F6F7F9] text-[#2B1810] font-serif overflow-hidden select-none">
      {/* Sidebar */}
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        conversations={conversations}
        activeConversationId={activeConversationId}
        onSelectConversation={handleSelectConversation}
        onDeleteConversation={handleDeleteConversation}
        onNewConversation={handleNewConversation}
        onOpenDocuments={() => setDocumentPanelOpen(true)}
        onOpenMemory={() => setMemoryDrawerOpen(true)}
        onOpenTools={() => setToolsModalOpen(true)}
        onOpenSettings={() => setSettingsModalOpen(true)}
      />

      {/* Long-Term Memory Drawer */}
      <MemoryDrawer
        isOpen={memoryDrawerOpen}
        onClose={() => setMemoryDrawerOpen(false)}
        userId="user-default"
      />

      {/* Knowledge Documents Panel */}
      <DocumentPanel
        isOpen={documentPanelOpen}
        onClose={() => setDocumentPanelOpen(false)}
        userId="user-default"
      />

      {/* System Settings Modal */}
      <SettingsModal
        isOpen={settingsModalOpen}
        onClose={() => setSettingsModalOpen(false)}
        userId="user-default"
        onClearHistory={handleNewConversation}
      />

      {/* Agent Tools Registry Modal */}
      <ToolsModal
        isOpen={toolsModalOpen}
        onClose={() => setToolsModalOpen(false)}
      />

      {/* Main Operating Surface */}
      <main
        className={`flex-1 flex flex-col transition-all duration-300 ${
          sidebarOpen ? "ml-64" : "ml-16"
        }`}
      >
        {/* Top bar */}
        <header className="h-16 flex items-center justify-between px-6 border-b border-[#2B1810]/10 bg-white/80 backdrop-blur-md">
          <div className="flex items-center space-x-3">
            <h1 className="font-serif font-bold tracking-widest text-base text-[#2B1810]">
              NOVA
            </h1>
            <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-[#2B1810]/5 text-[#45281C] border border-[#2B1810]/15 font-sans font-medium tracking-wide flex items-center gap-1.5">
              <Globe className="w-3 h-3 text-[#8C6552]" />
              Multilingual Voice Engine
            </span>
          </div>

          <div className="flex items-center space-x-4">
            {/* Quick legal links */}
            <div className="hidden sm:flex items-center space-x-4 text-xs text-[#6B4E3D]">
              <Link
                href="/privacy-policy"
                className="hover:text-[#2B1810] flex items-center space-x-1.5 transition-colors"
              >
                <Shield className="w-3.5 h-3.5 text-[#8C6552]" />
                <span>Privacy Policy</span>
              </Link>
              <Link
                href="/terms-and-conditions"
                className="hover:text-[#2B1810] flex items-center space-x-1.5 transition-colors"
              >
                <FileCode2 className="w-3.5 h-3.5 text-[#8C6552]" />
                <span>Terms</span>
              </Link>
            </div>

            {/* Status indicator */}
            <div className="flex items-center space-x-2 text-xs font-sans text-[#6B4E3D] pl-4 sm:border-l sm:border-[#2B1810]/15">
              <div
                className={`w-2 h-2 rounded-full ${
                  status === "IDLE"
                    ? "bg-emerald-600"
                    : status === "LISTENING"
                    ? "bg-amber-600 animate-ping"
                    : status === "SPEAKING"
                    ? "bg-emerald-600 animate-pulse"
                    : status === "INTERRUPTED"
                    ? "bg-amber-600"
                    : status === "THINKING" || status === "USING_TOOL"
                    ? "bg-amber-600 animate-pulse"
                    : "bg-rose-600"
                }`}
              />
              <span className="capitalize font-medium">{status.toLowerCase()}</span>
            </div>
          </div>
        </header>

        {/* Core Stage */}
        <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
          {/* Left / Center: Voice Core Orb */}
          <div className="flex-1 flex flex-col items-center justify-center p-6 border-b md:border-b-0 md:border-r border-[#2B1810]/10 relative bg-[#F6F7F9]">
            <VoiceOrb
              status={status}
              audioLevel={audioLevel}
              onClick={toggleRecording}
            />

            <div className="mt-5 text-center">
              <h2 className="text-lg sm:text-xl font-serif font-semibold text-[#2B1810]">
                {status === "IDLE" && "How can I assist you today?"}
                {status === "LISTENING" && "Listening attentively..."}
                {status === "THINKING" && "Reasoning..."}
                {status === "GENERATING" && "Synthesizing answer..."}
                {status === "SPEAKING" && "Speaking..."}
                {status === "INTERRUPTED" && "Interrupted — listening..."}
                {status === "ERROR" && "Encountered an issue."}
              </h2>
              <p className="text-xs text-[#6B4E3D] mt-1.5 font-sans">
                {isListening
                  ? "Voice activity active — speak naturally or click orb to stop"
                  : "Click orb or microphone below to talk"}
              </p>
            </div>

            {/* Live Web Audio Waveform */}
            <div className="mt-6 w-full max-w-xs">
              <WaveformVisualizer
                analyserNode={analyserNode}
                isActive={isListening || status === "SPEAKING"}
              />
            </div>
          </div>

          {/* Right: Conversation Transcript */}
          <div className="flex-1 flex flex-col bg-white overflow-hidden">
            <TranscriptView messages={messages} />
            <div className="border-t border-[#2B1810]/10 bg-[#F6F7F9]/80 backdrop-blur-sm">
              <MultimodalInput
                status={status}
                isRecording={isListening}
                onToggleRecording={toggleRecording}
                onSendText={sendTextMessage}
                onAttachFile={handleAttachFile}
              />
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
