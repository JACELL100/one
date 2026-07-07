"use client";

import { useCallback, useEffect, useRef, useState } from "react";

const DURATION_S = 8;

/**
 * A fully client-side "gait sensor": no video, no ML model, no camera
 * permission — the runner taps in rhythm with one foot-strike (e.g. every
 * time their right foot lands) for a few seconds. We turn that tap rhythm
 * into an estimated running cadence (steps per minute, both feet), which
 * feeds the same /scan/gait contract that a full pose-estimation pipeline
 * would in production. It's a genuinely novel way to capture a real
 * biomechanical signal without any hardware or hosted inference call.
 */
export default function CadenceTapper({
  onComplete,
}: {
  onComplete: (cadenceSpm: number) => void;
}) {
  const [phase, setPhase] = useState<"idle" | "running" | "done">("idle");
  const [remaining, setRemaining] = useState(DURATION_S);
  const [tapCount, setTapCount] = useState(0);
  const [result, setResult] = useState<number | null>(null);
  const tapsRef = useRef<number[]>([]);
  const startRef = useRef<number>(0);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const finish = useCallback(() => {
    if (intervalRef.current) clearInterval(intervalRef.current);
    const taps = tapsRef.current;
    let cadence = 0;
    if (taps.length >= 2) {
      const elapsedS = (taps[taps.length - 1] - taps[0]) / 1000;
      const tapsPerMinute = ((taps.length - 1) / Math.max(elapsedS, 1)) * 60;
      cadence = Math.round(Math.min(230, Math.max(120, tapsPerMinute * 2)));
    }
    setResult(cadence || null);
    setPhase("done");
  }, []);

  const start = useCallback(() => {
    tapsRef.current = [];
    setTapCount(0);
    setResult(null);
    setRemaining(DURATION_S);
    startRef.current = performance.now();
    setPhase("running");
    intervalRef.current = setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          finish();
          return 0;
        }
        return r - 1;
      });
    }, 1000);
  }, [finish]);

  const tap = useCallback(() => {
    if (phase !== "running") return;
    tapsRef.current.push(performance.now());
    setTapCount((c) => c + 1);
  }, [phase]);

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.code === "Space") {
        e.preventDefault();
        tap();
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [tap]);

  useEffect(() => () => {
    if (intervalRef.current) clearInterval(intervalRef.current);
  }, []);

  return (
    <div className="card rounded-2xl p-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold">Tap-your-cadence sensor</h3>
        <span className="text-xs uppercase tracking-widest text-white/40">
          No video needed
        </span>
      </div>
      <p className="mt-2 text-sm text-white/60">
        Tap the pad (or hit spacebar) every time one foot lands, like you&apos;re
        jogging in place, for {DURATION_S} seconds. We&apos;ll estimate your running
        cadence from the rhythm.
      </p>

      <div className="mt-5 flex flex-col items-center gap-4">
        <button
          type="button"
          onClick={phase === "idle" || phase === "done" ? start : tap}
          className={`relative flex h-40 w-40 select-none items-center justify-center rounded-full border-2 text-center font-black transition active:scale-95 ${
            phase === "running"
              ? "border-volt-500 bg-volt-500/10 text-volt-400"
              : "border-white/15 bg-white/[0.03] text-white/80 hover:border-volt-500/50"
          }`}
        >
          {phase === "idle" && <span>Start<br />8s tap test</span>}
          {phase === "running" && (
            <span className="text-4xl">
              {tapCount}
              <div className="mt-1 text-xs font-medium text-white/60">{remaining}s left — keep tapping</div>
            </span>
          )}
          {phase === "done" && <span>Tap to<br />retry</span>}
        </button>

        {phase === "done" && (
          <div className="text-center">
            {result ? (
              <>
                <div className="text-3xl font-black text-volt-400">{result} spm</div>
                <p className="mt-1 text-sm text-white/60">Estimated running cadence</p>
                <button
                  type="button"
                  onClick={() => onComplete(result)}
                  className="btn-volt mt-4 rounded-full px-6 py-2 text-sm"
                >
                  Use this cadence
                </button>
              </>
            ) : (
              <p className="text-sm text-ember-500">
                Not enough taps registered — try again with a few more taps.
              </p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
