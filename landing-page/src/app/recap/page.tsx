import type { Metadata } from "next";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { RecapDashboard } from "@/components/RecapDashboard";
import { getGitHubStats } from "@/lib/github";

export const metadata: Metadata = {
  title: "Rekap Nilai Tugas & Kuis — UBSI API",
  description:
    "Dashboard rekap nilai tugas dan kuis MyBest Elearning per pertemuan, ditarik langsung dari backend UBSI API milik Anda sendiri.",
};

export const revalidate = 3600;

export default async function RecapPage() {
  const stats = await getGitHubStats();

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <div className="ambient-bg" aria-hidden="true">
        <div className="ambient-blob ambient-blob-1" />
        <div className="ambient-blob ambient-blob-2" />
        <div className="ambient-blob ambient-blob-3" />
        <div className="ambient-blob ambient-blob-4" />
      </div>
      <div className="grid-overlay" aria-hidden="true" />

      <Navbar starsCount={stats.stars} />
      <main id="main-content" className="flex-1">
        <RecapDashboard />
      </main>
      <Footer />
    </div>
  );
}
