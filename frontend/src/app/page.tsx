import Link from "next/link";

const STEPS = [
  {
    n: "01",
    title: "Scan",
    body: "Photograph your foot on any A4 sheet. We use the sheet's known size to measure your foot in real millimetres.",
  },
  {
    n: "02",
    title: "Profile",
    body: "Tell us your sport, surface and feel. Add a short run clip and we read your gait — neutral, cushion or stability.",
  },
  {
    n: "03",
    title: "Match",
    body: "Get ranked one8 shoes with your exact size, a fit badge and a plain-language reason you can trust.",
  },
];

const IMPACT = [
  { stat: "~30%", label: "of footwear e-com is returned — mostly fit." },
  { stat: "< 8s", label: "from photo to sized recommendation." },
  { stat: "6", label: "one8 models tuned with per-model sizing." },
];

export default function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="bg-perf relative overflow-hidden rounded-3xl border border-white/10 px-6 py-20 text-center sm:py-28">
        <p className="mb-4 inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1 text-xs uppercase tracking-[0.25em] text-white/60">
          AI Fit & Performance Studio
        </p>
        <h1 className="mx-auto max-w-3xl text-4xl font-black leading-tight sm:text-6xl">
          Buy the <span className="text-gradient">right size</span>, the first
          time.
        </h1>
        <p className="mx-auto mt-5 max-w-xl text-base text-white/60 sm:text-lg">
          one8 FitLab measures your actual foot from a phone photo and matches
          it to how you move — so every pair fits, and far fewer come back.
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <Link
            href="/studio"
            className="btn-volt rounded-full px-7 py-3 text-base"
          >
            Scan my foot
          </Link>
          <a
            href="#how"
            className="rounded-full border border-white/15 px-7 py-3 text-base text-white/80 hover:bg-white/5"
          >
            How it works
          </a>
        </div>
      </section>

      {/* Impact strip */}
      <section className="mt-6 grid gap-4 sm:grid-cols-3">
        {IMPACT.map((i) => (
          <div key={i.label} className="card rounded-2xl p-6 text-center">
            <div className="text-3xl font-black text-volt-400">{i.stat}</div>
            <div className="mt-1 text-sm text-white/60">{i.label}</div>
          </div>
        ))}
      </section>

      {/* How it works */}
      <section id="how" className="mt-16">
        <h2 className="text-center text-2xl font-bold sm:text-3xl">
          Three steps. One perfect fit.
        </h2>
        <div className="mt-8 grid gap-5 md:grid-cols-3">
          {STEPS.map((s) => (
            <div key={s.n} className="card rounded-2xl p-6">
              <div className="text-sm font-black text-volt-500">{s.n}</div>
              <h3 className="mt-2 text-xl font-semibold">{s.title}</h3>
              <p className="mt-2 text-sm text-white/60">{s.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Why it matters */}
      <section className="mt-16 card rounded-3xl p-8 sm:p-12">
        <h2 className="text-2xl font-bold sm:text-3xl">
          Why this matters for one8
        </h2>
        <ul className="mt-6 grid gap-4 text-white/70 sm:grid-cols-2">
          <li>
            <span className="font-semibold text-white">Cut returns.</span> Fit
            is the #1 reason shoes come back. Measuring the real foot removes
            the guesswork that drives returns and refunds.
          </li>
          <li>
            <span className="font-semibold text-white">Lift conversion.</span>{" "}
            Confident shoppers check out more often — an explainable fit badge
            builds trust at the moment of decision.
          </li>
          <li>
            <span className="font-semibold text-white">
              Own the performance story.
            </span>{" "}
            Matching gait + goals to the right model reinforces one8&apos;s
            high-performance positioning.
          </li>
          <li>
            <span className="font-semibold text-white">Runs on free tiers.</span>{" "}
            Vercel + Render + Supabase with hosted inference — differentiated,
            not expensive.
          </li>
        </ul>
        <div className="mt-8">
          <Link
            href="/studio"
            className="btn-volt rounded-full px-7 py-3 text-base"
          >
            Try the studio
          </Link>
        </div>
      </section>
    </div>
  );
}
