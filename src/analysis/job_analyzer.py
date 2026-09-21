import json
import poml
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

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

    response = llm.invoke(langchain_messages)

    return json.loads(response.content)