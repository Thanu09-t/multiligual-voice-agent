"use client";

import React, { useState, useEffect } from "react";
import { X, UploadCloud, FileText, Trash2, CheckCircle2, AlertCircle, Loader2 } from "lucide-react";
import { API_BASE_URL } from "@/lib/config";

interface DocumentItem {
  id: string;
  filename: string;
  file_type: string;
  file_size: number;
  status: "uploading" | "processing" | "indexed" | "error";
  chunk_count: number;
  created_at: string;
}

interface DocumentPanelProps {
  isOpen: boolean;
  onClose: () => void;
  userId?: string;
}

export const DocumentPanel: React.FC<DocumentPanelProps> = ({
  isOpen,
  onClose,
  userId = "user-default",
}) => {
  const [documents, setDocuments] = useState<DocumentItem[]>([]);
  const [uploading, setUploading] = useState(false);
  const [loading, setLoading] = useState(false);

  const fetchDocuments = () => {
    setLoading(true);
    fetch(`${API_BASE_URL}/api/documents?user_id=${userId}`)
      .then((res) => res.json())
      .then((data) => {
        if (Array.isArray(data)) setDocuments(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  useEffect(() => {
    if (isOpen) {
      fetchDocuments();
    }
  }, [isOpen, userId]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);
    formData.append("user_id", userId);

    try {
      const res = await fetch(`${API_BASE_URL}/api/documents/upload`, {
        method: "POST",
        body: formData,
      });
      if (res.ok) {
        fetchDocuments();
      }
    } catch (err) {
      console.error("Upload failed:", err);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await fetch(`${API_BASE_URL}/api/documents/${id}`, {
        method: "DELETE",
      });
      setDocuments((prev) => prev.filter((d) => d.id !== id));
    } catch (err) {
      console.error("Failed to delete document:", err);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex justify-end bg-black/40 backdrop-blur-sm animate-fade-in font-serif">
      <div className="w-full max-w-md h-full bg-white border-l border-[#2B1810]/15 flex flex-col p-6 text-[#2B1810] shadow-2xl">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-[#2B1810]/10">
          <div className="flex items-center space-x-2.5">
            <div className="w-8 h-8 rounded-lg bg-[#2B1810]/8 border border-[#2B1810]/15 flex items-center justify-center text-[#2B1810]">
              <FileText className="w-4 h-4 text-[#8C6552]" />
            </div>
            <div>
              <h3 className="font-semibold text-sm text-[#2B1810]">Knowledge Documents</h3>
              <p className="text-[11px] text-[#6B4E3D]">RAG reference papers & documents</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 rounded-lg hover:bg-[#2B1810]/5 text-[#6B4E3D] hover:text-[#2B1810] transition-colors"
          >
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Upload Dropzone */}
        <div className="py-4">
          <label className="flex flex-col items-center justify-center p-6 border-2 border-dashed border-[#2B1810]/20 hover:border-[#2B1810]/50 rounded-2xl cursor-pointer bg-[#F6F7F9] hover:bg-[#EFECE8] transition-all group">
            {uploading ? (
              <Loader2 className="w-8 h-8 text-[#2B1810] animate-spin mb-2" />
            ) : (
              <UploadCloud className="w-8 h-8 text-[#8C6552] group-hover:text-[#2B1810] mb-2 transition-colors" />
            )}
            <span className="text-xs font-medium text-[#2B1810]">
              {uploading ? "Extracting & Indexing..." : "Upload PDF, TXT, or DOCX"}
            </span>
            <span className="text-[10px] text-[#8C6552] mt-1 font-sans">Up to 15MB file size</span>
            <input
              type="file"
              accept=".pdf,.txt,.docx,.doc"
              onChange={handleFileUpload}
              disabled={uploading}
              className="hidden"
            />
          </label>
        </div>

        {/* Document List */}
        <div className="flex-1 overflow-y-auto space-y-2 pr-1">
          {loading ? (
            <div className="text-center py-8 text-xs text-[#8C6552]">Loading documents...</div>
          ) : documents.length === 0 ? (
            <div className="text-center py-12 text-xs text-[#8C6552]">
              No documents uploaded yet. Upload reference files above for NOVA to read and answer questions.
            </div>
          ) : (
            documents.map((d) => (
              <div
                key={d.id}
                className="group p-3 rounded-xl bg-[#F6F7F9] hover:bg-[#EFECE8] border border-[#2B1810]/10 hover:border-[#2B1810]/20 transition-all flex items-start justify-between"
              >
                <div className="space-y-1 overflow-hidden">
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] uppercase font-sans px-2 py-0.5 rounded-full bg-white border border-[#2B1810]/15 text-[#45281C] font-semibold">
                      {d.file_type}
                    </span>
                    <span className="text-xs font-medium text-[#2B1810] truncate max-w-[200px]" title={d.filename}>
                      {d.filename}
                    </span>
                  </div>

                  <div className="flex items-center space-x-3 text-[11px] text-[#8C6552] font-sans">
                    <div className="flex items-center space-x-1">
                      {d.status === "indexed" ? (
                        <>
                          <CheckCircle2 className="w-3 h-3 text-emerald-700" />
                          <span className="text-emerald-700 font-medium">Indexed</span>
                        </>
                      ) : d.status === "processing" ? (
                        <>
                          <Loader2 className="w-3 h-3 text-amber-600 animate-spin" />
                          <span className="text-amber-600 font-medium">Processing</span>
                        </>
                      ) : (
                        <>
                          <AlertCircle className="w-3 h-3 text-rose-600" />
                          <span className="text-rose-600 font-medium">Error</span>
                        </>
                      )}
                    </div>
                    <span>{d.chunk_count} chunks</span>
                    <span>{(d.file_size / 1024).toFixed(1)} KB</span>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(d.id)}
                  className="p-1 rounded-lg opacity-0 group-hover:opacity-100 hover:bg-rose-100 text-rose-600 transition-all"
                  title="Delete document"
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
