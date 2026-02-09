import type { PropsWithChildren } from "react";

type Props = PropsWithChildren<{
  className?: string;
}>;

/**
 * Static gradient border wrapper (no animation / no moving light).
 */
export function ShimmerBorder({ children, className }: Props) {
  return (
    <div className={"relative rounded-3xl p-[1px] " + (className ?? "")}>
      <div
        aria-hidden
        className="pointer-events-none absolute inset-0 rounded-3xl bg-[linear-gradient(135deg,rgba(56,189,248,0.55),rgba(139,92,246,0.45),rgba(236,72,153,0.30))] opacity-70"
      />
      <div className="relative rounded-3xl border border-white/10 bg-black/20 backdrop-blur-xl">
        {children}
      </div>
    </div>
  );
}
