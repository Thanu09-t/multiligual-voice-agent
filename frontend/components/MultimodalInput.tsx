"use client";

import React, { useState, KeyboardEvent } from "react";
import { Mic, MicOff, Send, Paperclip } from "lucide-react";
import { AgentStatusType } from "@/types/agent";

interface MultimodalInputProps {
  status: AgentStatusType;
  isRecording: boolean;
  onToggleRecording: () => void;
  onSendText: (text: string) => void;
  onAttachFile?: (file: File) => void;
}

export const MultimodalInput: React.FC<MultimodalInputProps> = ({
  status,
  isRecording,
  onToggleRecording,
  onSendText,
  onAttachFile,
}) => {
  const [text, setText] = useState("");

  const handleKeyDown = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (text.trim()) {
        onSendText(text.trim());
        setText("");
      }
    }
  };

  const handleSend = () => {
    if (text.trim()) {
      onSendText(text.trim());
      setText("");
    }
  };

  return (
    <div className="w-full max-w-2xl mx-auto px-4 py-3 flex items-center space-x-3 font-serif">
      {/* Voice Toggle Button */}
      <button
        onClick={onToggleRecording}
        className={`relative flex items-center justify-center w-11 h-11 rounded-xl transition-all duration-200 shadow-sm ${
          isRecording
            ? "bg-rose-600 hover:bg-rose-700 text-white animate-pulse"
            : status === "SPEAKING"
            ? "bg-emerald-700 hover:bg-emerald-800 text-white"
            : "bg-[#2B1810] hover:bg-[#45281C] text-[#F6F7F9]"
        }`}
        title={isRecording ? "Stop Listening" : "Start Voice"}
        aria-label={isRecording ? "Stop Listening" : "Start Voice"}
      >
        {isRecording ? (
          <MicOff className="w-4 h-4" />
        ) : (
          <Mic className="w-4 h-4" />
        )}
      </button>

      {/* Input bar */}
      <div className="flex-1 flex items-center bg-white border border-[#2B1810]/20 rounded-xl px-3.5 py-1.5 focus-within:border-[#2B1810]/60 shadow-xs transition-all">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Speak aloud or type an inquiry..."
          className="flex-1 bg-transparent text-xs sm:text-sm text-[#2B1810] placeholder-[#8C6552]/60 font-serif focus:outline-none"
        />

        <div className="flex items-center space-x-1 ml-2 text-[#8C6552]">
          <label
            className="p-1.5 rounded-lg hover:bg-[#2B1810]/5 hover:text-[#2B1810] cursor-pointer transition-colors"
            title="Attach document (PDF, TXT, DOCX)"
            aria-label="Attach document"
          >
            <Paperclip className="w-4 h-4" />
            <input
              type="file"
              accept=".pdf,.txt,.docx,.doc"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file && onAttachFile) onAttachFile(file);
              }}
            />
          </label>

          <button
            onClick={handleSend}
            disabled={!text.trim()}
            className={`p-1.5 rounded-lg transition-colors ${
              text.trim()
                ? "text-[#2B1810] hover:bg-[#2B1810]/10"
                : "text-[#8C6552]/30 cursor-not-allowed"
            }`}
            title="Send message"
            aria-label="Send message"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};
