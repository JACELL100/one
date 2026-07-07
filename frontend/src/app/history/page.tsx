"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import FitBadge from "@/components/FitBadge";
import { type ScanHistoryItem, deleteScan, listScans } from "@/lib/api";
import { useAuth } from "@/lib/AuthProvider";

export default function HistoryPage() {
  const { ready, configured, user, accessToken } = useAuth();
  const [scans, setScans] = useState<ScanHistoryItem[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!accessToken) return;
    listScans(accessToken)
      .then(setScans)
      .catch(() => setError("Could not load your scan history."));
  }, [accessToken]);

  if (!ready) return null;

  if (!configured) {
    return (
      <div className="card mx-auto mt-10 max-w-md rounded-2xl p-8 text-center">
        <h1 className="text-xl font-bold">History unavailable</h1>
        <p className="mt-2 text-sm text-white/60">Supabase isn&apos;t configured on this deployment.</p>
      </div>
    );
  }

  if (!user) {
    return (
      <div className="card mx-auto mt-10 max-w-md rounded-2xl p-8 text-center">
        <h1 className="text-xl font-bold">Sign in to view history</h1>
        <Link href="/login" className="btn-volt mt-6 inline-block rounded-full px-6 py-2 text-sm">
          Sign in
        </Link>
      </div>
    );
  }

  async function handleDelete(id: string) {
    if (!accessToken) return;
    await deleteScan(accessToken, id);
    setScans((prev) => (prev ? prev.filter((s) => s.id !== id) : prev));
  }

  return (
    <div className="mx-auto max-w-3xl py-8">
      <h1 className="text-2xl font-bold">Your scan history</h1>
      <p className="mt-1 text-sm text-white/50">Saved scans for {user.email}.</p>

      {error && <p className="mt-6 text-sm text-ember-500">{error}</p>}

      {scans === null && !error && <p className="mt-6 text-sm text-white/50">Loading…</p>}

      {scans?.length === 0 && (
        <div className="card mt-6 rounded-2xl p-8 text-center">
          <p className="text-sm text-white/60">No saved scans yet.</p>
          <Link href="/studio" className="btn-volt mt-4 inline-block rounded-full px-6 py-2 text-sm">
            Run a scan
          </Link>
        </div>
      )}

      <div className="mt-6 space-y-4">
        {scans?.map((s) => {
          const top = s.recommendations[0];
          return (
            <div key={s.id} className="card flex items-center justify-between gap-4 rounded-2xl p-5">
              <div className="min-w-0">
                <div className="text-xs text-white/40">{new Date(s.created_at).toLocaleString()}</div>
                <div className="mt-1 text-sm text-white/70">
                  {s.measurement.length_mm.toFixed(0)}mm foot · {s.goals?.sport ?? "—"} · {s.goals?.surface ?? "—"}
                </div>
                {top && (
                  <div className="mt-2 flex items-center gap-2">
                    <span className="font-semibold">{top.name}</span>
                    <FitBadge fit={top.fit} />
                    <span className="text-sm text-white/60">{top.size_label}</span>
                  </div>
                )}
              </div>
              <button
                onClick={() => handleDelete(s.id)}
                className="shrink-0 rounded-full border border-white/15 px-4 py-2 text-xs text-white/60 hover:border-ember-500/50 hover:text-ember-500"
              >
                Delete
              </button>
            </div>
          );
        })}
      </div>
    </div>
  );
}
