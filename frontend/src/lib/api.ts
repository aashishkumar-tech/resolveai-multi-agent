export type ChatResponse = {
  final_response: string;
  trace_id?: string;
  duration_s?: number;
  customer_name?: string;
  mobile_number?: string;
};

export type ChatRequest = {
  query: string;
  customer_name?: string;
  mobile_number?: string;
};

// API base URL - uses /api/v1 prefix for versioned endpoints
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export async function chat(payload: ChatRequest): Promise<ChatResponse> {
  const res = await fetch(`${API_BASE_URL}/api/v1/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    const text = await res.text();
    throw new Error(`API error ${res.status}: ${text}`);
  }

  return (await res.json()) as ChatResponse;
}

export async function healthCheck(): Promise<{ status: string; service: string }> {
  const res = await fetch(`${API_BASE_URL}/health`);
  if (!res.ok) {
    throw new Error(`Health check failed: ${res.status}`);
  }
  return res.json();
}
