from __future__ import annotations

from langchain_core.messages import AIMessage

from app.workflow.llm import get_llm
from app.workflow.state import HierarchicalState
from app.workflow.tools import search_web


def chief_manager(state: HierarchicalState):
    activity_log = state.get("activity_log", [])
    iteration_count = state.get("iteration_count", 0)
    max_iterations = state.get("max_iterations", 15)
    department_status = state.get("department_status", {})

    if iteration_count >= max_iterations:
        next_agent = "END"
        decision = "Maximum iterations reached"
    elif not department_status.get("analysis"):
        next_agent = "analysis_manager"
        decision = "Delegating to Analysis Department for query processing"
    elif department_status.get("analysis") == "complete" and not department_status.get("content"):
        next_agent = "content_manager"
        decision = "Analysis complete, delegating to Content Department"
    elif department_status.get("content") == "complete" and not department_status.get("quality"):
        next_agent = "quality_manager"
        decision = "Content ready, delegating to Quality Department"
    elif department_status.get("quality") == "complete":
        next_agent = "END"
        decision = "All departments complete, finalizing response"
    else:
        next_agent = "END"
        decision = "Workflow complete"

    activity_log.append(
        {
            "level": "chief",
            "agent": "chief_manager",
            "iteration": iteration_count,
            "action": f"Routing to {next_agent}",
            "decision": decision,
        }
    )

    return {
        "messages": [AIMessage(content=f"Chief Manager: {decision}")],
        "current_level": "chief",
        "next_agent": next_agent,
        "iteration_count": iteration_count + 1,
        "activity_log": activity_log,
    }


def analysis_manager(state: HierarchicalState):
    activity_log = state.get("activity_log", [])
    department_status = state.get("department_status", {})

    activity_log.append(
        {
            "level": "department",
            "agent": "analysis_manager",
            "action": "Dispatching workers: classifier, researcher, sentiment",
        }
    )

    department_status["analysis"] = "in_progress"

    return {
        "messages": [AIMessage(content="Analysis Manager: starting analysis workers")],
        "current_level": "department",
        "active_department": "analysis",
        "department_status": department_status,
        "next_agent": "classifier_agent",
        "activity_log": activity_log,
    }


def classifier_agent(state: HierarchicalState):
    llm = get_llm()
    query = state["customer_query"]

    prompt = (
        "Classify this customer support query into a type (technical/billing/account/general) "
        "and urgency (low/medium/high/critical). Return JSON with keys query_type, urgency_level.\n\n"
        f"Query: {query}"
    )

    result = llm.invoke(prompt).content

    return {
        "messages": [AIMessage(content=f"Classifier: {result}")],
        "query_classification": result,
        "team_outputs": {**state.get("team_outputs", {}), "classifier": result},
        "next_agent": "researcher_agent",
    }


def researcher_agent(state: HierarchicalState):
    query = state["customer_query"]
    results = search_web.invoke(query)  # tool invocation

    return {
        "messages": [AIMessage(content="Researcher: gathered web research")],
           "research_data": results,
        "team_outputs": {**state.get("team_outputs", {}), "researcher": results},
        "next_agent": "sentiment_agent",
    }


def sentiment_agent(state: HierarchicalState):
    llm = get_llm()
    query = state["customer_query"]

    prompt = (
        "Analyze the sentiment of this customer message (positive/neutral/negative) and "
        "briefly explain.\n\n"
        f"Message: {query}"
    )

    result = llm.invoke(prompt).content

    department_status = state.get("department_status", {})
    department_status["analysis"] = "complete"

    return {
        "messages": [AIMessage(content=f"Sentiment: {result}")],
        "sentiment_analysis": result,
        "department_status": department_status,
        "team_outputs": {**state.get("team_outputs", {}), "sentiment": result},
        "next_agent": "chief_manager",
    }


def content_manager(state: HierarchicalState):
    activity_log = state.get("activity_log", [])
    department_status = state.get("department_status", {})

    activity_log.append(
        {
            "level": "department",
            "agent": "content_manager",
            "action": "Dispatching workers: writer, formatter",
        }
    )

    department_status["content"] = "in_progress"

    return {
        "messages": [AIMessage(content="Content Manager: starting content workers")],
        "current_level": "department",
        "active_department": "content",
        "department_status": department_status,
        "next_agent": "writer_agent",
        "activity_log": activity_log,
    }


def writer_agent(state: HierarchicalState):
    llm = get_llm()

    query = state["customer_query"]
    research = state.get("research_data", "")
    classification = state.get("query_classification", "")
    sentiment = state.get("sentiment_analysis", "")

    customer_name = (state.get("customer_name") or "").strip() or "there"
    # Show only last 4 digits for privacy, but let the user recognize it
    mobile_last4 = (state.get("mobile_number") or "").strip()
    mobile_hint = f" (ending {mobile_last4[-4:]})" if len(mobile_last4) >= 4 else ""

    prompt = (
        "You are a customer support assistant. Write a friendly, clear, actionable response.\n"
        "Rules:\n"
        "- Personalize greeting using the provided customer name.\n"
        "- Do NOT use placeholders like [Your Name], [Customer name].\n"
        "- Keep it concise and practical.\n"
        "- Prefer bullet points.\n"
        "- Include a short 'Next questions' section (max 3 questions) only if needed.\n"
        "\n"
        f"Customer name: {customer_name}\n"
        f"Customer mobile hint: {mobile_hint}\n"
        f"Customer issue: {query}\n\n"
        f"Classification: {classification}\n\nSentiment: {sentiment}\n\n"
        f"Relevant research (if any): {research}\n\n"
        "Output format (use these headings exactly):\n"
        "Greeting:\n"
        "Summary:\n"
        "What to do now:\n"
        "What happens next:\n"
        "Closing:\n"
    )

    result = llm.invoke(prompt).content

    return {
        "messages": [AIMessage(content="Writer: drafted response")],
        "draft_response": result,
        "team_outputs": {**state.get("team_outputs", {}), "writer": result},
        "next_agent": "formatter_agent",
    }


def formatter_agent(state: HierarchicalState):
    llm = get_llm()
    draft = state.get("draft_response", "")

    prompt = (
        "Improve readability of this support response without changing facts.\n"
        "Rules:\n"
        "- Keep headings: Greeting, Summary, What to do now, What happens next, Closing\n"
        "- Turn steps into short bullets.\n"
        "- Ensure no placeholders like [Your Name] remain.\n\n"
        f"Draft:\n{draft}"
    )

    result = llm.invoke(prompt).content

    department_status = state.get("department_status", {})
    department_status["content"] = "complete"

    return {
        "messages": [AIMessage(content="Formatter: formatted response")],
        "formatted_response": result,
        "department_status": department_status,
        "team_outputs": {**state.get("team_outputs", {}), "formatter": result},
        "next_agent": "chief_manager",
    }


def quality_manager(state: HierarchicalState):
    activity_log = state.get("activity_log", [])
    department_status = state.get("department_status", {})

    activity_log.append(
        {
            "level": "department",
            "agent": "quality_manager",
            "action": "Dispatching workers: reviewer, compliance",
        }
    )

    department_status["quality"] = "in_progress"

    return {
        "messages": [AIMessage(content="Quality Manager: starting quality workers")],
        "current_level": "department",
        "active_department": "quality",
        "department_status": department_status,
        "next_agent": "reviewer_agent",
        "activity_log": activity_log,
    }


def reviewer_agent(state: HierarchicalState):
    llm = get_llm()
    formatted = state.get("formatted_response", "")

    prompt = (
        "Review this response for clarity, correctness, tone, and completeness. "
        "Return bullet points with issues and improvements.\n\n"
        f"Response: {formatted}"
    )

    result = llm.invoke(prompt).content

    return {
        "messages": [AIMessage(content="Reviewer: completed review")],
        "quality_review": result,
        "team_outputs": {**state.get("team_outputs", {}), "reviewer": result},
        "next_agent": "compliance_agent",
    }


def compliance_agent(state: HierarchicalState):
    llm = get_llm()
    formatted = state.get("formatted_response", "")

    prompt = (
        "Check this response for compliance issues (no sensitive data, no prohibited claims, "
        "no unsafe instructions). If issues, list them; otherwise return 'COMPLIANT'.\n\n"
        f"Response: {formatted}"
    )

    result = llm.invoke(prompt).content

    department_status = state.get("department_status", {})
    department_status["quality"] = "complete"

    final = formatted

    return {
        "messages": [AIMessage(content="Compliance: check complete")],
        "compliance_check": result,
        "final_response": final,
        "department_status": department_status,
        "team_outputs": {**state.get("team_outputs", {}), "compliance": result},
        "next_agent": "chief_manager",
    }
