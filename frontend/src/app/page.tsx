"use client";

import { useMemo, useRef, useState, type ChangeEvent, type FormEvent } from "react";
import { Card } from "../components/aceternity/Card";
import { Container } from "../components/aceternity/Container";
import { GlowButton } from "../components/aceternity/GlowButton";
import { ShimmerBorder } from "../components/aceternity/ShimmerBorder";
import { AnimatedTabs } from "../components/aceternity/AnimatedTabs";
import { FeaturePills } from "../components/aceternity/FeaturePills";
import { chat, type ChatRequest } from "../lib/api";
import { TracePanel, type TracePayload } from "../components/trace/TracePanel";

type ChatMessage =
  | { role: "user"; content: string; ts: number }
  | { role: "assistant"; content: string; ts: number };

function formatPhone(value: string) {
  return value.replace(/[^0-9+]/g, "").slice(0, 16);
}

function splitSections(text: string): Array<{ title: string; body: string }> {
  // Very small heuristic: split on common headings.
  const lines = text.split(/\r?\n/);
  const sections: Array<{ title: string; body: string }> = [];

  let currentTitle = "Answer";
  let buf: string[] = [];
  const push = () => {
    const body = buf.join("\n").trim();
    if (body) sections.push({ title: currentTitle, body });
    buf = [];
  };

  const headingRe = /^(greeting|summary|steps|next steps|closing|resolution|what to do next)\s*[:\-]?$/i;
  for (const raw of lines) {
    const line = raw.trim();
    if (headingRe.test(line)) {
      push();
      currentTitle = line.replace(/[:\-]+$/, "").replace(/^\w/, (c) => c.toUpperCase());
      continue;
    }
    buf.push(raw);
  }
  push();

  return sections.length ? sections : [{ title: "Answer", body: text.trim() }];
}

export default function Page() {
  const [customerName, setCustomerName] = useState("");
  const [mobileNumber, setMobileNumber] = useState("");

  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  const [traceId, setTraceId] = useState<string | null>(null);
  const [trace, setTrace] = useState<TracePayload | null>(null);
  const [showDetails, setShowDetails] = useState(false);
  const [showLatestAnswer, setShowLatestAnswer] = useState(true);
  const [lastDurationS, setLastDurationS] = useState<number | null>(null);

  const lastUserQueryRef = useRef<string | null>(null);

  const [activeTab, setActiveTab] = useState<"chat" | "answer" | "details">("chat");

  const canSend = useMemo(() => input.trim().length > 0 && !loading, [input, loading]);

  async function fetchTrace(runTraceId: string) {
    const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";
    const t = await fetch(`${baseUrl}/runs/${runTraceId}`).then((r) => r.json());
    const graph_png_url = t.graph_png_url ? `${baseUrl}${t.graph_png_url}` : undefined;
    setTrace({ ...t, graph_png_url });
  }

  async function sendQuery(query: string) {
    setLoading(true);
    setTrace(null);
    setTraceId(null);
    setLastDurationS(null);

    const payload: ChatRequest = {
      query,
      customer_name: customerName.trim() || undefined,
      mobile_number: mobileNumber.trim() || undefined,
    };

    try {
      const res = await chat(payload);
      setTraceId(res.trace_id ?? null);
      setLastDurationS(res.duration_s ?? null);

      // Add assistant message
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: res.final_response, ts: Date.now() },
      ]);

      if (res.trace_id && showDetails) {
        await fetchTrace(res.trace_id);
      }
    } finally {
      setLoading(false);
    }
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    const q = input.trim();
    if (!q) return;

    lastUserQueryRef.current = q;

    setMessages((prev) => [...prev, { role: "user", content: q, ts: Date.now() }]);
    setInput("");
    await sendQuery(q);
  }

  async function onRegenerate() {
    const q = lastUserQueryRef.current;
    if (!q || loading) return;
    await sendQuery(q);
  }

  function onClear() {
    setMessages([]);
    setInput("");
    setTrace(null);
    setTraceId(null);
    setLastDurationS(null);
    lastUserQueryRef.current = null;
  }

  async function onCopyLast() {
    const last = [...messages].reverse().find((m) => m.role === "assistant");
    if (!last) return;
    await navigator.clipboard.writeText(last.content);
  }

  const lastAssistant = useMemo(
    () => [...messages].reverse().find((m) => m.role === "assistant") ?? null,
    [messages],
  );

  const sections = useMemo(() => {
    if (!lastAssistant) return [];
    return splitSections(lastAssistant.content);
  }, [lastAssistant]);

  const combinedStructured = useMemo(() => {
    if (!sections.length) return "";
    return sections.map((s) => `**${s.title}**\n\n${s.body}`.trim()).join("\n\n");
  }, [sections]);

  return (
    <Container>
      <div className="mx-auto flex w-full max-w-5xl flex-col gap-6">
        {/* Header + tabs */}
        <ShimmerBorder>
          <div className="p-5 md:p-6">
            <div className="flex flex-col gap-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div className="flex items-center gap-3">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <div className="flex h-12 w-12 items-center justify-center rounded-2xl border border-white/10 bg-white/90 p-1">
                    <img
                      src="/logo.PNG"
                      alt="ResolveAI logo"
                      className="h-full w-full rounded-xl object-contain"
                    />
                  </div>

                  <div className="leading-tight">
                    <div className="text-3xl font-semibold tracking-tight">
                      <span>Resolve</span>
                      <span className="relative ml-0.5 inline-flex align-baseline">
                        <span
                          aria-hidden
                          className="bg-gradient-to-r from-cyan-300 to-violet-300 bg-clip-text text-transparent [animation:aiTypeCycle_4.2s_steps(2,end)_infinite]"
                          style={{ display: "inline-block", overflow: "hidden", whiteSpace: "nowrap" }}
                        >
                          AI
                        </span>
                        <span className="sr-only">AI</span>
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-white/70">
                      Fast, clear support answers — personalized for your customer.
                    </p>
                  </div>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                  <button
                    type="button"
                    onClick={onClear}
                    className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-xs text-white/75 hover:bg-white/5"
                  >
                    Clear
                  </button>
                  <button
                    type="button"
                    onClick={onRegenerate}
                    disabled={!lastUserQueryRef.current || loading}
                    className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-xs text-white/75 hover:bg-white/5 disabled:opacity-50"
                  >
                    Regenerate
                  </button>
                  <button
                    type="button"
                    onClick={onCopyLast}
                    disabled={!lastAssistant}
                    className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-xs text-white/75 hover:bg-white/5 disabled:opacity-50"
                  >
                    Copy answer
                  </button>
                </div>
              </div>

              <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <AnimatedTabs
                  value={activeTab}
                  onChange={(k) => setActiveTab(k as any)}
                  items={[
                    { key: "chat", label: "Chat" },
                    { key: "answer", label: "Latest answer" },
                    { key: "details", label: "Details" },
                  ]}
                />

                <div className="text-xs text-white/55">
                  {loading ? "Generating…" : lastDurationS != null ? `Time taken: ${lastDurationS}s` : ""}
                </div>
              </div>

              <FeaturePills
                items={[
                  { text: "Personalized" },
                  { text: "Search + reasoning" },
                  { text: "Saved runs" },
                  { text: "Workflow graph" },
                ]}
              />

              <style jsx>{`
                @keyframes aiTypeCycle {
                  0% {
                    width: 0ch;
                    opacity: 0.15;
                  }
                  20% {
                    width: 2ch;
                    opacity: 1;
                  }
                  55% {
                    width: 2ch;
                    opacity: 1;
                  }
                  75% {
                    width: 0ch;
                    opacity: 0.2;
                  }
                  100% {
                    width: 0ch;
                    opacity: 0.15;
                  }
                }
              `}</style>
            </div>
          </div>
        </ShimmerBorder>

        {/* Customer info */}
        <Card>
          <div className="grid gap-4 sm:grid-cols-2">
            <div className="flex flex-col gap-2">
              <label className="text-sm text-white/70">Customer name</label>
              <input
                value={customerName}
                onChange={(e) => setCustomerName(e.target.value)}
                placeholder="e.g., Aashish Kumar"
                className="w-full rounded-xl border border-card-border bg-black/25 px-4 py-3 text-sm outline-none placeholder:text-white/35 focus:border-white/20"
              />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-sm text-white/70">Mobile number</label>
              <input
                value={mobileNumber}
                onChange={(e) => setMobileNumber(formatPhone(e.target.value))}
                placeholder="e.g., +91XXXXXXXXXX"
                className="w-full rounded-xl border border-card-border bg-black/25 px-4 py-3 text-sm outline-none placeholder:text-white/35 focus:border-white/20"
              />
              <div className="text-xs text-white/45">Used only to personalize the response.</div>
            </div>
          </div>
        </Card>

        {/* Chat */}
        {activeTab === "chat" ? (
          <Card>
            <div className="flex flex-col gap-4">
              <div className="flex items-center justify-between">
                <div className="text-sm font-semibold">Conversation</div>
                <div className="text-xs text-white/50">
                  {messages.length ? `${messages.length} messages` : ""}
                </div>
              </div>

              <div className="max-h-[360px] overflow-auto rounded-2xl border border-white/10 bg-black/10 p-3">
                {messages.length === 0 ? (
                  <div className="text-sm text-white/60">
                    Ask a question to start. Example: “My payment failed but money was deducted.”
                  </div>
                ) : (
                  <div className="flex flex-col gap-3">
                    {messages.map((m) => (
                      <div
                        key={m.ts}
                        className={
                          "max-w-[90%] rounded-2xl border px-4 py-3 text-sm leading-relaxed " +
                          (m.role === "user"
                            ? "ml-auto border-white/10 bg-white/5 text-white/90"
                            : "mr-auto border-white/10 bg-black/25 text-white/85")
                        }
                      >
                        <div className="whitespace-pre-wrap">{m.content}</div>
                      </div>
                    ))}
                    {loading ? (
                      <div className="mr-auto max-w-[90%] rounded-2xl border border-white/10 bg-black/25 px-4 py-3 text-sm text-white/70">
                        <div className="animate-pulse">Thinking…</div>
                        <div className="mt-2 grid gap-2">
                          <div className="h-2 w-3/4 rounded bg-white/10" />
                          <div className="h-2 w-2/3 rounded bg-white/10" />
                          <div className="h-2 w-1/2 rounded bg-white/10" />
                        </div>
                      </div>
                    ) : null}
                  </div>
                )}
              </div>

              <form onSubmit={onSubmit} className="flex flex-col gap-3">
                <label className="text-sm text-white/70">Your message</label>

                <div className="relative">
                  <textarea
                    value={input}
                    onChange={(e: ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
                    rows={4}
                    placeholder="Type your issue here…"
                    className="w-full resize-none rounded-2xl border border-card-border bg-black/25 px-4 py-4 pr-24 text-sm outline-none ring-0 placeholder:text-white/35 focus:border-white/20"
                  />

                  <div className="absolute bottom-3 right-3">
                    <GlowButton disabled={!canSend} onClick={() => undefined}>
                      {loading ? "Sending…" : "Send"}
                    </GlowButton>
                  </div>
                </div>

                <div className="text-xs text-white/50">Don’t include passwords, OTPs, or card numbers.</div>
              </form>
            </div>
          </Card>
        ) : null}

        {/* Latest answer */}
        {activeTab === "answer" && lastAssistant ? (
          <Card>
            <div className="flex flex-col gap-3">
              <button
                type="button"
                onClick={() => setShowLatestAnswer((v) => !v)}
                className="flex items-center justify-between rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-left text-sm text-white/80 hover:bg-white/5"
              >
                <span className="font-semibold">Latest answer</span>
                <span className="text-xs text-white/50">{showLatestAnswer ? "Hide" : "Show"}</span>
              </button>

              {showLatestAnswer ? (
                <div className="rounded-2xl border border-white/10 bg-black/15 p-4">
                  <div className="whitespace-pre-wrap text-sm text-white/85">
                    {combinedStructured || lastAssistant.content}
                  </div>
                </div>
              ) : null}
            </div>
          </Card>
        ) : null}

        {/* Details */}
        {activeTab === "details" ? (
          <Card>
            <div className="flex flex-col gap-3">
              <button
                type="button"
                onClick={async () => {
                  const next = !showDetails;
                  setShowDetails(next);
                  if (next && traceId && !trace) await fetchTrace(traceId);
                }}
                className="flex items-center justify-between rounded-xl border border-white/10 bg-black/20 px-4 py-3 text-left text-sm text-white/80 hover:bg-white/5"
              >
                <span className="font-semibold">Details & transparency</span>
                <span className="text-xs text-white/50">{showDetails ? "Hide" : "Show"}</span>
              </button>

              {showDetails ? (
                <div className="text-xs text-white/60">
                  Optional technical details (workflow diagram and internal logs).
                </div>
              ) : null}

              {showDetails ? (
                <div className="rounded-2xl border border-white/10 bg-black/10 p-3">
                  <TracePanel trace={trace} />
                </div>
              ) : null}
            </div>
          </Card>
        ) : null}

        {/* Keep answer visible when there is no answer yet */}
        {activeTab === "answer" && !lastAssistant ? (
          <Card>
            <div className="text-sm text-white/65">No answer yet. Ask a question in the Chat tab.</div>
          </Card>
        ) : null}
      </div>
    </Container>
  );
}
