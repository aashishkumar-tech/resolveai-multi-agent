from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from app.core.config import settings
from app.workflow import agents
from app.workflow.state import HierarchicalState


def build_graph():
    g = StateGraph(HierarchicalState)

    g.add_node("chief_manager", agents.chief_manager)

    g.add_node("analysis_manager", agents.analysis_manager)
    g.add_node("classifier_agent", agents.classifier_agent)
    g.add_node("researcher_agent", agents.researcher_agent)
    g.add_node("sentiment_agent", agents.sentiment_agent)

    g.add_node("content_manager", agents.content_manager)
    g.add_node("writer_agent", agents.writer_agent)
    g.add_node("formatter_agent", agents.formatter_agent)

    g.add_node("quality_manager", agents.quality_manager)
    g.add_node("reviewer_agent", agents.reviewer_agent)
    g.add_node("compliance_agent", agents.compliance_agent)

    g.add_edge(START, "chief_manager")

    def route(state: HierarchicalState):
        nxt = state.get("next_agent", "END")
        if nxt == "END":
            return END
        return nxt

    g.add_conditional_edges(
        "chief_manager",
        route,
        {
            "analysis_manager": "analysis_manager",
            "content_manager": "content_manager",
            "quality_manager": "quality_manager",
            "classifier_agent": "classifier_agent",
            "researcher_agent": "researcher_agent",
            "sentiment_agent": "sentiment_agent",
            "writer_agent": "writer_agent",
            "formatter_agent": "formatter_agent",
            "reviewer_agent": "reviewer_agent",
            "compliance_agent": "compliance_agent",
            END: END,
        },
    )

    g.add_edge("analysis_manager", "classifier_agent")
    g.add_edge("classifier_agent", "researcher_agent")
    g.add_edge("researcher_agent", "sentiment_agent")
    g.add_edge("sentiment_agent", "chief_manager")

    g.add_edge("content_manager", "writer_agent")
    g.add_edge("writer_agent", "formatter_agent")
    g.add_edge("formatter_agent", "chief_manager")

    g.add_edge("quality_manager", "reviewer_agent")
    g.add_edge("reviewer_agent", "compliance_agent")
    g.add_edge("compliance_agent", "chief_manager")

    compiled = g.compile()

    # Provide defaults via initial state in runner; settings here for parity
    _ = settings.max_iterations

    return compiled
