"use client";

import { useRef, useState } from "react";
import type { Measurement, Recommendation } from "@/lib/api";
import FitBadge from "./FitBadge";

export default function FitCard({
  measurement,
  top,
}: {
  measurement: Measurement;
  top: Recommendation;
}) {
  const cardRef = useRef<HTMLDivElement>(null);
  const [busy, setBusy] = useState(false);
  const [copied, setCopied] = useState(false);

  async function downloadPng() {
    if (!cardRef.current) return;
    setBusy(true);
    try {
      const { toPng } = await import("html-to-image");
      const dataUrl = await toPng(cardRef.current, {
        pixelRatio: 2,
        backgroundColor: "#05060a",
      });
      const a = document.createElement("a");
      a.href = dataUrl;
      a.download = "one8-fitlab-result.png";
      a.click();
    } finally {
      setBusy(false);
    }
  }

  async function share() {
    const text = `My one8 FitLab result: ${top.name} in ${top.size_label} (${top.fit} fit) — matched by AI foot scan.`;
    if (typeof navigator !== "undefined" && "share" in navigator) {
      try {
        await navigator.share({ text, title: "one8 FitLab" });
        return;
      } catch {
        // user cancelled — fall through to copy
      }
    }
    await navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  return (
    <div>
      <div
        ref={cardRef}
        className="mx-auto max-w-md rounded-3xl border border-white/10 bg-gradient-to-b from-ink-800 to-ink-950 p-8"
      >
        <div className="flex items-center justify-between">
          <span className="text-xl font-black tracking-tight">
            one<span className="text-volt-500">8</span>{" "}
            <span className="text-sm font-medium text-white/50">FitLab</span>
          </span>
          <span className="text-[10px] uppercase tracking-[0.25em] text-white/40">
            AI Fit Result
          </span>
        </div>

        <div className="mt-6 flex items-center gap-4">
          <div className="flex h-24 w-24 shrink-0 items-center justify-center rounded-2xl bg-white/5 p-3">
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={top.image_url} alt={top.name} className="h-full w-full object-contain" />
          </div>
          <div>
            <div className="text-xs uppercase tracking-widest text-white/40">Best match</div>
            <div className="text-xl font-bold">{top.name}</div>
            <div className="mt-1 flex items-center gap-2">
              <FitBadge fit={top.fit} />
              <span className="text-sm text-white/70">{top.size_label}</span>
            </div>
          </div>
        </div>

        <div className="mt-6 grid grid-cols-2 gap-3 text-center">
          <div className="rounded-xl bg-white/[0.04] p-3">
            <div className="text-lg font-black text-volt-400">{measurement.length_mm.toFixed(0)}mm</div>
            <div className="text-[11px] text-white/40">Foot length</div>
          </div>
          <div className="rounded-xl bg-white/[0.04] p-3">
            <div className="text-lg font-black text-volt-400">{Math.round(top.match_score * 100)}%</div>
            <div className="text-[11px] text-white/40">Match score</div>
          </div>
        </div>

        <p className="mt-5 text-center text-[11px] text-white/35">
          Measured with a phone camera + A4 sheet. one8fitlab.app
        </p>
      </div>

      <div className="mt-4 flex justify-center gap-3">
        <button
          onClick={downloadPng}
          disabled={busy}
          className="rounded-full border border-white/15 px-5 py-2 text-sm text-white/80 hover:bg-white/5 disabled:opacity-50"
        >
          {busy ? "Rendering…" : "Download PNG"}
        </button>
        <button onClick={share} className="btn-volt rounded-full px-5 py-2 text-sm">
          {copied ? "Copied!" : "Share result"}
        </button>
      </div>
    </div>
  );
}
