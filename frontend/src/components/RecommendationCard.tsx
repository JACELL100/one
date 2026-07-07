import type { Recommendation } from "@/lib/api";
import FitBadge from "./FitBadge";

export default function RecommendationCard({
  rec,
  rank,
}: {
  rec: Recommendation;
  rank: number;
}) {
  const pct = Math.round(rec.match_score * 100);
  return (
    <div className="card relative overflow-hidden rounded-2xl p-5">
      {rank === 1 && (
        <span className="absolute right-4 top-4 rounded-full bg-volt-500 px-3 py-1 text-[10px] font-black uppercase tracking-wide text-ink-950">
          Best match
        </span>
      )}
      <div className="flex items-start gap-4">
        <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-xl bg-white/5 p-2">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={rec.image_url} alt={rec.name} className="h-full w-full object-contain" />
        </div>
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2 text-xs text-white/40">#{rank}</div>
          <h3 className="truncate text-lg font-bold">{rec.name}</h3>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            <FitBadge fit={rec.fit} />
            <span className="rounded-full border border-white/10 px-2.5 py-0.5 text-xs text-white/70">
              {rec.size_label}
            </span>
            <span className="text-sm font-semibold text-white/80">
              ₹{rec.price_inr.toLocaleString("en-IN")}
            </span>
          </div>
        </div>
      </div>

      <p className="mt-4 text-sm leading-relaxed text-white/70">{rec.rationale}</p>

      <div className="mt-4">
        <div className="mb-1 flex items-center justify-between text-xs text-white/40">
          <span>Match score</span>
          <span className="font-semibold text-volt-400">{pct}%</span>
        </div>
        <div className="h-1.5 w-full overflow-hidden rounded-full bg-white/10">
          <div
            className="h-full rounded-full bg-gradient-to-r from-volt-600 to-volt-400"
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
    </div>
  );
}
