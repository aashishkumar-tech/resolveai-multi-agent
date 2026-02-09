import type { ButtonHTMLAttributes, PropsWithChildren } from "react";

export function GlowButton({
  children,
  className = "",
  ...props
}: PropsWithChildren<ButtonHTMLAttributes<HTMLButtonElement>> & { className?: string }) {
  return (
    <button
      {...props}
      className={
        "relative inline-flex items-center justify-center gap-2 rounded-xl bg-gradient-to-b from-blue-500 to-blue-700 px-4 py-2 text-sm font-semibold text-white shadow-[0_10px_30px_rgba(37,99,235,0.35)] ring-1 ring-white/15 transition hover:from-blue-400 hover:to-blue-700 active:translate-y-px disabled:opacity-50 " +
        className
      }
    >
      <span className="pointer-events-none absolute inset-0 rounded-xl bg-[radial-gradient(circle_at_30%_20%,rgba(255,255,255,0.35),transparent_35%)]" />
      <span className="relative">{children}</span>
    </button>
  );
}
