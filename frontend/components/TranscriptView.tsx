"use client";

import React, { useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { MessageItem } from "@/types/agent";
import { User, Bot, CheckCircle2, Loader2, AlertCircle, ExternalLink } from "lucide-react";

interface TranscriptViewProps {
  messages: MessageItem[];
}

/**
 * Lightweight inline markdown renderer.
 * Handles: **bold**, numbered lists, bullet lines (• or -), URL lines, plain text.
 */
function renderMarkdown(text: string): React.ReactNode {
  const lines = text.split("\n");
  const nodes: React.ReactNode[] = [];

  const renderInline = (line: string, key: number): React.ReactNode => {
    // Split on **bold** patterns
    const parts = line.split(/(\*\*[^*]+\*\*)/g);
    return (
      <span key={key}>
        {parts.map((part, i) => {
          if (part.startsWith("**") && part.endsWith("**")) {
            return <strong key={i} className="font-semibold text-[#2B1810]">{part.slice(2, -2)}</strong>;
          }
          return <span key={i}>{part}</span>;
        })}
      </span>
    );
  };

  lines.forEach((line, i) => {
    const trimmed = line.trim();
    if (!trimmed) {
      nodes.push(<div key={i} className="h-1" />);
      return;
    }

    // URL line (starts with • http or just http/https)
    if (/^[•·]\s*https?:\/\//i.test(trimmed) || /^https?:\/\//i.test(trimmed)) {
      const url = trimmed.replace(/^[•·]\s*/, "");
      nodes.push(
        <a
          key={i}
          href={url}
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-1 text-[11px] text-[#6B4E3D] hover:text-[#2B1810] underline underline-offset-2 break-all font-sans transition-colors"
        >
          <ExternalLink className="w-3 h-3 shrink-0" />
          <span className="truncate">{url}</span>
        </a>
      );
      return;
    }

    // Numbered list item: "1. ..."
    const numberedMatch = trimmed.match(/^(\d+)\.\s+(.*)$/);
    if (numberedMatch) {
      nodes.push(
        <div key={i} className="flex items-start gap-2 py-0.5">
          <span className="text-[11px] text-[#8C6552] font-bold font-sans mt-0.5 shrink-0">{numberedMatch[1]}.</span>
          <span className="text-sm leading-snug">{renderInline(numberedMatch[2], i)}</span>
        </div>
      );
      return;
    }

    // Bullet line: starts with • or -
    if (/^[•·\-]\s/.test(trimmed)) {
      nodes.push(
        <div key={i} className="flex items-start gap-2 py-0.5">
          <span className="text-[#8C6552] mt-1.5 shrink-0 text-[8px]">●</span>
          <span className="text-sm leading-snug">{renderInline(trimmed.replace(/^[•·\-]\s/, ""), i)}</span>
        </div>
      );
      return;
    }

    // Regular paragraph
    nodes.push(
      <p key={i} className="text-sm leading-relaxed py-0.5">{renderInline(trimmed, i)}</p>
    );
  });

  return <div className="space-y-0.5">{nodes}</div>;
}

export const TranscriptView: React.FC<TranscriptViewProps> = ({ messages }) => {
  const scrollEndRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    scrollEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-center p-8 text-[#8C6552] text-sm font-serif">
        <Bot className="w-8 h-8 mb-2 text-[#8C6552]/60" />
        <p>No messages yet. Speak aloud or type below to begin.</p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 max-w-3xl w-full mx-auto font-serif">
      <AnimatePresence initial={false}>
        {messages.map((m) => (
          <motion.div
            key={m.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className={`flex flex-col ${
              m.sender === "user" ? "items-end" : "items-start"
            }`}
          >
            {/* Tool chip if present */}
            {m.toolCall && (
              <div className="mb-1.5 flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-sans bg-[#F6F7F9] border border-[#2B1810]/15 text-[#45281C]">
                {m.toolCall.status === "running" ? (
                  <>
                    <Loader2 className="w-3 h-3 text-amber-600 animate-spin" />
                    <span>Executing {m.toolCall.tool}...</span>
                  </>
                ) : m.toolCall.status === "completed" ? (
                  <>
                    <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                    <span>Tool {m.toolCall.tool} completed</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-3 h-3 text-rose-600" />
                    <span>Tool {m.toolCall.tool} failed</span>
                  </>
                )}
              </div>
            )}

            <div className="flex items-start space-x-2.5 max-w-[85%]">
              {m.sender !== "user" && (
                <div className="w-7 h-7 rounded-lg bg-[#2B1810]/8 border border-[#2B1810]/15 flex items-center justify-center text-[#2B1810] shrink-0 mt-0.5 shadow-xs">
                  <Bot className="w-4 h-4" />
                </div>
              )}

              <div
                className={`p-4 rounded-2xl text-sm leading-relaxed ${
                  m.sender === "user"
                    ? "bg-[#2B1810]/8 text-[#2B1810] border border-[#2B1810]/15 rounded-tr-sm"
                    : "bg-white text-[#2B1810] border border-[#2B1810]/10 shadow-sm rounded-tl-sm"
                }`}
              >
                <div className="font-serif">
                  {m.sender === "agent"
                    ? renderMarkdown(m.content)
                    : <span className="whitespace-pre-wrap">{m.content}</span>
                  }
                </div>
                <div className="mt-1 text-[10px] text-[#8C6552] text-right font-sans">
                  {new Date(m.createdAt).toLocaleTimeString([], {
                    hour: "2-digit",
                    minute: "2-digit",
                  })}
                </div>
              </div>


              {m.sender === "user" && (
                <div className="w-7 h-7 rounded-lg bg-[#2B1810] text-[#F6F7F9] flex items-center justify-center shrink-0 mt-0.5 border border-[#2B1810] shadow-xs">
                  <User className="w-3.5 h-3.5" />
                </div>
              )}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
      <div ref={scrollEndRef} />
    </div>
  );
};
