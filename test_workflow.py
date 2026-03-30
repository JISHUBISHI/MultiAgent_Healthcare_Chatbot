from agents import create_workflow


class FailingLLM:
    def invoke(self, *_args, **_kwargs):
        raise ConnectionError("offline for test")


def test_workflow_returns_offline_fallback_sections():
    workflow = create_workflow(FailingLLM(), None)
    result = workflow.invoke(
        {
            "user_input": "headache and fever for 2 days",
            "symptom_analysis": "",
            "medication_advice": "",
            "home_remedies": "",
            "diet_lifestyle": "",
            "doctor_recommendations": "",
            "error": "",
        }
    )

    assert "Structured Symptom Analysis" in result["symptom_analysis"]
    assert "IMPORTANT: CONSULT A DOCTOR BEFORE TAKING ANY MEDICATION" in result["medication_advice"]
    assert "Home Remedies & Self-Care" in result["home_remedies"]
    assert "Hydration & Monitoring" in result["diet_lifestyle"]
    assert "Best Specialist Type & Why" in result["doctor_recommendations"]
    assert "offline guidance used" in result["error"].lower()
