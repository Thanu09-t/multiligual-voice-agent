"use client";

import React, { useState } from "react";
import Link from "next/link";
import { X, Sliders, Volume2, Cpu, Trash2, Check, Shield, FileText, Globe } from "lucide-react";

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
  userId?: string;
  onClearHistory?: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({
  isOpen,
  onClose,
  userId = "user-default",
  onClearHistory,
}) => {
  const [selectedVoice, setSelectedVoice] = useState("en-US-JennyNeural");
  const [selectedLanguage, setSelectedLanguage] = useState(
    () => (typeof window !== "undefined" && localStorage.getItem("nova_pref_lang")) || "en"
  );
  const [speechSpeed, setSpeechSpeed] = useState("1.0");
  const [selectedModel, setSelectedModel] = useState("groq");
  const [memoryEnabled, setMemoryEnabled] = useState(true);
  const [saved, setSaved] = useState(false);
  const [clearedNotice, setClearedNotice] = useState(false);

  if (!isOpen) return null;

  const handleSave = () => {
    localStorage.setItem("nova_pref_voice", selectedVoice);
    localStorage.setItem("nova_pref_lang", selectedLanguage);
    localStorage.setItem("nova_pref_speed", speechSpeed);
    localStorage.setItem("nova_pref_model", selectedModel);
    localStorage.setItem("nova_pref_memory", memoryEnabled ? "1" : "0");
    setSaved(true);
    setTimeout(() => {
      setSaved(false);
      onClose();
    }, 600);
  };

  const handleClearCache = () => {
    if (confirm("Clear local conversation cache and session storage?")) {
      localStorage.removeItem("nova_token");
      localStorage.removeItem("nova_user");
      onClearHistory?.();
      setClearedNotice(true);
      setTimeout(() => setClearedNotice(false), 2000);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/40 backdrop-blur-sm animate-fade-in font-serif">
      <div className="w-full max-w-lg bg-white rounded-3xl border border-[#2B1810]/15 p-6 text-[#2B1810] shadow-2xl relative overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#2B1810]/10">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#2B1810]/8 border border-[#2B1810]/15 flex items-center justify-center text-[#2B1810]">
              <Sliders className="w-4 h-4 text-[#8C6552]" />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-[#2B1810]">NOVA System Settings</h3>
              <p className="text-[11px] text-[#6B4E3D]">Voice, Model, Speed & Privacy</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-[#2B1810]/5 text-[#6B4E3D] hover:text-[#2B1810] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="py-4 space-y-4 max-h-[60vh] overflow-y-auto pr-1">
          {/* Voice Model */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-[#45281C] flex items-center space-x-2">
              <Volume2 className="w-3.5 h-3.5 text-[#8C6552]" />
              <span>Voice Selection</span>
            </label>
            <select
              value={selectedVoice}
              onChange={(e) => setSelectedVoice(e.target.value)}
              className="w-full bg-[#F6F7F9] border border-[#2B1810]/15 rounded-xl px-3 py-2 text-xs text-[#2B1810] focus:outline-none focus:border-[#2B1810]/50"
            >
              <option value="en-US-JennyNeural">Jenny (Natural Conversational)</option>
              <option value="en-US-GuyNeural">Guy (Authoritative Assistant)</option>
              <option value="en-US-AriaNeural">Aria (Expressive Dynamic)</option>
              <option value="synthetic-sine">Synthetic Local PCM (Zero-latency fallback)</option>
            </select>
          </div>

          {/* Multilingual Support */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-[#45281C] flex items-center space-x-2">
              <Globe className="w-3.5 h-3.5 text-[#8C6552]" />
              <span>Preferred Communication Language</span>
            </label>
            <select
              value={selectedLanguage}
              onChange={(e) => setSelectedLanguage(e.target.value)}
              className="w-full bg-[#F6F7F9] border border-[#2B1810]/15 rounded-xl px-3 py-2 text-xs text-[#2B1810] focus:outline-none focus:border-[#2B1810]/50"
            >
              <option value="en">English (Default)</option>
              <option value="auto">Auto-Detect Any Spoken Language</option>
              <option value="es">Español (Spanish)</option>
              <option value="fr">Français (French)</option>
              <option value="de">Deutsch (German)</option>
              <option value="hi">हिन्दी (Hindi)</option>
              <option value="ja">日本語 (Japanese)</option>
              <option value="zh">中文 (Mandarin Chinese)</option>
              <option value="ar">العربية (Arabic)</option>
              <option value="pt">Português (Portuguese)</option>
              <option value="it">Italiano (Italian)</option>
              <option value="ru">Русский (Russian)</option>
            </select>
            <p className="text-[10px] text-[#8C6552]">
              NOVA speaks and reasons natively in any language. Auto-detect automatically matches your speech.
            </p>
          </div>

          {/* Speech Rate */}
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-xs text-[#45281C]">
              <span className="flex items-center space-x-2">
                <Sliders className="w-3.5 h-3.5 text-[#8C6552]" />
                <span>Speech Speed</span>
              </span>
              <span className="font-sans font-semibold text-[11px] text-[#2B1810]">{speechSpeed}x</span>
            </div>
            <input
              type="range"
              min="0.75"
              max="1.5"
              step="0.05"
              value={speechSpeed}
              onChange={(e) => setSpeechSpeed(e.target.value)}
              className="w-full accent-[#2B1810] cursor-pointer"
            />
          </div>

          {/* Reasoning Engine */}
          <div className="space-y-1.5">
            <label className="text-xs font-medium text-[#45281C] flex items-center space-x-2">
              <Cpu className="w-3.5 h-3.5 text-emerald-700" />
              <span>Reasoning Provider</span>
            </label>
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="w-full bg-[#F6F7F9] border border-[#2B1810]/15 rounded-xl px-3 py-2 text-xs text-[#2B1810] focus:outline-none focus:border-[#2B1810]/50"
            >
              <option value="groq">Groq (Llama-3.3-70B Low Latency)</option>
              <option value="gemini">Google Gemini (Gemini-2.5-Flash)</option>
              <option value="openai">OpenAI (GPT-4o-mini)</option>
              <option value="mock">Local Deterministic Engine (Offline)</option>
            </select>
          </div>

          {/* Memory Toggle */}
          <div className="flex items-center justify-between p-3 rounded-xl bg-[#F6F7F9] border border-[#2B1810]/10">
            <div>
              <div className="text-xs font-medium text-[#2B1810]">Enable Long-Term Memory</div>
              <div className="text-[10px] text-[#6B4E3D]">Persist user facts and conversational preferences</div>
            </div>
            <button
              onClick={() => setMemoryEnabled(!memoryEnabled)}
              className={`w-10 h-6 rounded-full transition-colors relative ${
                memoryEnabled ? "bg-[#2B1810]" : "bg-[#8C6552]/30"
              }`}
              aria-label="Toggle Long-Term Memory"
            >
              <div
                className={`w-4 h-4 rounded-full bg-white absolute top-1 transition-transform ${
                  memoryEnabled ? "left-5" : "left-1"
                }`}
              />
            </button>
          </div>

          {/* Data & Privacy Actions */}
          <div className="pt-2 border-t border-[#2B1810]/10 space-y-2">
            <div className="text-xs font-semibold text-[#8C6552] uppercase tracking-wider font-sans">
              Privacy & Storage
            </div>

            <button
              onClick={handleClearCache}
              className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-[#F6F7F9] hover:bg-rose-50 border border-[#2B1810]/10 hover:border-rose-300 text-xs text-[#45281C] transition-colors group"
            >
              <span>{clearedNotice ? "Cache Cleared" : "Clear Conversation & Session Cache"}</span>
              <Trash2 className="w-3.5 h-3.5 text-[#8C6552] group-hover:text-rose-600" />
            </button>

            <div className="flex items-center space-x-4 pt-2 text-xs text-[#6B4E3D]">
              <Link
                href="/privacy-policy"
                onClick={onClose}
                className="hover:text-[#2B1810] flex items-center space-x-1.5 transition-colors"
              >
                <Shield className="w-3.5 h-3.5 text-[#8C6552]" />
                <span>Privacy Policy</span>
              </Link>
              <Link
                href="/terms-and-conditions"
                onClick={onClose}
                className="hover:text-[#2B1810] flex items-center space-x-1.5 transition-colors"
              >
                <FileText className="w-3.5 h-3.5 text-[#8C6552]" />
                <span>Terms and Conditions</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex justify-end space-x-2 pt-4 border-t border-[#2B1810]/10">
          <button
            onClick={onClose}
            className="px-4 py-2 rounded-xl text-xs text-[#6B4E3D] hover:text-[#2B1810] transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleSave}
            className="flex items-center space-x-1.5 px-4 py-2 rounded-xl bg-[#2B1810] text-[#F6F7F9] text-xs font-semibold hover:bg-[#45281C] transition-colors shadow-sm"
          >
            {saved ? (
              <>
                <Check className="w-3.5 h-3.5" />
                <span>Saved</span>
              </>
            ) : (
              <span>Save Preferences</span>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
