"use client";

import type { Session, User } from "@supabase/supabase-js";
import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";

import { getSupabaseClient, supabaseConfigured } from "./supabase";

interface AuthState {
  ready: boolean;
  configured: boolean;
  session: Session | null;
  user: User | null;
  accessToken: string | null;
  signInWithEmail: (email: string) => Promise<{ error: string | null }>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const supabase = getSupabaseClient();
    if (!supabase) {
      setReady(true);
      return;
    }
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setReady(true);
    });
    const { data: sub } = supabase.auth.onAuthStateChange((_event, next) => {
      setSession(next);
    });
    return () => sub.subscription.unsubscribe();
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      ready,
      configured: supabaseConfigured,
      session,
      user: session?.user ?? null,
      accessToken: session?.access_token ?? null,
      async signInWithEmail(email: string) {
        const supabase = getSupabaseClient();
        if (!supabase) return { error: "Supabase is not configured." };
        const { error } = await supabase.auth.signInWithOtp({
          email,
          options: {
            emailRedirectTo:
              typeof window !== "undefined" ? window.location.origin + "/history" : undefined,
          },
        });
        return { error: error?.message ?? null };
      },
      async signOut() {
        const supabase = getSupabaseClient();
        if (supabase) await supabase.auth.signOut();
      },
    }),
    [ready, session]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
