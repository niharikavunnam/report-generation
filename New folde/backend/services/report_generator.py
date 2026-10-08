from typing import Any


def generate_report(classification: dict, findings: list, patient_info: dict | None = None) -> str:
    patient_name = (patient_info or {}).get("patient_name") or "Patient"
    patient_id = (patient_info or {}).get("patient_id") or "N/A"
    clinical_notes = (patient_info or {}).get("clinical_notes") or "No additional clinical notes were provided."

    summary = findings[0]["name"] if findings else "No significant abnormality detected"
    conclusion = "The current findings are AI-generated for research and educational use only and do not replace a radiologist's interpretation."

    return (
        f"Radiology Impression:\n"
        f"Patient: {patient_name} | MRN/ID: {patient_id}\n"
        f"Exam Type: {classification.get('label', 'Generalized X-ray')}\n"
        f"Clinical Notes: {clinical_notes}\n\n"
        f"Findings: The study demonstrates a radiographic pattern consistent with {summary.lower()}. "
        f"The AI-based assessment identified several findings: "
        f"{'; '.join(item['name'] for item in findings[:3])}. "
        "The image was normalized and analyzed using a generalized medical imaging pipeline.\n\n"
        f"Impression: Based on the image characteristics and the algorithmic assessment, the case shows mild abnormalities requiring further expert review. "
        f"{conclusion}"
    )
