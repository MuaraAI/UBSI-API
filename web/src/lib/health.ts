import { HealthStatus } from "@/types";

export async function checkApiHealth(): Promise<HealthStatus> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl) {
    return {
      status: "standby",
      redis: "unknown",
    };
  }

  const cleanUrl = apiUrl.replace(/\/+$/, "");
  const startTime = Date.now();

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000);

    const res = await fetch(`${cleanUrl}/health`, {
      signal: controller.signal,
      headers: { Accept: "application/json" },
      cache: "no-store",
    });
    clearTimeout(timeoutId);

    const latencyMs = Date.now() - startTime;
    if (res.ok) {
      const data = await res.json();
      return {
        status: data.status === "ok" ? "ok" : "degraded",
        redis: data.redis === "up" ? "up" : "down",
        latencyMs,
      };
    }

    return {
      status: "degraded",
      redis: "unknown",
      latencyMs,
    };
  } catch {
    return {
      status: "down",
      redis: "unknown",
    };
  }
}
