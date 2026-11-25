import json

import poml
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from src.analysis.llm_retry import invoke_with_rate_limit_retry
from src.analysis.response_formats import (
    BATCH_MATCH_RESPONSE_FORMAT,
    MATCH_RESPONSE_FORMAT,
)

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_retries=0,
    timeout=60,
)


def _render_messages(prompt_path, context):
    rendered = json.loads(poml.poml(prompt_path, context=context, format="raw"))
    messages = []
    for message in rendered["messages"]:
        if message["speaker"] == "system":
            messages.append(SystemMessage(content=message["content"]))
        elif message["speaker"] == "human":
            messages.append(HumanMessage(content=message["content"]))
    return messages


def analyze_match(requirement: str, resume_evidence: str):
    messages = _render_messages(
        "src/prompts/match_analyzer.poml",
        {"requirement": requirement, "resume_evidence": resume_evidence},
    )
    structured_llm = llm.bind(
        response_format=MATCH_RESPONSE_FORMAT,
        reasoning_effort="low",
    )
    response = invoke_with_rate_limit_retry(structured_llm, messages)
    if not response.content:
        raise ValueError("Groq returned an empty match-analysis response.")
    return json.loads(response.content)


def analyze_matches(items):
    """Analyze a batch of (requirement, evidence_chunks) pairs in one LLM call."""
    evidence_ids = {}
    for _, chunks in items:
        for chunk in chunks:
            normalized = chunk.strip()
            if normalized and normalized not in evidence_ids:
                evidence_ids[normalized] = f"C{len(evidence_ids) + 1}"

    evidence_text = "\n\n".join(
        f"[{evidence_id}] {chunk}" for chunk, evidence_id in evidence_ids.items()
    ) or "No resume evidence was retrieved."

    requirements_text = "\n".join(
        f"{index}. Requirement: {requirement}\n"
        f"Evidence IDs: {', '.join(evidence_ids[chunk.strip()] for chunk in chunks if chunk.strip()) or 'none'}"
        for index, (requirement, chunks) in enumerate(items, start=1)
    )
    messages = _render_messages(
        "src/prompts/match_batch_analyzer.poml",
        {"requirements": requirements_text, "resume_evidence": evidence_text},
    )
    structured_llm = llm.bind(
        response_format=BATCH_MATCH_RESPONSE_FORMAT,
        reasoning_effort="low",
    )
    response = invoke_with_rate_limit_retry(structured_llm, messages)
    if not response.content:
        raise ValueError("Groq returned an empty batch match-analysis response.")

    parsed = json.loads(response.content)
    matches_by_id = {item["id"]: item for item in parsed.get("matches", [])}
    matches = []
    for index, (requirement, chunks) in enumerate(items, start=1):
        match = matches_by_id.get(index)
        if match is None:
            match = analyze_match(requirement, "\n\n".join(chunks))
        matches.append({"status": match["status"], "explanation": match["explanation"]})
    return matches
