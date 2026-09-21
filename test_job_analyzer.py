from src.analysis.job_analyzer import extract_requirements

with open("data/job_description/software_engineer.txt", "r") as file:
    job_description = file.read()

requirements = extract_requirements(job_description)

print("\n===== JOB REQUIREMENTS =====")

for category, items in requirements.items():
    print(f"\n{category.upper()}:")

    for item in items:
        print(f"- {item}")