"use client";

import React, { useEffect, useState } from "react";
import { checkApiHealth } from "@/lib/health";
import { HealthStatus } from "@/types";

export function HealthBadge() {
  const [health, setHealth] = useState<HealthStatus>({
    status: "standby",
    redis: "unknown",
  });

  useEffect(() => {
    checkApiHealth().then(setHealth);
    const interval = setInterval(() => {
      checkApiHealth().then(setHealth);
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  if (health.status === "ok") {
    return (
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0A1220] border border-[#2DD4BF]/30 text-xs font-mono text-[#E6EDF3]">
        <span className="relative flex h-2 w-2">
          <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
          <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
        </span>
        <span className="text-[#2DD4BF] font-semibold">LIVE v1.1.0</span>
        {health.latencyMs && (
          <span className="text-[#94A7BC] hidden sm:inline">({health.latencyMs}ms)</span>
        )}
      </div>
    );
  }

  if (health.status === "standby") {
    return (
      <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0A1220] border border-white/10 text-xs font-mono text-[#94A7BC]">
        <span className="inline-flex rounded-full h-2 w-2 bg-[#94A7BC]"></span>
        <span>v1.1.0 STABLE</span>
      </div>
    );
  }

  return (
    <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0A1220] border border-amber-500/30 text-xs font-mono text-amber-300">
      <span className="inline-flex rounded-full h-2 w-2 bg-amber-400"></span>
      <span>CHECKING / OFFLINE</span>
    </div>
  );
}
