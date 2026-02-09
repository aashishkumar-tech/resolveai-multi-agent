"use client";

import { useLayoutEffect, useMemo, useRef, useState, type ReactNode } from "react";

export type TabItem = {
  key: string;
  label: string;
  icon?: ReactNode;
};

type Props = {
  items: TabItem[];
  value?: string;
  onChange?: (key: string) => void;
};

/**
 * Tabs with a pill background for the active item.
 * (No moving animation; stable sizing to avoid misalignment.)
 */
export function AnimatedTabs({ items, value, onChange }: Props) {
  const [internal, setInternal] = useState(items[0]?.key ?? "");
  const active = value ?? internal;

  const containerRef = useRef<HTMLDivElement | null>(null);
  const itemRefs = useRef<Record<string, HTMLButtonElement | null>>({});

  const [pill, setPill] = useState<{ left: number; width: number }>({ left: 4, width: 60 });

  const activeIndex = useMemo(
    () => Math.max(0, items.findIndex((i) => i.key === active)),
    [items, active],
  );

  useLayoutEffect(() => {
    const container = containerRef.current;
    const el = itemRefs.current[active];
    if (!container || !el) return;

    const c = container.getBoundingClientRect();
    const r = el.getBoundingClientRect();

    // 4px because of p-1 on container
    setPill({
      left: Math.max(4, r.left - c.left),
      width: Math.max(44, r.width),
    });
  }, [active, activeIndex, items.length]);

  const set = (k: string) => {
    if (onChange) onChange(k);
    else setInternal(k);
  };

  return (
    <div
      ref={containerRef}
      className="relative inline-flex max-w-full flex-wrap gap-1 rounded-2xl border border-white/10 bg-black/25 p-1 backdrop-blur-xl"
    >
      <div
        aria-hidden
        className="pointer-events-none absolute inset-y-1 rounded-xl bg-gradient-to-r from-cyan-400/30 via-violet-400/25 to-pink-400/20 shadow-[0_0_0_1px_rgba(255,255,255,0.06)]"
        style={{ left: pill.left, width: pill.width }}
      />

      {items.map((t) => (
        <button
          key={t.key}
          ref={(node) => {
            itemRefs.current[t.key] = node;
          }}
          type="button"
          onClick={() => set(t.key)}
          className={
            "relative z-10 flex items-center gap-2 rounded-xl px-3 py-2 text-xs " +
            (t.key === active ? "text-white" : "text-white/65 hover:text-white/85")
          }
        >
          {t.icon}
          <span className="whitespace-nowrap">{t.label}</span>
        </button>
      ))}
    </div>
  );
}
