import asyncio
from src.services.clinical_decision_service import create_clinical_decision_service


def test_clinical_decision_service_contract():
    """Contract test: service returns normalized shape expected by routers.
    Ensures nursing_interventions is a string, safety_considerations is a list,
    and clinical_context is a dict containing comorbidities/concerns.
    """
    svc = create_clinical_decision_service()
    assert svc is not None, "ClinicalDecisionService factory returned None"

    result = asyncio.run(
        svc.get_nursing_interventions(
            patient_condition="acute heart failure",
            severity="moderate",
            comorbidities=["diabetes"]
        )
    )

    assert isinstance(result, dict), f"Service must return a dict, got {type(result)}"

    assert "nursing_interventions" in result, "Missing nursing_interventions"
    assert isinstance(result["nursing_interventions"], str), "nursing_interventions must be a string"
    assert result["nursing_interventions"].strip(), "nursing_interventions should not be empty"

    assert "evidence_level" in result and isinstance(result["evidence_level"], str)
    assert "safety_considerations" in result and isinstance(result["safety_considerations"], list)
    assert "clinical_context" in result and isinstance(result["clinical_context"], dict)

    cc = result["clinical_context"]
    assert ("comorbidities" in cc) or ("concerns" in cc), "clinical_context should include comorbidities or concerns"
