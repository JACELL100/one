import type { FitBadge as FitBadgeKind } from "@/lib/api";

const MAP: Record<FitBadgeKind, { label: string; cls: string }> = {
  true: { label: "True fit", cls: "bg-volt-500/15 text-volt-400 border-volt-500/40" },
  snug: { label: "Snug", cls: "bg-ember-500/15 text-ember-500 border-ember-500/40" },
  roomy: { label: "Roomy", cls: "bg-sky-400/15 text-sky-300 border-sky-400/40" },
};

export default function FitBadge({ fit }: { fit: FitBadgeKind }) {
  const m = MAP[fit];
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${m.cls}`}
    >
      {m.label}
    </span>
  );
}
