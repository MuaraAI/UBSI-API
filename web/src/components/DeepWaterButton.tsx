import React from "react";
import { cva, type VariantProps } from "class-variance-authority";

/**
 * Deep Water button system.
 * Variants mirror the two CTA styles already used on the landing page
 * (solid teal primary, navy surface secondary) with polished
 * hover/focus/active states and an optional sliding shine effect.
 */

const buttonVariants = cva(
  // Base
  [
    "group relative inline-flex items-center justify-center gap-2 overflow-hidden",
    "font-semibold text-sm rounded-md select-none",
    "transition-all duration-200 ease-out",
    "focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#2DD4BF]",
    "active:scale-[0.97]",
    "disabled:opacity-50 disabled:pointer-events-none",
  ].join(" "),
  {
    variants: {
      variant: {
        primary: [
          "bg-[#2DD4BF] text-[#06251F] shadow-float",
          "hover:bg-[#54E3D1] hover:shadow-[0_8px_30px_rgba(45,212,191,0.35)]",
          "hover:-translate-y-0.5",
        ].join(" "),
        secondary: [
          "bg-[#111C2E] text-[#E6EDF3] border border-white/10",
          "hover:bg-[#17263D] hover:border-[#2DD4BF]/50",
          "hover:-translate-y-0.5 hover:shadow-[0_8px_30px_rgba(0,0,0,0.35)]",
        ].join(" "),
        ghost: [
          "bg-transparent text-[#94A7BC]",
          "hover:text-[#E6EDF3] hover:bg-[#111C2E]",
        ].join(" "),
      },
      size: {
        sm: "px-3 py-1.5 text-xs",
        md: "px-6 py-3 text-sm",
        lg: "px-7 py-3.5 text-sm sm:text-base",
      },
      shine: {
        true: "dw-shine",
        false: "",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
      shine: false,
    },
  }
);

export type DeepWaterButtonProps = React.ButtonHTMLAttributes<HTMLButtonElement> &
  VariantProps<typeof buttonVariants>;

export function DeepWaterButton({
  className,
  variant,
  size,
  shine,
  children,
  ...props
}: DeepWaterButtonProps) {
  return (
    <button className={buttonVariants({ variant, size, shine, className })} {...props}>
      {shine ? (
        <span
          aria-hidden="true"
          className="absolute inset-0 -translate-x-full bg-[linear-gradient(110deg,transparent_30%,rgba(255,255,255,0.25)_50%,transparent_70%)] transition-transform duration-700 ease-out group-hover:translate-x-full"
        />
      ) : null}
      <span className="relative z-10 inline-flex items-center gap-2">{children}</span>
    </button>
  );
}

export type DeepWaterLinkProps = React.ComponentPropsWithoutRef<"a"> &
  VariantProps<typeof buttonVariants>;

export function DeepWaterLink({
  className,
  variant,
  size,
  shine,
  children,
  ...props
}: DeepWaterLinkProps) {
  return (
    <a className={buttonVariants({ variant, size, shine, className })} {...props}>
      {shine ? (
        <span
          aria-hidden="true"
          className="absolute inset-0 -translate-x-full bg-[linear-gradient(110deg,transparent_30%,rgba(255,255,255,0.25)_50%,transparent_70%)] transition-transform duration-700 ease-out group-hover:translate-x-full"
        />
      ) : null}
      <span className="relative z-10 inline-flex items-center gap-2">{children}</span>
    </a>
  );
}
