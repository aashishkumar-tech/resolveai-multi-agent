import type { PropsWithChildren } from "react";

/**
 * Lightweight “Aceternity-like” spotlight background.
 * No external deps; uses pure CSS gradients.
 */
export function Spotlight({ children }: PropsWithChildren) {
  return (
    <div className="relative overflow-hidden rounded-3xl">
      <div
        aria-hidden
        className="pointer-events-none absolute -top-24 left-1/2 h-[420px] w-[820px] -translate-x-1/2 rounded-full bg-[radial-gradient(circle_at_center,rgba(56,189,248,0.26),rgba(139,92,246,0.14),transparent_60%)] blur-2xl"
      />
      <div
        aria-hidden
        className="pointer-events-none absolute -bottom-28 left-1/2 h-[380px] w-[820px] -translate-x-1/2 rounded-full bg-[radial-gradient(circle_at_center,rgba(139,92,246,0.22),rgba(56,189,248,0.12),transparent_60%)] blur-2xl"
      />
      <div className="relative">{children}</div>
    </div>
  );
}
