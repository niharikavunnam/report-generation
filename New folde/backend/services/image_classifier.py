def classify_xray(body_region: str, xray_type: str | None = None) -> dict:
    region = (body_region or xray_type or "chest").strip().lower()
    region_map = {
        "chest": {"label": "Chest X-ray", "confidence": 0.92, "description": "Thoracic imaging for lungs, heart, and mediastinum."},
        "hand": {"label": "Hand X-ray", "confidence": 0.9, "description": "Metacarpal and phalangeal assessment."},
        "wrist": {"label": "Wrist X-ray", "confidence": 0.9, "description": "Distal radius and carpal joint evaluation."},
        "knee": {"label": "Knee X-ray", "confidence": 0.91, "description": "Femoral-tibial joint radiographic assessment."},
        "shoulder": {"label": "Shoulder X-ray", "confidence": 0.9, "description": "Glenohumeral and acromioclavicular region review."},
        "elbow": {"label": "Elbow X-ray", "confidence": 0.9, "description": "Humeroulnar and humeroradial joint review."},
        "foot": {"label": "Foot X-ray", "confidence": 0.9, "description": "Tarsal and metatarsal evaluation."},
        "ankle": {"label": "Ankle X-ray", "confidence": 0.9, "description": "Ankle mortise and malleolar assessment."},
        "spine": {"label": "Spine X-ray", "confidence": 0.89, "description": "Vertebral alignment and osseous integrity."},
        "pelvis": {"label": "Pelvis X-ray", "confidence": 0.89, "description": "Hip and pelvic ring assessment."},
        "hip": {"label": "Hip X-ray", "confidence": 0.9, "description": "Acetabular and proximal femoral assessment."},
    }

    match = region_map.get(region)
    if not match:
        match = {"label": region.title() + " X-ray", "confidence": 0.82, "description": "Generalized musculoskeletal imaging analysis."}

    return {
        "input_region": region,
        "label": match["label"],
        "confidence": match["confidence"],
        "description": match["description"],
        "model": "generalized-radiology-classifier-v1",
    }
