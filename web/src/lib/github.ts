import { GitHubStats } from "@/types";

export async function getGitHubStats(): Promise<GitHubStats> {
  const defaultStats: GitHubStats = {
    stars: 2,
    contributors: {
      Curzyori: 28,
      MyKineID: 6,
    },
  };

  try {
    const [repoRes, contribRes] = await Promise.all([
      fetch("https://api.github.com/repos/MuaraAI/UBSI-API", {
        next: { revalidate: 3600 },
        headers: { Accept: "application/vnd.github.v3+json" },
      }),
      fetch("https://api.github.com/repos/MuaraAI/UBSI-API/contributors", {
        next: { revalidate: 3600 },
        headers: { Accept: "application/vnd.github.v3+json" },
      }),
    ]);

    if (!repoRes.ok || !contribRes.ok) {
      return defaultStats;
    }

    const repoData = await repoRes.json();
    const contribData = await contribRes.json();

    const contributorsMap: { [username: string]: number } = {};
    if (Array.isArray(contribData)) {
      contribData.forEach((c: { login: string; contributions: number }) => {
        contributorsMap[c.login] = c.contributions;
      });
    }

    return {
      stars: repoData.stargazers_count ?? defaultStats.stars,
      contributors:
        Object.keys(contributorsMap).length > 0
          ? contributorsMap
          : defaultStats.contributors,
    };
  } catch {
    return defaultStats;
  }
}
