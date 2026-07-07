"use client";

export default function Stepper({
  steps,
  current,
}: {
  steps: string[];
  current: number;
}) {
  return (
    <div className="mb-8 flex items-center gap-1.5 sm:gap-2">
      {steps.map((label, i) => {
        const done = i < current;
        const active = i === current;
        return (
          <div key={label} className="flex flex-1 items-center gap-1.5 sm:gap-2">
            <div className="flex flex-1 flex-col items-center gap-2">
              <div
                className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-bold transition ${
                  done
                    ? "bg-volt-500 text-ink-950"
                    : active
                      ? "border-2 border-volt-500 text-volt-400"
                      : "border border-white/15 text-white/40"
                }`}
              >
                {done ? "✓" : i + 1}
              </div>
              <span
                className={`hidden text-center text-[11px] uppercase tracking-wide sm:block ${
                  active ? "text-white" : "text-white/40"
                }`}
              >
                {label}
              </span>
            </div>
            {i < steps.length - 1 && (
              <div className={`h-px flex-1 ${done ? "bg-volt-500" : "bg-white/10"}`} />
            )}
          </div>
        );
      })}
    </div>
  );
}
