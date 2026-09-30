export interface CampusModule {
  id: string;
  name: string;
  service: string;
  description: string;
  endpointsCount: number;
  endpoints: string[];
  status: "Active" | "Cached" | "SWR";
}

export interface CodeExample {
  language: "curl" | "python" | "typescript";
  title: string;
  snippet: string;
  response: string;
  latencyMs: number;
}

export interface Contributor {
  name: string;
  username: string;
  role: string;
  nim: string;
  prodi: string;
  kelas: string;
  avatarUrl: string;
  profileUrl: string;
  fallbackCommits: number;
}

export interface RoadmapItem {
  version: string;
  title: string;
  description: string;
  badge: string;
  status: "upcoming" | "in-progress" | "planned";
}

export interface GitHubStats {
  stars: number;
  contributors: { [username: string]: number };
}
