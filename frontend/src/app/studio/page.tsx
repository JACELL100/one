"use client";

import { useRef, useState } from "react";

import CadenceTapper from "@/components/CadenceTapper";
import FitCard from "@/components/FitCard";
import RecommendationCard from "@/components/RecommendationCard";
import SegmentedControl from "@/components/SegmentedControl";
import Stepper from "@/components/Stepper";
import {
  type FootScanResponse,
  type GaitResult,
  type Goals,
  type Measurement,
  type Recommendation,
  recommend,
  saveScan,
  scanFoot,
  scanFootManual,
  scanGait,
} from "@/lib/api";
import { useAuth } from "@/lib/AuthProvider";

const STEPS = ["Scan", "Fit goals", "Run profile", "Results"];

const DEFAULT_GOALS: Goals = {
  sport: "running",
  surface: "road",
  cushioning: "balanced",
  use_case: "daily",
};

type Phase =
  | "instructions"
  | "capturing"
  | "analyzing"
  | "manual"
  | "measured"
  | "goals"
  | "gait"
  | "matching"
  | "results";

export default function StudioPage() {
  const { accessToken, ready, configured } = useAuth();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [phase, setPhase] = useState<Phase>("instructions");
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);

  const [measurement, setMeasurement] = useState<Measurement | null>(null);
  const [manualLength, setManualLength] = useState("26.0");
  const [goals, setGoals] = useState<Goals>(DEFAULT_GOALS);
  const [gait, setGait] = useState<GaitResult | null>(null);
  const [gaitStatus, setGaitStatus] = useState<"pending" | "skipped" | "done">("pending");

  const [recs, setRecs] = useState<Recommendation[] | null>(null);
  const [ranker, setRanker] = useState<string>("");
  const [saved, setSaved] = useState<"idle" | "saving" | "saved" | "error">("idle");

  const stepIndex =
    phase === "instructions" || phase === "capturing" || phase === "analyzing" || phase === "manual" || phase === "measured"
      ? 0
      : phase === "goals"
        ? 1
        : phase === "gait"
          ? 2
          : 3;

  async function handleFile(file: File) {
    setError(null);
    setPreview(URL.createObjectURL(file));
    setPhase("analyzing");
    try {
      const result: FootScanResponse = await scanFoot(file);
      if (result.manual_fallback_recommended) {
        setMeasurement(result.measurement.length_mm > 0 ? result.measurement : null);
        setPhase("manual");
      } else {
        setMeasurement(result.measurement);
        setPhase("measured");
      }
    } catch (e) {
      setError("We couldn't reach the scan service. You can still enter your size manually.");
      setPhase("manual");
    }
  }

  async function handleManualSubmit() {
    setError(null);
    const cm = parseFloat(manualLength);
    if (Number.isNaN(cm) || cm < 15 || cm > 35) {
      setError("Enter a foot length between 15 and 35 cm.");
      return;
    }
    try {
      const result = await scanFootManual(cm);
      setMeasurement(result.measurement);
      setPhase("measured");
    } catch {
      setError("Something went wrong saving your measurement. Please try again.");
    }
  }

  async function runMatching(finalGait: GaitResult | null) {
    if (!measurement) return;
    setPhase("matching");
    setError(null);
    try {
      const res = await recommend({
        length_mm: measurement.length_mm,
        width_mm: measurement.width_mm,
        goals,
        gait: finalGait,
        limit: 4,
      });
      setRecs(res.recommendations);
      setRanker(res.ranker);
      setPhase("results");
    } catch {
      setError("The matching engine is unavailable right now. Please try again shortly.");
      setPhase("gait");
    }
  }

  async function handleSave() {
    if (!accessToken || !measurement || !recs) return;
    setSaved("saving");
    try {
      await saveScan(accessToken, { measurement, goals, gait, recommendations: recs });
      setSaved("saved");
    } catch {
      setSaved("error");
    }
  }

  return (
    <div className="mx-auto max-w-3xl py-6">
      <Stepper steps={STEPS} current={stepIndex} />

      {error && (
        <div className="mb-6 rounded-xl border border-ember-500/40 bg-ember-500/10 px-4 py-3 text-sm text-ember-500">
          {error}
        </div>
      )}

      {phase === "instructions" && (
        <div className="card rounded-2xl p-8 text-center">
          <h1 className="text-2xl font-bold sm:text-3xl">Let&apos;s measure your foot</h1>
          <p className="mx-auto mt-3 max-w-md text-sm text-white/60">
            Place a plain A4 sheet flat on the floor, put your bare foot on it, and
            photograph it from directly above with good light. The sheet gives us a
            real-world ruler, accurate to the millimetre.
          </p>
          <div className="mx-auto mt-6 grid max-w-sm grid-cols-3 gap-3 text-xs text-white/50">
            <div className="card rounded-xl p-3">📄 Flat A4 sheet</div>
            <div className="card rounded-xl p-3">📷 Shot from above</div>
            <div className="card rounded-xl p-3">💡 Good lighting</div>
          </div>
          <button
            className="btn-volt mt-8 rounded-full px-8 py-3 text-base"
            onClick={() => {
              setPhase("capturing");
              fileInputRef.current?.click();
            }}
          >
            Take or upload a photo
          </button>
          <button
            className="mt-3 block w-full text-sm text-white/50 underline-offset-4 hover:underline"
            onClick={() => setPhase("manual")}
          >
            I&apos;d rather enter my size manually
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            capture="environment"
            className="hidden"
            onChange={(e) => {
              const file = e.target.files?.[0];
              if (file) handleFile(file);
            }}
          />
        </div>
      )}

      {(phase === "capturing" || phase === "analyzing") && (
        <div className="card rounded-2xl p-10 text-center">
          {preview && (
            // eslint-disable-next-line @next/next/no-img-element
            <img src={preview} alt="Your foot scan" className="mx-auto mb-6 max-h-64 rounded-xl object-contain" />
          )}
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-volt-500 border-t-transparent" />
          <p className="mt-4 text-sm text-white/60">Detecting the reference sheet and measuring your foot…</p>
        </div>
      )}

      {phase === "manual" && (
        <div className="card mx-auto max-w-md rounded-2xl p-8">
          <h2 className="text-xl font-bold">Enter your foot length</h2>
          <p className="mt-2 text-sm text-white/60">
            Measure heel to longest toe in centimetres. This still drives an exact,
            per-model size — you&apos;re never blocked.
          </p>
          <label className="mt-5 block text-sm text-white/70">
            Foot length (cm)
            <input
              type="number"
              step="0.1"
              min={15}
              max={35}
              value={manualLength}
              onChange={(e) => setManualLength(e.target.value)}
              className="mt-1 w-full rounded-lg border border-white/15 bg-white/5 px-3 py-2 text-white outline-none focus:border-volt-500"
            />
          </label>
          <button onClick={handleManualSubmit} className="btn-volt mt-5 w-full rounded-full py-3 text-sm">
            Continue
          </button>
          <button
            onClick={() => setPhase("instructions")}
            className="mt-3 w-full text-center text-sm text-white/50 hover:underline"
          >
            ← Back to photo scan
          </button>
        </div>
      )}

      {phase === "measured" && measurement && (
        <div className="card mx-auto max-w-md rounded-2xl p-8 text-center">
          <p className="text-xs uppercase tracking-widest text-volt-400">Scan complete</p>
          <div className="mt-3 text-4xl font-black">{measurement.length_mm.toFixed(0)} mm</div>
          <p className="mt-1 text-sm text-white/50">
            width ≈ {measurement.width_mm.toFixed(0)}mm · confidence {Math.round(measurement.confidence * 100)}%
          </p>
          <button onClick={() => setPhase("goals")} className="btn-volt mt-6 rounded-full px-8 py-3 text-sm">
            Continue to fit goals
          </button>
        </div>
      )}

      {phase === "goals" && (
        <div className="card mx-auto max-w-2xl rounded-2xl p-8">
          <h2 className="text-xl font-bold">What are you buying for?</h2>
          <p className="mt-1 text-sm text-white/60">This tunes which one8 model fits your use case best.</p>

          <div className="mt-6 space-y-5">
            <div>
              <div className="mb-2 text-sm font-semibold text-white/80">Sport</div>
              <SegmentedControl
                options={[
                  { value: "running", label: "Running" },
                  { value: "training", label: "Training" },
                  { value: "court", label: "Court" },
                  { value: "lifestyle", label: "Lifestyle" },
                ]}
                value={goals.sport}
                onChange={(v) => setGoals({ ...goals, sport: v })}
              />
            </div>
            <div>
              <div className="mb-2 text-sm font-semibold text-white/80">Surface</div>
              <SegmentedControl
                options={[
                  { value: "road", label: "Road" },
                  { value: "trail", label: "Trail" },
                  { value: "gym", label: "Gym" },
                  { value: "mixed", label: "Mixed" },
                ]}
                value={goals.surface}
                onChange={(v) => setGoals({ ...goals, surface: v })}
              />
            </div>
            <div>
              <div className="mb-2 text-sm font-semibold text-white/80">Cushioning feel</div>
              <SegmentedControl
                options={[
                  { value: "firm", label: "Firm" },
                  { value: "balanced", label: "Balanced" },
                  { value: "plush", label: "Plush" },
                ]}
                value={goals.cushioning}
                onChange={(v) => setGoals({ ...goals, cushioning: v })}
              />
            </div>
            <div>
              <div className="mb-2 text-sm font-semibold text-white/80">Use case</div>
              <SegmentedControl
                options={[
                  { value: "daily", label: "Daily" },
                  { value: "race", label: "Race day" },
                  { value: "recovery", label: "Recovery" },
                  { value: "allday", label: "All-day" },
                ]}
                value={goals.use_case}
                onChange={(v) => setGoals({ ...goals, use_case: v })}
              />
            </div>
          </div>

          <button onClick={() => setPhase("gait")} className="btn-volt mt-8 w-full rounded-full py-3 text-sm">
            Continue to run profile
          </button>
        </div>
      )}

      {phase === "gait" && (
        <div className="mx-auto max-w-md space-y-4">
          <CadenceTapper
            onComplete={async (cadence) => {
              try {
                const g = await scanGait({ cadence_spm: cadence });
                setGait(g);
                setGaitStatus("done");
              } catch {
                setGait(null);
                setGaitStatus("skipped");
              }
            }}
          />
          {gaitStatus === "done" && gait && (
            <div className="card rounded-2xl p-5 text-center">
              <p className="text-sm text-white/70">{gait.descriptor}</p>
              <button
                onClick={() => runMatching(gait)}
                className="btn-volt mt-4 rounded-full px-8 py-3 text-sm"
              >
                Get my matches
              </button>
            </div>
          )}
          <button
            onClick={() => {
              setGait(null);
              setGaitStatus("skipped");
              runMatching(null);
            }}
            className="block w-full text-center text-sm text-white/50 hover:underline"
          >
            Skip — match on fit &amp; goals only
          </button>
        </div>
      )}

      {phase === "matching" && (
        <div className="card rounded-2xl p-10 text-center">
          <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-volt-500 border-t-transparent" />
          <p className="mt-4 text-sm text-white/60">Ranking one8 models against your fit and profile…</p>
        </div>
      )}

      {phase === "results" && recs && measurement && (
        <div>
          <div className="mb-6 flex flex-wrap items-center justify-between gap-2">
            <div>
              <h2 className="text-2xl font-bold">Your matches</h2>
              <p className="text-sm text-white/50">
                Ranked by {ranker === "rules+llm" ? "fit + AI-tuned rationale" : "explainable rules engine"}.
              </p>
            </div>
            {ready && configured && (
              <button
                onClick={handleSave}
                disabled={!accessToken || saved === "saving" || saved === "saved"}
                className="rounded-full border border-white/15 px-4 py-2 text-sm text-white/80 hover:bg-white/5 disabled:opacity-50"
              >
                {!accessToken
                  ? "Sign in to save"
                  : saved === "saving"
                    ? "Saving…"
                    : saved === "saved"
                      ? "Saved ✓"
                      : "Save to history"}
              </button>
            )}
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            {recs.map((r, i) => (
              <RecommendationCard key={r.product_id} rec={r} rank={i + 1} />
            ))}
          </div>

          <div className="mt-12">
            <h3 className="mb-4 text-center text-lg font-semibold text-white/80">Share your fit card</h3>
            <FitCard measurement={measurement} top={recs[0]} />
          </div>

          <div className="mt-10 text-center">
            <button
              onClick={() => {
                setPhase("instructions");
                setMeasurement(null);
                setRecs(null);
                setPreview(null);
                setGait(null);
                setGaitStatus("pending");
                setSaved("idle");
              }}
              className="text-sm text-white/50 hover:underline"
            >
              Start a new scan
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
