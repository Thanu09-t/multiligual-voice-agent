import React from "react";
import Link from "next/link";
import { ArrowLeft, Shield, Lock, Database, Eye, Mail } from "lucide-react";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Privacy Policy",
  description: "Privacy Policy for NOVA Voice Agent, detailing audio handling, data storage, and user privacy rights.",
};

export default function PrivacyPolicyPage() {
  const lastUpdated = "September 21, 2026";

  return (
    <div className="min-h-screen bg-[#F6F7F9] text-[#2B1810] font-serif py-12 px-6 sm:px-10 max-w-4xl mx-auto">
      {/* Back button */}
      <div className="mb-8">
        <Link
          href="/"
          className="inline-flex items-center space-x-2 text-xs font-sans text-[#6B4E3D] hover:text-[#2B1810] transition-colors"
        >
          <ArrowLeft className="w-4 h-4" />
          <span>Back to NOVA Voice Agent</span>
        </Link>
      </div>

      {/* Header */}
      <header className="border-b border-[#2B1810]/15 pb-6 mb-8">
        <div className="flex items-center space-x-3 mb-3">
          <div className="w-9 h-9 rounded-xl bg-[#2B1810]/8 border border-[#2B1810]/15 flex items-center justify-center text-[#2B1810]">
            <Shield className="w-5 h-5 text-[#8C6552]" />
          </div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight text-[#2B1810]">
            Privacy Policy
          </h1>
        </div>
        <p className="text-xs text-[#6B4E3D] font-sans">
          Last Updated: {lastUpdated} &bull; Controller: NOVA Voice Agent Entity
        </p>
      </header>

      {/* Content */}
      <div className="space-y-8 text-sm text-[#45281C] leading-relaxed">
        {/* Section 1 */}
        <section className="space-y-3">
          <h2 className="text-base font-semibold text-[#2B1810] flex items-center space-x-2">
            <span className="text-[#8C6552] font-sans text-xs">01.</span>
            <span>Introduction & Scope</span>
          </h2>
          <p>
            This Privacy Policy explains how NOVA (&quot;we&quot;, &quot;us&quot;, or &quot;our&quot;) collects, processes, and protects information when you use the NOVA Voice Agent application and associated services.
          </p>
          <p>
            We strictly limit data collection to what is technically necessary to provide real-time voice interaction, agent reasoning, document retrieval, and persistent conversation memory.
          </p>
        </section>

        {/* Section 2 */}
        <section className="space-y-3">
          <h2 className="text-base font-semibold text-[#2B1810] flex items-center space-x-2">
            <span className="text-[#8C6552] font-sans text-xs">02.</span>
            <span>Information We Collect & How We Handle It</span>
          </h2>

          <div className="grid gap-3 sm:grid-cols-2 mt-3">
            <div className="p-4 rounded-xl bg-white border border-[#2B1810]/12 shadow-xs space-y-2">
              <div className="flex items-center space-x-2 text-[#2B1810] font-medium text-xs">
                <Lock className="w-4 h-4 text-[#8C6552]" />
                <span>Real-Time Voice Audio</span>
              </div>
              <p className="text-xs text-[#6B4E3D]">
                Audio is streamed via secure WebSockets (<code className="text-[#2B1810] font-sans">/api/voice</code>) and processed strictly in-memory for speech-to-text conversion. Raw microphone audio is transient and is not permanently recorded or archived.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white border border-[#2B1810]/12 shadow-xs space-y-2">
              <div className="flex items-center space-x-2 text-[#2B1810] font-medium text-xs">
                <Database className="w-4 h-4 text-[#8C6552]" />
                <span>Transcripts & Memory</span>
              </div>
              <p className="text-xs text-[#6B4E3D]">
                Text messages and derived user facts (e.g. preferences, project context) are stored in your database instance to enable conversational continuity. You can inspect or delete memories anytime from the Memory drawer.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white border border-[#2B1810]/12 shadow-xs space-y-2">
              <div className="flex items-center space-x-2 text-[#2B1810] font-medium text-xs">
                <Eye className="w-4 h-4 text-[#8C6552]" />
                <span>Knowledge Documents (RAG)</span>
              </div>
              <p className="text-xs text-[#6B4E3D]">
                Files you explicitly upload (PDF, TXT, DOCX) are parsed and chunked in the local database to answer factual queries. You retain full ownership and can delete documents at any time.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-white border border-[#2B1810]/12 shadow-xs space-y-2">
              <div className="flex items-center space-x-2 text-[#2B1810] font-medium text-xs">
                <Shield className="w-4 h-4 text-[#8C6552]" />
                <span>Account Credentials</span>
              </div>
              <p className="text-xs text-[#6B4E3D]">
                If you register for an account, your email address and an irreversibly hashed password (bcrypt) are stored locally in the database. Plaintext passwords are never stored or logged.
              </p>
            </div>
          </div>
        </section>

        {/* Section 3 */}
        <section className="space-y-3">
          <h2 className="text-base font-semibold text-[#2B1810] flex items-center space-x-2">
            <span className="text-[#8C6552] font-sans text-xs">03.</span>
            <span>Cookies & Local Storage</span>
          </h2>
          <p>
            NOVA does not use third-party tracking cookies, behavioral ad pixels, or cross-site analytics scripts.
          </p>
          <p>
            We use browser <code className="text-[#2B1810] font-sans">localStorage</code> strictly to store your active authentication session token (<code className="text-[#2B1810] font-sans">nova_token</code>) and local UI preferences (such as speech speed and voice selection).
          </p>
        </section>

        {/* Section 4 */}
        <section className="space-y-3">
          <h2 className="text-base font-semibold text-[#2B1810] flex items-center space-x-2">
            <span className="text-[#8C6552] font-sans text-xs">04.</span>
            <span>Third-Party AI Services & Data Transfer</span>
          </h2>
          <p>
            Depending on backend configuration, queries may be processed using configured AI model providers (such as Groq, OpenAI, or Google Gemini) to generate speech-to-text transcriptions, LLM reasoning responses, and speech synthesis.
          </p>
          <p>
            Data sent to external model providers is governed by each respective provider&apos;s enterprise API data policies. We do not sell your data or license it to third parties for advertising.
          </p>
        </section>

        {/* Section 5 */}
        <section className="space-y-3">
          <h2 className="text-base font-semibold text-[#2B1810] flex items-center space-x-2">
            <span className="text-[#8C6552] font-sans text-xs">05.</span>
            <span>Data Retention & User Rights</span>
          </h2>
          <p>
            You have full control over your stored data:
          </p>
          <ul className="list-disc list-inside space-y-1 pl-2 text-[#45281C]">
            <li><strong className="text-[#2B1810]">Delete Memories:</strong> Remove individual long-term memory entries or clear all saved memories with one click.</li>
            <li><strong className="text-[#2B1810]">Delete Documents:</strong> Remove uploaded knowledge documents and their vector chunks immediately.</li>
            <li><strong className="text-[#2B1810]">Clear History:</strong> Reset conversation transcripts and local browser storage at any time.</li>
          </ul>
        </section>

        {/* Section 6 */}
        <section className="space-y-3">
          <h2 className="text-base font-semibold text-[#2B1810] flex items-center space-x-2">
            <span className="text-[#8C6552] font-sans text-xs">06.</span>
            <span>Security Measures</span>
          </h2>
          <p>
            We implement cryptographic standards including bcrypt password hashing, JSON Web Tokens (JWT) for session authentication, parameter validation via Pydantic, and isolated WebSocket channels.
          </p>
        </section>

        {/* Section 7 */}
        <section className="space-y-3 border-t border-[#2B1810]/15 pt-6">
          <h2 className="text-base font-semibold text-[#2B1810] flex items-center space-x-2">
            <Mail className="w-4 h-4 text-[#8C6552]" />
            <span>Contact Information</span>
          </h2>
          <p>
            For any privacy inquiries, data deletion requests, or questions regarding this policy, please reach out to:
          </p>
          <div className="p-4 rounded-xl bg-white border border-[#2B1810]/12 text-xs font-sans space-y-1 text-[#45281C] shadow-xs">
            <div><strong>Entity:</strong> NOVA Voice Agent Platform</div>
            <div><strong>Repository:</strong> <a href="https://github.com/Thanu09-t/multiligual-voice-agent" target="_blank" rel="noopener noreferrer" className="text-[#2B1810] underline">github.com/Thanu09-t/multiligual-voice-agent</a></div>
          </div>
        </section>
      </div>

      {/* Footer link back */}
      <footer className="mt-12 pt-6 border-t border-[#2B1810]/15 flex justify-between text-xs text-[#8C6552]">
        <div>&copy; {new Date().getFullYear()} NOVA. All rights reserved.</div>
        <div className="space-x-4">
          <Link href="/terms-and-conditions" className="hover:text-[#2B1810] transition-colors">
            Terms and Conditions
          </Link>
          <Link href="/" className="hover:text-[#2B1810] transition-colors">
            App Home
          </Link>
        </div>
      </footer>
    </div>
  );
}
