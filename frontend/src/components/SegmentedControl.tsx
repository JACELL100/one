"use client";

interface Option<T extends string> {
  value: T;
  label: string;
  hint?: string;
}

const COLS: Record<number, string> = {
  2: "grid-cols-2",
  3: "grid-cols-3",
  4: "grid-cols-2 sm:grid-cols-4",
};

export default function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
}: {
  options: Option<T>[];
  value: T;
  onChange: (v: T) => void;
}) {
  const gridCls = COLS[options.length] ?? "grid-cols-2 sm:grid-cols-4";
  return (
    <div className={`grid gap-2 ${gridCls}`}>
      {options.map((opt) => {
        const active = opt.value === value;
        return (
          <button
            key={opt.value}
            type="button"
            onClick={() => onChange(opt.value)}
            className={`rounded-xl border px-3 py-3 text-left text-sm transition ${
              active
                ? "border-volt-500/60 bg-volt-500/10 text-white"
                : "border-white/10 bg-white/[0.02] text-white/70 hover:border-white/25 hover:bg-white/[0.05]"
            }`}
          >
            <div className="font-semibold capitalize">{opt.label}</div>
            {opt.hint && (
              <div className="mt-0.5 text-xs text-white/40">{opt.hint}</div>
            )}
          </button>
        );
      })}
    </div>
  );
}
