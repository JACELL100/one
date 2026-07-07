"use client";

import Link from "next/link";

import { useAuth } from "@/lib/AuthProvider";

export default function SiteHeader() {
  const { ready, configured, user, signOut } = useAuth();

  return (
    <header className="flex items-center justify-between py-6">
      <Link href="/" className="flex items-center gap-2">
        <span className="text-2xl font-black tracking-tight">
          one<span className="text-volt-500">8</span>
        </span>
        <span className="hidden text-sm uppercase tracking-[0.3em] text-white/50 sm:inline">
          FitLab
        </span>
      </Link>
      <nav className="flex items-center gap-4 text-sm text-white/70 sm:gap-6">
        <Link href="/studio" className="hover:text-white">
          Studio
        </Link>
        {configured && (
          <Link href="/history" className="hidden hover:text-white sm:inline">
            History
          </Link>
        )}
        {ready && configured && (
          user ? (
            <button onClick={() => signOut()} className="hidden text-white/50 hover:text-white sm:inline">
              Sign out
            </button>
          ) : (
            <Link href="/login" className="hidden hover:text-white sm:inline">
              Sign in
            </Link>
          )
        )}
        <Link href="/studio" className="btn-volt rounded-full px-4 py-2 text-sm">
          Start scan
        </Link>
      </nav>
    </header>
  );
}
