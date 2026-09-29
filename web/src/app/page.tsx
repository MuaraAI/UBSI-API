import { Navbar } from "@/components/Navbar";
import { Hero } from "@/components/Hero";
import { CodeShowcase } from "@/components/CodeShowcase";
import { ModulesGrid } from "@/components/ModulesGrid";
import { Architecture } from "@/components/Architecture";
import { Quickstart } from "@/components/Quickstart";
import { Contributors } from "@/components/Contributors";
import { RoadmapTeaser } from "@/components/RoadmapTeaser";
import { Footer } from "@/components/Footer";
import { getGitHubStats } from "@/lib/github";

export const revalidate = 3600; // SWR cache at page root

export default async function Home() {
  const stats = await getGitHubStats();

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground selection:bg-accent selection:text-accent-dark">
      <Navbar starsCount={stats.stars} />
      <main id="main-content" className="flex-1">
        <Hero />
        <CodeShowcase />
        <ModulesGrid />
        <Architecture />
        <Quickstart />
        <RoadmapTeaser />
        <Contributors contributions={stats.contributors} />
      </main>
      <Footer />
    </div>
  );
}
