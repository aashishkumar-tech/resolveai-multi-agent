
import time
from dataclasses import dataclass, field


GROQ_PRICING = {
    "llama3-70b-8192": {"input": 0.59, "output": 0.79},
    "llama3-8b-8192": {"input": 0.05, "output": 0.08},
    "mixtral-8x7b-32768": {"input": 0.24, "output": 0.24},
}


@dataclass
class ConversationMetrics:
    trace_id: str
    model: str = "llama3-70b-8192"
    start_time: float = field(default_factory=time.time)
    input_tokens: int = 0
    output_tokens: int = 0
    agent_calls: int = 0
    tool_calls: int = 0

    @property
    def duration_seconds(self) -> float:
        return round(time.time() - self.start_time, 2)

    @property
    def estimated_cost_usd(self) -> float:
        p = GROQ_PRICING.get(self.model, {"input": 0.59, "output": 0.79})
        return round(
            (self.input_tokens / 1_000_000) * p["input"] +
            (self.output_tokens / 1_000_000) * p["output"], 6
        )

    def to_dict(self) -> dict:
        return {
            "trace_id": self.trace_id,
            "duration_seconds": self.duration_seconds,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "agent_calls": self.agent_calls,
            "tool_calls": self.tool_calls,
            "estimated_cost_usd": self.estimated_cost_usd,
        }


_registry: dict[str, ConversationMetrics] = {}


def start_tracking(trace_id: str, model: str = "llama3-70b-8192") -> ConversationMetrics:
    m = ConversationMetrics(trace_id=trace_id, model=model)
    _registry[trace_id] = m
    return m


def get_metrics(trace_id: str) -> ConversationMetrics | None:
    return _registry.get(trace_id)
