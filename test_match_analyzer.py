from src.analysis.match_analyzer import analyze_match


requirement = "Experience with TypeScript"

resume_evidence = """
The candidate developed 25+ modular and reusable React.js components
for an enterprise-scale agent portal. They also worked on complex
state-driven user journeys and wrote tests using Jest and React Testing Library.
"""


result = analyze_match(
    requirement=requirement,
    resume_evidence=resume_evidence
)

print("\n===== MATCH RESULT =====")
print("Status:", result["status"])
print("Explanation:", result["explanation"])