"use client";

import { useState } from "react";
import Link from "next/link";

import { useAuth } from "@/lib/AuthProvider";

export default function LoginPage() {
  const { signInWithEmail, configured, user } = useAuth();
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const [message, setMessage] = useState<string | null>(null);

  if (!configured) {
    return (
      <div className="card mx-auto mt-10 max-w-md rounded-2xl p-8 text-center">
        <h1 className="text-xl font-bold">Sign-in not configured</h1>
        <p className="mt-2 text-sm text-white/60">
          This deployment hasn&apos;t set Supabase environment variables yet, so
          scan history is unavailable. The scan &amp; match experience at{" "}
          <Link href="/studio" className="text-volt-400 underline">
            /studio
          </Link>{" "}
          still works fully without an account.
        </p>
      </div>
    );
  }

  if (user) {
    return (
      <div className="card mx-auto mt-10 max-w-md rounded-2xl p-8 text-center">
        <h1 className="text-xl font-bold">You&apos;re signed in</h1>
        <p className="mt-2 text-sm text-white/60">{user.email}</p>
        <Link href="/history" className="btn-volt mt-6 inline-block rounded-full px-6 py-2 text-sm">
          View scan history
        </Link>
      </div>
    );
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setStatus("sending");
    setMessage(null);
    const { error } = await signInWithEmail(email);
    if (error) {
      setStatus("error");
      setMessage(error);
    } else {
      setStatus("sent");
    }
  }

  return (
    <div className="card mx-auto mt-10 max-w-md rounded-2xl p-8">
      <h1 className="text-xl font-bold">Sign in to save your scans</h1>
      <p className="mt-2 text-sm text-white/60">
        We use passwordless magic links via Supabase — no password to remember.
      </p>
      {status === "sent" ? (
        <div className="mt-6 rounded-xl border border-volt-500/40 bg-volt-500/10 px-4 py-3 text-sm text-volt-400">
          Check {email} for a sign-in link.
        </div>
      ) : (
        <form onSubmit={submit} className="mt-6 space-y-3">
          <input
            type="email"
            required
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full rounded-lg border border-white/15 bg-white/5 px-3 py-2 text-white outline-none focus:border-volt-500"
          />
          <button type="submit" disabled={status === "sending"} className="btn-volt w-full rounded-full py-3 text-sm">
            {status === "sending" ? "Sending…" : "Send magic link"}
          </button>
          {message && <p className="text-sm text-ember-500">{message}</p>}
        </form>
      )}
    </div>
  );
}
