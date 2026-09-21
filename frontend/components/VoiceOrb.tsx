"use client";

import React, { useEffect, useRef } from "react";
import { AgentStatusType } from "@/types/agent";

interface VoiceOrbProps {
  status: AgentStatusType;
  audioLevel?: number; // Normalized 0.0 to 1.0
  onClick?: () => void;
}

export const VoiceOrb: React.FC<VoiceOrbProps> = ({
  status,
  audioLevel = 0,
  onClick,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    let animationFrameId: number;
    let time = 0;

    const render = () => {
      time += 0.025;
      const width = canvas.width;
      const height = canvas.height;
      const centerX = width / 2;
      const centerY = height / 2 - 4; // Slight optical centering

      ctx.clearRect(0, 0, width, height);

      // Base radius of the 3D sphere
      const sphereRadius = 66 + (status === "LISTENING" || status === "SPEAKING" ? audioLevel * 14 : 0);

      // 1. GROUND PLANE CONTACT SHADOW (Grounding the sphere in 3D space)
      const shadowY = centerY + sphereRadius + 22;
      const shadowRadiusX = sphereRadius * (0.85 + Math.sin(time * 1.5) * 0.03);
      const shadowRadiusY = sphereRadius * 0.22;
      const groundShadow = ctx.createRadialGradient(
        centerX,
        shadowY,
        2,
        centerX,
        shadowY,
        shadowRadiusX
      );
      groundShadow.addColorStop(0, "rgba(43, 24, 16, 0.28)");
      groundShadow.addColorStop(0.5, "rgba(43, 24, 16, 0.10)");
      groundShadow.addColorStop(1, "transparent");

      ctx.fillStyle = groundShadow;
      ctx.beginPath();
      ctx.ellipse(centerX, shadowY, shadowRadiusX, shadowRadiusY, 0, 0, Math.PI * 2);
      ctx.fill();

      // Palette definition based on agent status (no purple gradients)
      let lightColor = "#FFFFFF";
      let highlightTone = "#F5EBE1";
      let bodyColor = "#45281C";
      let shadowColor = "#1D0F08";
      let rimColor = "rgba(140, 101, 82, 0.45)";
      let auraColor = "rgba(140, 101, 82, 0.15)";

      if (status === "LISTENING") {
        highlightTone = "#E0F7FA";
        bodyColor = "#00838F";
        shadowColor = "#00363A";
        rimColor = "rgba(0, 188, 212, 0.55)";
        auraColor = "rgba(0, 188, 212, 0.22)";
      } else if (status === "SPEAKING") {
        highlightTone = "#E8F5E9";
        bodyColor = "#2E7D32";
        shadowColor = "#1B5E20";
        rimColor = "rgba(46, 125, 50, 0.55)";
        auraColor = "rgba(76, 175, 80, 0.22)";
      } else if (status === "THINKING" || status === "USING_TOOL") {
        highlightTone = "#FFF8E1";
        bodyColor = "#D97706";
        shadowColor = "#78350F";
        rimColor = "rgba(217, 119, 6, 0.55)";
        auraColor = "rgba(245, 158, 11, 0.22)";
      } else if (status === "ERROR") {
        highlightTone = "#FFEBEE";
        bodyColor = "#C62828";
        shadowColor = "#3E0B0B";
        rimColor = "rgba(198, 40, 40, 0.55)";
        auraColor = "rgba(239, 68, 68, 0.22)";
      }

      // 2. SOFT AMBIENT 3D AURA
      const auraPulse = Math.sin(time * 2) * 4;
      const auraGradient = ctx.createRadialGradient(
        centerX,
        centerY,
        sphereRadius * 0.6,
        centerX,
        centerY,
        sphereRadius * 1.55 + auraPulse
      );
      auraGradient.addColorStop(0, auraColor);
      auraGradient.addColorStop(0.6, auraColor.replace("0.22", "0.08").replace("0.15", "0.05"));
      auraGradient.addColorStop(1, "transparent");

      ctx.fillStyle = auraGradient;
      ctx.beginPath();
      ctx.arc(centerX, centerY, sphereRadius * 1.55 + auraPulse, 0, Math.PI * 2);
      ctx.fill();

      // 3. BACK ORBITAL RINGS (Behind sphere in 3D depth)
      const ringTilt = 0.55; // Perspective foreshortening
      const ringCount = 2;

      for (let r = 0; r < ringCount; r++) {
        ctx.save();
        ctx.translate(centerX, centerY);
        const rotAngle = (time * 0.4 * (r === 0 ? 1 : -1)) + (r * Math.PI) / 2.5;
        ctx.rotate(rotAngle);

        // Draw back half of ring
        ctx.beginPath();
        const rx = sphereRadius * (1.35 + r * 0.22);
        const ry = rx * ringTilt;
        ctx.ellipse(0, 0, rx, ry, 0, Math.PI, Math.PI * 2);
        ctx.strokeStyle = rimColor.replace("0.55", "0.25").replace("0.45", "0.2");
        ctx.lineWidth = 1.2;
        ctx.setLineDash([4, 6]);
        ctx.stroke();
        ctx.restore();
      }

      // 4. MAIN 3D VOLUMETRIC SPHERE
      // Light source placed top-left in 3D space
      const lightX = centerX - sphereRadius * 0.38;
      const lightY = centerY - sphereRadius * 0.38;

      const sphereGrad = ctx.createRadialGradient(
        lightX,
        lightY,
        sphereRadius * 0.05,
        centerX + sphereRadius * 0.15,
        centerY + sphereRadius * 0.15,
        sphereRadius * 1.05
      );
      sphereGrad.addColorStop(0, lightColor);
      sphereGrad.addColorStop(0.18, highlightTone);
      sphereGrad.addColorStop(0.55, bodyColor);
      sphereGrad.addColorStop(0.88, shadowColor);
      sphereGrad.addColorStop(1, "#0A0503");

      ctx.save();
      ctx.beginPath();
      ctx.arc(centerX, centerY, sphereRadius, 0, Math.PI * 2);
      ctx.fillStyle = sphereGrad;
      ctx.fill();

      // 5. 3D FRESNEL BACK-RIM LIGHT
      const rimGrad = ctx.createRadialGradient(
        centerX + sphereRadius * 0.45,
        centerY + sphereRadius * 0.45,
        sphereRadius * 0.7,
        centerX,
        centerY,
        sphereRadius
      );
      rimGrad.addColorStop(0, "transparent");
      rimGrad.addColorStop(0.75, "transparent");
      rimGrad.addColorStop(0.95, rimColor);
      rimGrad.addColorStop(1, "transparent");

      ctx.fillStyle = rimGrad;
      ctx.beginPath();
      ctx.arc(centerX, centerY, sphereRadius, 0, Math.PI * 2);
      ctx.fill();

      // 6. SPECULAR REFLECTION HOTSPOT (Curved glossy surface)
      const specGrad = ctx.createRadialGradient(
        lightX,
        lightY,
        1,
        lightX,
        lightY,
        sphereRadius * 0.32
      );
      specGrad.addColorStop(0, "rgba(255, 255, 255, 0.85)");
      specGrad.addColorStop(0.3, "rgba(255, 255, 255, 0.35)");
      specGrad.addColorStop(1, "transparent");

      ctx.fillStyle = specGrad;
      ctx.beginPath();
      ctx.arc(lightX, lightY, sphereRadius * 0.32, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();

      // 7. FRONT ORBITAL RINGS (In front of sphere in 3D depth)
      for (let r = 0; r < ringCount; r++) {
        ctx.save();
        ctx.translate(centerX, centerY);
        const rotAngle = (time * 0.4 * (r === 0 ? 1 : -1)) + (r * Math.PI) / 2.5;
        ctx.rotate(rotAngle);

        // Draw front half of ring
        ctx.beginPath();
        const rx = sphereRadius * (1.35 + r * 0.22);
        const ry = rx * ringTilt;
        ctx.ellipse(0, 0, rx, ry, 0, 0, Math.PI);
        ctx.strokeStyle = rimColor;
        ctx.lineWidth = 1.4;
        ctx.setLineDash([]);
        ctx.stroke();

        // 3D Orbital node particle travelling along the ring
        const nodeAngle = (time * 1.2 * (r === 0 ? 1 : -1)) % (Math.PI * 2);
        if (nodeAngle >= 0 && nodeAngle <= Math.PI) {
          const nx = rx * Math.cos(nodeAngle);
          const ny = ry * Math.sin(nodeAngle);
          ctx.beginPath();
          ctx.arc(nx, ny, 2.5, 0, Math.PI * 2);
          ctx.fillStyle = "#FFFFFF";
          ctx.shadowColor = rimColor;
          ctx.shadowBlur = 6;
          ctx.fill();
        }

        ctx.restore();
      }

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => {
      cancelAnimationFrame(animationFrameId);
    };
  }, [status, audioLevel]);

  return (
    <div
      onClick={onClick}
      className="relative flex flex-col items-center justify-center cursor-pointer group select-none"
      role="button"
      tabIndex={0}
      aria-label={`Voice core status: ${status}. Click to toggle speech.`}
      onKeyDown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          onClick?.();
        }
      }}
    >
      <div className="relative w-64 h-64 flex items-center justify-center">
        <canvas
          ref={canvasRef}
          width={256}
          height={256}
          className="w-full h-full transform transition-transform duration-500 group-hover:scale-[1.03]"
        />
        {/* Note: The center text badge has been completely removed per request */}
      </div>
    </div>
  );
};
