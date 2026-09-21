"use client";

import React from "react";
import Link from "next/link";
import {
  Plus,
  MessageSquare,
  FileText,
  Brain,
  Wrench,
  Settings,
  ChevronLeft,
  ChevronRight,
  Shield,
  FileCode2,
  ExternalLink,
  Trash2,
} from "lucide-react";
import { ConversationItem } from "@/types/agent";

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
  conversations: ConversationItem[];
  activeConversationId: string | null;
  onSelectConversation: (id: string) => void;
  onDeleteConversation?: (id: string) => void;
  onNewConversation: () => void;
  onOpenDocuments: () => void;
  onOpenMemory: () => void;
  onOpenTools: () => void;
  onOpenSettings: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  isOpen,
  onToggle,
  conversations,
  activeConversationId,
  onSelectConversation,
  onDeleteConversation,
  onNewConversation,
  onOpenDocuments,
  onOpenMemory,
  onOpenTools,
  onOpenSettings,
}) => {
  return (
    <aside
      className={`fixed top-0 bottom-0 left-0 z-30 transition-all duration-300 flex flex-col bg-white/95 backdrop-blur-md border-r border-[#2B1810]/10 font-serif ${
        isOpen ? "w-64" : "w-16"
      }`}
    >
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-3.5 border-b border-[#2B1810]/10">
        {isOpen ? (
          <div className="flex items-center space-x-2.5">
            <img src="/nova-icon.svg" className="w-6 h-6 rounded-md" alt="NOVA" />
            <span className="font-serif font-bold tracking-wider text-sm text-[#2B1810]">
              NOVA
            </span>
          </div>
        ) : (
          <div className="mx-auto">
            <img src="/nova-icon.svg" className="w-6 h-6 rounded-md" alt="NOVA" />
          </div>
        )}

        <button
          onClick={onToggle}
          className="p-1 rounded-lg hover:bg-[#2B1810]/5 text-[#6B4E3D] hover:text-[#2B1810] transition-colors"
          title={isOpen ? "Collapse Sidebar" : "Expand Sidebar"}
          aria-label={isOpen ? "Collapse Sidebar" : "Expand Sidebar"}
        >
          {isOpen ? <ChevronLeft className="w-4 h-4" /> : <ChevronRight className="w-4 h-4" />}
        </button>
      </div>

      {/* New conversation button */}
      <div className="p-3">
        <button
          onClick={onNewConversation}
          className="w-full flex items-center justify-center space-x-2 p-2.5 rounded-xl bg-[#2B1810] hover:bg-[#45281C] text-[#F6F7F9] text-xs font-serif font-medium transition-all shadow-sm group"
          title="Start a new conversation"
        >
          <Plus className="w-4 h-4 text-[#F6F7F9] transition-transform group-hover:rotate-90" />
          {isOpen && <span>New Conversation</span>}
        </button>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1">
        {isOpen && (
          <div className="text-[10px] uppercase font-sans tracking-wider text-[#8C6552] px-2 py-1 font-semibold">
            Conversations
          </div>
        )}

        {conversations.length === 0 && isOpen && (
          <div className="text-xs text-[#8C6552]/70 px-2 py-3 text-center italic">
            No saved chats
          </div>
        )}

        {conversations.map((c) => (
          <div
            key={c.id}
            className={`group relative flex items-center w-full rounded-lg transition-colors ${
              activeConversationId === c.id
                ? "bg-[#2B1810]/10 text-[#2B1810] font-semibold border border-[#2B1810]/20"
                : "text-[#45281C] hover:bg-[#2B1810]/5 hover:text-[#2B1810]"
            }`}
          >
            <button
              onClick={() => onSelectConversation(c.id)}
              className="flex-1 flex items-center space-x-2.5 px-2.5 py-2 text-xs truncate text-left"
              title={c.title || "Untitled Chat"}
            >
              <MessageSquare className="w-3.5 h-3.5 shrink-0 opacity-70 text-[#8C6552]" />
              {isOpen && <span className="truncate">{c.title || "Untitled Chat"}</span>}
            </button>
            {isOpen && onDeleteConversation && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDeleteConversation(c.id);
                }}
                className="opacity-0 group-hover:opacity-100 p-1.5 mr-1 text-[#8C6552]/70 hover:text-rose-600 rounded transition-all"
                title="Delete chat"
                aria-label="Delete chat"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            )}
          </div>
        ))}
      </div>

      {/* Navigation Panels */}
      <div className="p-3 border-t border-[#2B1810]/10 space-y-1">
        <button
          onClick={onOpenDocuments}
          className="w-full flex items-center space-x-2.5 px-2.5 py-2 rounded-lg text-xs text-[#45281C] hover:bg-[#2B1810]/5 hover:text-[#2B1810] transition-colors"
          title="Open Documents (RAG)"
        >
          <FileText className="w-4 h-4 text-[#8C6552] shrink-0" />
          {isOpen && <span>Documents</span>}
        </button>

        <button
          onClick={onOpenMemory}
          className="w-full flex items-center space-x-2.5 px-2.5 py-2 rounded-lg text-xs text-[#45281C] hover:bg-[#2B1810]/5 hover:text-[#2B1810] transition-colors"
          title="Open Long-Term Memory"
        >
          <Brain className="w-4 h-4 text-[#8C6552] shrink-0" />
          {isOpen && <span>Memory</span>}
        </button>

        <button
          onClick={onOpenTools}
          className="w-full flex items-center space-x-2.5 px-2.5 py-2 rounded-lg text-xs text-[#45281C] hover:bg-[#2B1810]/5 hover:text-[#2B1810] transition-colors"
          title="Open Agent Tool Registry"
        >
          <Wrench className="w-4 h-4 text-[#8C6552] shrink-0" />
          {isOpen && <span>Tools Registry</span>}
        </button>

        <button
          onClick={onOpenSettings}
          className="w-full flex items-center space-x-2.5 px-2.5 py-2 rounded-lg text-xs text-[#45281C] hover:bg-[#2B1810]/5 hover:text-[#2B1810] transition-colors"
          title="System Settings"
        >
          <Settings className="w-4 h-4 text-[#8C6552] shrink-0" />
          {isOpen && <span>Settings</span>}
        </button>
      </div>

      {/* Legal & Repo Links */}
      {isOpen && (
        <div className="px-4 py-3 border-t border-[#2B1810]/10 flex flex-col space-y-2 text-[11px] text-[#6B4E3D]">
          <div className="flex items-center justify-between">
            <Link
              href="/privacy-policy"
              className="hover:text-[#2B1810] flex items-center space-x-1 transition-colors"
            >
              <Shield className="w-3 h-3 text-[#8C6552]" />
              <span>Privacy</span>
            </Link>
            <Link
              href="/terms-and-conditions"
              className="hover:text-[#2B1810] flex items-center space-x-1 transition-colors"
            >
              <FileCode2 className="w-3 h-3 text-[#8C6552]" />
              <span>Terms</span>
            </Link>
          </div>
          <a
            href="https://github.com/Thanu09-t/multiligual-voice-agent"
            target="_blank"
            rel="noopener noreferrer"
            className="hover:text-[#2B1810] flex items-center space-x-1 transition-colors pt-1 border-t border-[#2B1810]/10 text-[10px] font-sans"
          >
            <span>GitHub Repository</span>
            <ExternalLink className="w-2.5 h-2.5" />
          </a>
        </div>
      )}
    </aside>
  );
};
