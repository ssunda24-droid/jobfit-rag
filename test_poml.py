import poml

with open("data/job_descriptions/software_engineer.txt", "r") as file:
    job_description = file.read()

result = poml.poml(
    "src/prompts/job_analyzer.poml",
    context={
        "job_description": job_description
    },
    format="raw"
)

print("\n===== RENDERED POML PROMPT =====\n")
print(result)