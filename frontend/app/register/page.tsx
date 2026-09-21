"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Lock, Mail, User, ArrowRight, AlertCircle } from "lucide-react";
import { API_BASE_URL } from "@/lib/config";

export default function RegisterPage() {
  const router = useRouter();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (password.length < 6) {
      setError("Password must be at least 6 characters long.");
      return;
    }

    setLoading(true);

    try {
      const res = await fetch(`${API_BASE_URL}/api/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email,
          password,
          full_name: fullName,
        }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Registration failed.");
      }

      localStorage.setItem("nova_token", data.access_token);
      localStorage.setItem("nova_user", JSON.stringify(data));
      router.push("/");
    } catch (err: any) {
      setError(err.message || "Failed to register.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 bg-[#F6F7F9] text-[#2B1810] font-serif">
      <div className="bg-white max-w-md w-full p-8 rounded-3xl border border-[#2B1810]/15 shadow-2xl relative overflow-hidden">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-2xl bg-[#2B1810]/5 border border-[#2B1810]/15 mb-3">
            <img src="/nova-icon.svg" className="w-7 h-7" alt="NOVA" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-[#2B1810]">
            Create an Account
          </h2>
          <p className="text-xs text-[#6B4E3D] mt-1">
            Access persistent memory and document workspace tools
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleRegister} className="space-y-4">
          <div className="space-y-1.5">
            <label className="text-xs text-[#45281C] font-medium">Full Name</label>
            <div className="flex items-center bg-[#F6F7F9] border border-[#2B1810]/15 rounded-xl px-3 py-2.5 focus-within:border-[#2B1810]/50 transition-all">
              <User className="w-4 h-4 text-[#8C6552] mr-2.5" />
              <input
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                placeholder="Your Name"
                className="w-full bg-transparent text-sm text-[#2B1810] placeholder-[#8C6552]/60 focus:outline-none font-serif"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs text-[#45281C] font-medium">Email Address</label>
            <div className="flex items-center bg-[#F6F7F9] border border-[#2B1810]/15 rounded-xl px-3 py-2.5 focus-within:border-[#2B1810]/50 transition-all">
              <Mail className="w-4 h-4 text-[#8C6552] mr-2.5" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@domain.com"
                className="w-full bg-transparent text-sm text-[#2B1810] placeholder-[#8C6552]/60 focus:outline-none font-serif"
              />
            </div>
          </div>

          <div className="space-y-1.5">
            <label className="text-xs text-[#45281C] font-medium">Password</label>
            <div className="flex items-center bg-[#F6F7F9] border border-[#2B1810]/15 rounded-xl px-3 py-2.5 focus-within:border-[#2B1810]/50 transition-all">
              <Lock className="w-4 h-4 text-[#8C6552] mr-2.5" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="At least 6 characters"
                className="w-full bg-transparent text-sm text-[#2B1810] placeholder-[#8C6552]/60 focus:outline-none font-serif"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full flex items-center justify-center space-x-2 py-3 px-4 rounded-xl bg-[#2B1810] hover:bg-[#45281C] text-[#F6F7F9] font-medium text-sm transition-all shadow-sm disabled:opacity-50"
          >
            <span>{loading ? "Creating Account..." : "Register"}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="mt-6 text-center text-xs text-[#6B4E3D]">
          Already have an account?{" "}
          <Link href="/login" className="text-[#2B1810] underline font-medium hover:text-[#45281C]">
            Sign in
          </Link>
        </div>
      </div>

      {/* Footer links */}
      <footer className="mt-8 flex items-center space-x-4 text-xs text-[#8C6552]">
        <Link href="/" className="hover:text-[#2B1810] transition-colors">
          App Home
        </Link>
        <span>&bull;</span>
        <Link href="/privacy-policy" className="hover:text-[#2B1810] transition-colors">
          Privacy Policy
        </Link>
        <span>&bull;</span>
        <Link href="/terms-and-conditions" className="hover:text-[#2B1810] transition-colors">
          Terms
        </Link>
      </footer>
    </div>
  );
}
