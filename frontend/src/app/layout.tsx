import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/lib/AuthProvider";
import SiteHeader from "@/components/SiteHeader";

export const metadata: Metadata = {
  title: "one8 FitLab — AI Fit & Performance Studio",
  description:
    "Scan your foot with your phone, profile your run, and get the right one8 shoe — with an explainable fit. Built to cut returns and lift conversion.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans antialiased">
        <AuthProvider>
          <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-5">
            <SiteHeader />
            <main className="flex-1">{children}</main>
            <footer className="py-10 text-center text-xs text-white/40">
              one8 FitLab — portfolio concept for the one8 brand. Not
              affiliated; catalog is illustrative.
            </footer>
          </div>
        </AuthProvider>
      </body>
    </html>
  );
}
