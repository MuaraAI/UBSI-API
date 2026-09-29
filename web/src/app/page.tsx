import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { CodeShowcase } from "@/components/CodeShowcase";
import { ModulesGrid } from "@/components/ModulesGrid";
import { Architecture } from "@/components/Architecture";
import { ElementsGallery } from "@/components/ElementsGallery";
import { Quickstart } from "@/components/Quickstart";
import { Contributors } from "@/components/Contributors";
import { RoadmapTeaser } from "@/components/RoadmapTeaser";
import { Footer } from "@/components/Footer";
import { getGitHubStats } from "@/lib/github";

export const revalidate = 3600; // SWR cache at page root

export default async function Home() {
  const stats = await getGitHubStats();

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground selection:bg-accent/25 selection:text-foreground">
      {/* Ambient background blobs */}
      <div className="ambient-bg" aria-hidden="true">
        <div className="ambient-blob ambient-blob-1" />
        <div className="ambient-blob ambient-blob-2" />
        <div className="ambient-blob ambient-blob-3" />
      </div>
      {/* Grid overlay */}
      <div className="grid-overlay" aria-hidden="true" />

      <Navbar starsCount={stats.stars} />
      <main id="main-content" className="flex-1">
        <Hero />
        <CodeShowcase />
        <ModulesGrid />
        <Architecture />
        <ElementsGallery />
        <Quickstart />
        <RoadmapTeaser />
        <Contributors contributions={stats.contributors} />
      </main>
      <Footer />
    </div>
  );
}
