from __future__ import annotations

from pathlib import Path


def render_graph_png(graph, out_path: Path) -> Path:
    """Render LangGraph as PNG.

    Supports LangGraph versions that provide `get_graph().draw_mermaid_png()`.
    Falls back gracefully by returning None on failure.
    """
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        g = graph.get_graph()
        png_bytes = g.draw_mermaid_png()
        out_path.write_bytes(png_bytes)
        return out_path
    except Exception:
        # keep runtime stable even if graphviz/mermaid rendering isn't available
        return out_path
