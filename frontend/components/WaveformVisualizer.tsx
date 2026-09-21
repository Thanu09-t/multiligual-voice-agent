"use client";

import React, { useEffect, useRef } from "react";

interface WaveformVisualizerProps {
  analyserNode: AnalyserNode | null;
  isActive: boolean;
  height?: number;
}

export const WaveformVisualizer: React.FC<WaveformVisualizerProps> = ({
  analyserNode,
  isActive,
  height = 56,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationId: number;
    let phase = 0;
    const bufferLength = analyserNode ? analyserNode.frequencyBinCount : 64;
    const dataArray = new Uint8Array(bufferLength);

    const draw = () => {
      animationId = requestAnimationFrame(draw);
      phase += 0.04;

      const width = canvas.width;
      const h = canvas.height;
      const centerY = h / 2;
      ctx.clearRect(0, 0, width, h);

      // Extract frequency/time data if active
      let energy = 0;
      if (isActive && analyserNode) {
        analyserNode.getByteFrequencyData(dataArray);
        let sum = 0;
        const sampleCount = Math.min(32, bufferLength);
        for (let i = 0; i < sampleCount; i++) {
          sum += dataArray[i];
        }
        energy = (sum / sampleCount) / 255;
      }

      // Dynamic amplitude: gentle organic breathing when idle, responsive acoustic amplitude when active
      const baseAmp = isActive ? 4 + energy * 18 : 2.5;

      // Draw dual organic continuous harmonic waves
      const drawWave = (
        amplitude: number,
        frequency: number,
        speed: number,
        phaseOffset: number,
        strokeColor: string,
        fillColor: string,
        lineWidth: number
      ) => {
        ctx.beginPath();
        const steps = 60;
        const stepWidth = width / steps;

        // Start at left center
        ctx.moveTo(0, centerY);

        for (let i = 0; i <= steps; i++) {
          const x = i * stepWidth;
          // Smooth Hann windowing tapering to zero at both edges
          const windowing = Math.sin((i / steps) * Math.PI);
          // Multi-frequency harmonic synthesis
          const harmonic =
            Math.sin(i * frequency + phase * speed + phaseOffset) * 0.7 +
            Math.sin(i * (frequency * 1.6) - phase * (speed * 0.8)) * 0.3;

          const y = centerY + harmonic * amplitude * windowing;
          ctx.lineTo(x, y);
        }

        ctx.strokeStyle = strokeColor;
        ctx.lineWidth = lineWidth;
        ctx.stroke();

        // Subtle translucent fill to center baseline
        ctx.lineTo(width, centerY);
        ctx.lineTo(0, centerY);
        ctx.closePath();
        ctx.fillStyle = fillColor;
        ctx.fill();
      };

      // 1. Secondary subtle harmonic undertone (warm bronze)
      drawWave(
        baseAmp * 0.75,
        0.14,
        1.1,
        1.2,
        "rgba(140, 101, 82, 0.45)",
        "rgba(140, 101, 82, 0.05)",
        1.2
      );

      // 2. Primary natural soundwave (rich dark chocolate)
      drawWave(
        baseAmp,
        0.18,
        1.6,
        0.0,
        "rgba(43, 24, 16, 0.85)",
        "rgba(43, 24, 16, 0.08)",
        1.8
      );

      // Subtle center baseline reference tick marks
      ctx.strokeStyle = "rgba(43, 24, 16, 0.12)";
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(0, centerY);
      ctx.lineTo(width, centerY);
      ctx.stroke();
    };

    draw();

    return () => {
      cancelAnimationFrame(animationId);
    };
  }, [analyserNode, isActive]);

  return (
    <div className="w-full max-w-sm flex items-center justify-center p-2.5 rounded-2xl bg-white/70 border border-[#2B1810]/12 shadow-sm backdrop-blur-sm">
      <canvas
        ref={canvasRef}
        width={340}
        height={height}
        className="w-full h-12"
      />
    </div>
  );
};
