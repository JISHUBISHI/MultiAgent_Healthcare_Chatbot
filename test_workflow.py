import sys
from config import initialize_clients
from agents import create_workflow, AgentState

def main():
    llm, tavily_client, error = initialize_clients()
    if error:
        print("Initialization Error:", error)
        sys.exit(1)
        
    print("Clients initialized. Creating workflow...")
    workflow = create_workflow(llm, tavily_client)
    
    initial_state = {
        "user_input": "headache and fever",
        "symptom_analysis": "",
        "medication_advice": "",
        "home_remedies": "",
        "diet_lifestyle": "",
        "doctor_recommendations": "",
        "error": ""
    }
    
    print("Invoking workflow...")
    try:
        result = workflow.invoke(initial_state)
        print("Result keys:", result.keys())
    except Exception as e:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
