def generate_explainability(findings: list) -> dict:
    evidence = []
    for item in findings:
        evidence.append({
            "area": item.get("name"),
            "confidence": item.get("confidence", 0.0),
            "severity": item.get("severity", "mild"),
            "interpretation": item.get("description", "Reviewed for radiographic significance."),
        })

    return {
        "model_notes": "This prototype uses a generalized detection pipeline to highlight probable abnormal regions for research review.",
        "evidence": evidence,
        "medical_disclaimer": "AI-generated findings are for research and educational purposes only and are not a substitute for diagnosis by a qualified radiologist.",
    }
