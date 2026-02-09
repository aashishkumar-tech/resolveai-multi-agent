import type { ReactNode } from "react";

type Pill = {
  text: string;
  icon?: ReactNode;
};

export function FeaturePills({ items }: { items: Pill[] }) {
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((p) => (
        <div
          key={p.text}
          className="inline-flex items-center gap-2 rounded-xl border border-white/10 bg-black/25 px-3 py-2 text-xs text-white/70 backdrop-blur-xl"
        >
          {p.icon}
          <span className="whitespace-nowrap">{p.text}</span>
        </div>
      ))}
    </div>
  );
}
