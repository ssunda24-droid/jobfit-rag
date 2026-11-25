JOB_REQUIREMENTS_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "job_requirements",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "technical_skills": {"type": "array", "items": {"type": "string"}},
                "soft_skills": {"type": "array", "items": {"type": "string"}},
                "experience_requirements": {"type": "array", "items": {"type": "string"}},
                "responsibilities": {"type": "array", "items": {"type": "string"}},
            },
            "required": [
                "technical_skills",
                "soft_skills",
                "experience_requirements",
                "responsibilities",
            ],
            "additionalProperties": False,
        },
    },
}

MATCH_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "resume_match",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "status": {
                    "type": "string",
                    "enum": ["SUPPORTED", "PARTIAL", "MISSING"],
                },
                "explanation": {"type": "string"},
            },
            "required": ["status", "explanation"],
            "additionalProperties": False,
        },
    },
}

BATCH_MATCH_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "resume_matches",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "matches": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "integer"},
                            "status": {
                                "type": "string",
                                "enum": ["SUPPORTED", "PARTIAL", "MISSING"],
                            },
                            "explanation": {"type": "string"},
                        },
                        "required": ["id", "status", "explanation"],
                        "additionalProperties": False,
                    },
                }
            },
            "required": ["matches"],
            "additionalProperties": False,
        },
    },
}
