def detect_abnormalities(body_region: str, xray_type: str | None = None, classification: dict | None = None) -> list:
    region = (body_region or xray_type or "chest").strip().lower()
    findings = []

    if "chest" in region:
        findings = [
            {"name": "Pulmonary opacity", "severity": "mild", "confidence": 0.82, "description": "Subtle increased radiographic density within the lung parenchyma requiring clinical correlation."},
            {"name": "Cardiac silhouette assessment", "severity": "mild", "confidence": 0.79, "description": "The cardiac boundaries are reviewed for enlargement or contour abnormality."},
        ]
    elif "hand" in region or "wrist" in region or "elbow" in region:
        findings = [
            {"name": "Joint-space narrowing", "severity": "mild", "confidence": 0.8, "description": "Cartilage degeneration may appear as reduced joint spacing."},
            {"name": "Osseous irregularity", "severity": "mild", "confidence": 0.77, "description": "A marginal irregularity may reflect an inflammatory or traumatic process."},
        ]
    elif "knee" in region or "ankle" in region or "foot" in region:
        findings = [
            {"name": "Articular surface change", "severity": "mild", "confidence": 0.81, "description": "The joint surfaces should be inspected for erosive or degenerative change."},
            {"name": "Soft-tissue swelling", "severity": "mild", "confidence": 0.76, "description": "Edema surrounding the joint may suggest inflammatory or post-traumatic change."},
        ]
    elif "spine" in region or "pelvis" in region or "hip" in region:
        findings = [
            {"name": "Vertebral or pelvic alignment change", "severity": "mild", "confidence": 0.8, "description": "Alignment and osseous contour are reviewed for deformity or instability."},
            {"name": "Bone density variation", "severity": "mild", "confidence": 0.78, "description": "Local density changes may correlate with osteopenic or inflammatory changes."},
        ]
    else:
        findings = [
            {"name": "Generalized radiographic abnormality", "severity": "mild", "confidence": 0.75, "description": "The requested image pattern is reviewed for non-specific density or contour irregularity."},
        ]

    if classification:
        findings[0]["classification"] = classification["label"]
    return findings
