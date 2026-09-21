import type { Metadata, Viewport } from "next";
import "./globals.css";

export const metadata: Metadata = {
  metadataBase: new URL(process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"),
  title: {
    default: "NOVA — Multimodal Real-Time AI Voice Agent",
    template: "%s | NOVA Voice Agent",
  },
  description:
    "A production-grade voice-first AI agent featuring client-side VAD, instant interruption barge-in, document RAG retrieval, and long-term memory.",
  keywords: [
    "Voice AI",
    "Real-time Audio",
    "Voice Activity Detection",
    "Agentic Reasoning",
    "FastAPI",
    "Next.js",
  ],
  authors: [{ name: "Thanu09-t" }],
  icons: {
    icon: "/nova-icon.svg",
    apple: "/nova-icon.svg",
  },
  openGraph: {
    title: "NOVA — Multimodal Real-Time AI Voice Agent",
    description:
      "A production-grade voice-first AI agent with real-time audio streaming, instant interruption barge-in, document RAG, and memory.",
    url: "/",
    siteName: "NOVA Voice Agent",
    locale: "en_US",
    type: "website",
  },
  robots: {
    index: true,
    follow: true,
  },
};

export const viewport: Viewport = {
  themeColor: "#F6F7F9",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-[#F6F7F9] text-[#2B1810] font-serif antialiased selection:bg-[#5A3828]/20 selection:text-[#2B1810]">
        {children}
      </body>
    </html>
  );
}
