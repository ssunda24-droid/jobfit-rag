import json
import poml
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from src.analysis.llm_retry import invoke_with_rate_limit_retry
from src.analysis.response_formats import JOB_REQUIREMENTS_RESPONSE_FORMAT

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


def extract_requirements(job_description: str):

    result = poml.poml(
        "src/prompts/job_analyzer.poml",
        context={
            "job_description": job_description
        },
        format="raw"
    )

    result = json.loads(result)

    messages = result["messages"]

    langchain_messages = []

    for message in messages:
        if message["speaker"] == "system":
            langchain_messages.append(
                SystemMessage(content=message["content"])
            )

        elif message["speaker"] == "human":
            langchain_messages.append(
                HumanMessage(content=message["content"])
            )

    structured_llm = llm.bind(
        response_format=JOB_REQUIREMENTS_RESPONSE_FORMAT,
        reasoning_effort="low",
    )
    response = invoke_with_rate_limit_retry(structured_llm, langchain_messages)

    if not response.content:
        raise ValueError("Groq returned an empty job-requirements response.")

    return json.loads(response.content)
