import React from "react";

export function Monogram({ className = "w-7 h-7" }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
      aria-hidden="true"
    >
      <rect width="32" height="32" rx="6" fill="#0e1726" />
      <path
        d="M8 24V11L16 19L24 11V24"
        stroke="#92EEFF"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <circle cx="16" cy="19" r="1.5" fill="#B8F5FF" />
    </svg>
  );
}
