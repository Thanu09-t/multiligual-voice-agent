"use client";

import React, { useState, useEffect } from "react";
import { X, Trash2, Brain, Plus, Check } from "lucide-react";
import { API_BASE_URL } from "@/lib/config";

interface MemoryItem {
  id: string;
  category: string;
  key: string;
  value: string;
  updated_at: string;
}

interface MemoryDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  userId?: string;
}

export const MemoryDrawer: React.FC<MemoryDrawerProps> = ({
  isOpen,
  onClose,
  userId = "user-default",
}) => {
  const [memories, setMemories] = useState<MemoryItem[]>([]);
  const [newKey, setNewKey] = useState("");
  const [newValue, setNewValue] = useState("");
  const [newCategory, setNewCategory] = useState("preference");
  const [isAdding, setIsAdding] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchMemories = () => {
    setLoading(true);
    fetch(`${API_BASE_URL}/api/memory?user_id=${userId}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) setMemories(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    if (isOpen) {
      fetchMemories();
    }
  }, [isOpen, userId]);

  const handleAddMemory = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKey.trim() || !newValue.trim()) return;

    try {
      const res = await fetch(`${API_BASE_URL}/api/memory`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          user_id: userId,
          category: newCategory,
          key: newKey.trim(),
          value: newValue.trim(),
        }),
      });
      if (res.ok) {
        setNewKey("");
        setNewValue("");
        setIsAdding(false);
        fetchMemories();
      }
    } catch (err) {
      console.error("Failed to add memory:", err);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await fetch(`${API_BASE_URL}/api/memory/${id}?user_id=${userId}`, {
        method: "DELETE",
      });
      setMemories((prev) => prev.filter((m) => m.id !== id));
    } catch (err) {
      console.error("Failed to delete memory:", err);
    }
  };

  const handleClearAll = async () => {
    if (confirm("Are you sure you want to clear all permanent memories?")) {
      try {
        await fetch(`${API_BASE_URL}/api/memory?user_id=${userId}`, {
          method: "DELETE",
        });
        setMemories([]);
      } catch (err) {
        console.error("Failed to clear memories:", err);
      }
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm animate-fade-in font-serif">
      <div className="w-full max-w-md h-full bg-white border-l border-[#2B1810]/15 flex flex-col p-6 text-[#2B1810] shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#2B1810]/10">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-emerald-100/80 border border-emerald-300 flex items-center justify-center text-emerald-800">
              <Brain className="w-4 h-4" />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-[#2B1810]">Long-Term Memory</h3>
              <p className="text-[11px] text-[#6B4E3D]">User facts, preferences & project info</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-[#2B1810]/5 text-[#6B4E3D] hover:text-[#2B1810] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Action bar */}
        <div className="flex items-center justify-between py-4">
          <button
            onClick={() => setIsAdding(!isAdding)}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-[#2B1810] text-[#F6F7F9] text-xs font-medium hover:bg-[#45281C] transition-colors shadow-sm"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Memory</span>
          </button>

          {memories.length > 0 && (
            <button
              onClick={handleClearAll}
              className="text-xs text-rose-700 hover:text-rose-800 hover:underline transition-colors"
            >
              Clear All
            </button>
          )}
        </div>

        {/* Add form */}
        {isAdding && (
          <form
            onSubmit={handleAddMemory}
            className="mb-4 p-3.5 rounded-xl bg-[#F6F7F9] border border-[#2B1810]/15 space-y-2.5"
          >
            <div className="flex space-x-2">
              <select
                value={newCategory}
                onChange={(e) => setNewCategory(e.target.value)}
                className="bg-white border border-[#2B1810]/15 rounded-lg px-2 py-1.5 text-xs text-[#2B1810] focus:outline-none"
              >
                <option value="preference">Preference</option>
                <option value="project">Project</option>
                <option value="fact">Fact</option>
                <option value="persona">Persona</option>
              </select>

              <input
                type="text"
                placeholder="Key (e.g. project_name)"
                value={newKey}
                onChange={(e) => setNewKey(e.target.value)}
                className="flex-1 bg-white border border-[#2B1810]/15 rounded-lg px-2.5 py-1.5 text-xs text-[#2B1810] placeholder-[#8C6552]/60 focus:outline-none"
              />
            </div>

            <textarea
              placeholder="Value (e.g. Real-time voice agent platform)"
              value={newValue}
              onChange={(e) => setNewValue(e.target.value)}
              className="w-full bg-white border border-[#2B1810]/15 rounded-lg p-2.5 text-xs text-[#2B1810] placeholder-[#8C6552]/60 focus:outline-none h-16 resize-none"
            />

            <div className="flex justify-end space-x-2">
              <button
                type="button"
                onClick={() => setIsAdding(false)}
                className="px-2.5 py-1 rounded-lg text-xs text-[#6B4E3D] hover:text-[#2B1810]"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-3 py-1 rounded-lg bg-[#2B1810] text-[#F6F7F9] text-xs font-semibold hover:bg-[#45281C]"
              >
                Save
              </button>
            </div>
          </form>
        )}

        {/* Memory list */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {loading ? (
            <div className="text-center py-8 text-xs text-[#8C6552]">Loading memories...</div>
          ) : memories.length === 0 ? (
            <div className="text-center py-12 text-xs text-[#8C6552]">
              <Brain className="w-6 h-6 mx-auto mb-2 opacity-40 text-emerald-800" />
              No memories saved yet. State a fact in conversation or click &apos;Add Memory&apos;.
            </div>
          ) : (
            memories.map((m) => (
              <div
                key={m.id}
                className="group p-3 rounded-xl bg-[#F6F7F9] hover:bg-[#EFECE8] border border-[#2B1810]/10 hover:border-[#2B1810]/20 transition-all flex items-start justify-between"
              >
                <div className="space-y-1">
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] uppercase font-sans px-2 py-0.5 rounded-full bg-white border border-[#2B1810]/15 text-[#45281C] font-semibold">
                      {m.category}
                    </span>
                    <span className="font-sans text-xs text-[#2B1810] font-semibold">{m.key}</span>
                  </div>
                  <p className="text-xs text-[#45281C] pl-0.5 font-serif">{m.value}</p>
                </div>

                <button
                  onClick={() => handleDelete(m.id)}
                  className="p-1 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-rose-100 text-rose-600 transition-all"
                  title="Delete memory"
                >
                  <Trash2 className="w-3.5 h-3.5" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};
