"use client";

import { useMemo, useState } from "react";

export type TracePayload = {
  trace_id?: string;
  duration_s?: number;
  activity_log?: Array<Record<string, any>>;
  team_outputs?: Record<string, any>;
  saved_dir?: string;
  graph_png_url?: string;
};

function Disclosure({
  title,
  children,
  defaultOpen = false,
}: {
  title: string;
  children: React.ReactNode;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  return (
    <div className="rounded-2xl border border-white/10 bg-black/20">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center justify-between px-4 py-3 text-left"
      >
        <div className="text-xs font-semibold text-white/80">{title}</div>
        <div className="text-xs text-white/50">{open ? "Hide" : "Show"}</div>
      </button>
      {open ? <div className="border-t border-white/10 px-4 py-3">{children}</div> : null}
    </div>
  );
}

export function TracePanel({ trace }: { trace: TracePayload | null }) {
  const activity = useMemo(() => trace?.activity_log ?? [], [trace]);
  const outputs = useMemo(() => trace?.team_outputs ?? {}, [trace]);

  return (
    <div className="flex flex-col gap-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="text-sm font-semibold">Run details</div>
      </div>

      <div className="grid gap-2 text-xs text-white/70 md:grid-cols-2">
        <div className="rounded-xl border border-white/10 bg-black/20 p-3">
          <div className="text-white/90">Run ID</div>
          <div className="font-mono break-all">{trace?.trace_id ?? "—"}</div>
        </div>
        <div className="rounded-xl border border-white/10 bg-black/20 p-3">
          <div className="text-white/90">Time taken</div>
          <div className="font-mono">{trace?.duration_s != null ? `${trace.duration_s}s` : "—"}</div>
        </div>
        <div className="rounded-xl border border-white/10 bg-black/20 p-3 md:col-span-2">
          <div className="text-white/90">Saved files (server path)</div>
          <div className="font-mono break-all">{trace?.saved_dir ?? "—"}</div>
        </div>
      </div>

      {trace?.graph_png_url ? (
        <Disclosure title="Workflow diagram" defaultOpen={false}>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src={trace.graph_png_url} alt="workflow graph" className="w-full rounded-xl" />
          <div className="mt-2 text-[11px] text-white/50">
            Shows the internal steps used to generate the answer.
          </div>
        </Disclosure>
      ) : null}

      <Disclosure title="Internal activity log" defaultOpen={false}>
        <div className="max-h-[320px] overflow-auto">
          <pre className="whitespace-pre-wrap break-words text-xs text-white/70">
            {activity.length ? JSON.stringify(activity, null, 2) : "—"}
          </pre>
        </div>
      </Disclosure>

      <Disclosure title="Agent outputs (raw)" defaultOpen={false}>
        <div className="max-h-[320px] overflow-auto">
          <pre className="whitespace-pre-wrap break-words text-xs text-white/70">
            {Object.keys(outputs).length ? JSON.stringify(outputs, null, 2) : "—"}
          </pre>
        </div>
      </Disclosure>
    </div>
  );
}
