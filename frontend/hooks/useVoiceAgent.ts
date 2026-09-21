"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { AgentStatusType, MessageItem } from "@/types/agent";
import { WS_BASE_URL } from "@/lib/config";

interface UseVoiceAgentProps {
  serverUrl?: string;
  conversationId?: string | null;
  userId?: string | null;
  onMessageReceived?: (message: MessageItem) => void;
  onConversationUpdate?: (conversationId: string) => void;
  onTranscriptPartial?: (text: string) => void;
  onStatusChange?: (status: AgentStatusType) => void;
}

export function useVoiceAgent({
  serverUrl = `${WS_BASE_URL}/api/voice`,
  conversationId = null,
  userId = null,
  onMessageReceived,
  onConversationUpdate,
  onTranscriptPartial,
  onStatusChange,
}: UseVoiceAgentProps) {
  const [status, setStatus] = useState<AgentStatusType>("IDLE");
  const [audioLevel, setAudioLevel] = useState<number>(0);
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [isListening, setIsListening] = useState<boolean>(false);

  const wsRef = useRef<WebSocket | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const recordedChunksRef = useRef<Blob[]>([]);
  const isSpeakingSpeechRef = useRef<boolean>(false);
  const silenceTimerRef = useRef<NodeJS.Timeout | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const statusRef = useRef<AgentStatusType>("IDLE");

  const onMessageReceivedRef = useRef(onMessageReceived);
  onMessageReceivedRef.current = onMessageReceived;

  const onConversationUpdateRef = useRef(onConversationUpdate);
  onConversationUpdateRef.current = onConversationUpdate;

  const onTranscriptPartialRef = useRef(onTranscriptPartial);
  onTranscriptPartialRef.current = onTranscriptPartial;

  const onStatusChangeRef = useRef(onStatusChange);
  onStatusChangeRef.current = onStatusChange;

  // Update status ref and state
  const updateStatus = useCallback((newStatus: AgentStatusType) => {
    statusRef.current = newStatus;
    setStatus(newStatus);
    if (onStatusChangeRef.current) onStatusChangeRef.current(newStatus);
  }, []);

  // Helper to get supported recording MIME type
  const getSupportedMimeType = (): string => {
    if (typeof MediaRecorder === "undefined") return "audio/webm";
    const types = [
      "audio/webm;codecs=opus",
      "audio/webm",
      "audio/ogg;codecs=opus",
      "audio/mp4",
      "audio/wav",
    ];
    for (const t of types) {
      if (MediaRecorder.isTypeSupported(t)) return t;
    }
    return "audio/webm";
  };

  // Helper to detect language of text for native neural TTS pronunciation
  const detectLanguage = (text: string): string => {
    if (typeof window !== "undefined") {
      const pref = localStorage.getItem("nova_pref_lang");
      if (pref && pref !== "auto") return pref;
    }
    // Devanagari script (Hindi / Marathi / Sanskrit / Nepali)
    if (/[\u0900-\u097F]/.test(text)) return "hi";
    // Arabic
    if (/[\u0600-\u06FF]/.test(text)) return "ar";
    // Japanese
    if (/[\u3040-\u30FF]/.test(text)) return "ja";
    // Chinese
    if (/[\u4E00-\u9FFF]/.test(text)) return "zh";
    // Cyrillic (Russian / Ukrainian)
    if (/[\u0400-\u04FF]/.test(text)) return "ru";
    // Spanish indicators
    if (/[¿¡]/.test(text) || /\b(hola|gracias|buenos|por favor|está|cómo|qué|amigo|bienvenido)\b/i.test(text)) return "es";
    // French indicators
    if (/\b(bonjour|merci|oui|s'il vous plaît|c'est|comment|bienvenue)\b/i.test(text)) return "fr";
    // German indicators
    if (/\b(guten tag|danke|bitte|hallo|wie geht|ich bin|willkommen)\b/i.test(text)) return "de";
    // Italian indicators
    if (/\b(ciao|grazie|buongiorno|come stai|benvenuto)\b/i.test(text)) return "it";
    // Portuguese indicators
    if (/\b(olá|obrigado|como vai|tudo bem|bem-vindo)\b/i.test(text)) return "pt";
    return "en";
  };

  // Speak agent response using browser's Neural Speech Synthesis with Multilingual Support
  const speakText = useCallback((text: string) => {
    if (typeof window === "undefined" || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();

    // Clean markdown tags for spoken audio
    const cleanText = text
      .replace(/\*\*([^*]+)\*\*/g, "$1")
      .replace(/\*([^*]+)\*/g, "$1")
      .replace(/^#+\s+/gm, "")
      .replace(/```[\s\S]*?```/g, "")
      .replace(/`([^`]+)`/g, "$1")
      .replace(/\[([^\]]+)\]\([^)]+\)/g, "$1")
      .trim();

    if (!cleanText) return;

    const langCode = detectLanguage(cleanText);
    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = langCode;

    const voices = window.speechSynthesis.getVoices();
    // Prioritize high-quality natural/neural voice matching detected language
    const matchedVoice =
      voices.find(
        (v) =>
          v.lang.toLowerCase().startsWith(langCode) &&
          (v.name.includes("Natural") ||
            v.name.includes("Neural") ||
            v.name.includes("Google") ||
            v.name.includes("Jenny") ||
            v.name.includes("Guy") ||
            v.name.includes("Aria"))
      ) ||
      voices.find((v) => v.lang.toLowerCase().startsWith(langCode)) ||
      voices.find((v) => v.lang.startsWith("en")) ||
      voices[0];

    if (matchedVoice) {
      utterance.voice = matchedVoice;
      utterance.lang = matchedVoice.lang || langCode;
    }
    utterance.rate = 1.12;
    utterance.pitch = 1.0;

    utterance.onstart = () => {
      statusRef.current = "SPEAKING";
      setStatus("SPEAKING");
      if (onStatusChangeRef.current) onStatusChangeRef.current("SPEAKING");
    };
    utterance.onend = () => {
      if (statusRef.current === "SPEAKING") {
        statusRef.current = "IDLE";
        setStatus("IDLE");
        if (onStatusChangeRef.current) onStatusChangeRef.current("IDLE");
      }
    };
    utterance.onerror = () => {
      if (statusRef.current === "SPEAKING") {
        statusRef.current = "IDLE";
        setStatus("IDLE");
        if (onStatusChangeRef.current) onStatusChangeRef.current("IDLE");
      }
    };

    window.speechSynthesis.speak(utterance);
  }, []);

  // Instant Barge-In
  const interrupt = useCallback(() => {
    // 1. Immediately kill local speech synthesis
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }

    // 2. Notify server over WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "interrupt" }));
    }

    statusRef.current = "LISTENING";
    setStatus("LISTENING");
    if (onStatusChangeRef.current) onStatusChangeRef.current("LISTENING");
  }, []);

  // Connect WebSocket - STABLE connection that does not disconnect on parent re-renders
  useEffect(() => {
    let url = serverUrl;
    const params = new URLSearchParams();
    if (conversationId) params.append("conversation_id", conversationId);
    if (userId) params.append("user_id", userId);
    if (params.toString()) url += `?${params.toString()}`;

    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const msg = JSON.parse(event.data);
        switch (msg.type) {
          case "agent_status":
            // Avoid clobbering local SPEAKING state from speech synthesis
            if (
              statusRef.current === "SPEAKING" &&
              (msg.status === "IDLE" || msg.status === "SPEAKING")
            ) {
              // speech synthesis will transition to IDLE onend
            } else {
              updateStatus(msg.status as AgentStatusType);
            }
            break;

          case "transcript_partial":
            if (onTranscriptPartialRef.current) onTranscriptPartialRef.current(msg.text);
            break;

          case "transcript_final":
            if (onMessageReceivedRef.current) {
              onMessageReceivedRef.current({
                id: `u-${Date.now()}`,
                sender: "user",
                content: msg.text,
                createdAt: new Date().toISOString(),
              });
            }
            break;

          case "response_text":
            if (onMessageReceivedRef.current) {
              onMessageReceivedRef.current({
                id: `a-${Date.now()}`,
                sender: "agent",
                content: msg.display_text,
                spokenContent: msg.spoken_text,
                createdAt: new Date().toISOString(),
              });
            }
            if (msg.conversation_id && onConversationUpdateRef.current) {
              onConversationUpdateRef.current(msg.conversation_id);
            }
            // Trigger natural spoken synthesis with zero latency
            speakText(msg.spoken_text || msg.display_text);
            break;

          case "interrupted":
            if (typeof window !== "undefined" && "speechSynthesis" in window) {
              window.speechSynthesis.cancel();
            }
            updateStatus("LISTENING");
            break;

          case "error":
            updateStatus("ERROR");
            setTimeout(() => updateStatus("IDLE"), 2500);
            break;
        }
      } catch (err) {
        console.error("WS Parse error:", err);
      }
    };

    ws.onclose = () => {
      setIsConnected(false);
    };

    return () => {
      ws.close();
      if (typeof window !== "undefined" && "speechSynthesis" in window) {
        window.speechSynthesis.cancel();
      }
    };
  }, [serverUrl, conversationId, userId, updateStatus, speakText]);

  // Start continuous microphone listening with sharp VAD and real MediaRecorder capture
  const startListening = async () => {
    try {
      interrupt(); // Immediately stop speaking if active

      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      mediaStreamRef.current = stream;

      const audioCtx = new (window.AudioContext || (window as any).webkitAudioContext)();
      audioContextRef.current = audioCtx;

      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 256;
      analyser.smoothingTimeConstant = 0.25;
      analyserRef.current = analyser;

      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      const bufferLength = analyser.frequencyBinCount;
      const dataArray = new Uint8Array(bufferLength);

      const mimeType = getSupportedMimeType();

      // Start / Stop utterance recorder helper
      const startUtteranceRecording = () => {
        if (
          mediaRecorderRef.current &&
          mediaRecorderRef.current.state === "recording"
        ) {
          return;
        }
        recordedChunksRef.current = [];
        try {
          const recorder = new MediaRecorder(stream, { mimeType });
          mediaRecorderRef.current = recorder;

          recorder.ondataavailable = (e) => {
            if (e.data && e.data.size > 0) {
              recordedChunksRef.current.push(e.data);
            }
          };

          recorder.onstop = () => {
            const fullBlob = new Blob(recordedChunksRef.current, { type: mimeType });
            recordedChunksRef.current = [];

            // Ignore tiny noise clicks (< 300 bytes)
            if (fullBlob.size > 300) {
              const reader = new FileReader();
              reader.onloadend = () => {
                const b64 = (reader.result as string).split(",")[1];
                if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
                  wsRef.current.send(
                    JSON.stringify({
                      type: "audio_data",
                      data: b64,
                      mime_type: mimeType,
                    })
                  );
                }
              };
              reader.readAsDataURL(fullBlob);
            }
          };

          recorder.start(40); // Ultra-fast 40ms chunk slices for instantaneous capture
        } catch (e) {
          console.error("MediaRecorder initiation failed:", e);
        }
      };

      const stopUtteranceRecording = () => {
        if (
          mediaRecorderRef.current &&
          mediaRecorderRef.current.state === "recording"
        ) {
          mediaRecorderRef.current.stop();
        }
      };

      // Ultra-responsive energy threshold to catch voice immediately on first phoneme
      const energyThreshold = 0.010;
      const silenceTimeoutMs = 260; // Ultra-fast turn-taking (260ms)

      const vadLoop = () => {
        analyser.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < bufferLength; i++) {
          sum += dataArray[i];
        }
        const avg = sum / bufferLength / 255;

        // When speaking, simulate organic pulse for visualizer; otherwise use live mic
        if (statusRef.current === "SPEAKING") {
          const pulse = 0.25 + 0.2 * Math.sin(Date.now() / 150);
          setAudioLevel(pulse);
        } else {
          setAudioLevel(avg);
        }

        // Voice Activity Detection
        if (avg > energyThreshold) {
          // If agent was speaking and user speaks, barge in immediately!
          if (statusRef.current === "SPEAKING") {
            interrupt();
          }

          if (!isSpeakingSpeechRef.current) {
            isSpeakingSpeechRef.current = true;
            startUtteranceRecording();
            if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
              wsRef.current.send(JSON.stringify({ type: "speech_started" }));
            }
            updateStatus("LISTENING");
          }

          if (silenceTimerRef.current) {
            clearTimeout(silenceTimerRef.current);
            silenceTimerRef.current = null;
          }
        } else {
          // User fell below threshold -> check silence duration
          if (isSpeakingSpeechRef.current && !silenceTimerRef.current) {
            silenceTimerRef.current = setTimeout(() => {
              isSpeakingSpeechRef.current = false;
              stopUtteranceRecording();
              silenceTimerRef.current = null;
            }, silenceTimeoutMs);
          }
        }

        animFrameRef.current = requestAnimationFrame(vadLoop);
      };

      vadLoop();
      setIsListening(true);
      updateStatus("LISTENING");
    } catch (err) {
      console.error("Microphone error:", err);
      updateStatus("ERROR");
    }
  };

  const stopListening = () => {
    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === "recording") {
      mediaRecorderRef.current.stop();
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    if (silenceTimerRef.current) {
      clearTimeout(silenceTimerRef.current);
      silenceTimerRef.current = null;
    }
    if (typeof window !== "undefined" && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
    }
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "speech_stopped" }));
    }
    isSpeakingSpeechRef.current = false;
    setIsListening(false);
    setAudioLevel(0);
    updateStatus("IDLE");
  };

  const sendTextMessage = (text: string) => {
    if (!text.trim()) return;
    interrupt();
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: "text_input", text }));
      if (onMessageReceivedRef.current) {
        onMessageReceivedRef.current({
          id: `u-${Date.now()}`,
          sender: "user",
          content: text,
          createdAt: new Date().toISOString(),
        });
      }
    }
  };

  return {
    status,
    audioLevel,
    isConnected,
    isListening,
    analyserNode: analyserRef.current,
    startListening,
    stopListening,
    interrupt,
    sendTextMessage,
  };
}
