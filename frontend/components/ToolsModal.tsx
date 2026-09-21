"use client";

import React from "react";
import { X, Wrench, Calculator, CloudSun, Globe, FileSearch, CheckCircle2 } from "lucide-react";

interface ToolsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const ToolsModal: React.FC<ToolsModalProps> = ({ isOpen, onClose }) => {
  if (!isOpen) return null;

  const tools = [
    {
      name: "Calculator",
      description: "Safe AST mathematical expression evaluation for exact arithmetic and multi-step math.",
      icon: Calculator,
      status: "Active",
      invocation: "Automatic on numeric calculation queries",
    },
    {
      name: "Weather",
      description: "Retrieves current meteorological conditions, temperatures, and forecasts.",
      icon: CloudSun,
      status: "Active",
      invocation: "Automatic on city weather questions",
    },
    {
      name: "Web Search",
      description:
        "Multi-provider real-time web search (DuckDuckGo · Tavily · Serper). Retrieves current news, facts, biographies, prices, and any live information beyond model training.",
      icon: Globe,
      status: "Active",
      invocation: 'Triggered by: "who is…", "what is…", "latest news on…", "search for…", "tell me about…"',
    },
    {
      name: "Knowledge RAG Search",
      description: "Semantic vector similarity retrieval across user-uploaded PDF, TXT, and DOCX files.",
      icon: FileSearch,
      status: "Active",
      invocation: "Automatic when relevant documents are indexed",
    },
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-fade-in font-serif">
      <div className="w-full max-w-lg bg-white rounded-3xl border border-[#2B1810]/15 p-6 text-[#2B1810] shadow-2xl relative overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#2B1810]/10">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#2B1810]/8 border border-[#2B1810]/15 flex items-center justify-center text-[#2B1810]">
              <Wrench className="w-4 h-4 text-[#8C6552]" />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-[#2B1810]">Agent Tool Registry</h3>
              <p className="text-[11px] text-[#6B4E3D]">Registered multi-step execution tools</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-[#2B1810]/5 text-[#6B4E3D] hover:text-[#2B1810] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Tools list */}
        <div className="py-4 space-y-3 max-h-[60vh] overflow-y-auto pr-1">
          {tools.map((tool) => {
            const Icon = tool.icon;
            return (
              <div
                key={tool.name}
                className="p-3.5 rounded-2xl bg-[#F6F7F9] border border-[#2B1810]/10 hover:border-[#2B1810]/20 transition-all space-y-1.5"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <div className="w-6 h-6 rounded-lg bg-white flex items-center justify-center text-[#8C6552] shadow-xs">
                      <Icon className="w-3.5 h-3.5" />
                    </div>
                    <span className="text-xs font-semibold text-[#2B1810]">{tool.name}</span>
                  </div>

                  <span className="inline-flex items-center space-x-1 px-2.5 py-0.5 rounded-full text-[10px] font-sans bg-emerald-100/80 border border-emerald-300 text-emerald-800 font-medium">
                    <CheckCircle2 className="w-2.5 h-2.5" />
                    <span>{tool.status}</span>
                  </span>
                </div>

                <p className="text-xs text-[#45281C] pl-8 leading-relaxed font-serif">
                  {tool.description}
                </p>

                <div className="text-[10px] text-[#8C6552] pl-8 font-sans">
                  {tool.invocation}
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className="flex justify-end pt-3 border-t border-[#2B1810]/10">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs font-medium bg-[#2B1810] hover:bg-[#45281C] text-[#F6F7F9] transition-colors shadow-sm"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
