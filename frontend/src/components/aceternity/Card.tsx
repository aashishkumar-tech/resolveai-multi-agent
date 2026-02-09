import type { PropsWithChildren } from "react";

export function Card({ children }: PropsWithChildren) {
  return (
    <div className="relative rounded-2xl border border-card-border bg-card shadow-glow backdrop-blur-xl">
      <div className="pointer-events-none absolute inset-0 rounded-2xl bg-gradient-to-b from-white/10 to-transparent" />
      <div className="relative p-5 md:p-6">{children}</div>
    </div>
  );
}
